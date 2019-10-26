import sys
import math
import collections
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import receiver

LINE_COLORS = [
        (0, 1, 0), (1, 0, 0), (0, 0, 1),
        (1, 1, 0), (0, 1, 1), (1, 0, 1)]

MAX_POINTS = 1000

class Scope:
    def __init__(self):
        self.window = glfw.create_window(640, 480, "oscosc", None, None)

        self.y_per_div = 0.5
        self.time_per_div = 0.5

        self.num_divs_v = 8
        self.num_divs_h = 8

        self.grid_color = (0.7, 0.7, 0.7)
        
        self.lines = dict()
        self.lines['/x'] = collections.deque(maxlen=MAX_POINTS)
        self.lines['/y'] = collections.deque(maxlen=MAX_POINTS)

        # Use timestamp of the first received OSC message or bundle as t=0
        self.time_offset = 0.0
        self.time_offset_ready = False

    def run(self):
        # launch receiver thread
        self.receiver = receiver.Receiver()
        self.receiver.start_thread(12345)
        # rendering loop
        glfw.make_context_current(self.window)
        while not glfw.window_should_close(self.window):
            self.process_messages()
            self.draw()
            glfw.swap_buffers(self.window)
            glfw.poll_events()
        # cleanup
        self.receiver.stop_thread()
    
    def draw(self):
        width, height = glfw.get_framebuffer_size(self.window)
        glViewport(0, 0, width, height)

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        glPushMatrix()
        glScale(0.3, 0.3, 1)

        self.draw_grid()
        self.plot()

        glPopMatrix()

    def draw_grid(self):
        glColor3dv(self.grid_color)

        left = -self.time_per_div * self.num_divs_h / 2
        right = self.time_per_div * self.num_divs_h / 2
        bottom = -self.y_per_div * self.num_divs_v / 2
        top = self.y_per_div * self.num_divs_v / 2
        # Horizontal lines
        glBegin(GL_LINES)
        for i in range(-self.num_divs_v // 2, self.num_divs_v // 2 + 1):
            glVertex2d(left, i * self.y_per_div)
            glVertex2d(right, i * self.y_per_div)
        glEnd()
        # Vertical lines
        glBegin(GL_LINES)
        for i in range(-self.num_divs_h // 2, self.num_divs_h // 2 + 1):
            glVertex2d(i * self.time_per_div, bottom)
            glVertex2d(i * self.time_per_div, top)
        glEnd()

    # Plot data sequences
    def plot(self):
        for i, pair in enumerate(self.lines.items()):
            addr, line = pair
            self.plot_line(line, LINE_COLORS[i % len(LINE_COLORS)])

    # Plot single line
    def plot_line(self, line, color):
        glColor3dv(color)
        glBegin(GL_LINE_STRIP)
        for t, value in line:
            glVertex2d(t - self.time_offset, value)
        glEnd()

    # Process incoming OSC messages
    def process_messages(self):
        while self.receiver.available():
            msgs, timestamp, sender = self.receiver.get()
            if not self.time_offset_ready:
                self.time_offset = timestamp
                self.time_offset_ready = True
            for msg in msgs:
                self.add_data(msg, timestamp, sender)

    def add_data(self, msg, timestamp, sender):
        # TODO currently, wildcard in OSC address is not supported
        if msg.address in self.lines:
            self.lines[msg.address].append(
                    (timestamp, msg.params[0]))

if __name__ == '__main__':
    if not glfw.init():
        sys.exit(-1)
    
    try:
        scope = Scope()
        scope.run()
    finally:
        glfw.terminate()

import sys
import math
import collections
import time
import pyglet
# pyglet has its own OpenGL wrapper but it needs ctypes arguments.
# However PyOpenGL can be used.
# (See https://pyglet.readthedocs.io/en/stable/programming_guide/gl.html )
from OpenGL.GL import *
import imgui
from imgui.integrations.pyglet import PygletRenderer
import receiver

LINE_COLORS = [
        (0, 1, 0), (1, 0, 0), (0, 0, 1),
        (1, 1, 0), (0, 1, 1), (1, 0, 1)]

MAX_POINTS = 1000

TIME_PER_DIV_OPTIONS = [10.0, 5.0, 1.0, 0.5, 0.1, 0.05, 0.01]
Y_PER_DIV_OPTIONS = [10.0, 5.0, 1.0, 0.5, 0.1, 0.05, 0.01]

class Scope(pyglet.window.Window):
    def __init__(self):
        super().__init__(caption="oscosc", resizable=True)

        self.y_per_div = 0.5
        self.time_per_div = 0.5
        self.y_per_div_selected = 3
        self.time_per_div_selected = 3

        self.num_divs_v = 8
        self.num_divs_h = 8

        self.grid_color = (0.7, 0.7, 0.7)
        
        self.lines = dict()

        # Use timestamp of the first received OSC message or bundle as t=0
        self.time_offset = 0.0
        self.time_offset_ready = False

        self.start_time = 0.0

        # List of OSC addresses received
        self.addresses = set()

        # launch receiver thread
        self.receiver = receiver.Receiver()
        self.receiver.start_thread(12345)

        # Initialize IMGUI for pyglet
        # (See https://github.com/swistakm/pyimgui/blob/master/doc/examples/integrations_pyglet.py)
        imgui.create_context()
        self.imgui_renderer = PygletRenderer(self)

        pyglet.clock.schedule_interval(self.update, 1 / 60)

    # called 60 times per second
    def update(self, dt):
        # In pyglet, state update is separated from drawing
        self.process_messages()
        self.do_gui()

    def on_close(self):
        super().on_close()
        # cleanup
        self.receiver.stop_thread()
        self.imgui_renderer.shutdown()

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)

    # called each frame
    def on_draw(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        glPushMatrix()
        glScaled(0.7, 0.7, 1)

        glScaled(
            2 / (self.time_per_div * self.num_divs_h),
            2 / (self.y_per_div * self.num_divs_v),
            1)

        self.draw_grid()
        self.plot()

        glPopMatrix()

        # GUI comes in front of other things
        self.imgui_renderer.render(imgui.get_draw_data())

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
        glPushMatrix()
        # t=0 is the left end of the grid
        glTranslated(-self.num_divs_h * self.time_per_div / 2, 0, 0)
        # scroll
        glTranslated(
                -max(0, self.get_time() - self.num_divs_h*self.time_per_div),
                0, 0)

        for i, pair in enumerate(self.lines.items()):
            addr, line = pair
            self.plot_line(line, LINE_COLORS[i % len(LINE_COLORS)])

        glPopMatrix()

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
                self.start_time = time.time()
            for msg in msgs:
                self.add_data(msg, timestamp, sender)

    def add_data(self, msg, timestamp, sender):
        # TODO currently, wildcard in OSC address is not supported
        self.addresses.add(msg.address)
        if msg.address in self.lines:
            self.lines[msg.address].append(
                    (timestamp, msg.params[0]))

    def do_gui(self):
        imgui.new_frame()

        imgui.begin("win", closable=False)

        changed, self.time_per_div_selected = imgui.combo(
            "TIME/DIV", self.time_per_div_selected,
            [str(option) for option in TIME_PER_DIV_OPTIONS])
        if changed:
            self.time_per_div = TIME_PER_DIV_OPTIONS[self.time_per_div_selected]

        changed, self.y_per_div_selected = imgui.combo(
            "Y/DIV", self.y_per_div_selected,
            [str(option) for option in Y_PER_DIV_OPTIONS])
        if changed:
            self.y_per_div = Y_PER_DIV_OPTIONS[self.y_per_div_selected]

        imgui.text("Values")
        for addr in self.addresses:
            changed, selected = imgui.selectable(addr, addr in self.lines)
            if changed and selected:
                self.lines[addr] = collections.deque(maxlen=MAX_POINTS)
            elif changed and not selected:
                del self.lines[addr]

        imgui.end()

        # imgui.render() in on_draw caused a "newFrame is not called" error on Windows,
        # therefore we invoke it here
        imgui.render()

    def get_time(self):
        return time.time() - self.start_time

if __name__ == '__main__':
    scope = Scope()
    pyglet.app.run()

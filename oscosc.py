import sys
import math
import collections
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import imgui
from imgui.integrations.glfw import GlfwRenderer
import receiver

LINE_COLORS = [
        (0, 1, 0), (1, 0, 0), (0, 0, 1),
        (1, 1, 0), (0, 1, 1), (1, 0, 1)]

MAX_POINTS = 1000

class Scope:
    def __init__(self):
        # pyimgui GLFW backend uses Programmable Pipeline.
        # (See the definition of GlfwRenderer at https://github.com/swistakm/pyimgui/blob/master/imgui/integrations/glfw.py)
        # GLFW initializes OpenGL 1.0 by default (cf. https://www.glfw.org/docs/latest/window_guide.html#window_hints_values ), window hints are needed.
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

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

        # OpenGL context must be made current before GlfwRenderer init
        # Forgetting this leads to a NullFunctionError of glGenVertexArrays
        glfw.make_context_current(self.window)
        # Initialize IMGUI for GLFW
        # (See https://github.com/swistakm/pyimgui/blob/master/doc/examples/integrations_glfw3.py)
        imgui.create_context()
        self.imgui_renderer = GlfwRenderer(self.window)

        # rendering loop
        while not glfw.window_should_close(self.window):
            self.process_messages()
            self.imgui_renderer.process_inputs()
            self.draw()
            glfw.swap_buffers(self.window)
            glfw.poll_event()

        # cleanup
        self.receiver.stop_thread()
    
    def draw(self):
        width, height = glfw.get_framebuffer_size(self.window)
        glViewport(0, 0, width, height)

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        self.do_gui()

        glPushMatrix()
        glScaled(0.3, 0.3, 1)

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
        glPushMatrix()
        # t=0 is the left end of the grid
        glTranslated(-self.num_divs_h * self.time_per_div / 2, 0, 0)
        # scroll
        glTranslated(
                -max(0, glfw.get_time() - self.num_divs_h*self.time_per_div),
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
                glfw.set_time(0)
            for msg in msgs:
                self.add_data(msg, timestamp, sender)

    def add_data(self, msg, timestamp, sender):
        # TODO currently, wildcard in OSC address is not supported
        if msg.address in self.lines:
            self.lines[msg.address].append(
                    (timestamp, msg.params[0]))

    def do_gui(self):
        imgui.new_frame()

        imgui.begin("win", closable=False)
        imgui.text("hoge")
        imgui.end()

        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())

if __name__ == '__main__':
    if not glfw.init():
        sys.exit(-1)
    
    try:
        scope = Scope()
        scope.run()
    finally:
        glfw.terminate()

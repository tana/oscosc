import sys
import math
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from pythonosc import osc_server
from pythonosc import dispatcher

LINE_COLORS = [
        (0, 1, 0), (1, 0, 0), (0, 0, 1),
        (1, 1, 0), (0, 1, 1), (1, 0, 1)]

class Scope:
    def __init__(self):
        self.window = glfw.create_window(640, 480, "oscosc", None, None)

        self.y_per_div = 0.5
        self.time_per_div = 0.5

        self.num_divs_v = 8
        self.num_divs_h = 8

        self.grid_color = (0.7, 0.7, 0.7)
        
        self.max_points = 10000

    def run(self):
        glfw.make_context_current(self.window)
        #self.last_time = glfw.get_time()
        while not glfw.window_should_close(self.window):
            self.draw()
            #print(1 / (glfw.get_time() - self.last_time))
            #self.last_time = glfw.get_time()
            glfw.swap_buffers(self.window)
            glfw.poll_events()
    
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
        glColor3fv(self.grid_color)

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
        pass

if __name__ == '__main__':
    if not glfw.init():
        sys.exit(-1)
    
    try:
        scope = Scope()
        scope.run()
    finally:
        glfw.terminate()

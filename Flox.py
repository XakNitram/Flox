import pyglet

from boid import Flock
from shader import get_default_shader, World
from vectors import Vec2


class Simulation:
    FPS = 30.

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        self.window = pyglet.window.Window(width, height, "Flox")
        self.fps = pyglet.window.FPSDisplay(self.window)

        self.shader = get_default_shader()
        self.projection = World(self.shader)
        self.projection.set(width, height)

        self.flock = Flock(50, Vec2(0., 0.), min(width, height) / 3)

    def update(self, dt: float):
        self.flock.update(dt)

    def on_draw(self):
        self.window.clear()

        with self.shader:
            self.flock.draw()

        self.fps.draw()

    def run(self):
        self.window.push_handlers(self.on_draw)
        pyglet.clock.schedule_interval(self.update, 1. / self.FPS)
        pyglet.app.run()


if __name__ == '__main__':
    sim = Simulation(960, 720)
    sim.run()

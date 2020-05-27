import pyglet

from boid import Flock
from timer import Timer
from vectors import Vec2


class Simulation:
    FPS = 30.

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        self.timer = Timer()

        self.window = pyglet.window.Window(width, height, "Flox")
        self.fps = pyglet.window.FPSDisplay(self.window)

        self.flock = Flock(150, Vec2(0., 0.), min(width, height) / 3)
        self.flock.renderer.set_world(width, height)

    def update(self, dt: float):
        # self.timer.timed(self.flock.update)(dt)
        self.flock.update(dt)

    def on_draw(self):
        self.window.clear()

        self.fps.draw()
        # self.timer.timed(self.flock.draw)()
        self.flock.draw()

    def on_close(self):
        self.timer.show_graph()

    def run(self):
        self.window.push_handlers(self.on_draw)
        self.window.push_handlers(self.on_close)
        pyglet.clock.schedule_interval(self.update, 1. / self.FPS)
        pyglet.app.run()


if __name__ == '__main__':
    sim = Simulation(1440, 1080)
    sim.run()

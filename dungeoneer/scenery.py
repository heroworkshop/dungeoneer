from contextlib import suppress
from random import randint

import pygame


class VisualEffect(pygame.sprite.Sprite):
    FOREVER = -1

    def __init__(self, x, y, filmstrip, frame_length=200, repeats=0, reverse=False, motion=iter([])):
        super().__init__()
        self.filmstrip = filmstrip
        if reverse:
            self.filmstrip = self.filmstrip[::-1]
        self.repeats = repeats
        self.frame_length = frame_length
        self.frame = 0
        self.image = self.filmstrip[self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.next_frame_t = pygame.time.get_ticks() + self.frame_length
        self.motion = motion

    def update(self):
        self.move()
        self.animate()

    def move(self):
        with suppress(StopIteration):
            dx, dy = next(self.motion)
            x, y = self.rect.center
            self.rect.center = x + dx, y + dy

    def animate(self):
        t = pygame.time.get_ticks()
        if t > self.next_frame_t:
            self.frame += 1
            self.next_frame_t = pygame.time.get_ticks() + self.frame_length
        if self.frame == len(self.filmstrip):
            if self.repeats:
                self.frame = 0
                self.repeats -= 1
            else:
                self.kill()
                return
        self.image = self.filmstrip[self.frame]


class ScenerySprite(VisualEffect):
    def __init__(self, x, y, filmstrip, frame_length=1200, reverse=False, scale=1, animated=True):
        super().__init__(x, y, filmstrip, frame_length=frame_length, repeats=self.FOREVER,
                         reverse=reverse)
        self.animated = animated
        self.vitality = 1000
        # Put different items of scenery out of sync with each other...
        self.frame = (x + y) % len(self.filmstrip)  # in space...
        if self.animated:
            self.next_frame_t += randint(0, self.frame_length)  # and, if animated, in time.

    def on_hit(self):
        pass

    def update(self):
        if self.animated:
            self.animate()


def parabolic_motion(arc_width, steps, dy, g=1):
    direction = 1 if arc_width > 1 else -1
    if direction == -1:
        arc_width = abs(arc_width)

    dx = arc_width / steps
    result = []
    x = 0
    prev_x = 0
    while x < arc_width:
        x += dx
        result.append((direction * (int(x) - int(prev_x)), int(dy)))
        dy += g
        prev_x = x
    return result
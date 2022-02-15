from itertools import chain
from random import randint
import random

import pygame


class Squiggly(pygame.sprite.Sprite):
    def __init__(self, x, y, filmstrip, velocity=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.filmstrip = self.make_filmstrip(filmstrip[0])
        self.frame = 0
        self.image = self.filmstrip[self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.dx, self.dy = velocity  # unit vector. Actual velocity is speed x this value
        self.facing = (0, 1)  # direction the actor is facing
        self.speed = 1
        self._connected_sprites = []

    def make_filmstrip(self, image):
        return [image]

    def move(self, solid_object_group, bounds: pygame.rect):
        if not self.dx and not self.dy:
            return
        vx, vy = self.dx * self.speed, self.dy * self.speed
        self.frame = (self.frame + 1) % len(self.filmstrip)

        x, y = self.rect.center
        self.image = self.filmstrip[self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.rect.centerx += vx

        if self.collided(solid_object_group) or self.rect.right > bounds.right or self.rect.left < bounds.left:
            self.rect.centerx -= vx
            vx = 0
            self.dx = -self.dx
        self.rect.centery += vy
        if self.collided(solid_object_group) or self.rect.bottom > bounds.bottom \
                or self.rect.top < bounds.top:
            self.rect.centery -= vy
            vy = 0
            self.dy = -self.dy
        for sprite in self._connected_sprites:
            sprite.rect.x += vx
            sprite.rect.y += vy

    def collided(self, group):
        collisions = pygame.sprite.spritecollide(self, group, dokill=False,
                                                 collided=pygame.sprite.collide_rect_ratio(0.8))
        return any([c is not self for c in collisions])


class Throbber(Squiggly):
    def make_filmstrip(self, image):
        filmstrip = []
        rect = image.get_rect()
        for i in chain(range(-5, 5), (5, ) * 5, range(5, -5, -1)):
            width = rect.width + i
            height = rect.height + i
            frame = pygame.transform.smoothscale(image, (width, height))
            filmstrip.append(frame)
        return filmstrip


class Wobbler(Squiggly):
    def __init__(self, *args, amplitude=50, **kwargs):
        self.offset = (0, 0)
        self.amplitude = amplitude
        super().__init__(*args, **kwargs)

    def make_filmstrip(self, image):
        filmstrip = []
        rect = image.get_rect()
        for i in chain(range(-self.amplitude, self.amplitude), range(self.amplitude, -self.amplitude, -1)):
            width = rect.width - i
            height = rect.height + i
            frame = pygame.transform.smoothscale(image, (width, height))
            filmstrip.append(frame)
        return filmstrip


class Jaggedy(Squiggly):
    def __init__(self, *args, frequency=50, **kwargs):
        self.offset = (0, 0)
        self.frequency = frequency
        super().__init__(*args, **kwargs)

    def move(self, solid_object_group, bounds: pygame.rect):
        dx, dy = self.offset
        x, y = self.rect.center
        self.rect.center = x - dx, y - dy
        self.offset = 0, 0
        if randint(0, self.frequency) == 1:
            self.offset = random.choice([-20, -10, 10, 20]), random.choice([-20, -10, 10, 20])
            dx, dy = self.offset
            x, y = self.rect.center
            self.rect.center = x + dx, y + dy
        super().move(solid_object_group, bounds)

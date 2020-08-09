from enum import Enum

import pygame

from dungeoneer.interfaces import Observer


class Direction(Enum):
    LEFT_TO_RIGHT = (1, 0)
    RIGHT_TO_LEFT = (-1, 0)
    TOP_DOWN = (0, 1)
    BOTTOM_UP = (0, -1)


class ScoreBar(pygame.sprite.Sprite, Observer):
    def __init__(self, x, y, unit_filmstrip, score, score_per_unit=10,
                 direction=Direction.LEFT_TO_RIGHT, frame_length=1):
        super().__init__()
        self.unit_filmstrip = unit_filmstrip
        self.frame = 0
        self.next_frame_t = 0
        self.frame_length = frame_length
        self.x = x
        self.y = y
        self.direction = direction
        self.score = score
        self.score_per_unit = score_per_unit
        self.image = None
        self.rect = None
        self.filmstrip = self.render_filmstrip(score)
        self.animate()

    def notify(self, value):
        self.score = value
        self.filmstrip = self.render_filmstrip(value)
        self.image = self.filmstrip[self.frame]
        self.update_rect()

    def render_filmstrip(self, value):
        return [self.render_bar(value, image) for image in self.unit_filmstrip]

    def render_bar(self, score, frame_image):
        unit_image = frame_image
        n = score // self.score_per_unit
        width, height = unit_image.get_rect().size
        dx, dy = self.direction.value
        x, y = 0, 0
        dx = abs(dx * width)
        dy = abs(dy * height)
        if dx:
            width *= n
        else:
            height *= n

        image = pygame.Surface((width, height), flags=pygame.SRCALPHA)
        while n:
            image.blit(unit_image, (x, y))
            x += dx
            y += dy
            n -= 1
        return image

    def update_rect(self):
        self.rect = self.image.get_rect()
        if self.direction in (Direction.LEFT_TO_RIGHT, Direction.TOP_DOWN):
            self.rect.topleft = (self.x, self.y)
        elif self.direction in (Direction.RIGHT_TO_LEFT,):
            self.rect.topright = (self.x, self.y)
        elif self.direction in (Direction.BOTTOM_UP,):
            self.rect.bottomleft = (self.x, self.y)

    def update(self):
        self.animate()

    def animate(self):
        t = pygame.time.get_ticks()
        if t > self.next_frame_t:
            self.frame += 1
            self.next_frame_t = pygame.time.get_ticks() + self.frame_length
        if self.frame == len(self.filmstrip):
            self.frame = 0

        self.image = self.filmstrip[self.frame]
        self.update_rect()
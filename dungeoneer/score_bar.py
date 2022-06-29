from functools import lru_cache

import pygame

from dungeoneer.fonts import make_font
from dungeoneer.interfaces import Observer, Item, Direction


class ScoreBar(pygame.sprite.Sprite, Observer):
    def __init__(self, x: int, y: int, unit_filmstrip, score: int, score_per_unit=10,
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

    def on_update(self, attribute, value: Item):
        self.score = value.count if value else 0
        self.filmstrip = self.render_filmstrip(self.score)
        self.image = self.filmstrip[self.frame]
        self.update_rect()

    def render_filmstrip(self, value):
        return [self.render_bar(value, image) for image in self.unit_filmstrip]

    def render_bar(self, score, frame_image):
        score = max(score, 0)
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

        image = pygame.Surface((max(width, 1), max(height, 1)), flags=pygame.SRCALPHA)
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


class NumericScoreBar(ScoreBar):
    SPACING = 5

    def __init__(self, x: int, y: int, unit_filmstrip, score: int,
                 direction=Direction.LEFT_TO_RIGHT, font_size=20):
        self.font_size = font_size
        self.font = make_font("Times New Roman", self.font_size)
        super().__init__(x, y, unit_filmstrip, score, direction=direction)

    def render_bar(self, score, frame_image):
        width, height = frame_image.get_rect().size
        dx, dy = self.direction.value

        score_text = str(int(score))
        text_width, text_height = self.font.size(score_text)
        if dx:
            v_space = (height - text_height) // 2
            h_space = 0
            total_width = width + text_width + self.SPACING
            total_height = height
            min_width = 1
            min_height = text_height
        else:
            v_space = 0
            h_space = width - text_width
            total_width = width
            total_height = height + text_height + self.SPACING
            min_width = text_width
            min_height = 1

        image = pygame.Surface((max(total_width, min_width), max(total_height, min_height)), flags=pygame.SRCALPHA)

        x = image.get_width() - width if dx < 0 else 0
        y = image.get_height() - height if dy < 0 else 0
        padx = min(h_space, 0)
        pady = min(v_space, 0)
        image.blit(frame_image, (x + padx, y + pady))

        x = x + width + padx + self.SPACING if dx > 0 else 0
        y = y + height + pady + self.SPACING if dy > 0 else 0
        padx = max(h_space, 0)
        pady = max(v_space, 0)
        caption = self.font.render(score_text, True, (255, 255, 255))
        image.blit(caption, (x + padx, y + pady))

        return image

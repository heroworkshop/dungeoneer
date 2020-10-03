from collections import namedtuple
from functools import lru_cache

import pygame

SubArea = namedtuple("subarea", "left top width height")


class SpriteSheet:
    def __init__(self, image, columns, rows, sub_area=None):
        assert isinstance(image, pygame.Surface)
        if sub_area:
            self.sub_area = SubArea(*sub_area)
        else:
            self.sub_area = None
        self.image = image
        self.columns = columns
        self.rows = rows
        self.image_count = columns * rows

    def surface_by_index(self, n):
        width = self.image.get_width() // self.columns
        height = self.image.get_height() // self.rows

        x = (n % self.columns) * width
        y = (n // self.columns) * height
        return self.image.subsurface(pygame.Rect(x, y, width, height))

    def sub_area_indices(self):
        indices = []  # Need to use these to create film strips so order matters
        for y in range(self.sub_area.top, self.sub_area.top + self.sub_area.height):
            for x in range(self.sub_area.left, self.sub_area.left + self.sub_area.width):
                index = y * self.columns + x
                indices.append(index)
        return indices

    @lru_cache(1000)
    def filmstrip(self, start=0, length=None, rotate=0, scale=1):
        if not length:
            length = self.image_count

        if self.sub_area:
            indices = self.sub_area_indices()[start: start + length]
        else:
            indices = range(start, start + length)

        def transform(surface):
            if rotate and scale != 1:
                return pygame.transform.rotozoom(surface, rotate, scale)
            if rotate:
                return pygame.transform.rotate(surface, rotate)
            if scale:
                width, height = int(surface.get_width() * scale), int(surface.get_height() * scale)
                return pygame.transform.smoothscale(surface, (width, height))
            return surface.convert_alpha()

        return [transform(self.surface_by_index(i)) for i in indices]

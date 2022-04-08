"""
The game universe is divided into realms, regions and tiles

Tiles are arranged in a grid big enough for one screen. This is known as a region
Regions are also arranged in a grid of variable size and this is known as a realm.

  ================
  I    |    |    I     ===
  I    |    |    I     I I   REALM
  ----------------     ===
  I    |****|    I
  I    |****|    I
  ----------------     ---
  I    |    |    I     | |   REGION
  I    |    |    I     ---
  ----------------
  I    |    |    I      *     TILE
  I    |    |    I
  ================
"""
from random import randint

import pygame

from dungeoneer.map_maker import generate_map, DesignType
from dungeoneer.regions import Position, Region


class Realm:
    """A realm is a variable sized grid of Regions"""

    def __init__(self, size, region_size=(50, 30)):
        region_width, region_height = region_size
        self.regions = dict()
        self.width, self.height = size

        self.create_empty_regions(region_height, region_size, region_width)

    def create_empty_regions(self, region_height, region_size, region_width):
        for x in range(self.width):
            for y in range(self.height):
                region = Region(region_size)
                if y > 0:
                    region.exits["N"] = self.regions[Position(x, y - 1)].exits["S"]
                if y < self.height - 1:
                    region.exits["S"] = randint(1, region_width - 1)
                if x > 0:
                    region.exits["W"] = self.regions[Position(x - 1, y)].exits["E"]
                if x < self.width - 1:
                    region.exits["E"] = randint(1, region_height - 1)
                self.regions[Position(x, y)] = region

    def __len__(self):
        return len(self.regions)

    def region(self, position: Position):
        return self.regions[position]

    def generate_map(self):
        for region in self.regions.values():
            generate_map(region, DesignType.random())

    def render_tiles(self):
        pixel_width = self.regions[(0, 0)].pixel_width
        pixel_height = self.regions[(0, 0)].pixel_height

        surface = pygame.Surface((pixel_width * self.width, pixel_height * self.height))

        for x in range(self.width):
            for y in range(self.height):
                position = pygame.math.Vector2(x * pixel_width, y * pixel_height)
                self.regions[(x, y)].render_tiles_to_surface(surface, position)
        return surface

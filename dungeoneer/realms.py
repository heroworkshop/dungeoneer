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
import pygame

from dungeoneer.map_maker import generate_map, DesignType
from dungeoneer.regions import Position, Region


class Realm:
    """A realm is a variable sized grid of Regions"""

    def __init__(self, size, region_size=(50, 30)):
        self.regions = dict()
        self.width, self.height = size

        for x in range(self.width):
            for y in range(self.height):
                self.regions[Position(x, y)] = Region(region_size)

    def __len__(self):
        return len(self.regions)

    def region(self, position: Position):
        return self.regions[position]

    def generate_map(self):
        for region in self.regions.values():
            generate_map(region, DesignType.CONNECTED_ROOMS)

    def render_tiles(self):
        pixel_width = self.regions[(0, 0)].pixel_width
        pixel_height = self.regions[(0, 0)].pixel_height

        surface = pygame.Surface((pixel_width * self.width, pixel_height * self.height))

        for x in range(self.width):
            for y in range(self.height):
                position = pygame.math.Vector2(x * pixel_width, y * pixel_height)
                self.regions[(x, y)].render_tiles_to_surface(surface, position)
        return surface

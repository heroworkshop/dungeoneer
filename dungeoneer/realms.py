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
from contextlib import suppress
from random import randint
from typing import Dict

import pygame

from dungeoneer.interfaces import SpriteGroups
from dungeoneer.map_maker import generate_map, DesignType
from dungeoneer.regions import Position, Region


class PointOutsideRealmBoundary(ValueError):
    """Raised when trying to access position outside the realms boundaries"""


class Realm:
    """A realm is a variable sized grid of Regions

    Args:
        size (tuple[int, int]): Number of regions in the x and y direction
        tile_size (tuple[int, int]): pixel dimensions of a tile
        region_size  (tuple[int, int]): tile dimensions of a region
    """

    def __init__(self, size, tile_size, region_size=(50, 30)):
        region_width, region_height = region_size
        tile_width, tile_height = tile_size
        self.region_pixel_size = int(region_width * tile_width), int(region_height * tile_height)
        self.regions: Dict[Position, Region] = {}
        self.width, self.height = size
        self.groups = SpriteGroups()  # global across all regions

        self.create_empty_regions(region_size)

    def create_empty_regions(self, region_size):
        region_width, region_height = region_size
        for x in range(self.width):
            for y in range(self.height):
                region = Region(region_size, id_code=(x, y))
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
        try:
            return self.regions[position]
        except KeyError:
            raise PointOutsideRealmBoundary(f"Position {position} was outside the realm with "
                                            f"size ({self.width}, {self.height})")

    def region_coord_from_pixel_position(self, pixel_position):
        x, y = pixel_position
        width, height = self.region_pixel_size
        return x // width, y // height

    def region_from_pixel_position(self, pixel_position):
        try:
            return self.region(self.region_coord_from_pixel_position(pixel_position))
        except PointOutsideRealmBoundary:
            raise PointOutsideRealmBoundary(f"Pixel Position {pixel_position} "
                                            f"was outside the realm with size ({self.width}, {self.height})")

    def neighbouring_regions_from_pixel_position(self, pixel_position):
        pixel_position = pygame.Vector2(pixel_position)
        dx, dy = self.region_pixel_size
        dx -= 1
        dy -= 1
        neighbours = [(-dx, -dy), (0, -dy), (dx, -dy),
                      (-dx, 0), (0, 0), (dx, 0),
                      (-dx, dy), (0, dy), (dx, dy)]
        region_coords = {self.region_coord_from_pixel_position(pygame.Vector2(n) + pixel_position) for n in neighbours}
        results = []
        for p in region_coords:
            with suppress(PointOutsideRealmBoundary):
                results.append(self.region(p))
        return results

    def generate_map(self):
        width, height = self.region_pixel_size
        for coordinates, region in self.regions.items():
            generate_map(region, DesignType.random())
            x, y = coordinates
            region.build_world((x * width, y * height))

    def render_tiles(self):
        pixel_width = self.regions[(0, 0)].pixel_width
        pixel_height = self.regions[(0, 0)].pixel_height

        surface = pygame.Surface((pixel_width * self.width, pixel_height * self.height))

        for x in range(self.width):
            for y in range(self.height):
                position = pygame.math.Vector2(x * pixel_width, y * pixel_height)
                self.regions[(x, y)].render_tiles_to_surface(surface, position)
        return surface

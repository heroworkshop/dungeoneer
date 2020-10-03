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
from collections import namedtuple
from enum import Enum

import pygame

from dungeoneer import game_assets
from dungeoneer.spritesheet import SpriteSheet


class Tile:
    def __init__(self, sprite_sheet: SpriteSheet, is_solid=False):
        self.filmstrip = sprite_sheet.filmstrip()
        self.is_solid = is_solid
        self.width = self.filmstrip[0].get_width()
        self.height = self.filmstrip[0].get_height()


terrain = game_assets.load_image("terrain.png")
liquids = game_assets.load_image("liquids32.png")
vegetation = game_assets.load_image("vegetation.png")
lava = game_assets.load_image("lava.png")


class TileType(Enum):
    STONE_WALL = Tile(SpriteSheet(terrain, columns=8, rows=16, sub_area=(7, 3, 1, 1)), is_solid=True)
    STONE_FLOOR = Tile(SpriteSheet(terrain, columns=8, rows=16, sub_area=(7, 0, 1, 1)), is_solid=True)
    WATER = Tile(SpriteSheet(liquids, columns=16, rows=12, sub_area=(0, 0, 6, 1))),
    LAVA = Tile(SpriteSheet(lava, columns=10, rows=1)),
    WOOD = Tile(SpriteSheet(terrain, columns=8, rows=16, sub_area=(0, 4, 1, 2))),
    GRASS = Tile(SpriteSheet(terrain, columns=8, rows=16, sub_area=(0, 1, 1, 1)), ),
    EARTH = Tile(SpriteSheet(terrain, columns=8, rows=16, sub_area=(0, 1, 1, 1)), ),
    HEDGE = Tile(SpriteSheet(vegetation, columns=16, rows=16, sub_area=(1, 3, 1, 1)), is_solid=True),


Position = namedtuple("position", "x y")


class Region:
    """A region is a variable sized sparse grid of tiles"""

    def __init__(self, size, default_tile: Tile = TileType.STONE_FLOOR.value):
        self.tiles = dict()
        self.grid_width, self.grid_height = size
        self.tile_width = default_tile.width
        self.tile_height = default_tile.height
        self.pixel_width = self.grid_width * self.tile_width
        self.pixel_height = self.grid_height * self.tile_height
        self.default_tile = default_tile

    def __len__(self):
        return self.grid_width * self.grid_height

    def tile(self, position: Position):
        return self.tiles.get(position, self.default_tile)

    def place(self, position: Position, tile: Tile):
        self.tiles[position] = tile

    def place_by_type(self, position: Position, tile_type: TileType):
        self.place(position, tile_type.value)

    def render(self):
        surface = pygame.Surface((self.pixel_width, self.pixel_height))
        for column in range(self.grid_width):
            for row in range(self.grid_height):
                tile_to_plot = self.tile((column, row))
                x = column * self.tile_width
                y = row * self.tile_height
                surface.blit(tile_to_plot.filmstrip[0], (x, y))
        return surface


class Realm:
    """A realm a variable sized grid of Regions"""

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

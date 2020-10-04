from collections import namedtuple
from enum import Enum

import pygame

from dungeoneer import game_assets
from dungeoneer.characters import MonsterType
from dungeoneer.spritesheet import SpriteSheet

terrain = game_assets.load_image("terrain.png")
liquids = game_assets.load_image("liquids32.png")
vegetation = game_assets.load_image("vegetation.png")
lava = game_assets.load_image("lava.png")


class Tile:
    def __init__(self, sprite_sheet: SpriteSheet, is_solid=False):
        self.filmstrip = sprite_sheet.filmstrip()
        self.is_solid = is_solid
        self.width = self.filmstrip[0].get_width()
        self.height = self.filmstrip[0].get_height()


class TileType(Enum):
    STONE_WALL = Tile(SpriteSheet(terrain, columns=8, rows=16, sub_area=(7, 3, 1, 1)), is_solid=True)
    STONE_FLOOR = Tile(SpriteSheet(terrain, columns=8, rows=16, sub_area=(7, 0, 1, 1)), is_solid=True)
    WATER = Tile(SpriteSheet(liquids, columns=16, rows=12, sub_area=(0, 0, 6, 1)))
    LAVA = Tile(SpriteSheet(lava, columns=10, rows=1)),
    WOOD = Tile(SpriteSheet(terrain, columns=8, rows=16, sub_area=(0, 4, 1, 2)))
    GRASS = Tile(SpriteSheet(terrain, columns=8, rows=16, sub_area=(0, 1, 1, 1)))
    EARTH = Tile(SpriteSheet(terrain, columns=8, rows=16, sub_area=(0, 1, 1, 1)))
    HEDGE = Tile(SpriteSheet(vegetation, columns=16, rows=16, sub_area=(1, 3, 1, 1)), is_solid=True)


Position = namedtuple("position", "x y")


class Region:
    """A region is a variable sized sparse grid of tiles"""

    def __init__(self, size, default_tile: Tile = TileType.STONE_FLOOR.value):
        self.tiles = dict()
        self.animated_tiles = dict()
        self.solid_objects = dict()
        self.monsters = dict()
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

    def solid_object(self, position: Position):
        return self.solid_objects.get(position)

    def animated_tile(self, position: Position):
        return self.animated_tiles.get(position)

    def monster_eggs(self, position: Position):
        return self.monsters.get(position)

    def place(self, position: Position, tile: Tile):
        if len(tile.filmstrip) > 1:
            self.animated_tiles[position] = tile
        elif tile.is_solid:
            self.solid_objects[position] = tile
        else:
            self.tiles[position] = tile

    def place_by_type(self, position: Position, tile_type: TileType):
        self.place(position, tile_type.value)

    def place_monster_egg(self, position: Position, monster_type: MonsterType):
        self.monsters[position] = monster_type

    def render_tiles(self):
        surface = pygame.Surface((self.pixel_width, self.pixel_height))
        for column in range(self.grid_width):
            for row in range(self.grid_height):
                tile_to_plot = self.tile((column, row))
                x = column * self.tile_width
                y = row * self.tile_height
                surface.blit(tile_to_plot.filmstrip[0], (x, y))
        return surface

    def fill_all(self, tile: TileType):
        size = (self.grid_width, self.grid_height)
        top_left = (0, 0)
        self.fill(top_left, size, tile)

    def fill(self, top_left, size, tile: TileType):
        x, y = top_left
        width, height = size
        for column in range(x, x + width):
            for row in range(y, y + height):
                self.place_by_type((column, row), tile)

    def clear_area(self, top_left, size):
        x, y = top_left
        width, height = size
        for column in range(x, x + width):
            for row in range(y, y + height):
                self.solid_objects.pop((column, row), None)



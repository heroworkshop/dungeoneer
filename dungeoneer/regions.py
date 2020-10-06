from collections import namedtuple
from enum import Enum
from typing import Iterable

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
Size = namedtuple("size", "width height")


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

    def clear_nodes(self, nodes: Iterable[Position]):
        for p in nodes:
            self.solid_objects.pop(p, None)


class SubRegion:
    def __init__(self, region, top_left=Position(0, 0), size: Size = None):
        self.top_left = Position(*top_left)
        self.size = Size(*(size or (region.grid_width, region.grid_height)))
        self.region = region

    def __str__(self):
        return f"{self.top_left} {self.size}"

    def split_horizontally(self, split=0.5):
        if self.size.width < 2:
            raise ValueError("Cannot split SubRegion with width {}".format(self.size[0]))
        subregion1 = SubRegion(self.region, self.top_left, self.size)
        subregion2 = SubRegion(self.region, self.top_left, self.size)
        split_point = int(self.size.width * split) + self.top_left.x
        x, y = self.top_left
        subregion2.top_left = Position(split_point, y)
        width1 = split_point - x
        width2 = self.size.width - width1
        assert width1 > 0
        assert width2 > 0
        subregion1.size = Size(width1, self.size.height)
        subregion2.size = Size(width2, self.size.height)
        return subregion1, subregion2

    def split_vertically(self, split=0.5):
        if self.size.height < 2:
            raise ValueError("Cannot split SubRegion with height {}".format(self.size[1]))
        subregion1 = SubRegion(self.region, self.top_left, self.size)
        subregion2 = SubRegion(self.region, self.top_left, self.size)
        split_point = int(self.size.height * split) + self.top_left.y
        x, y = self.top_left
        subregion2.top_left = Position(x, split_point)
        height1 = split_point - y
        height2 = self.size[1] - height1
        subregion1.size = Size(self.size.width, height1)
        subregion2.size = Size(self.size.width, height2)
        return subregion1, subregion2

    def mid_point(self):
        x, y = self.top_left
        w, h = self.size
        x += w // 2
        y += h // 2
        return Position(x, y)

    def ascii_render(self, ascii_map):
        for x in range(self.top_left.x, self.top_left.x + self.size.width):
            ascii_map[(x, self.top_left.y)] = "."
            ascii_map[(x, self.top_left.y + self.size.height - 1)] = "."
        for y in range(self.top_left.y, self.top_left.y + self.size.height):
            ascii_map[(self.top_left.x, y)] = "."
            ascii_map[(self.top_left.x + self.size.width-1, y)] = "."

import itertools
from collections import namedtuple, deque
from enum import Enum
from typing import Iterable, Dict, Type

import pygame

from dungeoneer import game_assets
from dungeoneer.characters import MonsterType
from dungeoneer.interfaces import SpriteGroups
from dungeoneer.scenery import ScenerySprite
from dungeoneer.spritesheet import SpriteSheet

terrain = game_assets.load_image("terrain.png")
liquids = game_assets.load_image("liquids.png")
vegetation = game_assets.load_image("vegetation.png")
lava = game_assets.load_image("lava.png")


class Prefab:
    def __init__(self, sprite_class: Type[pygame.sprite.Sprite], filmstrip: Iterable, **parameters):
        self.sprite_class = sprite_class
        self.filmstrip = filmstrip
        self.parameters = parameters
        self.width = filmstrip[0].get_width()
        self.height = filmstrip[0].get_height()

    def make_sprite(self, x, y):
        return self.sprite_class(x, y, self.filmstrip, **self.parameters)


class Tile:
    def __init__(self, prefab: Prefab, is_solid=False, layer=0):
        self.is_solid = is_solid
        self.width = prefab.width
        self.height = prefab.height
        self.prefab = prefab
        self.layer = layer
        self.filmstrip = prefab.filmstrip

    @property
    def animated(self):
        return len(self.filmstrip) > 1


class TileType(Enum):
    @staticmethod
    def make_tile(sprite_sheet, is_solid=False):
        prefab = Prefab(ScenerySprite, sprite_sheet.filmstrip(), animated=False)
        return Tile(prefab, is_solid)

    STONE_WALL = make_tile(SpriteSheet(terrain, columns=8, rows=16, sub_area=(7, 3, 1, 1)), is_solid=True)
    STONE_FLOOR = make_tile(SpriteSheet(terrain, columns=8, rows=16, sub_area=(7, 0, 1, 1)))
    LARGE_FLAGSTONE = make_tile(SpriteSheet(terrain, columns=8, rows=16, sub_area=(1, 2, 1, 1)))
    CHECKERED_TILES = make_tile(SpriteSheet(terrain, columns=8, rows=16, sub_area=(7, 1, 1, 1)))
    WATER = make_tile(SpriteSheet(liquids, columns=16, rows=12, sub_area=(0, 0, 6, 1)))
    LAVA = make_tile(SpriteSheet(lava, columns=10, rows=1)),
    WOOD = make_tile(SpriteSheet(terrain, columns=8, rows=16, sub_area=(0, 4, 1, 2)))
    GRASS = make_tile(SpriteSheet(terrain, columns=8, rows=16, sub_area=(0, 1, 1, 1)))
    EARTH = make_tile(SpriteSheet(terrain, columns=8, rows=16, sub_area=(1, 1, 1, 1)))
    HEDGE = make_tile(SpriteSheet(vegetation, columns=16, rows=16, sub_area=(1, 3, 1, 1)), is_solid=True)


Position = namedtuple("position", "x y")
Size = namedtuple("size", "width height")


class NoFreeSpaceFound(Exception):
    """Raised when trying to find a free space near a specfic spot but a space could not be found"""


class Region:
    """A region is a variable sized sparse grid of tiles"""
    region_id = itertools.count()

    def __init__(self, size, default_tile: Tile = TileType.STONE_FLOOR.value, id_code=None, pixel_base=(0, 0)):
        id_code = id_code or next(self.region_id)
        self.pixel_base = pixel_base
        self.name = f"Region-{id_code}"
        self.grid_width, self.grid_height = size

        self.tiles = {}
        self.visual_effects = {}
        self.solid_objects = {}
        self.monsters = {}

        self.groups = SpriteGroups()
        self.tile_width = default_tile.width
        self.tile_height = default_tile.height
        self.pixel_width = self.grid_width * self.tile_width
        self.pixel_height = self.grid_height * self.tile_height
        self.default_tile = default_tile
        self.exits = {}

    def __repr__(self):
        return str(self.name)

    def __len__(self):
        return self.grid_width * self.grid_height

    def pixel_position(self, pos):
        col, row = pos
        bx, by = self.pixel_base
        return col * self.tile_width + bx, row * self.tile_height + by

    def coordinate_from_absolute_position(self, x, y):
        bx, by = self.pixel_base
        col = (x - bx) // self.tile_width
        row = (y - by) // self.tile_height
        return col, row

    def out_of_bounds(self, position):
        x, y = position
        return any([x < 0, y < 0, x >= self.grid_width, y >= self.grid_height])

    def tile(self, position: Position):
        return self.tiles.get(position, self.default_tile)

    def solid_object_at_position(self, position: Position):
        return self.solid_objects.get(position)

    def animated_tile(self, position: Position):
        return self.visual_effects.get(position)

    def monster_eggs(self, position: Position):
        return self.monsters.get(position)

    def place(self, position: Position, tile: Tile):
        if tile.is_solid:
            self.solid_objects[position] = tile
        if tile.layer == 0:
            self.tiles[position] = tile
            return
        self.visual_effects[position] = tile

    def place_by_type(self, position: Position, tile_type: TileType):
        self.place(position, tile_type.value)

    def place_monster_egg(self, position: Position, monster_type: MonsterType):
        self.monsters[position] = monster_type

    def render_tiles_to_surface(self, surface, position):
        for column in range(self.grid_width):
            for row in range(self.grid_height):
                tile_to_plot = self.tile((column, row))
                x = column * self.tile_width
                y = row * self.tile_height
                p = position[0] + x, position[1] + y
                surface.blit(tile_to_plot.prefab.filmstrip[0], p)
        return surface

    def render_tiles(self):
        surface = pygame.Surface((self.pixel_width, self.pixel_height))
        for column in range(self.grid_width):
            for row in range(self.grid_height):
                tile_to_plot = self.tile((column, row))
                x = column * self.tile_width
                y = row * self.tile_height
                surface.blit(tile_to_plot.filmstrip[0], (x, y))
        return surface

    def build_world(self, base_position):
        self.place_sprites(self.solid_objects, base_position, [self.groups.effects, self.groups.solid])
        self.place_sprites(self.visual_effects, base_position, [self.groups.effects, self.groups.items])

    def place_sprites(self, tiles: Dict[Position, Tile], base_position, groups):
        base_x, base_y = base_position
        for position, tile in tiles.items():
            position = Position(*position)
            # unlike tiles, sprites are positioned by centre so offset to allow for this
            x = base_x + position.x * self.tile_width + self.tile_width // 2
            y = base_y + position.y * self.tile_height + self.tile_height // 2
            tile_sprite = tile.prefab.make_sprite(x, y)
            for g in groups:
                g.add(tile_sprite)

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

    def clear_nodes(self, nodes: Iterable[Position], replace_tile=None):
        for p in nodes:
            self.solid_objects.pop(p, None)
            if replace_tile:
                self.place_by_type(p, replace_tile)
            else:
                self.tiles.pop(p, None)

    def nearest_free_space(self, x0: int, y0: int, max_distance=5):
        """Find nearest empty tile in the region
        Args:
            x0, y0 (int): start position
            max_distance (int): largest manhatten distance from x, y
        Raises:
            NoFreeSpaceFound
        Returns:
            col, row in region of free space
        """
        neighbours = [(-1, -1), (0, -1), (1, -1),
                      (-1, 0), (1, 0),
                      (-1, 1), (1, 0), (1, 1)]
        queue = deque([(x0, y0)])
        checked = set()
        while queue:
            x, y = queue.popleft()
            checked.add((x, y))
            if (x, y) not in self.solid_objects:
                return x, y
            for dx, dy in neighbours:
                manhatten_distance = abs(x + dx - x0) + abs(y + dy - y0)
                pos = (x + dx, y + dy)
                if self.out_of_bounds(pos):
                    continue
                if pos in checked:
                    continue
                if manhatten_distance > max_distance:
                    continue
                queue.append((x + dx, y + dy))
        raise NoFreeSpaceFound(f"Couldn't find free space within {max_distance} of {(x, y)}")


class SubRegion:
    def __init__(self, region, top_left=Position(0, 0), size: Size = None):
        self.top_left = Position(*top_left)
        self.size = Size(*(size or (region.grid_width, region.grid_height)))
        self.region = region

    @property
    def node(self):
        return self.mid_point()

    def __str__(self):
        return f"{self.top_left} {self.size}"

    def split_horizontally(self, split=0.5):
        if self.size.width < 2:
            raise ValueError(f"Cannot split SubRegion with width {self.size[0]}")
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
            raise ValueError(f"Cannot split SubRegion with height {self.size[1]}")
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
            ascii_map[(self.top_left.x + self.size.width - 1, y)] = "."

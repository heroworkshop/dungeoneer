from collections import namedtuple

import pygame

from dungeoneer import game_assets
from dungeoneer.spritesheet import SpriteSheet

Coord = namedtuple("coord", "x y")


class Tile:
    def __init__(self, images):
        try:
            iter(images)
            self.filmstrip = images
        except TypeError:
            self.filmstrip = [images]
        self.frame = 0
        self.size = self.filmstrip[0].get_size()


class TileManager:
    def __init__(self):
        self.tiles = []

    def import_tiles(self, filename, columns, rows):
        image = pygame.image.load(game_assets.image_file(filename))
        terrain_sheet = SpriteSheet(image, columns, rows)
        self.tiles.extend(terrain_sheet.filmstrip())


class TileMap:
    def __init__(self, default_tile, tile_size=None):
        self.default_tile = default_tile
        tile_size = tile_size or default_tile.get_size()
        self.tile_width, self.tile_height = tile_size
        self.tiles = dict()

    def tile_at(self, x: int, y: int):
        return self.tiles.get((x, y), self.default_tile)

    def place_tile(self, tile: pygame.Surface, x: int, y: int):
        self.tiles[(x, y)] = tile

    def render(self, surface, left, top, width, height, offset=(0, 0)):
        offset = Coord(*offset)
        for row in range(top, top + height):
            y = row * self.tile_height + offset.y
            for column in range(left, left + width):
                x = column * self.tile_width + offset.x
                tile_to_plot = self.tile_at(column, row)
                if tile_to_plot:
                    surface.blit(tile_to_plot, (x, y))

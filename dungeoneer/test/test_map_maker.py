import unittest

import pygame

from dungeoneer.map_maker import Realm, Region, TileType, Tile
from dungeoneer.spritesheet import SpriteSheet


def make_test_tile(colour, width=32, height=32):
    surface = pygame.Surface((width, height))
    surface.fill(colour)
    return Tile(SpriteSheet(surface, columns=1, rows=1), is_solid=False)


RED_TILE = make_test_tile((255, 0, 0))
BLUE_TILE = make_test_tile((0, 0, 255))

class TestRealm(unittest.TestCase):
    def test_Realm_withSize5by5_has25Regions(self):
        realm = Realm((5, 5))
        self.assertEqual(25, len(realm))
        self.assertIsInstance(realm.region((0, 0)), Region)


class TestRegion(unittest.TestCase):

    def test_Region_withSize5by5_has25Tiles(self):
        region = Region((5, 5))
        self.assertEqual(25, len(region))
        self.assertIsInstance(region.tile((0, 0)), Tile)

    def test_Region_withoutTiles_usesDefaultTile(self):
        region = Region((1, 1), default_tile=TileType.STONE_FLOOR.value)
        result = region.tile((0, 0))
        self.assertEqual(TileType.STONE_FLOOR.value, result)

    def test_place_by_type_placesTileAtPosition(self):
        region = Region((1, 1), default_tile=TileType.STONE_FLOOR.value)
        region.place_by_type((0, 0), TileType.GRASS)
        result = region.tile((0, 0))
        self.assertEqual(TileType.GRASS.value, result)

    def test_place_placesTileAtPosition(self):
        region = Region((1, 1), default_tile=TileType.STONE_FLOOR.value)
        region.place((0, 0), TileType.GRASS.value)
        result = region.tile((0, 0))
        self.assertEqual(TileType.GRASS.value, result)

    def test_render_with3x3Tiles32x32_returns96x96Surface(self):
        region = Region((3, 3), default_tile=RED_TILE)
        surface = region.render()
        self.assertEqual((96, 96), surface.get_size())

    def test_render_withOnlyRedDefaultTiles_returnsRedSurface(self):
        region = Region((3, 3), default_tile=RED_TILE)
        surface = region.render()
        w, h = surface.get_size()
        # examine colour of tile midpoints
        red = RED_TILE.filmstrip[0].get_at((0, 0))
        for x in range(w//6, w, w//3):
            for y in range(h//6, h, h//3):
                result = surface.get_at((x, y))
                self.assertEqual(red, result)

    def test_render_withBlueCenterTile_returnsRedDoughnutSurface(self):
        """Render this region:
                RRR
                RBR
                RRR
        """
        region = Region((3, 3), default_tile=RED_TILE)
        region.place((1, 1), BLUE_TILE)
        surface = region.render()
        w, h = surface.get_size()
        # examine colour of tile midpoints
        red = RED_TILE.filmstrip[0].get_at((0, 0))
        blue = BLUE_TILE.filmstrip[0].get_at((0, 0))
        for x in range(w//6, w, w//3):
            for y in range(h//6, h, h//3):
                result = surface.get_at((x, y))
                expected = blue if x == w//2 and y == h//2 else red
                self.assertEqual(expected, result)

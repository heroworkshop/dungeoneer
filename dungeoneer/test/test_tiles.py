import unittest

import pygame

from dungeoneer import tiles

BLUE = (0, 0, 255)
RED = (255, 0, 0)


class TestMap(unittest.TestCase):
    def setUp(self):
        self.blue_tile = pygame.Surface((1, 1))
        self.blue_tile.fill(BLUE)
        self.red_tile = pygame.Surface((1, 1))
        self.red_tile.fill(RED)

    def test_tile_at_withNoTiles_returnsDefaultTile(self):
        tile_map = tiles.TileMap(self.red_tile)
        result = tile_map.tile_at(1, 1)
        self.assertEqual(self.red_tile, result)

    def test_tile_at_withOneTileDefined_returnsThatTileAtOnlyThatLocation(self):
        tile_map = tiles.TileMap(self.red_tile)
        tile_map.place_tile(self.blue_tile, 1, 1)
        result = tile_map.tile_at(1, 1)
        r, g, b, alpha = result.get_at((0, 0))
        self.assertEqual(BLUE, (r, g, b))
        self.assertEqual(self.blue_tile, result)
        self.assertEqual(self.red_tile, tile_map.tile_at(0, 1))

    def test_render_withOneTileDefined_rendersToCorrectPlace(self):
        tile_map = tiles.TileMap(self.red_tile)
        tile_map.place_tile(self.blue_tile, 1, 1)
        surface = pygame.Surface((3, 3))
        tile_map.render(surface, 0, 0, 3, 3)
        # Expect to get this pattern:
        #   rrr
        #   rbr
        #   rrr
        for y in range(3):
            for x in range(3):
                expected = BLUE if y == 1 and x == 1 else RED
                colour = surface.get_at((x, y))
                self.assertEqual(expected, colour)

    def test_render_withRenderToPartOfSurface_onlyRendersSpecified(self):
        tile_map = tiles.TileMap(self.red_tile)
        surface = pygame.Surface((3, 3))
        surface.fill(BLUE)
        tile_map.render(surface, 1, 0, 2, 2)
        # Expect to get this pattern:
        #   brr
        #   brr
        #   bbb
        for y in range(3):
            for x in range(3):
                expected = BLUE if y == 2 or x == 0 else RED
                colour = surface.get_at((x, y))
                self.assertEqual(expected, colour)

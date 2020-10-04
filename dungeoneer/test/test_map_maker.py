import unittest

import pygame

from dungeoneer.characters import MonsterType
from dungeoneer.map_maker import generate_map, DesignType
from dungeoneer.realms import Realm
from dungeoneer.regions import TileType, Region, Tile
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

    def test_render_tiles_with3x3Tiles32x32_returns96x96Surface(self):
        region = Region((3, 3), default_tile=RED_TILE)
        surface = region.render_tiles()
        self.assertEqual((96, 96), surface.get_size())

    def test_render_tiles_withOnlyRedDefaultTiles_returnsRedSurface(self):
        region = Region((3, 3), default_tile=RED_TILE)
        surface = region.render_tiles()
        w, h = surface.get_size()
        # examine colour of tile midpoints
        red = RED_TILE.filmstrip[0].get_at((0, 0))
        for x in range(w//6, w, w//3):
            for y in range(h//6, h, h//3):
                result = surface.get_at((x, y))
                self.assertEqual(red, result)

    def test_render_tiles_withBlueCenterTile_returnsRedDoughnutSurface(self):
        """Render this region:
                RRR
                RBR
                RRR
        """
        region = Region((3, 3), default_tile=RED_TILE)
        region.place((1, 1), BLUE_TILE)
        surface = region.render_tiles()
        w, h = surface.get_size()
        # examine colour of tile midpoints
        red = RED_TILE.filmstrip[0].get_at((0, 0))
        blue = BLUE_TILE.filmstrip[0].get_at((0, 0))
        for x in range(w//6, w, w//3):
            for y in range(h//6, h, h//3):
                result = surface.get_at((x, y))
                expected = blue if x == w//2 and y == h//2 else red
                self.assertEqual(expected, result)

    def test_place_withAnimatedTile_addsTileToAnimatedTiles(self):
        region = Region((1, 1), default_tile=TileType.STONE_FLOOR.value)
        region.place_by_type((0, 0), TileType.WATER)
        tile = region.tile((0, 0))
        animated = region.animated_tile((0, 0))
        self.assertEqual(TileType.STONE_FLOOR.value, tile)
        self.assertEqual(TileType.WATER.value, animated)

    def test_place_withStoneWall_addsStoneWallToSolidObjects(self):
        region = Region((1, 1), default_tile=TileType.STONE_FLOOR.value)
        region.place_by_type((0, 0), TileType.STONE_WALL)
        tile = region.tile((0, 0))
        solid = region.solid_object((0, 0))
        self.assertEqual(TileType.STONE_FLOOR.value, tile)
        self.assertEqual(TileType.STONE_WALL.value, solid)

    def test_place_withMonster_addsMonsterTypeToMonsters(self):
        region = Region((1, 1))
        region.place_monster_egg((0, 0), MonsterType.ZOMBIE_GENERATOR)

        monster_type = region.monster_eggs((0, 0))

        self.assertEqual(MonsterType.ZOMBIE_GENERATOR, monster_type)

    def test_fill_all_withStoneWall_placesStoneWallItemInEachGridSquare(self):
        region = Region((3, 3))
        region.fill_all(TileType.STONE_WALL)
        self.assertTrue(all(i == TileType.STONE_WALL.value for i in region.solid_objects.values()))
        self.assertEqual(9, len(region.solid_objects))

    def test_fill_with2x2Area_placesTilesIn4Squares(self):
        region = Region((4, 4))
        region.fill((1, 1), (2, 2), TileType.STONE_WALL)
        self.assertEqual(4, len(region.solid_objects))

    def test_clear_area_with2x2Area_removes4SolidObjects(self):
        region = Region((4, 4))
        region.fill_all(TileType.STONE_WALL)
        region.clear_area((1, 1), (2, 2))
        self.assertEqual(16 - 4, len(region.solid_objects))


class TestGenerateMap(unittest.TestCase):
    def test_generate_withLargeRoom_hasOpenCentralCore(self):
        region = Region((50, 50))
        generate_map(region, DesignType.LARGE_ROOM)
        for column in range(1, 49):
            for row in range(1, 49):
                self.assertIsNone(region.solid_object((column, row)))

    def test_generate_map_withLargeRoom_hasWallsAroundPerimeterWithExit(self):
        region = Region((50, 50))
        generate_map(region, DesignType.LARGE_ROOM)
        # count solid objects around perimeter
        top = [region.solid_object((column, 0)) is not None for column in range(50)].count(True)
        bottom = [region.solid_object((column, 49)) is not None for column in range(50)].count(True)
        left = [region.solid_object((0, row)) is not None for row in range(1, 49)].count(True)
        right = [region.solid_object((49, row)) is not None for row in range(1, 49)].count(True)
        total = top + bottom + left + right
        self.assertLess(total, 198)
        self.assertGreater(total, 170)

    # def test_generate_map_withLevel2Room(self):
    #     region = Region((50, 40))
    #     split_room(region)

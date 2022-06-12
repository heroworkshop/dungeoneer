import unittest

import pygame
from assertpy import assert_that

from dungeoneer.characters import MonsterType
from dungeoneer.regions import Region, Tile, TileType, SubRegion, NoFreeSpaceFound
from dungeoneer.scenery import ScenerySprite
from dungeoneer.spritesheet import SpriteSheet


def make_test_tile(colour, width=32, height=32):
    surface = pygame.Surface((width, height))
    surface.fill(colour)
    sprite_sheet = SpriteSheet(surface, columns=1, rows=1)
    return Tile(ScenerySprite, sprite_sheet.filmstrip())


RED_TILE = make_test_tile((255, 0, 0))
BLUE_TILE = make_test_tile((0, 0, 255))


class TestRegion(unittest.TestCase):

    def test_Region_name_withNoIdCode_isUniqueShortString(self):
        region1 = Region((5, 5))
        region2 = Region((5, 5))
        assert_that(len(region1.name)).is_between(1, 15)
        assert_that(region1.name).is_not_equal_to(region2.name)

    def test_Region_name_withIdCode_usesIdCodeInName(self):
        region = Region((5, 5), id_code=(5, 12))
        assert_that(region.name).is_equal_to("Region-(5, 12)")


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
        for x in range(w // 6, w, w // 3):
            for y in range(h // 6, h, h // 3):
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
        for x in range(w // 6, w, w // 3):
            for y in range(h // 6, h, h // 3):
                result = surface.get_at((x, y))
                expected = blue if x == w // 2 and y == h // 2 else red
                self.assertEqual(expected, result)

    def test_place_withAnimatedTile_addsTileToAnimatedTiles(self):
        region = Region((1, 1), default_tile=TileType.STONE_FLOOR.value)
        region.place_by_type((0, 0), TileType.WATER, layer=1)
        tile = region.tile((0, 0))
        animated = region.animated_tile((0, 0))
        self.assertEqual(TileType.STONE_FLOOR.value, tile)
        self.assertEqual(TileType.WATER.value, animated)

    def test_place_withStoneWall_addsStoneWallToSolidObjects(self):
        region = Region((1, 1), default_tile=TileType.STONE_FLOOR.value)
        region.place_by_type((0, 0), TileType.STONE_WALL)
        tile = region.tile((0, 0))
        solid = region.solid_object_at_position((0, 0))
        self.assertEqual(TileType.STONE_WALL.value, tile)
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

    def test_build_world_withSolidObjects_addsSpritesToRegionsSolidLayer(self):
        region = Region((4, 4))
        region.fill((1, 1), (2, 2), TileType.STONE_WALL)
        region.build_world((0, 0))
        self.assertEqual(4, len(region.groups.solid))

    def test_clear_area_with2x2Area_removes4SolidObjects(self):
        region = Region((4, 4))
        region.fill_all(TileType.STONE_WALL)
        region.clear_area((1, 1), (2, 2))
        self.assertEqual(16 - 4, len(region.solid_objects))


class TestFindNearestFreeSpace(unittest.TestCase):
    def test_withEmptyRegion_returnsXY(self):
        region = Region((11, 11))
        space = region.nearest_free_space(5, 5)
        assert_that(space).is_equal_to((5, 5))

    def test_withOneEmptySpot_returnsFreeSpot(self):
        region = Region((11, 11))
        region.fill_all(TileType.STONE_WALL)
        region.clear_nodes([(5, 6)])
        space = region.nearest_free_space(5, 5)
        assert_that(space).is_equal_to((5, 6))

    def test_withTwoEmptySpots_returnsNearestFreeSpot(self):
        region = Region((11, 11))
        region.fill_all(TileType.STONE_WALL)
        region.clear_nodes([(6, 6), (3, 3)])
        space = region.nearest_free_space(5, 5)
        assert_that(space).is_equal_to((6, 6))

    def test_withSpotInTopLeftCorner_returnsNearestFreeSpot(self):
        region = Region((11, 11))
        region.fill_all(TileType.STONE_WALL)
        region.clear_nodes([(6, 6), (3, 3)])
        space = region.nearest_free_space(1, 1, 10)
        assert_that(space).is_equal_to((3, 3))

    def test_withSpotInBottomRightCorner_returnsNearestFreeSpot(self):
        region = Region((11, 11))
        region.fill_all(TileType.STONE_WALL)
        region.clear_nodes([(6, 6), (3, 3)])
        space = region.nearest_free_space(10, 10, 10)
        assert_that(space).is_equal_to((6, 6))

    def test_withAllSolidWalls_raisesNoFreeSpaceFound(self):
        region = Region((11, 11))
        region.fill_all(TileType.STONE_WALL)

        assert_that(region.nearest_free_space).raises(NoFreeSpaceFound).when_called_with(5, 5, max_distance=11)

    def test_coordinate_from_absolute_position(self):
        region = Region((11, 11), pixel_base=(1000, 1100))
        coord = region.coordinate_from_absolute_position(1400, 1400)
        expected = 400 // region.tile_width, 300 // region.tile_height
        assert_that(coord).is_equal_to(expected)


class TestSubRegion(unittest.TestCase):
    def test_split_horizontally_withDefaultSplit_makesEqualSizedAdjacentRegions(self):
        region = Region((10, 10))
        r1, r2 = SubRegion(region).split_horizontally()
        self.assertEqual((5, 10), r1.size)
        self.assertEqual((5, 10), r2.size)
        self.assertEqual(5, abs(r1.top_left[0] - r2.top_left[0]))

    def test_split_horizontally_with9WidthSplitEvenly_makesWidth4AndWidth5SubRegions(self):
        region = Region((9, 10))
        r1, r2 = SubRegion(region).split_horizontally(0.5)
        self.assertEqual(9, r1.size[0] + r2.size[0])
        self.assertEqual(1, abs(r1.size[0] - r2.size[0]))

    def test_split_horizontally_with1Width_raisesException(self):
        region = Region((1, 10))
        with self.assertRaises(ValueError):
            SubRegion(region).split_horizontally(0.5)

    def test_split_vertically_with1Height_raisesException(self):
        region = Region((10, 1))
        with self.assertRaises(ValueError):
            SubRegion(region).split_vertically(0.5)

    def test_split_vertically_withDefaultSplit_makesEqualSizedAdjacentRegions(self):
        for h in range(2, 100, 2):
            with self.subTest(h=h):
                region = Region((10, h))
                r1, r2 = SubRegion(region).split_vertically()
                self.assertEqual((10, h // 2), r1.size)
                self.assertEqual((10, h // 2), r2.size)
                self.assertEqual(h // 2, abs(r1.top_left.y - r2.top_left.y))

    def test_split_vertically_with9HeightSplitEvenly_makesHeight4AndHeight5SubRegions(self):
        for h in range(3, 101, 2):
            with self.subTest(h=h):
                region = Region((10, h))
                r1, r2 = SubRegion(region).split_vertically(0.5)
                self.assertEqual(h, r1.size.height + r2.size.height)
                self.assertGreater(r1.size.height, 0)
                self.assertGreater(r2.size.height, 0)
                self.assertEqual(1, abs(r1.size.height - r2.size.height))

    def test_split_vertically_withOffsetCorner(self):
        region = Region((50, 40))
        sub_region = SubRegion(region, (31, 0), (19, 40))
        r1, r2 = sub_region.split_vertically(0.5)
        self.assertEqual(40, r1.size.height + r2.size.height)
        self.assertGreater(r1.size.height, 0)
        self.assertGreater(r2.size.height, 0)
        self.assertEqual(20, abs(r1.top_left.y - r2.top_left.y))

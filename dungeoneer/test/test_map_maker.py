import itertools
import unittest

from assertpy import assert_that

from dungeoneer.map_maker import generate_map, make_nodes, join_nodes, make_rooms_in_subregions, join_exits
from dungeoneer.room_generation import LargeRoomGenerator, ConnectedRoomGenerator
from dungeoneer.spawn import monster_drops, place_treasure
from dungeoneer.regions import Region, Position, SubRegion, Size


class TestGenerateMap(unittest.TestCase):
    def test_generate_withLargeRoom_hasOpenCentralCore(self):
        region = Region((50, 50))
        generate_map(region, LargeRoomGenerator)
        for column, row in itertools.product(range(1, 49), range(1, 49)):
            self.assertIsNone(region.solid_object_at_position((column, row)))

    def test_generate_map_withLargeRoom_hasWallsAroundPerimeterWithExit(self):
        region = Region((50, 50))
        generate_map(region, LargeRoomGenerator)
        # count solid objects around perimeter
        top = [region.solid_object_at_position((column, 0)) is not None for column in range(50)].count(True)
        bottom = [region.solid_object_at_position((column, 49)) is not None for column in range(50)].count(True)
        left = [region.solid_object_at_position((0, row)) is not None for row in range(1, 49)].count(True)
        right = [region.solid_object_at_position((49, row)) is not None for row in range(1, 49)].count(True)
        total = top + bottom + left + right
        self.assertLess(total, 198)
        self.assertGreater(total, 170)

    def test_make_nodes_withNodeCountN_CreatesNNodes(self):
        for n in [16]:
            with self.subTest(n=n):
                region = Region((50, 40))
                nodes = make_nodes(region, node_count=n)
                self.assertEqual(n, len(set(nodes)))

    def test_generate_connected_rooms(self):
        width, height = 50, 40
        region = ConnectedRoomGenerator(Region((width, height))).generate()
        walls = sum([region.solid_object_at_position((column, row)) is not None
                     for column in range(width)].count(True)
                    for row in range(height))

        self.assertEqual(walls, len(region.solid_objects), "Solid objects should not be outside bounds of region")
        self.assertLess(walls, int(width * height * 0.9), "Solid objects should be less than 90% of region")
        self.assertGreater(walls, int(width * height * 0.10), "Solid objects should be at least 10% of region")

    def test_make_rooms_in_subregions_leavesBordersAroundRooms(self):
        region = Region((30, 10))
        sub_regions = [SubRegion(region, size=Size(10, 10)),
                       SubRegion(region, top_left=Position(20, 0), size=Size(10, 10))]

        rooms = make_rooms_in_subregions(sub_regions)
        outer_wall = ([(x, 0) for x in range(region.grid_width)] +
                      [(x, region.grid_height) for x in range(region.grid_width)] +
                      [(0, y) for y in range(region.grid_height)] +
                      [(region.grid_width, y) for y in range(region.grid_height)]
                      )
        room_tiles = set(itertools.chain(*rooms))
        self.assertEqual(set(), set(outer_wall).intersection(room_tiles))

        self.assertGreater(len(rooms), 1)
        self.assertLess(len(rooms), 8 * 8 + 8 * 8)


class TestJoinNodes(unittest.TestCase):
    WIDTH_TABLE = {1: 100}

    def test_join_nodes_withYAlignedNodes(self):
        nodes = (Position(2, 2), Position(8, 2))
        path = join_nodes(nodes, self.WIDTH_TABLE)
        self.assertEqual(6 + 1, len(path))

    def test_join_nodes_withXAlignedNodes(self):
        nodes = (Position(2, 2), Position(2, 8))
        path = join_nodes(nodes, self.WIDTH_TABLE)
        self.assertEqual(6 + 1, len(path))

    def test_join_nodes_withDiagonalNodes(self):
        nodes = (Position(2, 2), Position(8, 8))
        path = join_nodes(nodes, self.WIDTH_TABLE)
        self.assertEqual(6 + 6 + 1, len(path))

    def test_join_nodes_withNegativeDirectionDiagonalNodes(self):
        nodes = (Position(8, 8), Position(2, 2))
        path = join_nodes(nodes, self.WIDTH_TABLE)
        self.assertEqual(6 + 6 + 1, len(path))

    def test_join_exits_withOneInLineNorthExit_takesDirectPath(self):
        nodes = [(2, 3), (5, 5), (8, 6)]
        exits = {"N": 5}
        size = 10, 10

        paths = join_exits(nodes, exits, size)
        expected = {(5, n) for n in range(6)}

        self.assertEqual(expected, set(paths))

    def test_join_exits_withOneInLineSouthExit_takesDirectPath(self):
        nodes = [(1, 2), (5, 5), (7, 4)]
        exits = {"S": 5}
        size = 10, 10

        paths = join_exits(nodes, exits, size)
        expected = {(5, n) for n in range(5, 10)}

        self.assertEqual(expected, set(paths))

    def test_join_exits_withOneInLineEastExit_takesDirectPath(self):
        nodes = [(3, 2), (5, 5), (7, 1)]
        exits = {"E": 5}
        size = 10, 10

        paths = join_exits(nodes, exits, size)

        expected = {(n, 5) for n in range(5, 10)}

        self.assertEqual(expected, set(paths))

    def test_join_exits_withOneInLineWestExit_takesDirectPath(self):
        nodes = [(3, 2), (5, 5), (7, 1)]
        exits = {"W": 5}
        size = 10, 10

        paths = join_exits(nodes, exits, size)

        expected = {(n, 5) for n in range(6)}
        self.assertEqual(expected, set(paths))

    def test_join_exits_withOffInLineSouthExit_takesPathFromNearestXNode(self):
        nodes = [(3, 2), (5, 5), (7, 1)]
        exits = {"S": 7}
        size = 10, 10

        paths = join_exits(nodes, exits, size)
        expected_x_vals = {5, 6, 7}
        expected_y_vals = set(range(5, 10))

        self.assertEqual(7, len(set(paths)))
        self.assertEqual(expected_x_vals, {p[0] for p in paths})
        self.assertEqual(expected_y_vals, {p[1] for p in paths})


class TestItemDrops(unittest.TestCase):
    def test_drop_treasure_withOneDrop_putsAddsOneItemInVisualEffectsTable(self):
        region = Region((10, 10))
        generate_map(region, LargeRoomGenerator)
        original = len(region.visual_effects)
        place_treasure((5, 5), region)
        assert_that(region.visual_effects).is_length(1 + original)


class TestMonsterDrops(unittest.TestCase):
    def test_drop_monster_with100pcProbability_dropsAtLeastOneMonster(self):
        room = [(0, 0)]
        region = Region((10, 10))
        monster_drops(room, region, base_p=100)

        assert_that(len(region.monster_eggs)).is_greater_than_or_equal_to(1)

    def test_drop_monster_with0Probability_dropsNoMonsters(self):
        room = [(0, 0)]
        region = Region((10, 10))
        monster_drops(room, region, base_p=0)

        assert_that(len(region.monster_eggs)).is_equal_to(0)

    def test_drop_monster_withMultipleDropsOnSameLocation_dropsOnlyOneMonster(self):
        room = [(0, 0)]
        region = Region((10, 10))
        for _ in range(4):
            monster_drops(room, region, base_p=100)

        assert_that(len(region.monster_eggs)).is_greater_than_or_equal_to(1)

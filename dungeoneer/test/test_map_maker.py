import unittest

from dungeoneer.map_maker import generate_map, DesignType, make_nodes, join_nodes, generate_connected_rooms, \
    make_rooms_in_subregions
from dungeoneer.regions import Region, Position, SubRegion, Size


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

    def test_make_nodes_withNodeCountN_CreatesNNodes(self):
        for n in [16]:
            with self.subTest(n=n):
                region = Region((50, 40))
                nodes = make_nodes(region, node_count=n)
                self.assertEqual(n, len(set(nodes)))

    def test_generate_connected_rooms(self):
        width, height = 50, 40
        region = generate_connected_rooms(Region((width, height)))
        walls = 0
        for row in range(height):
            walls += [region.solid_object((column, row)) is not None
                      for column in range(width)].count(True)
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
        self.assertEqual(set(), set(outer_wall).intersection(set(rooms)))

        self.assertGreater(len(rooms), 1)
        self.assertLess(len(rooms), 8 * 8 + 8 * 8)


class TestJoinNodes(unittest.TestCase):
    def test_join_nodes_withYAlignedNodes(self):
        nodes = (Position(2, 2), Position(8, 2))
        path = join_nodes(nodes)
        self.assertEqual(6 + 1, len(path))

    def test_join_nodes_withXAlignedNodes(self):
        nodes = (Position(2, 2), Position(2, 8))
        path = join_nodes(nodes)
        self.assertEqual(6 + 1, len(path))

    def test_join_nodes_withDiagonalNodes(self):
        nodes = (Position(2, 2), Position(8, 8))
        path = join_nodes(nodes)
        self.assertEqual(6 + 6 + 1, len(path))

    def test_join_nodes_withNegativeDirectionDiagonalNodes(self):
        nodes = (Position(8, 8), Position(2, 2))
        path = join_nodes(nodes)
        self.assertEqual(6 + 6 + 1, len(path))

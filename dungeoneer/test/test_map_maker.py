import unittest

from dungeoneer.map_maker import generate_map, DesignType, make_nodes
from dungeoneer.regions import Region, SubRegion


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
        for n in range(2, 16):
            with self.subTest(n=n):
                region = Region((50, 40))
                nodes = make_nodes(SubRegion(region), node_count=n)
                self.assertEqual(n, len(set(nodes)))



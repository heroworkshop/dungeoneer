import unittest
from unittest import skip

import pygame
from assertpy import assert_that

from dungeoneer.fov import raycast, unit_vectors
from dungeoneer.realms import Realm
from dungeoneer.regions import TileType

TILES = {
    "#": TileType.STONE_WALL,
    " ": TileType.STONE_FLOOR,
    "O": TileType.STONE_FLOOR
}

def tile_place(char_map, region):
    x = 0
    y = 0
    for ch in char_map:
        tile = TILES[ch]
        region.place_by_type((x, y), tile)
        x += 1
        if x == region.grid_width:
            x = 0
            y += 1

@skip
class MyRayCast(unittest.TestCase):
    def setUp(self):
        self.realm = Realm((1, 1), tile_size=(20, 20), region_size=(10, 7))
        self.pos = pygame.Vector2(100, 70)
        self.region = self.realm.region((0, 0))

    def test_raycast_withSEDirection_intersectsCorrectNumberOfWalls(self):
        char_map = ("##########"
                    "#        #"
                    "#      # #"
                    "#    O ###"
                    "#      # #"
                    "#    ### #"
                    "##########"
                    )


        tile_place(char_map, self.region)
        result = raycast(self.realm, self.pos, (1, 1))
        assert_that(result).is_length(4)

    def test_raycast_withNEDirection_intersectsCorrectNumberOfWalls(self):
        char_map = ("##########"
                    "#    ### #"
                    "#      # #"
                    "#    O ###"
                    "#        #"
                    "#        #"
                    "##########"
                    )
        tile_place(char_map, self.region)
        result = raycast(self.realm, self.pos, (1, -1))
        assert_that(result).is_length(4)

    def test_raycast_withNWDirection_intersectsCorrectNumberOfWalls(self):
        char_map = ("##########"
                    "#  ###   #"
                    "#  #     #"
                    "#  # O   #"
                    "#        #"
                    "#        #"
                    "##########"
                    )
        tile_place(char_map, self.region)
        result = raycast(self.realm, self.pos, (-1, -1))
        assert_that(result).is_length(4)

    def test_raycast_withSWDirection_intersectsCorrectNumberOfWalls(self):
        char_map = ("##########"
                    "#        #"
                    "#        #"
                    "#  # O   #"
                    "#  #     #"
                    "#  ###   #"
                    "##########"
                    )
        tile_place(char_map, self.region)
        result = raycast(self.realm, self.pos, (-1, 1))
        assert_that(result).is_length(4)

    def test_raycast_withLongWall_blocksViewAroundWall(self):
        char_map = ("##########"
                    "#        #"
                    "#    O   #"
                    "#        #"
                    "####     #"
                    "#        #"
                    "##########"
                    )
        self.pos = pygame.Vector2(100, 50)
        tile_place(char_map, self.region)
        result = raycast(self.realm, self.pos, (-1, 1))
        assert_that(result).is_length(8)

def render_vectors(unit_vectors, size):
    width, height = size
    across, up = unit_vectors
    print("Across")
    for dy in across:
        grid = {(0,0)}
        x, y = 0, 0
        print(dy)
        while x < width:
            x += 1
            y += dy
            grid.add((x, int(y)))
        show_grid(grid, size)

    print("Up")
    for dx in up:
        grid = {(0, 0)}
        x, y = 0, 0
        print(dx)
        while y < height:
            x += dx
            y += 1
            grid.add((int(x), y))
        show_grid(grid, size)

def show_grid(grid, size):
    w, h = size
    for y in range(h):
        for x in range(w):
            ch = "x" if (x, y) in grid else "."
            print(ch, end="")
        print()
    print()


class TestUnitVectors(unittest.TestCase):
    def test_unit_vectors_with4x4Grid(self):
        across, up = unit_vectors(4, 4)
        # render_vectors((across, up), (4, 4))
        assert_that(across).is_equal_to([0.0, 0.25, 0.5, 0.75, 1.0])
        assert_that(up).is_equal_to([0.0, 0.25, 0.5, 0.75, 1.0])

    def test_unit_vectors_with4x2Grid(self):
        across, up = unit_vectors(4, 2)
        # render_vectors((across, up), (4, 2))
        assert_that(across).is_equal_to([0.0, 0.25, 0.5])
        assert_that(up).is_equal_to([0.0, 0.5, 1.0, 1.5, 2.0])


if __name__ == '__main__':
    unittest.main()


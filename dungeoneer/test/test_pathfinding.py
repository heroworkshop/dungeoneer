import unittest

import pygame

from dungeoneer.interfaces import SpriteGroups
from dungeoneer.pathfinding import move_to_nearest_empty_space


class TinyBlock(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(*groups)
        self.rect = pygame.Rect(x, y, 1, 1)


class BigBlock(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        super().__init__(*groups)
        self.rect = pygame.Rect(x, y, 10, 10)


class TestMoveToNearestEmptySpace(unittest.TestCase):
    def test_move_withSpriteAlreadyInSpace_doesNotMove(self):
        world = SpriteGroups()
        tile = TinyBlock(1, 1)
        result = move_to_nearest_empty_space(tile, [world.solid], 3)
        self.assertEqual((1, 1), result.rect.center)

    def test_move_withSpriteOnTop_movesAdjacent(self):
        world = SpriteGroups()
        block = TinyBlock(1, 1, world.solid)
        tile = TinyBlock(1, 1)
        result = move_to_nearest_empty_space(tile, [world.solid], 3)
        self.assertFalse(result.rect.colliderect(block.rect))
        self.assertTrue(-1 < result.rect.centerx < 3)
        self.assertTrue(-1 < result.rect.centery < 3)

    def test_move_withSpriteNextToFreeSpace_movesRightIntoSpace(self):
        """
          ###
          ##
          ###
        """
        world = SpriteGroups()
        for x in range(3):
            for y in range(3):
                if (x, y) != (2, 1):
                    TinyBlock(x, y, world.solid)
        tile = TinyBlock(1, 1)
        result = move_to_nearest_empty_space(tile, [world.solid], 3)
        self.assertEqual((2, 1), result.rect.center)

    def test_move_withSpriteNextToFreeSpace_movesLeftIntoSpace(self):
        """
          ####
          # ##
          ####
        """
        world = SpriteGroups()
        for x in range(4):
            for y in range(3):
                if (x, y) != (1, 1):
                    TinyBlock(x, y, world.solid)
        tile = TinyBlock(2, 1)
        result = move_to_nearest_empty_space(tile, [world.solid], 3)
        self.assertEqual((1, 1), result.rect.center)

    @unittest.skip("Something odd going on here")
    def test_move_withSpriteNextToFreeSpaceBigBlocks_movesIntoSpace(self):
        """
          ####
          # ##
          ####
        """
        world = SpriteGroups()
        for x in range(0, 40, 10):
            for y in range(0, 30, 10):
                if (x, y) != (10, 10):
                    BigBlock(x, y, world.solid)
        tile = BigBlock(20, 10)
        result = move_to_nearest_empty_space(tile, [world.solid], 30)
        self.assertEqual((10, 10), result.rect.center)


if __name__ == '__main__':
    unittest.main()

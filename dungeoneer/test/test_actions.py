import unittest
import pygame

from dungeoneer import actions

class TestSprite(pygame.sprite.Sprite):
    def __init__(self, rect):
        super().__init__()
        self.rect = rect

class TestBaseClass(unittest.TestCase):
    def test_createActionBaseClass_raisesTypeError(self):
        with self.assertRaises(TypeError):
            actions.Action()


class TestAttackAction(unittest.TestCase):

    def test_valid_target_withTargetInRange_returnsTrue(self):
        attack_action = actions.AttackAction("sprite_sheet", 10, reach=1)
        owner = TestSprite(pygame.Rect(0, 0, 10, 10))
        target = TestSprite(pygame.Rect(1, 0, 10, 10))
        result = attack_action.valid_target(owner, target)
        self.assertEqual(True, result)

    def test_valid_target_withTargetOutOfRange_returnsFalse(self):
        attack_action = actions.AttackAction("sprite_sheet", 10, reach=1)
        owner = TestSprite(pygame.Rect(0, 0, 10, 10))
        target = TestSprite(pygame.Rect(2, 0, 10, 10))
        result = attack_action.valid_target(owner, target)
        self.assertEqual(False, result)

    def test_valid_target_withDiagonalTargetOutOfRange_returnsFalse(self):
        attack_action = actions.AttackAction("sprite_sheet", 10, reach=1)
        owner = TestSprite(pygame.Rect(0, 0, 10, 10))
        target = TestSprite(pygame.Rect(1, 1, 10, 10))
        result = attack_action.valid_target(owner, target)
        self.assertEqual(False, result)

        
if __name__ == '__main__':
    unittest.main()

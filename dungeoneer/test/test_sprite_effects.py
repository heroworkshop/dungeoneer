import unittest

import pygame

from dungeoneer import sprite_effects


class TestScalingEffects(unittest.TestCase):
    def test_throbbing_withSurface_returnsMultipleFrames(self):
        base_image = pygame.Surface((1, 1))
        result = sprite_effects.throbbing(base_image)
        self.assertGreater(len(result), 10)

    def test_scaling_effect_with3Factors_returns3Frames(self):
        base_image = pygame.Surface((1, 1))
        result = sprite_effects.scaling_effect(base_image, (1, .9, 1))
        self.assertEqual(len(result), 3)

    def test_scaling_effect_withSquareImage_returnsSomeSmallerImages(self):
        """Start with a square and make a filmstrip that looks like:
         1     2     3
        ####  ....  ####
        ####  .##.  ####
        ####  .##.  ####
        ####  ....  ####

        """
        base_image = pygame.Surface((4, 4))
        base_image.fill((255, 0, 0))
        result = sprite_effects.scaling_effect(base_image, (1, .5, 1))
        corners = [frame.get_at((0, 0)) for frame in result]
        centers = [frame.get_at((1, 1)) for frame in result]
        self.assertEqual(corners[0], corners[2])
        self.assertNotEqual(corners[0], corners[1])
        self.assertEqual(corners[0], centers[1])



if __name__ == '__main__':
    unittest.main()

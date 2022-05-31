import unittest

from dungeoneer.interfaces import SpriteGroups
from dungeoneer.scenery import VisualEffect
from dungeoneer.scenery import parabolic_motion
from dungeoneer.spritesheet import SpriteSheet
from dungeoneer.test.pixel_grid import make_pixel_grid

SPRITE_SHEET = SpriteSheet(make_pixel_grid(5, 2), 5, 2)
FILM_STRIP = SPRITE_SHEET.filmstrip(0, 10)


class TestScenery(unittest.TestCase):
    def test_VisualEffect_withRepeat_hasStartFrameAfterAllFramesUsed(self):
        # Set frame_length to -1 so that time is not a factor: this allows
        # the test to run at full speed without flakiness
        effect = VisualEffect(0, 0, FILM_STRIP, repeats=VisualEffect.FOREVER,
                              frame_length=-1)
        frame0 = effect.frame
        count = 0
        while True:  # Keep updating until the effect loops
            effect.update()
            count += 1
            if effect.frame == frame0:
                break

        self.assertEqual(count, len(FILM_STRIP))

    def test_VisualEffect_withNoRepeat_diesAfterFramesAreUsedUp(self):
        effect = VisualEffect(0, 0, FILM_STRIP, repeats=0, frame_length=-1)
        count = 0
        world = SpriteGroups()
        world.all.add(effect)
        while effect.alive():
            effect.update()
            count += 1

        self.assertEqual(count, len(FILM_STRIP))

    def test_VisualEffect_withTranslationList_movesOnUpdate(self):
        effect = VisualEffect(0, 0, FILM_STRIP, repeats=0, frame_length=-1,
                              motion=iter([(1, 1), (2, 0), (0, 2)]))
        effect.update()
        self.assertEqual((1, 1), effect.rect.center)
        effect.update()
        self.assertEqual((3, 1), effect.rect.center)
        effect.update()
        self.assertEqual((3, 3), effect.rect.center)


class TestMotionPathGeneration(unittest.TestCase):
    def test_parabolic_motion_withExactDivisibleWidth(self):
        result = parabolic_motion(15, 5, -2, 1)
        expected = [(3, -2), (3, -1), (3, 0), (3, 1), (3, 2)]
        self.assertEqual(expected, result)

    def test_parabolic_motion_withoutExactDivisibleWidth(self):
        result = parabolic_motion(15, 4, -2, 1)
        expected = [(3, -2), (4, -1), (4, 0), (4, 1)]
        self.assertEqual(expected, result)

    def test_parabolic_motion_withNegativeWidth(self):
        result = parabolic_motion(-15, 5, -2, 1)
        expected = [(-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2)]
        self.assertEqual(expected, result)

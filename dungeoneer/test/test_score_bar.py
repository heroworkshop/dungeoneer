import unittest

import pygame.font
from assertpy import assert_that

from dungeoneer.interfaces import Direction
from dungeoneer.score_bar import ScoreBar, NumericScoreBar
from dungeoneer.spritesheet import SpriteSheet
from dungeoneer.test.pixel_grid import make_pixel_grid


class TestScoreBar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.filmstrip = SpriteSheet(make_pixel_grid(5, 2), 5, 2).filmstrip()

    def test_score_bar_with10Units_createRectWidth10(self):
        bar = ScoreBar(0, 0, self.filmstrip, score=10, score_per_unit=1, direction=Direction.LEFT_TO_RIGHT)
        self.assertEqual(10, bar.rect.width)

    def test_score_bar_with10UnitsHorizontal_draws10Units(self):
        for direction in (Direction.RIGHT_TO_LEFT, Direction.LEFT_TO_RIGHT):
            with self.subTest(direction=direction):
                filmstrip = SpriteSheet(make_pixel_grid(5, 2), 5, 2, sub_area=(1, 1, 1, 1)).filmstrip()
                bar = ScoreBar(0, 0, filmstrip, score=10, score_per_unit=1, direction=direction)

                for i in range(10):
                    c = bar.image.get_at((i, 0))
                    self.assertEqual(6, c[0])
                self.assertEqual(10, bar.rect.width)

    def test_score_bar_with10UnitsVertical_draws10Units(self):
        for direction in (Direction.TOP_DOWN, Direction.BOTTOM_UP):
            with self.subTest(direction=direction):
                filmstrip = SpriteSheet(make_pixel_grid(5, 2), 5, 2, sub_area=(1, 1, 1, 1)).filmstrip()
                bar = ScoreBar(0, 0, filmstrip, score=10, score_per_unit=1, direction=direction)

                for i in range(10):
                    c = bar.image.get_at((0, i))
                    self.assertEqual(6, c[0])
                self.assertEqual(10, bar.rect.height)

    def test_score_bar_withLeftToRightDirection_createsRectHeight1(self):
        bar = ScoreBar(0, 0, self.filmstrip, score=10, score_per_unit=1, direction=Direction.LEFT_TO_RIGHT)

        self.assertEqual(1, bar.rect.height)

    def test_score_bar_withLeftToRightDirection_isLeftAligned(self):
        bar = ScoreBar(0, 0, self.filmstrip, score=10, score_per_unit=1, direction=Direction.LEFT_TO_RIGHT)

        self.assertEqual(0, bar.rect.left)
        self.assertEqual(10, bar.rect.right)

    def test_score_bar_withRightToLeftDirection_isRightAligned(self):
        bar = ScoreBar(0, 0, self.filmstrip, score=10, score_per_unit=1, direction=Direction.RIGHT_TO_LEFT)

        self.assertEqual(0, bar.rect.right)
        self.assertEqual(-10, bar.rect.left)

    def test_score_bar_withTopDownDirection_createsRectWidth1(self):
        bar = ScoreBar(0, 0, self.filmstrip, score=1000, score_per_unit=100, direction=Direction.TOP_DOWN)

        self.assertEqual(1, bar.rect.width)

    def test_score_bar_withTopDownDirection_isTopAligned(self):
        bar = ScoreBar(0, 0, self.filmstrip, score=1000, score_per_unit=100, direction=Direction.TOP_DOWN)
        self.assertEqual(0, bar.rect.top)
        self.assertEqual(10, bar.rect.bottom)

    def test_score_bar_withBottomUpDirection_isBottomAligned(self):
        bar = ScoreBar(0, 0, self.filmstrip, score=1000, score_per_unit=100, direction=Direction.BOTTOM_UP)
        self.assertEqual(0, bar.rect.bottom)
        self.assertEqual(-10, bar.rect.top)

    def test_score_bar_withZeroScore_returnsWidth1Image(self):
        bar = ScoreBar(0, 0, self.filmstrip, score=0, score_per_unit=1)
        self.assertEqual(1, bar.image.get_width())


class TestNumericScoreBar(unittest.TestCase):
    EXPECTED_SIZES = {20: (7, 13)}

    @classmethod
    def setUpClass(cls):
        pygame.font.init()
        cls.filmstrip = SpriteSheet(make_pixel_grid(5, 2), 5, 2).filmstrip()

    def test_numeric_score_bar_withHorizontal3DigitNumber(self):
        font_size = 20
        expected_digit_width, expected_digit_height = self.EXPECTED_SIZES[font_size]
        for direction in (Direction.LEFT_TO_RIGHT, Direction.RIGHT_TO_LEFT):
            with self.subTest(direction=direction):
                bar = NumericScoreBar(0, 0, self.filmstrip, score=999, font_size=font_size, direction=direction)
                assert_that(bar.image.get_width()).is_equal_to(1 + 3 * expected_digit_width + 5)
                assert_that(bar.image.get_height()).is_equal_to(expected_digit_height)

    def test_numeric_score_bar_withHorizontal1DigitNumber(self):
        font_size = 20
        expected_digit_width, expected_digit_height = self.EXPECTED_SIZES[font_size]
        for direction in (Direction.LEFT_TO_RIGHT, Direction.RIGHT_TO_LEFT):
            with self.subTest(direction=direction):
                bar = NumericScoreBar(0, 0, self.filmstrip, score=9, font_size=font_size, direction=direction)
                assert_that(bar.image.get_width()).is_equal_to(1 + expected_digit_width + 5)
                assert_that(bar.image.get_height()).is_equal_to(expected_digit_height)

    def test_numeric_score_bar_withVertical3DigitNumber(self):
        font_size = 20
        expected_digit_width, expected_digit_height = self.EXPECTED_SIZES[font_size]
        for direction in (Direction.TOP_DOWN, Direction.BOTTOM_UP):
            with self.subTest(direction=direction):
                bar = NumericScoreBar(0, 0, self.filmstrip, score=999, font_size=font_size, direction=direction)
                assert_that(bar.image.get_height()).is_equal_to(1 + expected_digit_height + 5)
                assert_that(bar.image.get_width()).is_equal_to(3 * expected_digit_width)

    def test_numeric_score_bar_withVertical1DigitNumber(self):
        font_size = 20
        expected_digit_width, expected_digit_height = self.EXPECTED_SIZES[font_size]
        for direction in (Direction.TOP_DOWN, Direction.BOTTOM_UP):
            with self.subTest(direction=direction):
                bar = NumericScoreBar(0, 0, self.filmstrip, score=9, font_size=font_size, direction=direction)
                assert_that(bar.image.get_height()).is_equal_to(1 + expected_digit_height + 5)
                assert_that(bar.image.get_width()).is_equal_to(expected_digit_width)


if __name__ == '__main__':
    unittest.main()

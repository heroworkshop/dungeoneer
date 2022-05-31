import unittest

from dungeoneer.interfaces import Direction
from dungeoneer.score_bar import ScoreBar
from dungeoneer.spritesheet import SpriteSheet
from dungeoneer.test.pixel_grid import make_pixel_grid


class TestScoreBar(unittest.TestCase):
    def test_score_bar_with10Units_createRectWidth10(self):
        filmstrip = SpriteSheet(make_pixel_grid(5, 2), 5, 2).filmstrip()
        bar = ScoreBar(0, 0, filmstrip, score=10, score_per_unit=1, direction=Direction.LEFT_TO_RIGHT)
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
        filmstrip = SpriteSheet(make_pixel_grid(5, 2), 5, 2).filmstrip()
        bar = ScoreBar(0, 0, filmstrip, score=10, score_per_unit=1, direction=Direction.LEFT_TO_RIGHT)

        self.assertEqual(1, bar.rect.height)

    def test_score_bar_withLeftToRightDirection_isLeftAligned(self):
        filmstrip = SpriteSheet(make_pixel_grid(5, 2), 5, 2).filmstrip()
        bar = ScoreBar(0, 0, filmstrip, score=10, score_per_unit=1, direction=Direction.LEFT_TO_RIGHT)

        self.assertEqual(0, bar.rect.left)
        self.assertEqual(10, bar.rect.right)

    def test_score_bar_withRightToLeftDirection_isRightAligned(self):
        filmstrip = SpriteSheet(make_pixel_grid(5, 2), 5, 2).filmstrip()
        bar = ScoreBar(0, 0, filmstrip, score=10, score_per_unit=1, direction=Direction.RIGHT_TO_LEFT)

        self.assertEqual(0, bar.rect.right)
        self.assertEqual(-10, bar.rect.left)

    def test_score_bar_withTopDownDirection_createsRectWidth1(self):
        filmstrip = SpriteSheet(make_pixel_grid(5, 2), 5, 2).filmstrip()
        bar = ScoreBar(0, 0, filmstrip, score=1000, score_per_unit=100, direction=Direction.TOP_DOWN)

        self.assertEqual(1, bar.rect.width)

    def test_score_bar_withTopDownDirection_isTopAligned(self):
        filmstrip = SpriteSheet(make_pixel_grid(5, 2), 5, 2).filmstrip()
        bar = ScoreBar(0, 0, filmstrip, score=1000, score_per_unit=100, direction=Direction.TOP_DOWN)
        self.assertEqual(0, bar.rect.top)
        self.assertEqual(10, bar.rect.bottom)

    def test_score_bar_withBottomUpDirection_isBottomAligned(self):
        filmstrip = SpriteSheet(make_pixel_grid(5, 2), 5, 2).filmstrip()
        bar = ScoreBar(0, 0, filmstrip, score=1000, score_per_unit=100, direction=Direction.BOTTOM_UP)
        self.assertEqual(0, bar.rect.bottom)
        self.assertEqual(-10, bar.rect.top)

    def test_score_bar_withZeroScore_returnsWidth1Image(self):
        filmstrip = SpriteSheet(make_pixel_grid(5, 2), 5, 2).filmstrip()
        bar = ScoreBar(0, 0, filmstrip, score=0, score_per_unit=1)
        self.assertEqual(1, bar.image.get_width())


if __name__ == '__main__':
    unittest.main()

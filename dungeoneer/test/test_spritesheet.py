import unittest

from dungeoneer.spritesheet import SpriteSheet
from dungeoneer.test.pixel_grid import make_pixel_grid


class TestSpriteSheet(unittest.TestCase):
    def test_filmstrip_with2by3_returnsSixFrames(self):
        spritesheet = SpriteSheet(make_pixel_grid(5, 2), 5, 2)
        filmstrip = spritesheet.filmstrip(0, 10)
        self.assertEqual(10, len(filmstrip))
        for i, frame in enumerate(filmstrip):
            r, g, b, alpha = frame.get_at((0, 0))
            self.assertEqual(i, r)
            self.assertEqual((1, 1), frame.get_size())

    def test_surface_by_index_returnsSurface(self):
        spritesheet = SpriteSheet(make_pixel_grid(5, 2), 5, 2)
        for i in range(10):
            surface = spritesheet.surface_by_index(i)
            r, g, b, alpha = surface.get_at((0, 0))
            self.assertEqual(i, r)

    def test_sub_area_indices_withSubArea_returnsOnlySubAreaIndices(self):
        sub_area = (2, 0, 2, 2)
        spritesheet = SpriteSheet(make_pixel_grid(5, 2), 5, 2, sub_area)
        result = spritesheet.sub_area_indices()
        self.assertEqual([2, 3, 7, 8], result)

    def test_filmstrip_withSubArea_returnsSubarea(self):
        sub_area = (2, 0, 2, 2)
        image = make_pixel_grid(5, 2)

        spritesheet = SpriteSheet(image, 5, 2, sub_area)

        filmstrip = spritesheet.filmstrip(0, 4)
        self.assertEqual(4, len(filmstrip))
        expected = [2, 3, 7, 8]
        for i, frame in enumerate(filmstrip):
            r, g, b, alpha = frame.get_at((0, 0))
            self.assertEqual(expected[i], r)
            self.assertEqual((1, 1), frame.get_size())


if __name__ == '__main__':
    unittest.main()

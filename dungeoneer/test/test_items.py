import unittest
from dungeoneer import items


class TestItems(unittest.TestCase):
    def test_ammo_dict_containsArrow(self):
        arrow = items.ammo["arrow"]
        self.assertEqual("arrow", arrow.name)
        self.assertTrue(arrow.damage)
        self.assertTrue(arrow.speed)
        self.assertTrue(arrow.damage_profile)


if __name__ == '__main__':
    unittest.main()

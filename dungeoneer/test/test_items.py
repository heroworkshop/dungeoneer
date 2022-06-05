import unittest

from assertpy import assert_that

from dungeoneer import items


class TestItems(unittest.TestCase):
    def test_ammo_dict_containsValidArrow(self):
        arrow = items.ammo["arrow"]
        assert_that(arrow.name).is_equal_to("arrow")
        assert_that(arrow.damage).is_greater_than(0)
        assert_that(arrow.speed).is_greater_than(0)
        assert_that(sum(arrow.damage_profile)).is_equal_to(100)
        assert_that(arrow.survivability).is_greater_than_or_equal_to(0).is_less_than(100)


if __name__ == '__main__':
    unittest.main()

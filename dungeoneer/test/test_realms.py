import unittest

from assertpy import assert_that

from dungeoneer.realms import Realm, PointOutsideRealmBoundary
from dungeoneer.regions import Region


class TestRealm(unittest.TestCase):
    def test_Realm_withSize5by5_has25Regions(self):
        realm = Realm((5, 5), tile_size=(20, 20))

        assert_that(realm).is_length(25)
        assert_that(realm.region((0, 0))).is_instance_of(Region)

    def test_region_from_pixel_position_with10x10Regions_returnsCorrectRegion(self):
        coords = {
            (0, 0): (0, 0),
            (5, 0): (0, 0),
            (100, 0): (1, 0),
            (0, 200): (0, 1),
            (999, 1999): (9, 9),
        }
        realm = Realm((10, 10), tile_size=(10, 20), region_size=(10, 10))
        for pixel_pos, region_pos in coords.items():
            with self.subTest(pixel_pos=pixel_pos):
                region = realm.region_from_pixel_position(pixel_pos)
                assert_that(region).is_equal_to(realm.region(region_pos))

    def test_region_from_pixel_position_withPixelPosOutsideRealm_raisesPointOutsideRealmBoundary(self):
        coords = [
            (-1, -1),
            (-1, 0),
            (0, -1),
            (1000, 0),
            (0, 2000),
            (1000, 2000)
        ]
        realm = Realm((10, 10), tile_size=(10, 20), region_size=(10, 10))
        for pixel_pos in coords:
            with self.subTest(pixel_pos=pixel_pos):
                assert_that(realm.region_from_pixel_position). \
                    raises(PointOutsideRealmBoundary). \
                    when_called_with(pixel_pos)

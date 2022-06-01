import unittest

import pygame
from assertpy import assert_that

from dungeoneer.realms import Realm, PointOutsideRealmBoundary
from dungeoneer.regions import Region


class TestRealm(unittest.TestCase):
    def test_out_of_bounds_withSpriteInsideRealm_returnsFalse(self):
        realm = Realm((5, 5), tile_size=(20, 20))
        sprite = pygame.sprite.Sprite()
        sprite.rect = pygame.Rect(100, 100, 5, 5)
        assert_that(realm.out_of_bounds(sprite)).is_false()

    def test_out_of_bounds_withSpriteOutsideRealm_returnsFalse(self):
        realm = Realm((5, 5), tile_size=(20, 20), region_size=(10, 10))
        sprite = pygame.sprite.Sprite()
        sprite.rect = pygame.Rect(1050, 100, 5, 5)
        assert_that(realm.out_of_bounds(sprite)).is_true()


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

    def test_neighbouring_regions_withPixelInCornerOfRegion_has4Neighbours(self):
        realm = Realm((5, 5), tile_size=(20, 20), region_size=(10, 10))
        # region pixel width and height are 10 * 20 = (200 x 200)
        # pick pixel in region(1, 1) which should have 9 neighbours
        neighbours = realm.neighbouring_regions_from_pixel_position((200, 200))
        assert_that(neighbours).is_length(4)


    def test_neighbouring_regions_withPixelNotInCornerOfRegion_has9Neighbours(self):
        realm = Realm((5, 5), tile_size=(20, 20), region_size=(10, 10))
        # region pixel width and height are 10 * 20 = (200 x 200)
        # pick pixel in region(1, 1) which should have 9 neighbours
        neighbours = realm.neighbouring_regions_from_pixel_position((201, 201))
        assert_that(neighbours).is_length(9)


    def test_neighbouring_regions_withPixelInCornerOfBorderRegion_has1Neighbour(self):
        # Because it is a corner region, there are no neighbours so the only match is
        # the region itself
        realm = Realm((5, 5), tile_size=(20, 20), region_size=(10, 10))
        neighbours = realm.neighbouring_regions_from_pixel_position((0, 0))
        assert_that(neighbours).is_length(1)

import unittest

from assertpy import assert_that

from dungeoneer.main import DungeoneerGame


class TestDungeoneerGame(unittest.TestCase):
    def setUp(self):
        self.game = DungeoneerGame((1000, 1000), realm_size=(2, 2))

    def test_initialise_realm_generatesABackground_asBigAsAllRegionsInRealm(self):
        self.game.initialise_realm()
        assert_that(self.game.background.get_size()).is_equal_to((2000, 2000))

    def test_place_player_inEmptyRegion_placesPlayerInCentreOfRegion(self):
        self.game.place_player((1, 1))
        assert_that(self.game.player.rect.center).is_equal_to((1500, 1500))

    def test_place_player_movesCameraCenteredOnPlayer(self):
        self.game.place_player((1, 1))
        assert_that(self.game.camera.offset).is_equal_to((-1000, -1000))

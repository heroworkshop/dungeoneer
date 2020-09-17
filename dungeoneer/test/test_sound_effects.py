import unittest

import pygame

from dungeoneer.sound_effects import SfxEvents


class TestItemSoundFiles(unittest.TestCase):
    def test_SfxEvents_withNoSoundEffects_hhasPickupAttributeInSfxEventsWithPlayMethod(self):
        sfx = SfxEvents()
        pygame.init()
        pygame.mixer.init(frequency=44100)
        self.assertTrue(hasattr(sfx.pickup, "play"))

    def test_Item_withOnPickupSoundEffect_hasPickupAttributeInSfxEventsWithPlayMethod(self):
        sfx = SfxEvents(pickup="sword_pickup.ogg")
        pygame.init()
        pygame.mixer.init(frequency=44100)
        self.assertTrue(hasattr(sfx.pickup, "play"))


if __name__ == '__main__':
    unittest.main()

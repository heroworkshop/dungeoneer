from contextlib import suppress

import pygame
import random

from dungeoneer.actors import Player
from dungeoneer.interfaces import KeyObserver
from dungeoneer.inventory import Inventory
from dungeoneer.scenery import parabolic_motion

SLOT_KEYS = {
    pygame.K_0: 0,
    pygame.K_1: 1,
    pygame.K_2: 2,
    pygame.K_3: 3,
    pygame.K_4: 4,
    pygame.K_5: 5,
    pygame.K_6: 6,
    pygame.K_7: 7,
    pygame.K_8: 8,
    pygame.K_9: 9,
}

ACTION_KEYS = {
    pygame.K_RETURN,
    pygame.K_SPACE,
    pygame.K_a,  # left
    pygame.K_d,  # right
    pygame.K_s,  # down
}


class InventoryController(KeyObserver):
    """The InventoryController accepts user input and converts them into commands to perform on an inventory.

    This class is part of MVC architecture
      For the model see Inventory.
      For the view see InventoryView

    It is intended that this is used in conjunction with a KeyEventDispatcher.
    """
    def __init__(self, inventory: Inventory, player: Player, key_map=SLOT_KEYS):
        self.inventory = inventory
        self.key_map = key_map
        self.player = player

    def observes_keys(self):
        """Return set of pygame key ids that the controller is interested in"""
        return set(self.key_map.keys()).union(ACTION_KEYS)

    def on_key_down(self, key):
        slot_index = self.inventory.current_selection
        if slot_index is None:
            with suppress(KeyError):
                slot_number = self.key_map[key]
                self.inventory.select(slot_number)
            return

        # do special stuff:
        if key == pygame.K_s:  # down direction = drop
            self.throw_item(slot_index, 15 * random.choice((1, -1)))
        elif key == pygame.K_a:  # left = throw left
            self.throw_item(slot_index, -100)
        elif key == pygame.K_d:  # right = throw right
            self.throw_item(slot_index, 100)
        # return = activate
        elif key in SLOT_KEYS.keys():  # number = swap
            self.inventory.swap(SLOT_KEYS[key], slot_index)
        self.inventory.current_selection = None

    def throw_item(self, slot_index, distance):
        arc = parabolic_motion(distance, 15, -3, 0.5)
        drop_item = self.inventory.remove_item(slot_index)
        if drop_item:
            self.player.drop(drop_item, motion=iter(arc))

    def on_key_up(self, key):
        pass

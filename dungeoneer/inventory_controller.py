from contextlib import suppress

import pygame

from dungeoneer.actors import Player
from dungeoneer.interfaces import KeyObserver
from dungeoneer.inventory import Inventory

SLOT_KEYS = {
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

ACTION_KEYS ={
    pygame.K_RETURN,
    pygame.K_SPACE,
    pygame.K_a,  # left
    pygame.K_d,  # right
    pygame.K_s,  # down
}


class InventoryController(KeyObserver):
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

        # down direction = drop
        if key == pygame.K_s:
            drop_item = self.inventory.remove_item(slot_index)
            self.player.drop(drop_item)
        # left or right = throw
        # return = activate
        # number = swap
        self.inventory.current_selection = None

    def on_key_up(self, key):
        pass

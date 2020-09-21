import unittest
from unittest.mock import MagicMock

import pygame

from dungeoneer import interfaces
from dungeoneer.actors import Player
from dungeoneer.event_dispatcher import KeyEventDispatcher
from dungeoneer.interfaces import Item
from dungeoneer.inventory import Inventory
from dungeoneer.inventory_controller import InventoryController


class TestInventoryController(unittest.TestCase):
    def test_on_key_down_withKey9DownFromDispatcher_selectsSlot9(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), 9)
        controller = InventoryController(inventory, player=None)
        dispatcher = KeyEventDispatcher()
        dispatcher.register(controller)
        dispatcher.event(pygame.KEYDOWN, pygame.K_9)
        selected_item = inventory.slot(inventory.current_selection)
        self.assertEqual("arrow", selected_item.name)

    def test_on_key_down_withAlreadySelectedItem_deselectsItem(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), 9)
        inventory.current_selection = 9
        controller = InventoryController(inventory, player=None)
        dispatcher = KeyEventDispatcher()
        dispatcher.register(controller)
        dispatcher.event(pygame.KEYDOWN, pygame.K_9)
        self.assertEqual(None, inventory.current_selection)

    def test_on_key_down_withDropKey_tellsPlayerToDropItem(self):

        player = MagicMock()
        inventory = Inventory()
        arrow = Item("arrow")
        inventory.add_item(arrow, 9)
        inventory.current_selection = 9
        controller = InventoryController(inventory, player)
        dispatcher = KeyEventDispatcher()
        dispatcher.register(controller)
        dispatcher.event(pygame.KEYDOWN, pygame.K_s)  # by default this is the down key = drop
        self.assertEqual(0, len(inventory.items))
        player.drop.called_with(arrow)


if __name__ == '__main__':
    unittest.main()

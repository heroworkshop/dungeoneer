import unittest

from dungeoneer import interfaces, item_sprites
from dungeoneer.interfaces import Item


class TestItemSpriteActions(unittest.TestCase):
    def test_drop_item_withItemStackAsSpec_dropsSingleItem(self):
        item_spec = Item("sword", count=5)
        world = interfaces.SpriteGroups()
        dropped_item = item_sprites.drop_item(item_spec, world, 0, 0)

        self.assertEqual(1, dropped_item.item_spec.count)

    def test_drop_item_withCountOf5_dropsItemWithCountOf5(self):
        item_spec = Item("sword", count=2)
        world = interfaces.SpriteGroups()
        dropped_item = item_sprites.drop_item(item_spec, world, 0, 0, count=5)
        self.assertEqual(5, dropped_item.item_spec.count)

    def test_drop_item_addsItemToAllGroup(self):
        item_spec = Item("sword")
        world = interfaces.SpriteGroups()
        dropped_item = item_sprites.drop_item(item_spec, world, 0, 0, count=5)
        self.assertTrue(world.all.has(dropped_item))

    def test_drop_item_addsItemToItemsGroup(self):
        item_spec = Item("sword")
        world = interfaces.SpriteGroups()
        dropped_item = item_sprites.drop_item(item_spec, world, 0, 0, count=5)
        self.assertTrue(world.items.has(dropped_item))

if __name__ == '__main__':
    unittest.main()

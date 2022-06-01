import unittest

from dungeoneer import interfaces, item_sprites
from dungeoneer.interfaces import Item
from dungeoneer.realms import Realm


class TestItemSpriteActions(unittest.TestCase):
    def setUp(self):
        self.realm = Realm((10, 10), tile_size=(40, 40))
        self.region = self.realm.region_from_pixel_position((0, 0))

    def test_drop_item_withItemStackAsSpec_dropsSingleItem(self):
        item_spec = Item("sword", count=5)
        dropped_item = item_sprites.drop_item(item_spec, self.realm, 0, 0)
        self.assertEqual(1, dropped_item.item_spec.count)

    def test_drop_item_withCountOf5_dropsItemWithCountOf5(self):
        item_spec = Item("sword", count=2)
        dropped_item = item_sprites.drop_item(item_spec, self.realm, 0, 0, count=5)
        self.assertEqual(5, dropped_item.item_spec.count)

    def test_drop_item_addsItemToAllGroup(self):
        item_spec = Item("sword")
        dropped_item = item_sprites.drop_item(item_spec, self.realm, 0, 0, count=5)
        self.assertTrue(self.region.groups.all.has(dropped_item))

    def test_drop_item_addsItemToItemsGroup(self):
        item_spec = Item("sword")
        dropped_item = item_sprites.drop_item(item_spec, self.realm, 0, 0, count=5)
        self.assertTrue(self.region.groups.items.has(dropped_item))


if __name__ == '__main__':
    unittest.main()

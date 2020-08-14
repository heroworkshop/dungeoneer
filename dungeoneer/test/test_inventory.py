import unittest
from dungeoneer.inventory import Inventory, InventoryFull
from dungeoneer.interfaces import Item


class FakeSword(Item):
    @staticmethod
    def name():
        return "sword"


class FakeArrow(Item):
    @staticmethod
    def name():
        return "arrow"


class TestInventory(unittest.TestCase):
    def test_creatingInventory_isEmpty(self):
        inventory = Inventory()
        self.assertEqual(0, len(inventory.items))

    def test_add_item_withEmptyInventory_addsItemToTopOfInventory(self):
        inventory = Inventory()

        inventory.add_item(FakeSword())

        items = inventory.items
        self.assertEqual("sword", items[0].name())
        self.assertEqual(1, len(inventory.items))

    def test_add_item_withPartiallyFullInventory_addsItemInFirstEmptySlotItems(self):
        inventory = Inventory()
        inventory.add_item(FakeSword())
        inventory.add_item(FakeArrow())
        items = inventory.items
        self.assertEqual("sword", items[0].name())
        self.assertEqual("arrow", items[1].name())
        self.assertEqual(2, len(inventory.items))

    def test_add_item_withMatchingItemInInventory_IncreasesItemCount(self):
        inventory = Inventory()
        inventory.add_item(FakeArrow())
        inventory.add_item(FakeArrow())
        self.assertEqual(1, len(inventory.items))

    def test_len_of_inventory_returnsNumberOfSlots(self):
        inventory = Inventory()
        size = len(inventory)
        self.assertEqual(len(inventory.slots), size)

    def test_add_item_withFullInventory_raisesInventoryFull(self):
        inventory = Inventory()
        for i, item in enumerate([FakeSword()] * len(inventory)):
            inventory.add_item(item, slot=i)
        with self.assertRaises(InventoryFull):
            inventory.add_item(FakeArrow())

    def test_add_item_withIndex_replacesItemAtIndex(self):
        inventory = Inventory()
        inventory.slots[0] = FakeSword()
        drop = inventory.add_item(FakeArrow(), slot=0)
        self.assertEqual("sword", drop.name())

    def test_add_item_withEmptyInventory_hasItemCountOnOne(self):
        inventory = Inventory()
        inventory.add_item(FakeArrow(), slot=0)
        item = inventory.slots[0]
        self.assertEqual(1, item.count)

    def test_add_item_withExistingDuplicateItem_incrementsItemCount(self):
        inventory = Inventory()
        inventory.add_item(FakeArrow(), slot=5)
        inventory.add_item(FakeArrow())
        item = inventory.slots[5]
        self.assertEqual(2, item.count)

    def test_ammo_withItemInAmmoSlot_returnsAmmo(self):
        inventory = Inventory()
        inventory.slots[inventory.AMMO] = FakeArrow()
        self.assertEqual("arrow", inventory.ammo.name())


if __name__ == '__main__':
    unittest.main()

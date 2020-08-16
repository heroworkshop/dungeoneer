import unittest
from dungeoneer.inventory import Inventory, InventoryFull
from dungeoneer.interfaces import Item


class TestInventory(unittest.TestCase):
    def test_creatingInventory_isEmpty(self):
        inventory = Inventory()
        self.assertEqual(0, len(inventory.items))

    def test_add_item_withEmptyInventory_addsItemToTopOfInventory(self):
        inventory = Inventory()

        inventory.add_item(Item("sword"))

        items = inventory.items
        self.assertEqual("sword", items[0].name)
        self.assertEqual(1, len(inventory.items))

    def test_add_item_withPartiallyFullInventory_addsItemInFirstEmptySlotItems(self):
        inventory = Inventory()
        inventory.add_item(Item("sword"))
        inventory.add_item(Item("arrow"))
        items = inventory.items
        self.assertEqual("sword", items[0].name)
        self.assertEqual("arrow", items[1].name)
        self.assertEqual(2, len(inventory.items))

    def test_add_item_withMatchingItemInInventory_IncreasesItemCount(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"))
        inventory.add_item(Item("arrow"))
        self.assertEqual(1, len(inventory.items))

    def test_len_of_inventory_returnsNumberOfSlots(self):
        inventory = Inventory()
        size = len(inventory)
        self.assertEqual(len(inventory.slots), size)

    def test_add_item_withFullInventory_raisesInventoryFull(self):
        inventory = Inventory()
        for i, item in enumerate([Item("sword")] * len(inventory)):
            inventory.add_item(item, slot=i)
        with self.assertRaises(InventoryFull):
            inventory.add_item(Item("arrow"))

    def test_add_item_withIndex_replacesItemAtIndex(self):
        inventory = Inventory()
        inventory.slots[0] = Item("sword")
        drop = inventory.add_item(Item("arrow"), slot=0)
        self.assertEqual("sword", drop.name)

    def test_add_item_withEmptyInventory_hasItemCountOnOne(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), slot=0)
        item = inventory.slots[0]
        self.assertEqual(1, item.count)

    def test_add_item_withExistingDuplicateItem_incrementsItemCount(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), slot=5)
        inventory.add_item(Item("arrow"))
        item = inventory.slots[5]
        self.assertEqual(2, item.count)

    def test_ammo_withItemInAmmoSlot_returnsAmmo(self):
        inventory = Inventory()
        inventory.slots[inventory.AMMO] = Item("arrow")
        self.assertEqual("arrow", inventory.ammo.name)

    def test_remove_withItemInSlot_returnsItem(self):
        inventory = Inventory()
        inventory.slots[inventory.AMMO] = Item("arrow")
        item = inventory.remove(inventory.AMMO)
        self.assertEqual("arrow", item.name)

    def test_remove_withItemInSlot_removesItem(self):
        inventory = Inventory()
        inventory.slots[inventory.AMMO] = Item("arrow")
        inventory.slots[inventory.WEAPON] = Item("sword")
        inventory.remove(inventory.AMMO)
        self.assertEqual(1, len(inventory.items))
        self.assertEqual(None, inventory.slots[inventory.AMMO])

    def test_remove_withMultipleItemsInSlot_removesOneItem(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), slot=inventory.AMMO)
        inventory.add_item(Item("arrow"), slot=inventory.AMMO)
        inventory.remove(inventory.AMMO)
        self.assertEqual(1, len(inventory.items))
        self.assertEqual(1, inventory.slots[inventory.AMMO].count)


if __name__ == '__main__':
    unittest.main()

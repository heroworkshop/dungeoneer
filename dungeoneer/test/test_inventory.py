import unittest
from dungeoneer.inventory import Inventory, InventoryFull
from dungeoneer.interfaces import Item, Observer


class ItemListener(Observer):
    def __init__(self):
        self.last_received = dict()
        self.notification_count = 0

    def on_update(self, attribute, value):
        self.last_received[attribute] = value
        self.notification_count += 1


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
        self.assertEqual(len(inventory), size)

    def test_add_item_withFullInventory_raisesInventoryFull(self):
        inventory = Inventory()
        for i, item in enumerate([Item("sword")] * len(inventory)):
            inventory.add_item(item, slot=i)
        with self.assertRaises(InventoryFull):
            inventory.add_item(Item("arrow"))

    def test_add_item_withIndex_replacesItemAtIndex(self):
        inventory = Inventory()
        inventory.add_item(Item("sword"), slot=0)
        drop = inventory.add_item(Item("arrow"), slot=0)
        self.assertEqual("sword", drop.name)

    def test_add_item_withEmptyInventory_hasItemCountOnOne(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), slot=0)
        item = inventory.slot(0)
        self.assertEqual(1, item.count)

    def test_add_item_withExistingDuplicateItem_incrementsItemCount(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), slot=5)
        inventory.add_item(Item("arrow"))
        item = inventory.slot(5)
        self.assertEqual(2, item.count)

    def test_add_item_withPreferredSlotEmpty_addsToPreferredSlot(self):
        inventory = Inventory()
        arrow = Item("arrow")
        arrow.preferred_slot = inventory.AMMO
        inventory.add_item(arrow)
        self.assertEqual("arrow", inventory.slot(inventory.AMMO).name)

    def test_ammo_withItemInAmmoSlot_returnsAmmo(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), inventory.AMMO)
        self.assertEqual("arrow", inventory.ammo.name)

    def test_remove_withEmptySlot_returnsNone(self):
        inventory = Inventory()
        item = inventory.remove_item(inventory.AMMO)
        self.assertIs(None, item)

    def test_remove_withItemInSlot_returnsItem(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), inventory.AMMO)
        item = inventory.remove_item(inventory.AMMO)
        self.assertEqual("arrow", item.name)

    def test_remove_withItemInSlot_removesItem(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), slot=inventory.AMMO)
        inventory.add_item(Item("sword"), slot=inventory.WEAPON)
        inventory.remove_item(inventory.AMMO)
        self.assertEqual(1, len(inventory.items))
        self.assertEqual(None, inventory.slot(inventory.AMMO))

    def test_remove_withMultipleItemsInSlot_removesOneItem(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), slot=inventory.AMMO)
        inventory.add_item(Item("arrow"), slot=inventory.AMMO)
        inventory.remove_item(inventory.AMMO)
        self.assertEqual(1, len(inventory.items))
        self.assertEqual(1, inventory.slot(inventory.AMMO).count)

    def test_add_observer_withItemInInventory_notifiesListenerOfItem(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), slot=inventory.AMMO)
        listener = ItemListener()
        inventory.add_observer(listener, inventory.AMMO)
        result = listener.last_received[inventory.AMMO]
        self.assertEqual("arrow", result.name)

    def test_add_item_withListener_notifiesListenerOfNewItem(self):
        inventory = Inventory()
        listener = ItemListener()
        inventory.add_observer(listener, inventory.AMMO)
        inventory.add_item(Item("arrow"), slot=Inventory.AMMO)
        result = listener.last_received[inventory.AMMO]
        self.assertEqual("arrow", result.name)

    def test_remove_item_withListener_notifiesListenerOfNewState(self):
        inventory = Inventory()
        listener = ItemListener()
        inventory.add_item(Item("arrow", count=2), slot=Inventory.AMMO)
        inventory.add_observer(listener, inventory.AMMO)
        result = listener.last_received[inventory.AMMO]
        self.assertEqual("arrow", result.name)
        self.assertEqual(2, result.count)
        inventory.remove_item(Inventory.AMMO)
        result = listener.last_received[inventory.AMMO]
        self.assertEqual("arrow", result.name)
        self.assertEqual(1, result.count)

    def test_remove_item_withListenerAndLastItem_notifiesListenerOfEmpty(self):
        inventory = Inventory()
        listener = ItemListener()
        inventory.add_item(Item("arrow", count=1), slot=Inventory.AMMO)
        inventory.add_observer(listener, inventory.AMMO)
        inventory.remove_item(Inventory.AMMO)
        result = listener.last_received[inventory.AMMO]
        self.assertEqual(None, result)
        self.assertEqual(2, listener.notification_count)

    def test_replace_item_withListener_notifiesListenerOfNewItem(self):
        inventory = Inventory()
        listener = ItemListener()
        inventory.add_observer(listener, inventory.AMMO)
        inventory.add_item(Item("arrow", count=1), slot=Inventory.AMMO)
        inventory.remove_item(Inventory.AMMO)
        inventory.add_item(Item("iron shot", count=1), slot=Inventory.AMMO)
        result = listener.last_received[inventory.AMMO]
        self.assertEqual("iron shot", result.name)
        self.assertEqual(4, listener.notification_count)

    def test_iterate_withEmptyInventory_iterates10Nones(self):
        inventory = Inventory()
        result = list(inventory)
        self.assertEqual([None] * 10, result)

if __name__ == '__main__':
    unittest.main()

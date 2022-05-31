import unittest
from contextlib import suppress

from dungeoneer.interfaces import Item, Observer
from dungeoneer.inventory import Inventory, InventoryFull
from dungeoneer.items import Food


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
        first_generic_slot = len(inventory.special_slots)
        inventory.add_item(Item("A"))

        item = inventory.slot(first_generic_slot)
        self.assertEqual("A", item.name)
        self.assertEqual(1, len(inventory.items))

    def test_add_item_withPartiallyFullInventory_addsItemInFirstEmptySlot(self):
        inventory = Inventory()
        first_generic_slot = len(inventory.special_slots)
        inventory.add_item(Item("A"))
        inventory.add_item(Item("B"))
        item_a = inventory.slot(first_generic_slot)
        item_b = inventory.slot(first_generic_slot + 1)
        self.assertEqual("A", item_a.name)
        self.assertEqual("B", item_b.name)
        self.assertEqual(2, len(inventory.items))

    def test_add_item_withMatchingItemInInventory_IncreasesItemCount(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), slot=0)
        inventory.add_item(Item("arrow"))
        self.assertEqual(1, len(inventory.items))
        self.assertEqual(2, inventory.slot(0).count)

    def test_add_item_with2ItemsMatchingItemInInventory_IncreasesItemCountBy2(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), slot=0)
        inventory.add_item(Item("arrow", count=2))
        self.assertEqual(1, len(inventory.items))
        self.assertEqual(3, inventory.slot(0).count)

    def test_len_of_inventory_returnsNumberOfSlots(self):
        inventory = Inventory()
        size = len(inventory)
        self.assertEqual(len(inventory._slots), size)

    def test_add_item_withFullInventory_raisesInventoryFull(self):
        inventory = Inventory()
        # fill up the inventory
        for i, item in enumerate([Item("sword")] * len(inventory)):
            inventory.add_item(item, slot=i)
        # Add one more item
        with self.assertRaises(InventoryFull):
            inventory.add_item(Item("arrow"))

    def test_add_item_withIndex_replacesItemAtIndex(self):
        inventory = Inventory()
        inventory.add_item(Item("sword"), slot=0)
        drop = inventory.add_item(Item("arrow"), slot=0)
        self.assertEqual("sword", drop.name)

    def test_add_item_withEmptyInventory_hasItemCountOfOne(self):
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
        inventory.add_item(Item("sword"), slot=inventory.ON_HAND)
        inventory.remove_item(inventory.AMMO)
        self.assertEqual(1, len(inventory.items))
        self.assertEqual(None, inventory.slot(inventory.AMMO))

    def test_remove_withItemInSlot_dropsOneItem(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), slot=inventory.AMMO)
        drop = inventory.remove_item(inventory.AMMO)
        self.assertEqual(1, drop.count)
        self.assertEqual("arrow", drop.name)

    def test_remove_withMultipleItemsInSlot_removesOneItem(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), slot=inventory.AMMO)
        inventory.add_item(Item("arrow"), slot=inventory.AMMO)
        inventory.remove_item(inventory.AMMO)
        self.assertEqual(1, len(inventory.items))
        self.assertEqual(1, inventory.slot(inventory.AMMO).count)

    def test_add_item_withNonWeapon_alwaysIgnoresSpecialSlots(self):
        inventory = Inventory()
        with suppress(InventoryFull):
            for i in range(20):
                inventory.add_item(Food(f"sandwich{i}", 10))
        # cannot add any more sandwiches. Special slots should be still empty
        for slot_id in inventory.special_slots:
            self.assertIs(None, inventory.slot(slot_id))

    def test_swap_slots(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), slot=inventory.AMMO)
        inventory.add_item(Item("iron shot"), slot=5)

        inventory.swap(inventory.AMMO, 5)

        self.assertEqual("arrow", inventory.slot(5).name)
        self.assertEqual("iron shot", inventory.slot(inventory.AMMO).name)

    def test_iterate_withEmptyInventory_iterates10Nones(self):
        inventory = Inventory()
        result = list(inventory)
        self.assertEqual([None] * 10, result)


class TestInventoryEvents(unittest.TestCase):

    def test_add_observer_withItemInInventory_notifiesListenerOfItem(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), slot=inventory.AMMO)
        listener = ItemListener()
        inventory.add_observer(listener, inventory.AMMO)
        result = listener.last_received[inventory.AMMO]
        self.assertEqual("arrow", result.name)

    def test_add_observer_withItemSelect_notifiesListener(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), slot=inventory.AMMO)
        listener = ItemListener()
        inventory.add_observer(listener, inventory.AMMO)
        inventory.select(inventory.AMMO)
        result = listener.last_received[inventory.AMMO]
        self.assertEqual("arrow", result.name)
        self.assertEqual(True, result.selected)

    def test_add_observer_withItemDeselect_notifiesListener(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), slot=inventory.AMMO)
        listener = ItemListener()
        inventory.add_observer(listener, inventory.AMMO)
        inventory.select(inventory.AMMO)
        inventory.deselect(inventory.AMMO)
        result = listener.last_received[inventory.AMMO]
        self.assertEqual("arrow", result.name)
        self.assertEqual(False, result.selected)

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

    def test_swap_withListeners_notifiesBothListeners(self):
        inventory = Inventory()
        inventory.add_item(Item("arrow"), slot=Inventory.AMMO)
        inventory.add_item(Item("iron shot"), slot=5)
        listener_a = ItemListener()
        listener_b = ItemListener()
        inventory.add_observer(listener_a, inventory.AMMO)
        inventory.add_observer(listener_b, 5)
        inventory.swap(inventory.AMMO, 5)
        result_a = listener_a.last_received[inventory.AMMO]
        result_b = listener_b.last_received[5]
        self.assertEqual("iron shot", result_a.name)
        self.assertEqual("arrow", result_b.name)


if __name__ == '__main__':
    unittest.main()

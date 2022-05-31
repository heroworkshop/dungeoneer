from contextlib import suppress
from copy import copy

from dungeoneer.interfaces import Observable, Item


class InventoryFull(RuntimeError):
    """Raised when an item is added to an already full inventory"""


class Inventory(Observable):
    ON_HAND = 0
    OFF_HAND = 1
    AMMO = 2
    LAUNCHER = 3
    ARMOUR = 4
    special_slots = list(range(5))

    def __init__(self):
        super().__init__()
        self._slots = [None] * 10
        self.current_selection = None

    def __len__(self):
        return len(self._slots)

    def __iter__(self):
        return iter(self._slots)

    def attribute(self, attribute_id):
        return self.slot(attribute_id)

    def slot(self, i: int) -> Item:
        return self._slots[i]

    @property
    def items(self):
        return [i for i in self._slots if i]

    @property
    def ammo(self):
        return self.slot(self.AMMO)

    @property
    def selected_item(self) -> Item:
        return self.slot(self.current_selection)

    def find_available_slot(self, item=None):
        if item:
            with suppress(ValueError):
                return self.find_slot_containing_item(item)
        if item.preferred_slot is not None and self.slot(item.preferred_slot) is None:
            return item.preferred_slot
        return self.find_first_free_slot()

    def find_first_free_slot(self):
        generic_slots_start = len(self.special_slots)
        try:
            return generic_slots_start + self._slots[generic_slots_start:].index(None)
        except ValueError:
            raise InventoryFull

    def find_slot_containing_item(self, item):
        return self._slots.index(item)

    def add_item(self, item: Item, slot=None):
        assert item.count
        assert item.count < 99
        try:
            slot_index = slot if slot is not None else self.find_available_slot(item=item)
        except InventoryFull:
            raise InventoryFull(f"Could not add item '{item.name}'. There are no appropriate slots")
        if self.slot(slot_index) == item:
            self._slots[slot_index].count += item.count
            drop = None
        else:
            drop, self._slots[slot_index] = self._slots[slot_index], item
        self.notify_observers(slot_index)
        return drop

    def remove_item(self, slot_index):
        item = self._slots[slot_index]
        if item:
            drop = copy(item)
            drop.count = 1
            item.count -= 1
            if item.count == 0:
                self._slots[slot_index] = None
            self.notify_observers(slot_index)
            return drop
        return None

    def swap(self, slot_a, slot_b):
        self._slots[slot_a], self._slots[slot_b] = self._slots[slot_b], self._slots[slot_a]
        self.notify_observers(slot_a)
        self.notify_observers(slot_b)

    def select(self, slot_index):
        item = self.slot(slot_index)
        if item:
            item.selected = True
            self.notify_observers(slot_index)
            self.current_selection = slot_index

    def deselect(self, slot_index):
        item = self.slot(slot_index)
        if item:
            item.selected = False
            self.notify_observers(slot_index)

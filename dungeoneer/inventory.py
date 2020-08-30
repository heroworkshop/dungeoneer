from contextlib import suppress

from dungeoneer.interfaces import Observable, Observer, Item


class InventoryFull(RuntimeError):
    """Raised when an item is added to an already full inventory"""


class Inventory(Observable):
    WEAPON = 0
    AMMO = 1
    LAUNCHER = 2
    ARMOUR = 3

    def __init__(self):
        super().__init__()
        self._slots = [None] * 10

    def __len__(self):
        return len(self._slots)

    def __iter__(self):
        return iter(self._slots)

    def slot(self, i):
        return self._slots[i]

    @property
    def items(self):
        return [i for i in self._slots if i]

    @property
    def ammo(self):
        return self.slot(self.AMMO)

    def find_available_slot(self, item=None):
        if item:
            with suppress(ValueError):
                return self.find_slot_containing_item(item)
        if item.preferred_slot is not None and self.slot(item.preferred_slot) is None:
            return item.preferred_slot
        return self.find_first_free_slot()

    def find_first_free_slot(self):
        try:
            return self._slots.index(None)
        except ValueError:
            raise InventoryFull

    def find_slot_containing_item(self, item):
        return self._slots.index(item)

    def add_item(self, item: Item, slot=None):
        try:
            slot_index = slot if slot is not None else self.find_available_slot(item=item)
        except ValueError:
            raise InventoryFull(
                "Could not add item {}. Inventory already contains {} items".format(item.name,
                                                                                    len(self.slots)))
        if self.slot(slot_index) == item:
            self._slots[slot_index].count += 1
            drop = None
        else:
            drop, self._slots[slot_index] = self._slots[slot_index], item
        self.notify_observers(slot_index)
        return drop

    def remove_item(self, slot_index):
        drop = self._slots[slot_index]
        if drop:
            self._slots[slot_index].count -= 1
            if self._slots[slot_index].count == 0:
                self._slots[slot_index] = None
        self.notify_observers(slot_index)
        return drop

    def notify_observers(self, slot_index):
        for observer in self.observers[slot_index]:
            observer.on_update(slot_index, self.slot(slot_index))

    def add_observer(self, observer: Observer, attribute):
        self.observers[attribute].append(observer)
        observer.on_update(attribute, self._slots[attribute])

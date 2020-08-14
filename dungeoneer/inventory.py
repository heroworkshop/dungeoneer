from contextlib import suppress


class InventoryFull(RuntimeError):
    """Raised when an item is added to an already full inventory"""


class Inventory:
    WEAPON = 0
    AMMO = 1
    LAUNCHER = 2
    ARMOUR = 3

    def __init__(self):
        self.slots = [None] * 10

    def __len__(self):
        return len(self.slots)

    @property
    def items(self):
        return [i for i in self.slots if i]

    @property
    def ammo(self):
        return self.slots[self.AMMO]

    def find_available_slot(self, item=None):
        if item:
            with suppress(ValueError):
                return self.find_slot_containing_item(item)
        return self.find_first_free_slot()

    def find_first_free_slot(self):
        return self.slots.index(None)

    def find_slot_containing_item(self, item):
        return self.slots.index(item)

    def add_item(self, item, slot=None):
        try:
            index = slot if slot is not None else self.find_available_slot(item=item)
        except ValueError:
            raise InventoryFull(
                "Could not add item {}. Inventory already contains {} items".format(item.name(),
                                                                                    len(self.slots)))
        if self.slots[index] == item:
            self.slots[index].count += 1
            return None
        drop, self.slots[index] = self.slots[index], item
        return drop

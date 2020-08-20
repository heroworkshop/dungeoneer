from dungeoneer.interfaces import Item
from dungeoneer.inventory import Inventory


class Ammo(Item):
    def __init__(self, name, damage, damage_profile, speed):
        super().__init__(name)
        self.damage = damage
        self.damage_profile = damage_profile
        self.speed = speed
        self.preferred_slot = Inventory.AMMO


class Food(Item):
    def __init__(self, name, bonus):
        super().__init__(name)
        self.bonus = bonus


def make_item_dict(using_class, *args):
    result = dict()
    for item in args:
        name = item[0]
        result[name] = using_class(*item)
    return result


ammo = make_item_dict(
    Ammo,
    ("arrow", 10, [100], 12),
    ("stone shot", 4, [100], 6),
    ("iron shot", 6, [100], 6),
    ("firebolt", 10, [60, 40], 12)
)

weapons = [
    Item("sword"),
    Item("axe")
]

armour = [
    Item("chain mail"),
    Item("leather armour")
]

launchers = [
    Item("shortbow"),
    Item("sling")
]

food = make_item_dict(
    Food,
    ("melon", 10)
)

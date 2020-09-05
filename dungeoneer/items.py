from dungeoneer.interfaces import Item
from dungeoneer.inventory import Inventory


class Ammo(Item):
    def __init__(self, name, damage, damage_profile, speed, survivability):
        super().__init__(name)
        self.damage = damage
        self.damage_profile = damage_profile
        self.speed = speed
        self.preferred_slot = Inventory.AMMO
        self.survivability = survivability


class Melee(Item):
    def __init__(self, name, creates_effect):
        super().__init__(name)
        self.creates_effect = creates_effect
        self.preferred_slot = Inventory.ON_HAND


class Food(Item):
    def __init__(self, name, bonus):
        super().__init__(name)
        self.bonus = bonus


class Potion(Item):
    def __init__(self, name):
        super().__init__(name)


def make_item_dict(using_class, *args):
    result = dict()
    for item in args:
        name = item[0]
        result[name] = using_class(*item)
    return result


ammo = make_item_dict(
    Ammo,
    ("arrow", 10, [100], 12, 70),
    # ("stone shot", 4, [100], 6, 90),
    # ("iron shot", 6, [100], 6, 98),
)

generated_ammo = make_item_dict(
    Ammo,
    ("firebolt", 10, [60, 40], 12, 0),
    ("swipe", 12, [60, 0, 40], 0, 0)
)

weapons = make_item_dict(
    Melee,
    ("sword", "swipe"),
    ("battle axe", "swipe")
)

armour = make_item_dict(
    Item,
    ("chain mail",),
    ("leather armour",)
)

launchers = make_item_dict(
    Item,
    ("shortbow",),
    ("sling",)
)

food = make_item_dict(
    Food,
    ("melon", 10),
    ("strawberry", 5),
    ("pear", 7),
    ("lemon", 1),
    ("pineapple", 10),
    ("carrot", 4),
    ("bread", 15),
    ("cheese", 15),
)

potions = make_item_dict(
    Potion,
    ("red potion", ),
    ("orange potion",),
    ("yellow potion",),
    ("blue potion",),
    ("magenta potion",),
    ("green potion",),
    ("grey potion",),

)

all_items = {**ammo, **weapons, **armour, **launchers, **food, **potions}

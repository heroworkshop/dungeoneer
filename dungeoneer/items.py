from dungeoneer.game_assets import load_sound_file, sfx_file
from dungeoneer.interfaces import Item
from dungeoneer.inventory import Inventory
from dungeoneer.scenery import VisualEffect
from dungeoneer.sound_effects import SfxEvents


class Ammo(Item):
    """
    Args:
        name (str): name of item, for example "arrow"
        damage(int): how much damage the item does on a hit
        damage_profile (List[int]): some hits do damage on each frame of the animation until
                                    all the damage is delivered. Each entry represents a percentage
                                    of the damage. A damage profile pf [100] means it all gets delivered
                                    in a single burst
        speed (int): how fast the ammo item travels (pixels/frame)
        survivability (int): percent change that the ammo item will drop after hitting
        sfx_events (SfxEvents): sound effects to play on different events
    """
    def __init__(self, name, damage, damage_profile, speed, survivability, sfx_events):
        super().__init__(name, sfx_events=sfx_events)
        self.damage = damage
        self.damage_profile = damage_profile
        self.speed = speed
        self.preferred_slot = Inventory.AMMO
        self.survivability = survivability


class Melee(Item):
    def __init__(self, name, creates_effect, rate_of_fire, damage):
        super().__init__(name)
        self.creates_effect = creates_effect
        self.preferred_slot = Inventory.ON_HAND
        self.rate_of_fire = rate_of_fire
        self.damage = damage


class Food(Item):
    def __init__(self, name, bonus):
        super().__init__(name)
        self.bonus = bonus


class Launcher(Item):
    def __init__(self, name, rate_of_fire):
        super().__init__(name)
        self.rate_of_fire = rate_of_fire


class Potion(Item):
    def __init__(self, name):
        super().__init__(name)


def make_item_dict(using_class, *args):
    return {item[0]: using_class(*item) for item in args}


specials = make_item_dict(Melee, ("unarmed strike", "swipe", 1.5, 2))
specials.update(make_item_dict(Launcher, ("thrown", 1)))

ammo = make_item_dict(
    Ammo,
    ("arrow", 10, [100], 8, 70, SfxEvents(activate="arrow.wav")),
    # ("stone shot", 4, [100], 6, 90),
    # ("iron shot", 6, [100], 6, 98),
)

generated_ammo = make_item_dict(
    Ammo,
    ("firebolt", 10, [60, 40], 12, 0, SfxEvents(activate="firebolt.ogg")),
    ("swipe", 12, [60, 0, 40], 0, 0, SfxEvents(activate="swipe.ogg"))
)

weapons = make_item_dict(
    Melee,
    ("dagger", "swipe", 1.2, 4),
    ("sword", "swipe", 1.0, 10),
    ("battle axe", "swipe", 0.8, 12)
)

armour = make_item_dict(
    Item,
    ("chain mail",),
    ("leather armour",)
)

launchers = make_item_dict(
    Launcher,
    ("shortbow", 1),
    ("sling", 1)
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
    ("red potion",),
    ("orange potion",),
    ("yellow potion",),
    ("blue potion",),
    ("magenta potion",),
    ("green potion",),
    ("grey potion",),

)

# all_items does not include generated items. The intention is that all_items encompasses
# all the items that can be dropped.
all_items = {**ammo, **weapons, **armour, **launchers, **food, **potions}


class GoldItem(VisualEffect):
    """Gold is not an item because it does not fill up slots in the inventory.
    Instead, it has a side-effect when picked up (increases gold score)"""
    def __init__(self, x, y, filmstrip, value):
        super().__init__(x, y, filmstrip, repeats=VisualEffect.FOREVER)
        self.value = value
        self.sound_effect = load_sound_file(sfx_file("handleCoins.ogg"))

    def on_pick_up(self, player):
        player.gold += self.value
        self.sound_effect.play()

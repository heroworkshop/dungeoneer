import copy
from random import randint

from dungeoneer.game_assets import make_sprite_sheet
from dungeoneer.interfaces import Item
from dungeoneer.inventory import InventoryFull
from dungeoneer.scenery import VisualEffect, parabolic_motion


def make_item_sprite(item_spec: Item, x, y, motion=None):
    sprite_sheet = make_sprite_sheet(item_spec.name)
    return ItemSprite(item_spec, x, y, sprite_sheet.filmstrip(), motion=motion)


class ItemSprite(VisualEffect):
    def __init__(self, item_spec: Item, x, y, filmstrip, motion=None):
        super().__init__(x, y, filmstrip, repeats=VisualEffect.FOREVER, motion=motion)
        self.item_spec = copy.copy(item_spec)
        self.item_spec.sprite = self

    def on_pick_up(self, actor):
        try:
            actor.inventory.add_item(self.item_spec)
        except InventoryFull:
            arc = parabolic_motion(15, 15, -3, 0.5)
            actor.drop(self.item_spec, motion=iter(arc))


def drop_item(item_spec: Item, world, x: int, y: int, count=1):
    drop_x, drop_y = x + randint(-16, 16), y + randint(-16, 16)
    new_item = copy.copy(item_spec)
    new_item.count = count
    item = make_item_sprite(new_item, drop_x, drop_y)
    world.items.add(item)
    world.all.add(item)
    return item

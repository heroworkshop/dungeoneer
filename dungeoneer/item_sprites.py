import copy

from dungeoneer.game_assets import make_sprite_sheet
from dungeoneer.interfaces import Item
from dungeoneer.inventory import InventoryFull
from dungeoneer.scenery import VisualEffect, parabolic_motion


def make_item_sprite(item_spec: Item, x, y, motion=None):
    sprite_sheet = make_sprite_sheet(item_spec.name)
    return ItemSprite(x, y, sprite_sheet.filmstrip(), item_spec, motion=motion)


class ItemSprite(VisualEffect):
    def __init__(self, x, y, filmstrip, item_spec: Item, motion=None):
        super().__init__(x, y, filmstrip, repeats=VisualEffect.FOREVER, motion=motion)
        self.item_spec = copy.copy(item_spec)
        self.item_spec.sprite = self

    def on_pick_up(self, actor):
        try:
            actor.inventory.add_item(self.item_spec)
        except InventoryFull:
            arc = parabolic_motion(15, 15, -3, 0.5)
            actor.drop(self.item_spec, motion=iter(arc))

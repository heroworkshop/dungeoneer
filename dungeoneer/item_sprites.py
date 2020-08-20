from dungeoneer.game_assets import make_sprite_sheet
from dungeoneer.interfaces import Item
from dungeoneer.scenary import VisualEffect


def make_item_sprite(item_spec: Item, x, y):
    sprite_sheet = make_sprite_sheet(item_spec.name)
    return ItemSprite(item_spec, x, y, sprite_sheet.filmstrip())


class ItemSprite(VisualEffect):
    def __init__(self, item_spec: Item, x, y, filmstrip):
        super().__init__(x, y, filmstrip, repeats=VisualEffect.FOREVER)
        self.item_spec = item_spec
        self.item_spec.sprite = self

    def on_pick_up(self, actor):
        actor.inventory.add_item(self.item_spec)

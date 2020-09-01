import pygame

from dungeoneer.fonts import make_font
from dungeoneer.game_assets import make_sprite_sheet
from dungeoneer.interfaces import Direction, Observer
from dungeoneer.inventory import Inventory

EMPTY_BOX = make_sprite_sheet("inventory slot box").filmstrip()[0]


class SlotView(pygame.sprite.Sprite, Observer):

    def __init__(self, x, y, item=None):
        super().__init__()
        self.font = make_font("Times New Roman", 16)
        self.image = self.compose_item_image(item)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


    def on_update(self, attribute, value):
        del attribute  # not used
        self.image = self.compose_item_image(value)

    def compose_item_image(self, item):
        if item is None:
            return EMPTY_BOX
        result = EMPTY_BOX.copy()
        item_image = make_sprite_sheet(item.name).filmstrip()[0]
        x = (result.get_width() - item_image.get_width()) // 2
        y = (result.get_height() - item_image.get_height()) // 2
        result.blit(item_image, (x, y))

        caption = self.font.render(f"x{item.count}", True, (180, 180, 180))
        result.blit(caption, (30, 30))

        return result


class InventoryView:
    SPACING = 50  # px distance between top-left corners of slot views

    def __init__(self, inventory: Inventory, x=0, y=0, sprite_groups=None, orientation=Direction.TOP_DOWN):
        dx, dy = orientation.value
        dx *= self.SPACING
        dy *= self.SPACING
        self.slot_views = [SlotView(x + i * dx, y + i * dy, item) for i, item in enumerate(inventory)]
        # add each inventory slot to the sprite groups
        for slot in self.slot_views:
            slot.add(sprite_groups or [])
        # register for inventory updates
        for index, slot in enumerate(self.slot_views):
            inventory.add_observer(slot, index)

    def __len__(self):
        return len(self.slot_views)

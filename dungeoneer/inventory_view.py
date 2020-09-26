import pygame

from dungeoneer.fonts import make_font
from dungeoneer.game_assets import make_sprite_sheet
from dungeoneer.interfaces import Direction, Observer
from dungeoneer.inventory import Inventory

EMPTY_BOX = make_sprite_sheet("inventory slot box").filmstrip()[0]


class SlotView(pygame.sprite.Sprite, Observer):

    def __init__(self, x, y, hot_key="", item=None):
        super().__init__()
        self.hot_key = hot_key
        self.font = make_font("Times New Roman", 16)
        self.hot_key_font = make_font("Times New Roman", 24)
        self.image = self.compose_item_image(item)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def on_update(self, attribute, value):
        # value is an Item
        del attribute  # not used
        self.image = self.compose_item_image(value)
        if value and value.selected:
            self.draw_highlight()

    def compose_item_image(self, item):
        if item is None:
            return EMPTY_BOX
        result = EMPTY_BOX.copy()
        item_image = make_sprite_sheet(item.name).filmstrip()[0]
        x = (result.get_width() - item_image.get_width() - 25) // 2
        y = (result.get_height() - item_image.get_height()) // 2
        result.blit(item_image, (x, y))

        caption = self.font.render(f"x{item.count}", True, (180, 180, 180))
        result.blit(caption, (30, 30))

        hot_key_label = self.hot_key_font.render(self.hot_key, True, (220, 220, 220))
        result.blit(hot_key_label, (55, 20))

        return result

    def draw_highlight(self):
        colour = (255, 255, 0)
        pygame.draw.rect(self.image, colour, self.image.get_rect(), 4)


class InventoryView:
    """The InventoryView is a group of SlotViews. This class determines how the slot views
    are arranged on the screen. The rendering is left up to the slot views.

    This class is part of MVC architecture
      For the model see Inventory.
      For the controller see InventoryController
    """
    SPACING = 50  # px distance between top-left corners of slot views

    def __init__(self, inventory: Inventory, x=0, y=0, sprite_groups=None, orientation=Direction.TOP_DOWN):
        dx, dy = orientation.value
        dx *= self.SPACING
        dy *= self.SPACING
        self.slot_views = [SlotView(x + i * dx, y + i * dy, f"{i}", item)
                           for i, item in enumerate(inventory)]
        # add each inventory slot to the sprite groups
        for slot in self.slot_views:
            slot.add(sprite_groups or [])
        # register for inventory updates
        for index, slot in enumerate(self.slot_views):
            inventory.add_observer(slot, index)

    def __len__(self):
        return len(self.slot_views)

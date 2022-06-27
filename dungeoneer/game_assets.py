import os
from functools import lru_cache

import pygame

from dungeoneer.spritesheet import SpriteSheet


def _asset_file(subfolder, filename):
    return os.path.join(os.path.dirname(__file__), subfolder, filename)


def image_file(filename):
    return _asset_file("images", filename)


def music_file(filename):
    return _asset_file("music", filename)


def sfx_file(filename):
    return _asset_file("sfx", filename)


@lru_cache(maxsize=1000)
def load_image(filename):
    return pygame.image.load(image_file(filename))


def _make_sprite_sheet(filename, sheet_dimensions, sub_area=None):
    image = load_image(filename)
    columns, rows = sheet_dimensions
    return SpriteSheet(image, columns=columns, rows=rows, sub_area=sub_area)


@lru_cache(maxsize=1000)
def load_sound_file(filename):
    return pygame.mixer.Sound(filename)


def play_sound(name):
    load_sound_file(sfx_file(name)).play()


SPRITE_SHEET_TABLE = {
    "inventory slot box": ("slot_box.png", (1, 1)),
    "zombie": ("TombZombies.png", (12, 8), (3, 0, 3, 4)),
    "zombie generator": ("graveyard.png", (12, 8), (0, 1, 1, 1)),
    "skeleton": ("TombZombies.png", (12, 8), (9, 0, 3, 4)),
    "mummy": ("TombZombies.png", (12, 8), (6, 0, 3, 4)),
    "player01": ("player01_sheet.png", (3, 4)),
    "player02": ("player02_sheet.png", (3, 4)),
    "gold pieces": ("items_metal.png", (13, 10), (0, 3, 1, 1)),
    "gold pile": ("items_metal.png", (13, 10), (0, 4, 1, 1)),
    "arrow": ("arrow24.png", (1, 1)),
    "swipe": ("arc_strike.png", (13, 1)),
    "melon": ("equipment.png", (14, 32), (7, 0, 1, 1)),
    "strawberry": ("equipment.png", (14, 32), (8, 0, 1, 1)),
    "pear": ("equipment.png", (14, 32), (9, 0, 1, 1)),
    "lemon": ("equipment.png", (14, 32), (10, 0, 1, 1)),
    "pineapple": ("equipment.png", (14, 32), (11, 0, 1, 1)),
    "banana": ("equipment.png", (14, 32), (12, 0, 1, 1)),
    "carrot": ("equipment.png", (14, 32), (1, 1, 1, 1)),
    "bread": ("equipment.png", (14, 32), (7, 1, 1, 1)),
    "cheese": ("equipment.png", (14, 32), (9, 1, 1, 1)),
    "red potion": ("equipment.png", (14, 32), (0, 2, 1, 1)),
    "orange potion": ("equipment.png", (14, 32), (1, 2, 1, 1)),
    "yellow potion": ("equipment.png", (14, 32), (2, 2, 1, 1)),
    "blue potion": ("equipment.png", (14, 32), (3, 2, 1, 1)),
    "magenta potion": ("equipment.png", (14, 32), (4, 2, 1, 1)),
    "green potion": ("equipment.png", (14, 32), (5, 2, 1, 1)),
    "grey potion": ("equipment.png", (14, 32), (6, 2, 1, 1)),
    "unarmed strike": ("equipment.png", (14, 32), (7, 14, 1, 1)),
    "thrown": ("equipment.png", (14, 32), (7, 14, 1, 1)),
    "dagger": ("equipment.png", (14, 32), (0, 6, 1, 1)),
    "sword": ("equipment.png", (14, 32), (0, 5, 1, 1)),
    "battle axe": ("equipment.png", (14, 32), (2, 10, 1, 1)),
    "shortbow": ("equipment.png", (14, 32), (0, 11, 1, 1)),
    "sling": ("weapons-and-equipment.png", (12, 8), (3, 2, 1, 1)),
    "chain mail": ("equipment.png", (14, 32), (0, 13, 1, 1)),
    "leather armour": ("equipment.png", (14, 32), (2, 13, 1, 1)),
}


def make_sprite_sheet(name: str) -> SpriteSheet:
    return _make_sprite_sheet(*SPRITE_SHEET_TABLE[name])

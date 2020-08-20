import os
from functools import lru_cache

import pygame

from dungeoneer.spritesheet import SpriteSheet


def asset_file(subfolder, filename):
    return os.path.join(os.path.dirname(__file__), subfolder, filename)


def image_file(filename):
    return asset_file("images", filename)


def music_file(filename):
    return asset_file("music", filename)


def sfx_file(filename):
    return asset_file("sfx", filename)


@lru_cache(maxsize=1000)
def load_image(filename):
    return pygame.image.load(image_file(filename))


def _make_sprite_sheet(filename, sheet_dimensions, sub_area=None):
    image = load_image(filename)
    columns, rows = sheet_dimensions
    return SpriteSheet(image, columns=columns, rows=rows, sub_area=sub_area)


@lru_cache(maxsize=1000)
def load_sound(filename):
    return pygame.mixer.Sound(filename)


SPRITE_SHEET_TABLE = {
    "zombie": ("TombZombies.png", (12, 8), (3, 0, 3, 4)),
    "zombie generator": ("graveyard.png", (12, 8), (0, 1, 1, 1)),
    "mummy": ("TombZombies.png", (12, 8), (6, 0, 3, 4)),
    "player01": ("player01_sheet.png", (3, 4)),
    "player02": ("player02_sheet.png", (3, 4)),
    "gold pieces": ("items_metal.png", (13, 10), (0, 3, 1, 1)),
    "gold pile": ("items_metal.png", (13, 10), (0, 4, 1, 1)),
    "arrow": ("arrow24.png", (1, 1)),
    "swipe": ("arc_strike.png", (13, 1)),
    "melon": ("equipment.png", (14, 32), (7, 0, 1, 1))
}


def make_sprite_sheet(name):
    return _make_sprite_sheet(*SPRITE_SHEET_TABLE[name])

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
    "devious": ("devious.png", (1, 1)),
    "rage": ("rage.png", (1, 1)),
    "psychopath": ("psychopath.png", (1, 1)),
    "plagiarism": ("plagiarism.png", (1, 1)),
    "peachy": ("peachy.png", (1, 1))
}


def make_sprite_sheet(name: str) -> SpriteSheet:
    return _make_sprite_sheet(*SPRITE_SHEET_TABLE[name])

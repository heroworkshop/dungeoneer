import math
from collections import OrderedDict

import pygame
from pygame.sprite import Sprite
from dungeoneer.interfaces import SpriteGroups


def move_to_nearest_empty_space(tile: Sprite, world: SpriteGroups, max_distance: int):

    initial_x, initial_y = tile.rect.center
    locations = OrderedDict()
    checked = set()
    locations[0] = (initial_x, initial_y)
    midx = math.ceil(tile.rect.width / 2)
    midy = math.ceil(tile.rect.height / 2)
    max_distance_squared = max_distance ** 2

    def queue_up(cx, cy):
        if (cx, cy) not in checked:
            d_squared = (initial_x - cx) ** 2 + (initial_y - cy) ** 2
            locations[d_squared] = (cx, cy)

    while locations:
        distance_squared, (x, y) = locations.popitem(0)
        checked.add((x, y))
        # distance_squared = (initial_x - x) ** 2 + (initial_y - y) ** 2
        if distance_squared > max_distance_squared:
            continue
        tile.rect.center = (x, y)
        collided = pygame.sprite.spritecollideany(tile, world.solid)
        if not collided:
            return tile
        rect = collided.rect
        queue_up(rect.left - midx, rect.centery)
        queue_up(rect.right + midx, rect.centery)
        queue_up(rect.centerx, rect.top - midy)
        queue_up(rect.centerx, rect.centery + midy)
        locations = OrderedDict(sorted(locations.items()))

    return None


def move_to_nearest_empty_space_tiled(tile: Sprite, world: SpriteGroups, max_distance: int):

    initial_x, initial_y = tile.rect.center
    locations = OrderedDict()
    checked = set()
    locations = [(initial_x, initial_y)]

    def queue_up(cx, cy):
        if (cx, cy) not in checked:
            locations.append((cx, cy))

    width = tile.rect.width
    height = tile.rect.height
    search_breadth = 1

    while search_breadth*width < max_distance:
        while locations:
            x, y = locations.pop(0)
            checked.add((x, y))
            tile.rect.center = (x, y)
            collided = pygame.sprite.spritecollide(tile, world.solid, dokill=False,
                                                   collided=pygame.sprite.collide_rect_ratio(0.8))
            if not collided:
                return tile

        left = initial_x - search_breadth * width
        right = initial_x + search_breadth * width
        top = initial_y - search_breadth * height
        bottom = initial_y + search_breadth * height
        for qx in range(left, right, width):
            queue_up(qx, top)
            queue_up(qx, bottom)
        for qy in range(top, bottom, height):
            queue_up(left, qy)
            queue_up(right, qy)
        search_breadth += 2
    return None
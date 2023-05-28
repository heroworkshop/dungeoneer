"""Field Of Vision (FOV) algorithms"""

from collections import deque

import pygame

from dungeoneer.realms import Realm


def raycast_floodfill(realm: Realm, position: pygame.Vector2, direction):
    dx, dy = direction
    done = set()
    region = realm.region_from_pixel_position(position)
    x, y = region.coordinate_from_absolute_position(*position)
    queue = deque()

    def enqueue(p):
        if p not in done:
            queue.append(p)
            done.add(p)

    enqueue((x + dx, y))
    enqueue((x, y + dy))

    debug_map = {}
    found = []
    virtual_blocks = set()
    while queue:
        x, y = queue.popleft()
        if region.out_of_bounds((x, y)):
            debug_map[(x,y)] = "*"
            continue
        wall = region.solid_object_at_position((x, y))
        if wall:
            debug_map[(x, y)] = "#"
            found.append(wall)
            continue
        debug_map[(x, y)] = "."

        if region.solid_object_at_position((x + dx, y - dy)) or (x + dx, y - dy) in virtual_blocks:
            virtual_blocks.add((x + dx, y))
            done.add((x + dx, y))
        else:
            enqueue((x + dx, y))
        enqueue((x, y + dy))

    show_debug_map(debug_map, region)
    return found


def show_debug_map(debug_map, region):
    for y in range(region.grid_height):
        for x in range(region.grid_width):
            print(debug_map.get((x, y), "-"), end="")
        print()


def unit_vectors(cells_across: int, cells_up: int):
    across = [y / cells_across for y in range(cells_up + 1)]
    up = [x / cells_up for x in range(cells_across + 1)]
    return across, up


def raycast(realm: Realm, position: pygame.Vector2, direction):
    dir_x, dir_y = direction
    region = realm.region_from_pixel_position(position)
    x0, y0 = region.coordinate_from_absolute_position(*position)
    width = region.grid_width // 2
    height = region.grid_height // 2
    across, up = unit_vectors(width, height)

    debug_map = {}
    found = {}

    for dy in across:
        x, y = x0, y0
        while abs(x - x0) <= width:
            x += dir_x
            y += dy * dir_y
            ipos = int(x), int(y)
            if region.out_of_bounds(ipos):
                debug_map[ipos] = "*"
                break
            wall = region.solid_object_at_position(ipos)
            if wall:
                debug_map[ipos] = "#"
                found[ipos] = wall
                break
            debug_map[(x, y)] = "."

    for dx in across:
        x, y = x0, y0
        while abs(y - y0) <= height:
            x += dx * dir_x
            y += dir_y
            ipos = int(x), int(y)
            if region.out_of_bounds(ipos):
                debug_map[ipos] = "*"
                break
            wall = region.solid_object_at_position(ipos)
            if wall:
                debug_map[ipos] = "#"
                found[ipos] = wall
                break
            debug_map[ipos] = "."

    show_debug_map(debug_map, region)
    return found
from enum import Enum
import random

from dungeoneer.regions import TileType, Position, SubRegion


class DesignType(Enum):
    LARGE_ROOM = 0


def generate_map(region, design: DesignType):
    if design == DesignType.LARGE_ROOM:
        generate_large_room(region)
    return region


def generate_large_room(region):
    region.fill_all(TileType.STONE_WALL)
    region.clear_area((1, 1), (region.grid_width - 2, region.grid_height - 2))
    return region


def make_nodes(subregion: SubRegion, *, node_count):
    nodes = []
    subregions = [subregion]

    while len(subregions) < node_count:
        split = random.uniform(0.3, 0.7)
        subregion = subregions.pop(0)
        if subregion.size[0] < subregion.size[1]:  # narrow
            subregions.extend(subregion.split_vertically(split))
        else:  # square or wide
            subregions.extend(subregion.split_horizontally(split))

    for r in subregions:
        x, y = r.top_left
        w, h = r.size
        x += w // 2
        y += h // 2
        nodes.append((x, y))

    return nodes

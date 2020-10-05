from collections import defaultdict
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


def make_nodes(sub_region: SubRegion, *, node_count):
    sub_regions = [sub_region]

    while len(sub_regions) < node_count:
        split = random.uniform(0.3, 0.7)
        sr = sub_regions.pop(0)
        if sr.size.width < sr.size.height:  # narrow
            sub_regions.extend(sr.split_vertically(split))
        else:  # square or wide
            sub_regions.extend(sr.split_horizontally(split))

    nodes = [r.mid_point() for r in sub_regions]
    # dump_ascii_map(sub_region, sub_regions, nodes, f"subregions-{len(sub_regions)}.txt")

    return nodes


def dump_ascii_map(root_region: SubRegion, sub_regions: SubRegion,
                   nodes: Position, filename: str):
    with open(filename, "w") as f:
        for sr, n in zip(sub_regions, nodes):
            print(sr, n, file=f)

        ascii_map = defaultdict(str)
        for y in range(root_region.size.height):
            for x in range(root_region.size.width):
                ascii_map[(x, y)] = " "
        for r in sub_regions:
            r.ascii_render(ascii_map)

        for n in nodes:
            ascii_map[(n.x, n.y)] = "*"

        for y in range(root_region.size.height):
            for x in range(root_region.size.width):
                print(ascii_map[(x, y)], end="", file=f)
            print(file=f)




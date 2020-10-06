from collections import defaultdict
from contextlib import suppress
from enum import Enum
import random
from typing import Iterable, List

from dungeoneer.regions import TileType, Position, SubRegion, Region


class DesignType(Enum):
    LARGE_ROOM = 0
    CONNECTED_ROOMS = 1


def generate_map(region, design: DesignType):
    if design == DesignType.LARGE_ROOM:
        generate_large_room(region)
    if design == DesignType.CONNECTED_ROOMS:
        generate_connected_rooms(region)
    return region


def generate_large_room(region):
    region.fill_all(TileType.STONE_WALL)
    region.clear_area((1, 1), (region.grid_width - 2, region.grid_height - 2))
    return region


def generate_connected_rooms(region):
    sub_regions = make_sub_regions(region, node_count=16)
    nodes = sub_regions_to_nodes(sub_regions)
    paths = join_nodes(nodes)
    dump_ascii_map(region, sub_regions, nodes, paths, f"debug/subregions-{len(sub_regions)}.txt")
    region.fill_all(TileType.STONE_WALL)
    region.clear_nodes(nodes)
    region.clear_nodes(paths)
    return region


def make_nodes(root_region: Region, *, node_count) -> List[Position]:
    sub_regions = make_sub_regions(root_region, node_count=node_count)
    return sub_regions_to_nodes(sub_regions)


def sub_regions_to_nodes(sub_regions) -> List[Position]:
    return [r.mid_point() for r in sub_regions]


def make_sub_regions(root_region: Region, *, node_count) -> List[SubRegion]:
    sub_regions = [SubRegion(root_region)]

    while len(sub_regions) < node_count:
        split = random.uniform(0.3, 0.7)
        sr = sub_regions.pop(0)
        if sr.size.width < sr.size.height:  # narrow
            sub_regions.extend(sr.split_vertically(split))
        else:  # square or wide
            sub_regions.extend(sr.split_horizontally(split))

    return sub_regions


def join_nodes(nodes: Iterable[Position]) -> List[Position]:
    path = []
    i = iter(nodes)
    with suppress(StopIteration):
        src = next(i)
        while True:
            dest = next(i)
            path.extend(join_two_nodes(src, dest))
            src = dest
    return path


def join_two_nodes(src: Position, dest: Position):
    path = []
    x, y = src
    path.append((x, y))
    while True:
        x_count = dest.x - x
        y_count = dest.y - y

        if not x_count and not y_count:
            break

        dx = x_count // abs(x_count or 1)
        dy = y_count // abs(y_count or 1)

        steps = _random_path_segment(x_count, y_count)

        while steps[0]:
            x += dx
            steps[0] -= 1
            path.append((x, y))
        while steps[1]:
            y += dy
            steps[1] -= 1
            path.append((x, y))
    return path


def _random_path_segment(x_count, y_count):
    """Given a distance to travel (x_count, y_count), choose to either go a random distance
    in x direction or in y direction.

    Returns:
        List[int]: number of steps to travel. For example [0, 2] means travel in the y direction 2 steps
    """
    options = [(x_count, 0), (0, y_count)]
    option = random.choice([opt for opt in options if opt[0] or opt[1]])
    steps = [random.randint(0, abs(option[0])), random.randint(0, abs(option[1]))]
    return steps


def dump_ascii_map(root_region: Region, sub_regions: List[SubRegion],
                   nodes: List[Position], paths: List[Position], filename: str):
    with open(filename, "w") as f:
        for sr, n in zip(sub_regions, nodes):
            print(sr, n, file=f)

        ascii_map = defaultdict(str)
        for y in range(root_region.grid_height):
            for x in range(root_region.grid_width):
                ascii_map[(x, y)] = " "
        for r in sub_regions:
            r.ascii_render(ascii_map)

        for p in paths:
            ascii_map[p] = "*"

        for i, n in enumerate(nodes):
            ascii_map[(n.x, n.y)] = f"{hex(i)[-1]}"

        for y in range(root_region.grid_height):
            for x in range(root_region.grid_width):
                print(ascii_map[(x, y)], end="", file=f)
            print(file=f)

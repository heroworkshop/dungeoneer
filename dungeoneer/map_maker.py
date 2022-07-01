import heapq
import random
from collections import defaultdict
from contextlib import suppress
from typing import Iterable, List, Protocol, Type

from dungeoneer.dice_roll import pick_from_weighted_table
from dungeoneer.regions import TileType, Position, SubRegion, Region


class RegionGenerator(Protocol):
    def generate(self):
        ...


def generate_map(region, design_generator: Type[RegionGenerator]):
    return design_generator(region).generate()


def join_exits(nodes, exits, size):
    def find_best_node(exit_position):
        """Find node with shortest manhatten distance to the exit"""
        x, y = exit_position
        diffs = [(abs(n[0] - x) + abs(n[1] - y), n) for n in nodes]
        heapq.heapify(diffs)
        _, p = diffs[0]
        return p

    width, height = size
    paths = []
    directions = {
        "N": (exits.get("N"), 0),
        "S": (exits.get("S"), height - 1),
        "E": (width - 1, exits.get("E")),
        "W": (0, exits.get("W"))
    }
    for direction, exit_pos in directions.items():
        if direction in exits:
            exit_pos = Position(*exit_pos)
            node = find_best_node(exit_pos)
            paths.extend(join_two_nodes(node, exit_pos))
    return paths


def carve_out_dungeon(region, paths, rooms, wall_type=TileType.STONE_WALL):
    def random_floor():
        return random.choice((TileType.STONE_FLOOR, TileType.LARGE_FLAGSTONE, TileType.EARTH,
                              TileType.CHECKERED_TILES))

    floor_type = random_floor()  # floor types are themed (mostly)
    region.fill_all(wall_type)
    region.clear_nodes(paths)
    for room in rooms:
        region.clear_nodes(room, floor_type if random.randint(0, 100) < 95 else random_floor())


def random_floor_types(region, sub_regions: List[SubRegion]):
    for area in sub_regions:
        floor_type = random.choice((TileType.STONE_FLOOR, TileType.LARGE_FLAGSTONE, TileType.EARTH))
        x1, y1 = area.top_left
        width, height = area.size
        for x in range(x1, x1 + width):
            for y in range(y1, y1 + height):
                if (x, y) not in region.tiles:
                    region.place_by_type((x, y), floor_type)


def make_nodes(root_region: Region, *, node_count) -> List[Position]:
    sub_regions = make_sub_regions(root_region, node_count=node_count)
    return sub_regions_to_nodes(sub_regions)


def sub_regions_to_nodes(sub_regions) -> List[Position]:
    return [r.node for r in sub_regions]


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


DEFAULT_WIDTH_TABLE = {
    2: 20,
    1: 80
}


def join_nodes(nodes: Iterable[Position], width_table=DEFAULT_WIDTH_TABLE) -> List[Position]:
    path = []
    i = iter(nodes)
    with suppress(StopIteration):
        width = pick_from_weighted_table(width_table)
        src = next(i)
        while True:
            dest = next(i)
            path.extend(join_two_nodes(src, dest, width))
            src = dest
    return path


def join_two_nodes(src: Position, dest: Position, width=1) -> List[Position]:
    width = max(width, 1)
    x, y = src
    path = [Position(x, y)]
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
            path.extend(Position(x, y + w) for w in range(width))
        while steps[1]:
            y += dy
            steps[1] -= 1
            path.extend(Position(x + w, y) for w in range(width))
    return path


def _random_path_segment(x_count, y_count):
    """Given a distance to travel (x_count, y_count), choose to either go a random distance
    in x direction or in y direction.

    Returns:
        List[int]: number of steps to travel. For example [0, 2] means travel in the y direction 2 steps
    """
    options = [(x_count, 0), (0, y_count)]
    option = random.choice([opt for opt in options if opt[0] or opt[1]])
    return [random.randint(0, abs(option[0])), random.randint(0, abs(option[1]))]


def make_rooms_in_subregions(sub_regions: List[SubRegion], undersize_pc_probability=75):
    def weighted_scale_down(size):
        if random.randint(1, 100) > undersize_pc_probability:
            return size - 1
        return random.randint(1, size - 1)
    rooms = []
    for r in sub_regions:

        cx, cy = r.node
        x1, y1 = r.top_left
        x2, y2 = x1 + r.size.width, y1 + r.size.height
        # Shrink room by random amount with 2 conditions:
        #  - keep node inside room
        #  - keep room at least one unit inside sub-region boundary
        dx = cx - x1  # distance from centre to left wall
        if dx > 1:
            x1 = cx - weighted_scale_down(dx)
        dy = cy - y1  # distance from centre to top wall
        if dy > 1:
            y1 = cy - weighted_scale_down(dy)
        dx = x2 - cx  # distance from centre to right wall
        if dx > 1:
            x2 = cx + weighted_scale_down(dx)
        dy = y2 - cy  # distance from centre to bottom wall
        if dy > 1:
            y2 = cy + weighted_scale_down(dy)

        room = [Position(x, y)
                for x in range(x1, x2)
                for y in range(y1, y2)]

        rooms.append(room)
    return rooms


def dump_ascii_map(root_region: Region, sub_regions: List[SubRegion],
                   nodes: List[Position], paths: List[Position], rooms: List[Position],
                   filename: str):
    with suppress(FileNotFoundError):
        with open(filename, "w") as f:
            for sr, n in zip(sub_regions, nodes):
                print(sr, n, file=f)

            ascii_map = defaultdict(str)
            for y in range(root_region.grid_height):
                for x in range(root_region.grid_width):
                    ascii_map[(x, y)] = " "
            for r in sub_regions:
                r.ascii_render(ascii_map)

            for room in rooms:
                for p in room:
                    ascii_map[p] = "/"

            for p in paths:
                ascii_map[p] = "*"

            for i, n in enumerate(nodes):
                ascii_map[(n.x, n.y)] = f"{hex(i)[-1]}"

            for y in range(root_region.grid_height):
                for x in range(root_region.grid_width):
                    print(ascii_map[(x, y)], end="", file=f)
                print(file=f)

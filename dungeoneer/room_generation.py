from abc import ABC, abstractmethod
import random
from typing import List

from dungeoneer.dice_roll import pick_from_weighted_table, dice
from dungeoneer.map_maker import join_exits, carve_out_dungeon, make_sub_regions, \
    sub_regions_to_nodes, join_nodes, make_rooms_in_subregions, RegionGenerator, join_two_nodes
from dungeoneer.spawn import item_drops, monster_drops, place_treasure
from dungeoneer.regions import Position, SubRegion, Region


def random_room_generator() -> RegionGenerator:
    design_table = {
        LargeRoomGenerator: 1,
        BossRegionGenerator: 2,
        EnclosedBossChamberGenerator: 2,
        ConnectedRoomGenerator: 10
    }
    return pick_from_weighted_table(design_table)


class RoomGenerator(ABC):
    def __init__(self, region: Region):
        self.region = region
        self.sub_regions: List[SubRegion] = []
        self.paths: List[List[Position]] = []
        self.rooms: List[List[Position]] = []

    def generate(self) -> Region:
        nodes = self.make_nodes()
        self.make_corridors(nodes)
        self.make_rooms()
        self.region.rooms.add_rooms_list(self.rooms)
        carve_out_dungeon(self.region, self.paths, self.rooms)
        self.populate()
        room_type = str(self.__class__).split(".")[-1].split("Generator")[0]
        self.region.name = f"{room_type}-{self.region.pixel_base}"
        return self.region

    @abstractmethod
    def make_nodes(self):
        ...

    @abstractmethod
    def make_corridors(self, nodes):
        ...

    @abstractmethod
    def make_rooms(self):
        ...

    @abstractmethod
    def populate(self):
        ...


class ConnectedRoomGenerator(RoomGenerator):
    def make_nodes(self):
        self.sub_regions = make_sub_regions(self.region, node_count=16)
        return sub_regions_to_nodes(self.sub_regions)

    def make_corridors(self, nodes):
        self.paths = join_nodes(nodes)
        self.paths.extend(join_exits(nodes, self.region.exits, (self.region.grid_width, self.region.grid_height)))

    def make_rooms(self):
        self.rooms = make_rooms_in_subregions(self.sub_regions)

    def populate(self):
        for room in self.rooms:
            item_drops(room, self.region)
            monster_drops(room, self.region)


class BossRegionGenerator(ConnectedRoomGenerator):
    def make_nodes(self):
        self.sub_regions = make_sub_regions(self.region, node_count=2)
        return sub_regions_to_nodes(self.sub_regions)

    def make_corridors(self, nodes):
        self.paths = join_nodes(nodes, width_table={1: 2, 2: 10, 3: 2, 4: 1})
        self.paths.extend(join_exits(nodes, self.region.exits, (self.region.grid_width, self.region.grid_height)))


class EnclosedBossChamberGenerator(ConnectedRoomGenerator):
    def make_nodes(self):
        width, height = self.region.grid_width, self.region.grid_height
        boss_chamber = SubRegion(self.region, (3, 3), (width - 5, height - 5))

        self.sub_regions = [
            *boss_chamber.split_horizontally(random.uniform(0.7, 0.9))
        ]
        corners = [(1, 1), (width - 2, 1), (width - 2, height - 2), (1, height - 2)]
        corners = [Position(*p) for p in corners]
        return [*corners, *sub_regions_to_nodes(self.sub_regions)]

    def make_corridors(self, nodes):
        width = 2
        self.paths = [
            *join_two_nodes(nodes[0], nodes[1], width),
            *join_two_nodes(nodes[1], nodes[2], width),
            *join_two_nodes(nodes[2], nodes[3], width),
            *join_two_nodes(nodes[3], nodes[0], width),
            *join_two_nodes(nodes[0], nodes[4], width),
            *join_two_nodes(nodes[4], nodes[5], width),
        ]
        self.paths.extend(join_exits(nodes, self.region.exits, (self.region.grid_width, self.region.grid_height)))

    def make_rooms(self):
        self.rooms = make_rooms_in_subregions(self.sub_regions, undersize_pc_probability=0)

    def populate(self):
        for _ in range(20):
            item_drops(self.rooms[1], self.region, drop_table={place_treasure: 100})
        for _ in range(dice(3, 2)):
            item_drops(self.rooms[1], self.region)
        for _ in range(dice(3, 3) + 1):
            monster_drops(self.rooms[0], self.region)


class LargeRoomGenerator(ConnectedRoomGenerator):
    # def __init__(self, region):
    #     super().__init__(region)
    #     self.region.clear_area((1, 1), (self.region.grid_width - 1, self.region.grid_height - 1))

    def make_nodes(self):
        return [Position(10, 10)]

    def make_corridors(self, nodes):
        self.paths = join_exits(nodes, self.region.exits, (self.region.grid_width, self.region.grid_height))

    def make_rooms(self):
        self.rooms = [[Position(x, y)
                       for x in range(1, self.region.grid_width - 1)
                       for y in range(1, self.region.grid_height - 1)]]

    def populate(self):
        for room in self.rooms:
            for _ in range(4):
                item_drops(room, self.region)
                monster_drops(room, self.region)

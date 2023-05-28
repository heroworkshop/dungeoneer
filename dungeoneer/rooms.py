from typing import  List

from dungeoneer.characters import Character


class Rooms:
    def __init__(self):
        self.monsters_by_index = {}
        self.index_by_position = {}
        self.next_index = 0

    @property
    def count(self):
        return self.next_index

    def add_rooms_list(self, rooms_list: List[List]):
        for room in rooms_list:
            self.add_room(room)

    def add_room(self, room: List):
        for p in room:
            self.index_by_position[p] = self.next_index
        self.next_index += 1

    def add_monster(self, monster: Character, room_index: int):
        if room_index not in self.monsters_by_index:
            self.monsters_by_index[room_index] = []
        self.monsters_by_index[room_index].append(monster)

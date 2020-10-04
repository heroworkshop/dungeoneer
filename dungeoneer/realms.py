"""
The game universe is divided into realms, regions and tiles

Tiles are arranged in a grid big enough for one screen. This is known as a region
Regions are also arranged in a grid of variable size and this is known as a realm.

  ================
  I    |    |    I     ===
  I    |    |    I     I I   REALM
  ----------------     ===
  I    |****|    I
  I    |****|    I
  ----------------     ---
  I    |    |    I     | |   REGION
  I    |    |    I     ---
  ----------------
  I    |    |    I      *     TILE
  I    |    |    I
  ================
"""

from dungeoneer.regions import Position, Region


class Realm:
    """A realm is a variable sized grid of Regions"""

    def __init__(self, size, region_size=(50, 30)):
        self.regions = dict()
        self.width, self.height = size

        for x in range(self.width):
            for y in range(self.height):
                self.regions[Position(x, y)] = Region(region_size)

    def __len__(self):
        return len(self.regions)

    def region(self, position: Position):
        return self.regions[position]
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
import copy
from contextlib import suppress
from random import randint
from typing import Dict, Tuple, cast

import pygame

from dungeoneer.actors import Monster, MissileSprite, Player
from dungeoneer.interfaces import SpriteGroups, Item, SpriteGrouper, Collider, Observer
from dungeoneer.item_sprites import make_item_sprite
from dungeoneer.map_maker import generate_map
from dungeoneer.room_generation import random_room_generator
from dungeoneer.pathfinding import move_to_nearest_empty_space
from dungeoneer.regions import Position, Region


class PointOutsideRealmBoundary(ValueError):
    """Raised when trying to access position outside the realms boundaries"""


class Realm(SpriteGrouper, Observer):
    """A realm is a variable sized grid of Regions

    Args:
        size (tuple[int, int]): Number of regions in the x and y direction
        tile_size (tuple[int, int]): pixel dimensions of a tile
        region_size  (tuple[int, int]): tile dimensions of a region
    """

    def __init__(self, size, tile_size, region_size=(50, 30)):
        region_width, region_height = region_size
        self.tile_size = pygame.Vector2(tile_size)
        tile_width, tile_height = tile_size
        self.region_pixel_size = int(region_width * tile_width), int(region_height * tile_height)
        self.regions: Dict[Position, Region] = {}
        self.width, self.height = size
        self.pixel_bounds = pygame.Rect(0, 0, self.width * region_width * tile_width,
                                        self.height * region_height * tile_height)
        self.groups = SpriteGroups()  # global across all regions

        self.create_empty_regions(region_size)

    def on_update(self, attribute, value):
        """Implementation of method from Observer class"""
        if attribute == "move":
            # notify relevant region of movement
            mover = cast(pygame.sprite, value)
            region = self.region_from_pixel_position(mover.rect.center)
            x, y = mover.rect.center
            region.on_player_move(x, y)

    def create_empty_regions(self, region_size):
        region_width, region_height = region_size
        for x in range(self.width):
            for y in range(self.height):
                pixel_base = x * self.region_pixel_size[0], y * self.region_pixel_size[1]
                region = Region(region_size, id_code=(x, y), pixel_base=pixel_base,
                                tile_size=self.tile_size)
                if y > 0:
                    region.exits["N"] = self.regions[Position(x, y - 1)].exits["S"]
                if y < self.height - 1:
                    region.exits["S"] = randint(1, region_width - 1)
                if x > 0:
                    region.exits["W"] = self.regions[Position(x - 1, y)].exits["E"]
                if x < self.width - 1:
                    region.exits["E"] = randint(1, region_height - 1)
                self.regions[Position(x, y)] = region

    def __len__(self):
        return len(self.regions)

    def region(self, position: Position):
        try:
            return self.regions[position]
        except KeyError as e:
            raise PointOutsideRealmBoundary(f"Position {position} was outside the realm with "
                                            f"size ({self.width}, {self.height})") from e

    def region_coord_from_pixel_position(self, pixel_position):
        x, y = pixel_position
        width, height = self.region_pixel_size
        return x // width, y // height

    def region_from_pixel_position(self, pixel_position):
        try:
            return self.region(self.region_coord_from_pixel_position(pixel_position))
        except PointOutsideRealmBoundary as e:
            raise PointOutsideRealmBoundary(f"Pixel Position {pixel_position} "
                                            f"was outside the realm with size ({self.width}, {self.height})") from e

    def neighbouring_regions_from_pixel_position(self, pixel_position):
        pixel_position = pygame.Vector2(pixel_position)
        dx, dy = self.region_pixel_size
        dx = dx // 2 - 1
        dy = dx // 2 - 1
        neighbours = [(-dx, -dy), (dx, -dy),
                      (-dx, dy), (dx, dy)]
        region_coords = {self.region_coord_from_pixel_position(pygame.Vector2(n) + pixel_position)
                         for n in neighbours}
        results = []
        for p in region_coords:
            with suppress(PointOutsideRealmBoundary):
                results.append(self.region(p))
        return results

    def generate_map(self):
        for _coordinates, region in self.regions.items():
            generate_map(region, random_room_generator())
            region.build_world(self)

    def render_tiles(self):
        pixel_width = self.regions[(0, 0)].pixel_width
        pixel_height = self.regions[(0, 0)].pixel_height

        surface = pygame.Surface((pixel_width * self.width, pixel_height * self.height))

        for x in range(self.width):
            for y in range(self.height):
                position = pygame.math.Vector2(x * pixel_width, y * pixel_height)
                self.regions[(x, y)].render_tiles_to_surface(surface, position)
        return surface

    def out_of_bounds(self, sprite):
        return not sprite.rect.colliderect(self.pixel_bounds)

    def check_bounds(self, group):
        for sprite in group:
            if self.out_of_bounds(sprite):
                sprite.kill()

    def any_solid_collisions(self, other: Collider, position: Tuple[int]) -> bool:
        sub_groups = self.region_from_pixel_position(position).groups
        return any(other.collided(groups.solid) or other.collided(groups.player)
                   for groups in (sub_groups, self.groups))

    def shoot(self, sprite, affects_player):
        if affects_player:
            self.groups.missile.add(sprite)
        else:
            self.groups.player_missile.add(sprite)

    def drop(self, item, position, motion=None):
        x, y = position
        sprite = make_item_sprite(item, x, y, motion=motion)
        self.drop_item_sprite(sprite, position)
        return sprite

    def drop_item_sprite(self, item_sprite, position):
        item_sprite.center = position
        region = self.region_from_pixel_position(position)
        region.groups.items.add(item_sprite)
        region.groups.effects.add(item_sprite)

    def effect(self, effect_sprite: pygame.sprite.Sprite):
        self.groups.effects.add(effect_sprite)

    def spawn(self, monster_sprite):
        region = self.region_from_pixel_position(monster_sprite.rect.center)
        world = region.groups
        if move_to_nearest_empty_space(monster_sprite, (world.solid, world.player), 500):
            world.solid.add(monster_sprite)
            world.sleeping_monster.add(monster_sprite)
            return monster_sprite
        return None

    def centre_on_tile(self, pixel_pos, offset=(0, 0)):
        x, y = pixel_pos
        region = self.region_from_pixel_position(pixel_pos)
        width, height = region.tile_width, region.tile_height
        ox, oy = offset
        x = x - x % width + width // 2 + ox * width
        y = y - y % height + height // 2 + oy * height
        return pygame.Vector2(x, y)

    def update_monster_group(self, monster: Monster, from_region: Region):
        """Ensure that the monster is in the correct group based on its current position"""
        position = monster.rect.center
        region = self.region_from_pixel_position(position)
        if monster not in region.groups.monster:
            from_region.groups.monster.remove(monster)
            from_region.groups.solid.remove(monster)
            region.groups.monster.add(monster)
            region.groups.solid.add(monster)


def drop_item(item_spec: Item, realm: Realm, x: int, y: int, count=1):
    drop_x, drop_y = x + randint(-16, 16), y + randint(-16, 16)
    new_item = copy.copy(item_spec)
    new_item.count = count
    item = make_item_sprite(new_item, drop_x, drop_y)
    groups = realm.region_from_pixel_position((x, y)).groups
    groups.items.add(item)
    groups.effects.add(item)
    return item


def handle_missile_collisions(realm: Realm):
    # The player is not in the solid group so enemy missiles
    # will need to do collision detection with the player group instead.
    # It is important that player missiles don't collide with the player.
    missile: MissileSprite
    for missile in realm.groups.player_missile:
        region = realm.region_from_pixel_position(missile.rect.center)
        hit = pygame.sprite.spritecollideany(missile, region.groups.solid)
        if hit:
            missile.on_impact(hit, realm)

    for missile in realm.groups.missile:
        region = realm.region_from_pixel_position(missile.rect.center)

        hit = pygame.sprite.spritecollideany(missile, region.groups.solid)
        hit = hit or pygame.sprite.spritecollideany(missile, realm.groups.player)
        if hit:
            missile.on_impact(hit, realm)

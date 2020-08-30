import copy
import math
from collections import defaultdict
from random import randint
from types import SimpleNamespace

import pygame

from dungeoneer import game_assets, treasure
from dungeoneer.inventory import Inventory
from dungeoneer.item_sprites import make_item_sprite
from dungeoneer.items import Ammo
from dungeoneer.scenary import VisualEffect
from dungeoneer.characters import Character, MonsterType
from dungeoneer.game_assets import load_sound, sfx_file, make_sprite_sheet
from dungeoneer.interfaces import SpriteGroups, Item
from dungeoneer.pathfinding import move_to_nearest_empty_space
from dungeoneer.spritesheet import SpriteSheet


def extract_filmstrips(sprite_sheet: SpriteSheet):
    filmstrips = SimpleNamespace()
    filmstrip = sprite_sheet.filmstrip()
    step = len(filmstrip) // 4
    if not step:
        filmstrips.walk_south = filmstrips.walk_west = \
            filmstrips.walk_east = filmstrips.walk_north = filmstrip
    else:
        n = 0
        filmstrips.walk_south = filmstrip[n: n + step]
        n += step
        filmstrips.walk_west = filmstrip[n: n + step]
        n += step
        filmstrips.walk_east = filmstrip[n: n + step]
        n += step
        filmstrips.walk_north = filmstrip[n: n + step]
    return filmstrips


class Actor(pygame.sprite.Sprite):
    def __init__(self, x, y, character, world: SpriteGroups):
        pygame.sprite.Sprite.__init__(self)
        self.group = world
        self.filmstrips = extract_filmstrips(character.template.sprite_sheet)
        self.character = character
        self._vitality = character.vitality
        self.filmstrip = self.filmstrips.walk_south
        self.frame = 0
        self.image = self.filmstrip[self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 4
        self.dx, self.dy = (0, 0)  # unit vector. Actual velocity is speed x this value
        self.facing = (0, 1)  # direction the actor is facing
        self.attack_cooloff = 0
        self.actions = copy.deepcopy(character.template.actions)
        self._missile_sfx = None
        self._connected_sprites = []
        self.observers = defaultdict(list)

    def add_observer(self, observer, attribute):
        self.observers[attribute].append(observer)
        observer.on_update(attribute, Item(attribute, count=getattr(self, attribute)))

    @property
    def vitality(self):
        return self._vitality

    @vitality.setter
    def vitality(self, value):
        self._vitality = value
        for observer in self.observers["vitality"]:
            observer.on_update("vitality", Item("vitality", count=self._vitality))

    @property
    def missile_sfx(self):
        if not self._missile_sfx:
            self._missile_sfx = load_sound(sfx_file("arrow.wav"))
        return self._missile_sfx

    def on_collided(self):
        """overload this to determine what happens when hitting a solid object"""

    def move(self, solid_object_group):
        if not self.dx and not self.dy:
            return
        vx, vy = self.dx * self.speed, self.dy * self.speed
        self.filmstrip = self.filmstrip_from_direction(vx, vy)
        self.frame = (self.frame + 1) % len(self.filmstrip)
        self.image = self.filmstrip[self.frame]
        self.rect.centerx += vx
        if self.collided(solid_object_group):
            self.rect.centerx -= vx
            vx = 0
        self.rect.centery += vy
        if self.collided(solid_object_group):
            self.rect.centery -= vy
            vy = 0
        for sprite in self._connected_sprites:
            sprite.rect.x += vx
            sprite.rect.y += vy

    def filmstrip_from_direction(self, vx, vy):
        image_table = {(0, 1): self.filmstrips.walk_south,
                       (-1, 0): self.filmstrips.walk_west,
                       (1, 0): self.filmstrips.walk_east,
                       (0, -1): self.filmstrips.walk_north,
                       }

        if (0, self.dy) in image_table:
            self.filmstrip = image_table[(0, self.dy)]
        elif (self.dx, 0) in image_table:
            self.filmstrip = image_table[(self.dx, 0)]
        if self.dx or self.dy:
            self.facing = (self.dx, self.dy)
        return self.filmstrip

    def collided(self, group):
        collisions = pygame.sprite.spritecollide(self, group, dokill=False,
                                                 collided=pygame.sprite.collide_rect_ratio(0.8))
        return any([c is not self for c in collisions])

    def die(self):
        self.kill()

    def on_hit(self):
        if self.vitality < 0:
            self.die()

    @property
    def ammo(self):
        del self  # unused
        return 1

    def expend_ammo(self):
        del self  # unused
        """Unlimited ammo"""
        return Item("missile", 1)

    def shoot(self):
        t = pygame.time.get_ticks()
        if t < self.attack_cooloff:
            return None
        if not self.expend_ammo():
            return None
        self.missile_sfx.play()
        self.attack_cooloff = t + 1000 // self.character.rate_of_fire
        dx, dy = self.facing

        missile = self.make_missile(dx, dy)
        if not missile:
            return None
        if dx > 0:
            missile.rect.left = self.rect.right
        elif dx < 0:
            missile.rect.right = self.rect.left
        if dy > 0:
            missile.rect.top = self.rect.bottom
        elif dy < 0:
            missile.rect.bottom = self.rect.top
        return missile

    def make_missile(self, dx, dy):
        raise NotImplemented

    def connect(self, sprite):
        """A connected sprite will move when the other sprite moves"""
        self._connected_sprites.append(sprite)


class Player(Actor):
    def __init__(self, x, y, character, world: SpriteGroups):
        super().__init__(x, y, character, world)
        self.inventory = Inventory()

    def handle_keyboard(self, kb):
        self.dx = self.dy = 0

        if kb[pygame.K_a]:
            self.dx = -1
        if kb[pygame.K_d]:
            self.dx = 1
        if kb[pygame.K_w]:
            self.dy = -1
        if kb[pygame.K_s]:
            self.dy = 1
        if kb[pygame.K_RETURN]:
            self.shoot()

    @property
    def ammo(self):
        item = self.inventory.ammo
        if item:
            return item.count
        return 0

    def expend_ammo(self):
        return self.inventory.remove_item(slot_index=self.inventory.AMMO)

    def make_missile(self, dx, dy):
        ammo_item: Ammo = self.inventory.slot(Inventory.AMMO)

        return make_attack(self.rect.centerx, self.rect.centery,
                           (dx, dy), self.group,
                           ammo_item,
                           repeats=True)


class Monster(Actor):
    def __init__(self, x, y, character, group, direction=(0, 0)):
        super().__init__(x, y, character, group)
        self.dx, self.dy = direction

        self.speed = self.character.template.speed
        self.targeted_enemy = None

    def on_collided(self):
        self.dx, dy = (0, 0)

    def target_enemy(self, player):
        if self.character.sleeping:
            return
        if not player.alive():
            self.targeted_enemy = None
            return
        self.targeted_enemy = player
        px, py = player.rect.center
        x, y = self.rect.center

        def home_in(me, them):
            if me + self.speed < them:
                return 1
            if me - self.speed > them:
                return -1
            return 0
        self.dx, self.dy = (home_in(x, px), home_in(y, py))

    def die(self):
        sprite_sheet, value, scale = treasure.random_treasure(self.character.template.treasure)
        if randint(1, 100) < 20:
            item = GoldItem(self.rect.centerx, self.rect.centery, sprite_sheet.filmstrip(scale=scale), value)
            self.group.all.add(item)
            self.group.items.add(item)
        super().die()

    def do_actions(self, world):
        for action in self.actions:
            if action.ready_action(self, self.targeted_enemy):
                runner = action.create(world, self, self.targeted_enemy)
                runner_func = globals()[runner.name]
                result = runner_func(**runner.parameters)
                action.on_activated(result, self, self.targeted_enemy)


def rotation_from_direction(direction):
    rotate_table = {(0, 1): 180,
                    (0, -1): 0,
                    (1, 0): -90,
                    (-1, 0): 90,
                    (1, 1): -135,
                    (-1, 1): 135,
                    (1, -1): -45,
                    (-1, -1): 45}
    angle = rotate_table.get(direction)
    if angle is not None:
        return angle
    dx, dy = direction
    rads = math.atan2(-dy, dx)
    rads %= 2 * math.pi
    degs = math.degrees(rads)
    return degs


def make_small_impact(x, y):
    image = game_assets.load_image("small_short_effect_hit.png")
    sprite_sheet = SpriteSheet(image, columns=16, rows=1, sub_area=(0, 0, 3, 1))
    return VisualEffect(x, y, sprite_sheet.filmstrip(), reverse=True)


def drop_item(item_spec:Item, world, x: int, y: int):
    drop_x, drop_y = x + randint(-16, 16), y + randint(-16, 16)
    item = make_item_sprite(item_spec, drop_x, drop_y)
    world.items.add(item)
    world.all.add(item)


class MissileSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_sheet, direction, ammo_item: Ammo,
                 impact_maker=make_small_impact, repeats=False):
        super().__init__()
        self.impact_maker = impact_maker

        self.filmstrip = sprite_sheet.filmstrip(rotate=rotation_from_direction(direction))
        self.frame = 0
        self.image = self.filmstrip[self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.dx, self.dy = direction
        self.shot_from_item = ammo_item
        self.speed = ammo_item.speed
        self.damage = ammo_item.damage
        self.damage_profile = ammo_item.damage_profile or [100]
        extra_frames = sprite_sheet.image_count - len(self.damage_profile)
        if extra_frames > 0:
            self.damage_profile.extend([0] * extra_frames)

        self.hit_sfx = load_sound(sfx_file("splat.wav"))
        self.repeats = repeats

    def move(self, solid_object_group):
        self.frame += 1
        if self.frame >= len(self.filmstrip) and not self.repeats:
            self.kill()
            return
        self.frame = self.frame % len(self.filmstrip)
        self.image = self.filmstrip[self.frame]
        if not self.dx and not self.dy:
            return
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed

    def on_impact(self, target, world):
        if not self.damage_profile:
            return
        factor = self.damage_profile[self.frame % len(self.damage_profile)]
        actual_damage = int(self.damage * factor / 100.0)
        if actual_damage < 1:
            return
        self.damage -= actual_damage
        if self.damage <= 0:
            self.kill()
        target.vitality -= actual_damage
        self.hit_sfx.play()
        x, y = target.rect.center
        world.all.add(self.make_impact_effect(x, y))
        if randint(0, 100) <= self.shot_from_item.survivability:
            drop_item(self.shot_from_item, world, x, y)
        target.on_hit()

    def make_impact_effect(self, x, y):
        return self.impact_maker(x, y)


class GoldItem(VisualEffect):
    def __init__(self, x, y, filmstrip, value):
        super().__init__(x, y, filmstrip, repeats=VisualEffect.FOREVER)
        self.value = value
        self.sound_effect = load_sound(sfx_file("handleCoins.ogg"))

    def on_pick_up(self, player):
        player.character.gold += self.value
        self.sound_effect.play()


def make_arrow(x, y, direction, world):
    return make_attack(x, y, direction, world, "arrow", 10, [100], 12, repeats=True)


def make_attack(x, y, direction, world, attack_item: Ammo, repeats=False):
    if not attack_item:
        return None
    sprite_sheet = make_sprite_sheet(attack_item.name)

    sprite = MissileSprite(x, y, sprite_sheet, direction, attack_item, repeats=repeats)
    world.missile.add(sprite)
    world.all.add(sprite)
    return sprite


def make_monster(monster_type: MonsterType, x, y, world: SpriteGroups, sleeping=False):
    if type(monster_type) is str:
        monster_type = MonsterType[monster_type]
    monster = Character(monster_type)
    monster_sprite = Monster(x, y, monster, world)
    if move_to_nearest_empty_space(monster_sprite, world, 500):
        monster.sleeping = sleeping
        world.all.add(monster_sprite)
        world.solid.add(monster_sprite)
        world.monster.add(monster_sprite)
        return monster_sprite
    return None





import abc
import random
from collections import namedtuple
from copy import copy

import pygame

from dungeoneer import items
from dungeoneer.items import Ammo

Runner = namedtuple("runner", "name parameters")


class Action(abc.ABC):
    def __init__(self):
        self.cool_off = 0
        self.rate_of_fire = 1

    def ready_action(self, owner, target) -> bool:
        t = pygame.time.get_ticks()
        if t < self.cool_off:
            return False
        if not self.valid_target(owner, target):
            return False
        self.cool_off = t + 1000 // self.rate_of_fire
        return True

    def valid_target(self, owner, target) -> bool:
        del owner
        if not target:
            return False
        return True

    @abc.abstractmethod
    def create(self, world, owner, target) -> Runner:
        pass

    def on_activated(self, result, owner, target):
        pass


class SummonAction(Action):
    def __init__(self, monster_type_names, rate_of_fire):
        super().__init__()
        self.monster_type_names = monster_type_names
        self.rate_of_fire = rate_of_fire

    def create(self, realm, owner, target) -> Runner:
        x, y = owner.rect.center
        monster_type_name = random.choice(self.monster_type_names)
        parameters = dict(monster_type=monster_type_name, x=x, y=y, realm=realm)
        return Runner("make_monster_sprite", parameters)


class AttackAction(Action):
    def __init__(self, attack_item, damage, rate_of_fire=1.0, reach=32):
        super().__init__()
        self.attack_item = attack_item
        self.damage = damage
        self.rate_of_fire = rate_of_fire
        self.reach_squared = reach ** 2

    def create(self, realm, owner, target):
        x, y = target.rect.center
        ox, oy = owner.rect.center
        direction = x - ox, y - oy
        attack_item: Ammo = copy(items.generated_ammo[self.attack_item])
        attack_item.damage = self.damage
        world = realm.region_from_pixel_position((x, y)).groups
        parameters = dict(x=x, y=y, direction=direction, group=realm.groups.missile,
                          attack_item=attack_item)
        return Runner("make_attack_sprite", parameters)

    def on_activated(self, result, owner, target):
        owner.connect(result)

    def valid_target(self, owner, target):
        if not target:
            return False
        x, y = target.rect.center
        ox, oy = owner.rect.center
        reach_squared = (x - ox) ** 2 + (y - oy) ** 2
        return self.reach_squared >= reach_squared

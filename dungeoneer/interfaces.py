from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol, Tuple

import pygame.sprite
from pygame.sprite import Group

from dungeoneer.sound_effects import SfxEvents


@dataclass
class SpriteGroups:
    effects: Group = field(default_factory=Group)
    solid: Group = field(default_factory=Group)
    player: Group = field(default_factory=Group)
    monster: Group = field(default_factory=Group)
    missile: Group = field(default_factory=Group)
    player_missile: Group = field(default_factory=Group)
    items: Group = field(default_factory=Group)
    hud: Group = field(default_factory=Group)


class Collider(Protocol):
    def collided(self, group: pygame.sprite.Group):
        ...


class SpriteGrouper(Protocol):
    def any_solid_collisions(self, other: Collider, position: Tuple[int]) -> bool:
        ...

    def shoot(self, sprite, affects_player):
        ...

    def drop(self, item, position, motion=None):
        ...

    def drop_item_sprite(self, item_sprite, position):
        ...

    def effect(self, effect_sprite: pygame.sprite.Sprite):
        ...

    def spawn(self, monster_sprite):
        ...


class Observer(ABC):
    @abstractmethod
    def on_update(self, attribute, value):
        """Notify an observer of a change to an attribute"""


class Item:
    def __init__(self, name, count=1, sfx_events=None):
        self.count = count
        self.name = name
        self.preferred_slot = None
        self.sfx_events = sfx_events or SfxEvents()
        self.selected = False

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Observable(ABC):
    def __init__(self):
        self.observers = defaultdict(list)

    def add_observer(self, observer: Observer, attribute_id):
        self.observers[attribute_id].append(observer)
        observer.on_update(attribute_id, self.attribute(attribute_id))

    def notify_observers(self, attribute_id):
        """Notify all observers that have registered an interest in attribute_id of the current value"""
        for observer in self.observers[attribute_id]:
            observer.on_update(attribute_id, self.attribute(attribute_id))

    @abstractmethod
    def attribute(self, attribute_id):
        """return the value of attribute_id"""


class KeyObserver(ABC):
    @abstractmethod
    def on_key_down(self, key):
        """Notify observer when a key is pressed"""

    @abstractmethod
    def on_key_up(self, key):
        """Notify observer when a key is released"""


class Direction(Enum):
    LEFT_TO_RIGHT = (1, 0)
    RIGHT_TO_LEFT = (-1, 0)
    TOP_DOWN = (0, 1)
    BOTTOM_UP = (0, -1)

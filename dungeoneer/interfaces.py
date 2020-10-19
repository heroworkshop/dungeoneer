from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum

from pygame.sprite import Group


@dataclass
class SpriteGroups:
    all: Group = field(default_factory=Group)
    solid: Group = field(default_factory=Group)
    player: Group = field(default_factory=Group)
    monster: Group = field(default_factory=Group)
    missile: Group = field(default_factory=Group)
    player_missile: Group = field(default_factory=Group)
    items: Group = field(default_factory=Group)
    hud: Group = field(default_factory=Group)


class Observer(ABC):
    @abstractmethod
    def notify(self, value):
        pass


class Item:
    def __init__(self, name, count=1, sfx_events=None):
        self.count = count
        self.name = name
        self.preferred_slot = None
        self.sfx_events = sfx_events
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

    def add_observer(self, observer: Observer, attribute):
        """An observer can register an interest in an attribute"""


class Observer(ABC):
    @abstractmethod
    def on_update(self, attribute, value):
        """Notify an observer of a change to an attribute"""


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

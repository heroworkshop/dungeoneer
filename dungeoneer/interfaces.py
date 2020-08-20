from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from pygame.sprite import Group


@dataclass
class SpriteGroups:
    all: Group = field(default_factory=Group)
    solid: Group = field(default_factory=Group)
    monster: Group = field(default_factory=Group)
    missile: Group = field(default_factory=Group)
    items: Group = field(default_factory=Group)
    hud: Group = field(default_factory=Group)


class Observer(ABC):
    @abstractmethod
    def notify(self, value):
        pass


class Item:
    def __init__(self, name, count=1):
        self.count = count
        self.name = name
        self.preferred_slot = None

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
    def notify(self, attribute, value):
        """Notify an observer of a change to an attribute"""

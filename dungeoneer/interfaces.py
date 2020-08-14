from abc import ABC, abstractmethod
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


class Item(ABC):
    def __init__(self):
        self.count = 1

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name() == other.name()
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @staticmethod
    @abstractmethod
    def name():
        pass

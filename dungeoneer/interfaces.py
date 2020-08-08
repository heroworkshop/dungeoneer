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

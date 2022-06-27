import enum

from dungeoneer.actions import SummonAction, AttackAction
from dungeoneer.game_assets import make_sprite_sheet


class CharacterTemplate:
    def __init__(self, sprite_sheet, vitality=0,
                 armour=0,
                 speed=4,
                 treasure=10,
                 rate_of_fire=1.0,
                 actions=None,
                 retarget_period=15
                 ):
        self.vitality = vitality
        self.armour = armour
        self.speed = speed
        self.sprite_sheet = sprite_sheet
        self.treasure = treasure
        self.rate_of_fire = rate_of_fire
        self.actions = actions if actions else []
        self.retarget_period = retarget_period


class Character:
    def __init__(self, template_enum):
        self.type_name = template_enum.name
        self.template = template_enum.value
        self.vitality = self.template.vitality
        self.gold = 0

    @property
    def rate_of_fire(self):
        return self.template.rate_of_fire  # shots per second

    @property
    def retarget_period(self):
        return self.template.retarget_period


class MonsterType(enum.Enum):
    _CT = CharacterTemplate
    ZOMBIE = _CT(vitality=10, speed=2,
                 sprite_sheet=make_sprite_sheet("zombie"),
                 actions=[AttackAction("swipe", 10)]
                 )
    ZOMBIE_GENERATOR = _CT(vitality=100, speed=0, rate_of_fire=0.1,
                           sprite_sheet=make_sprite_sheet("zombie generator"),
                           actions=[SummonAction(["ZOMBIE"], 0.1)],
                           retarget_period=30
                           )
    MUMMY = _CT(vitality=30, speed=2,
                sprite_sheet=make_sprite_sheet("mummy"),
                actions=[AttackAction("swipe", 20)]
                )
    SKELETON = _CT(vitality=5, speed=4,
                sprite_sheet=make_sprite_sheet("skeleton"),
                actions=[AttackAction("swipe", 10)]
                )

class PlayerCharacterType(enum.Enum):
    _CT = CharacterTemplate
    GRIMSON = _CT(vitality=20, speed=4,
                  sprite_sheet=make_sprite_sheet("player01"),
                  armour=10,
                  )
    TOBY = _CT(vitality=150, speed=6,
               sprite_sheet=make_sprite_sheet("player02"),
               armour=0, rate_of_fire=1.5,
               )

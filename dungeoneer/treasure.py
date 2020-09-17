import enum
from collections import namedtuple
from random import randint

from dungeoneer.game_assets import make_sprite_sheet

coin_horde = namedtuple("coin_horde", "sprite_sheet lower upper scale")


class GoldType(enum.Enum):
    GOLD_COINS = coin_horde(sprite_sheet=make_sprite_sheet("gold pieces"),
                            lower=5, upper=30, scale=0.5
                            )
    GOLD_PILE = coin_horde(sprite_sheet=make_sprite_sheet("gold pile"),
                           lower=100, upper=500, scale=1
                           )


def random_treasure(multiplier):
    item_type = GoldType.GOLD_COINS.value
    value = randint(item_type.lower, item_type.upper)
    return item_type.sprite_sheet, value, item_type.scale

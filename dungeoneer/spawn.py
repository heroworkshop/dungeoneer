import random

from dungeoneer import treasure, items
from dungeoneer.characters import MonsterType
from dungeoneer.dice_roll import pick_from_weighted_table
from dungeoneer.game_assets import make_sprite_sheet
from dungeoneer.item_sprites import ItemSprite
from dungeoneer.items import GoldItem
from dungeoneer.regions import Tile


def monster_drops(room, region, base_p=30):
    drop_table = {
        place_monster: 100
    }
    type_table = {
        MonsterType.ZOMBIE: 50,
        MonsterType.SKELETON: 50,
        MonsterType.MUMMY: 20,
        MonsterType.TIGERMAN: 20
    }
    p = base_p
    while random.randint(1, 100) <= p:
        p //= 2
        pos = random.choice(room)
        dropper = pick_from_weighted_table(drop_table)
        monster_type = pick_from_weighted_table(type_table)
        dropper(pos, region, monster_type)


def place_treasure(pos, region):
    sprite_sheet, value, scale = treasure.random_treasure(1)
    region.visual_effects[pos] = Tile(GoldItem, sprite_sheet.filmstrip(scale=scale), layer=1, value=value)


def place_item(pos, region):
    item = random.choice(list(items.all_items.values()))
    sprite_sheet = make_sprite_sheet(item.name)
    region.visual_effects[pos] = Tile(ItemSprite, sprite_sheet.filmstrip(), layer=1, item_spec=item)


def place_monster(pos, region, monster_type):
    region.monster_eggs[pos] = monster_type


DEFAULT_DROP_TABLE = {
    place_treasure: 20,
    place_item: 80
}


def item_drops(room, region, drop_table=None):
    drop_table = drop_table or DEFAULT_DROP_TABLE
    p = 40
    while random.randint(0, 100) <= p:
        p //= 2
        pos = random.choice(room)
        dropper = pick_from_weighted_table(drop_table)
        dropper(pos, region)

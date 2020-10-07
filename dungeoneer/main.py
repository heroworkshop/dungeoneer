import sys
from random import randint

import pygame

from dungeoneer import interfaces, floorplan, sprite_effects, game_assets
from dungeoneer import intro
from dungeoneer import tiles
from dungeoneer.actors import Player, make_monster_sprite
from dungeoneer.debug import debug_filmstrips
from dungeoneer.characters import Character, PlayerCharacterType, MonsterType
from dungeoneer.event_dispatcher import KeyEventDispatcher
from dungeoneer.fonts import make_font
from dungeoneer.game_assets import image_file
from dungeoneer.interfaces import Item
from dungeoneer.inventory_controller import InventoryController
from dungeoneer.inventory_view import InventoryView
from dungeoneer.item_sprites import make_item_sprite
from dungeoneer import items
from dungeoneer.map_maker import generate_map, DesignType
from dungeoneer.pathfinding import move_to_nearest_empty_space
from dungeoneer.regions import Region
from dungeoneer.score_bar import ScoreBar
from dungeoneer.spritesheet import SpriteSheet

GENERATOR_EVENT = pygame.USEREVENT + 1

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

SCREEN_BOUNDS = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)


class GameInterrupt(RuntimeError):
    """Raised to signal game end"""


def out_of_bounds(sprite):
    return not sprite.rect.colliderect(SCREEN_BOUNDS)


def play():
    pygame.mixer.pre_init(frequency=44100)
    pygame.init()
    pygame.mixer.init(frequency=44100)
    screen_flags = pygame.FULLSCREEN | pygame.DOUBLEBUF
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), screen_flags)
    intro.play(screen)

    clock = pygame.time.Clock()

    tile_manager = tiles.TileManager()
    tile_manager.import_tiles("terrain.png", 8, 16)

    game_map = tiles.TileMap(tile_manager.tiles[7], (32, 32))
    world = interfaces.SpriteGroups()

    region = Region((SCREEN_WIDTH//game_map.tile_width, SCREEN_HEIGHT//game_map.tile_height))
    generate_map(region, DesignType.CONNECTED_ROOMS)
    background = region.render_tiles()
    region.build_world(world)

    screen.blit(background, (0, 0))

    player = create_player(world)
    move_to_nearest_empty_space(player, [world.solid], 50)
    create_health_bar(player, world)
    InventoryView(player.inventory, SCREEN_WIDTH - 80, 200,
                  sprite_groups=[world.hud])
    key_event_dispatcher = KeyEventDispatcher()
    key_event_dispatcher.register(InventoryController(player.inventory, player))

    add_demo_items(world)

    make_monster_sprite(MonsterType.ZOMBIE_GENERATOR, 200, randint(0, screen.get_height()), world)
    make_monster_sprite(MonsterType.ZOMBIE_GENERATOR, 800, randint(0, screen.get_height()), world)

    pygame.mixer.music.load(game_assets.music_file("Dragon_and_Toast.mp3"))
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play()

    while True:
        world.all.clear(screen, background)
        world.hud.clear(screen, background)
        world.all.update()
        world.hud.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise GameInterrupt
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    raise GameInterrupt
                elif event.key == pygame.K_F12:
                    debug_filmstrips(screen, world.all)
                    screen.blit(background, (0, 0))
                key_event_dispatcher.event(event.type, event.key)
        kb = pygame.key.get_pressed()
        player.handle_keyboard(kb)

        player.move([world.solid])
        for monster in world.monster:
            monster.target_enemy(player)
            monster.move((world.player, world.solid))
            monster.do_actions(world)
        for missile in world.missile:
            if out_of_bounds(missile):
                missile.kill()

        # This is for player missiles. The player is not in the solid group so enemy missiles
        # will need to do collision detection with the player group instead.
        # It is important that player missiles and items don't collide with the player.
        missile_hits = pygame.sprite.groupcollide(world.solid, world.missile, False, False)
        for hit, missiles in missile_hits.items():
            for m in missiles:
                m.on_impact(hit, world)

        pick_ups = pygame.sprite.spritecollide(player, world.items, dokill=False, collided=pygame.sprite.collide_mask)
        # refresh drop-lock
        player.recently_dropped_items = {item for item in player.recently_dropped_items if item in pick_ups}

        for item in pick_ups:
            if item not in player.recently_dropped_items:
                item.kill()
                item.on_pick_up(player)

        world.all.draw(screen)
        world.hud.draw(screen)
        display_fps(screen, clock, (0, 0))
        pygame.display.flip()
        clock.tick(25)


def add_demo_items(world):
    arrows: Item = items.ammo["arrow"]
    arrows.count = 5
    arrow_sprite = make_item_sprite(arrows, 500, 450)
    if move_to_nearest_empty_space(arrow_sprite, [world.solid], 50):
        world.items.add(arrow_sprite)
        world.all.add(arrow_sprite)
    melon = make_item_sprite(items.food["melon"], 550, 500)
    if move_to_nearest_empty_space(melon, [world.solid], 50):
        world.items.add(melon)
        world.all.add(melon)

    x = 650
    y = 500
    for i, item in enumerate(items.all_items.values()):
        item_sprite = make_item_sprite(item, x + 32 * (i % 8), y + 32 * (i // 8))
        if move_to_nearest_empty_space(arrow_sprite, [world.solid], 50):
            world.items.add(item_sprite)
            world.all.add(item_sprite)


def create_player(world):
    player_character = Character(PlayerCharacterType.TOBY)
    player = Player(500, 500, player_character, world)
    move_to_nearest_empty_space(player, [world.solid], 100)
    world.all.add(player)
    world.player.add(player)
    return player


def create_health_bar(player, world):
    heart = pygame.image.load(image_file("heart.png"))
    heart_filmstrip = SpriteSheet(heart, 1, 1).filmstrip(scale=0.1)
    throbbing_heart = sprite_effects.throbbing(heart_filmstrip[0])
    health_bar = ScoreBar(30, 30, throbbing_heart, 100, 10, frame_length=50)
    world.hud.add(health_bar)
    player.add_observer(health_bar, "vitality")

def display_fps(surface, clock, position):
    font = make_font("Times New Roman", 20)
    caption = font.render(str(int(clock.get_fps())), True, (255, 255, 255))
    surface.blit(caption, position)

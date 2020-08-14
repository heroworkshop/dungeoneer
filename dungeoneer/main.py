import sys
from random import randint

import pygame

from dungeoneer import interfaces, floorplan, sprite_effects
from dungeoneer import intro
from dungeoneer import tiles
from dungeoneer.actors import Player, make_monster
from dungeoneer.debug import debug_filmstrips
from dungeoneer.characters import Character, PlayerCharacterType, MonsterType
from dungeoneer.game_assets import image_file
from dungeoneer.pathfinding import move_to_nearest_empty_space
from dungeoneer.score_bar import ScoreBar, Direction
from dungeoneer.spritesheet import SpriteSheet

GENERATOR_EVENT = pygame.USEREVENT + 1

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

SCREEN_BOUNDS = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)


def out_of_bounds(sprite):
    return not sprite.rect.colliderect(SCREEN_BOUNDS)


def play():
    pygame.mixer.pre_init(frequency=44100)
    pygame.init()
    pygame.mixer.init(frequency=44100)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) #, pygame.FULLSCREEN)
    background = screen.copy()
    intro.play(screen)

    clock = pygame.time.Clock()

    tile_manager = tiles.TileManager()
    tile_manager.import_tiles("terrain.png", 8, 16)

    game_map = tiles.TileMap(tile_manager.tiles[7])
    world = interfaces.SpriteGroups()
    floorplan.create_objects(0, world, game_map)

    game_map.render(background, 0, 0,
                    SCREEN_WIDTH//game_map.tile_width,
                    SCREEN_HEIGHT//game_map.tile_height)
    screen.blit(background, (0, 0))

    player = create_player(world)
    create_health_bar(player, world)
    create_ammo_bar(player, world)

    make_monster(MonsterType.ZOMBIE_GENERATOR, 200, randint(0, screen.get_height()), world)
    make_monster(MonsterType.ZOMBIE_GENERATOR, 800, randint(0, screen.get_height()), world)


    while True:
        world.all.clear(screen, background)
        world.hud.clear(screen, background)
        world.all.update()
        world.hud.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                debug_filmstrips(screen, world.all)
                screen.blit(background, (0, 0))
        kb = pygame.key.get_pressed()
        player.handle_keyboard(kb)
        if kb[pygame.K_RETURN]:
            player.shoot()

        player.move(world.solid)
        for monster in world.monster:
            monster.notify(player)
            monster.move(world.solid)
            monster.do_actions(world)
        for missile in world.missile:
            missile.move(world.solid)
            if out_of_bounds(missile):
                missile.kill()
        missile_hits = pygame.sprite.groupcollide(world.solid, world.missile, False, False)
        for hit, missiles in missile_hits.items():
            for m in missiles:
                m.on_impact(hit, world)

        pick_ups = pygame.sprite.spritecollide(player, world.items, dokill=True, collided=pygame.sprite.collide_mask)
        for item in pick_ups:
            item.on_pick_up(player)

        world.all.draw(screen)
        world.hud.draw(screen)
        pygame.display.flip()
        clock.tick(20)


def create_player(world):
    player_character = Character(PlayerCharacterType.TOBY)
    player = Player(500, 500, player_character, world)
    move_to_nearest_empty_space(player, world, 100)
    world.all.add(player)
    world.solid.add(player)
    return player


def create_health_bar(player, world):
    heart = pygame.image.load(image_file("heart.png"))
    heart_filmstrip = SpriteSheet(heart, 1, 1).filmstrip(scale=0.1)
    throbbing_heart = sprite_effects.throbbing(heart_filmstrip[0])
    health_bar = ScoreBar(30, 30, throbbing_heart, 100, 10, frame_length=50)
    world.hud.add(health_bar)
    player.add_observer(health_bar, "vitality")


def create_ammo_bar(player, world):
    arrow = pygame.image.load(image_file("arrow24.png"))
    arrow_filmstrip = SpriteSheet(arrow, 1, 1).filmstrip(scale=1)
    ammo_bar = ScoreBar(SCREEN_WIDTH-100, 30, arrow_filmstrip, 5, 1, direction=Direction.RIGHT_TO_LEFT)
    world.hud.add(ammo_bar)
    player.add_observer(ammo_bar, "ammo")
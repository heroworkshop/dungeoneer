from random import randint

import pygame
from pygame.rect import Rect

from dungeoneer import sprite_effects
from dungeoneer import intro
from dungeoneer.actors import Player, make_monster_sprite, Monster
from dungeoneer.characters import Character, PlayerCharacterType, MonsterType
from dungeoneer.event_dispatcher import KeyEventDispatcher
from dungeoneer.events import WARNING_EVENT
from dungeoneer.fonts import make_font
from dungeoneer.game_assets import image_file
from dungeoneer.interfaces import Item
from dungeoneer.inventory_controller import InventoryController
from dungeoneer.inventory_view import InventoryView
from dungeoneer.item_sprites import make_item_sprite
from dungeoneer import items
from dungeoneer.messages import Messages
from dungeoneer.pathfinding import move_to_nearest_empty_space
from dungeoneer.realms import Realm
from dungeoneer.regions import Region
from dungeoneer.score_bar import ScoreBar
from dungeoneer.sound_effects import start_music
from dungeoneer.spritesheet import SpriteSheet

GENERATOR_EVENT = pygame.USEREVENT + 1

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

SCREEN_BOUNDS = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)


class GameInterrupt(RuntimeError):
    """Raised to signal game end"""


def out_of_bounds(sprite):
    return not sprite.rect.colliderect(SCREEN_BOUNDS)


class Camera:
    def __init__(self, display_surface, groups, position=(0, 0) ):
        super().__init__()
        self.display_surface = display_surface
        self.offset = pygame.math.Vector2(position)
        self.groups = list(groups)

    def draw_all(self):
        for group in self.groups:
            for sprite in group.sprites():
                offset_pos = sprite.rect.topleft + self.offset
                self.display_surface.blit(sprite.image, offset_pos)

    def move(self, by_vector):
        if by_vector:
            self.offset.update(self.offset + by_vector)


def play():
    pygame.mixer.pre_init(frequency=44100)
    pygame.init()
    pygame.mixer.init(frequency=44100)
    clock = pygame.time.Clock()
    screen_flags = pygame.DOUBLEBUF  # | pygame.FULLSCREEN
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), screen_flags)
    intro.play(screen)

    realm = Realm((10, 10), tile_size=(40, 40), region_size=(SCREEN_WIDTH // 40, SCREEN_HEIGHT // 40))
    realm.generate_map()
    region = realm.region((5, 5))
    world = region.groups
    background = realm.render_tiles()
    bg_offset = -5 * region.pixel_width, -5 * region.pixel_height

    x, y = bg_offset
    player = create_player(region, (-x + 500, -y + 500) )
    move_to_nearest_empty_space(player, [world.solid], 50)
    create_health_bar(player, world)
    static_sprites = pygame.sprite.Group()
    InventoryView(player.inventory, SCREEN_WIDTH - 80, 200, sprite_groups=[static_sprites])
    message_store = Messages()
    # MessagesView(message_store, Rect(SCREEN_WIDTH - 200, 0, 200, 50), screen)
    key_event_dispatcher = KeyEventDispatcher()
    key_event_dispatcher.register(InventoryController(player.inventory, player))

    add_demo_items(world, bg_offset)

    make_monster_sprite(MonsterType.ZOMBIE_GENERATOR, 200, randint(0, screen.get_height()), world)
    make_monster_sprite(MonsterType.ZOMBIE_GENERATOR, 800, randint(0, screen.get_height()), world)

    start_music("Dragon_and_Toast.mp3")

    # When the player moves, the rest of the world moves (blitted with an offset).
    # All the groups that need to move are included here
    scrolling_groups = (world.player, world.monster, world.missile, world.player_missile,
                        world.items)
    # Some things don't move but are still visible. They are included static_sprites

    camera = Camera(screen, scrolling_groups, position=bg_offset)

    while True:
        handle_events(key_event_dispatcher, player, message_store)
        move_vector = player.move([world.solid])
        if move_vector:
            world = realm.region_from_pixel_position(player.rect.center).groups
            camera.move(move_vector)

        monster: Monster
        for monster in world.monster:
            monster.target_enemy(player)
            monster.move((world.player, world.solid))
            monster.do_actions(world)
        check_bounds(world.missile)

        handle_missile_collisions(world)
        player.handle_item_pickup(world)

        # offset = camera.offset + bg_offset
        screen.blit(background, dest=camera.offset)
        camera.draw_all()

        static_sprites.update()
        static_sprites.draw(screen)
        display_debug(screen, (0, 0), clock, player, realm )
        pygame.display.flip()
        clock.tick(30)


def handle_missile_collisions(world):
    # The player is not in the solid group so enemy missiles
    # will need to do collision detection with the player group instead.
    # It is important that player missiles don't collide with the player.
    missile_hits = pygame.sprite.groupcollide(world.solid, world.player_missile, False, False)
    missile_hits.update(pygame.sprite.groupcollide(world.solid, world.missile, False, False))
    missile_hits.update(pygame.sprite.groupcollide(world.player, world.missile, False, False))
    for hit, missiles in missile_hits.items():
        for m in missiles:
            m.on_impact(hit, world)


def check_bounds(group):
    for missile in group:
        if out_of_bounds(missile):
            missile.kill()


def handle_events(key_event_dispatcher, player, message_store):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise GameInterrupt
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                raise GameInterrupt
            key_event_dispatcher.event(event.type, event.key)
        if event.type == WARNING_EVENT:
            message_store.send("warning", event.message)
    kb = pygame.key.get_pressed()
    player.handle_keyboard(kb)


def add_demo_items(world, position):
    x, y = position
    x, y = -x, -y
    arrows: Item = items.ammo["arrow"]
    arrows.count = 5
    arrow_sprite = make_item_sprite(arrows, x + 500, y + 450)
    if move_to_nearest_empty_space(arrow_sprite, [world.solid], 50):
        world.items.add(arrow_sprite)
        world.all.add(arrow_sprite)
    melon = make_item_sprite(items.food["melon"], x + 550, y + 500)
    if move_to_nearest_empty_space(melon, [world.solid], 50):
        world.items.add(melon)
        world.all.add(melon)

    x += 650
    y += 500
    for i, item in enumerate(items.all_items.values()):
        item_sprite = make_item_sprite(item, x + 32 * (i % 8), y + 32 * (i // 8))
        if move_to_nearest_empty_space(arrow_sprite, [world.solid], 50):
            world.items.add(item_sprite)
            world.all.add(item_sprite)


def create_player(region: Region, position) -> Player:
    player_character = Character(PlayerCharacterType.TOBY)
    x, y = position
    player = Player(x, y, player_character, region)
    move_to_nearest_empty_space(player, [region.groups.solid], 100)
    region.groups.all.add(player)
    region.groups.player.add(player)
    return player


def create_health_bar(player, world):
    heart = pygame.image.load(image_file("heart.png"))
    heart_filmstrip = SpriteSheet(heart, 1, 1).filmstrip(scale=0.1)
    throbbing_heart = sprite_effects.throbbing(heart_filmstrip[0])
    health_bar = ScoreBar(30, 30, throbbing_heart, 100, 10, frame_length=50)
    world.hud.add(health_bar)
    player.add_observer(health_bar, "vitality")


def display_debug(surface, position, clock, player, realm ):
    font = make_font("Times New Roman", 20)
    pygame.draw.rect(surface, (0, 0, 0), Rect(0, 0, 160, 160))
    x, y = position

    caption = font.render(str(int(clock.get_fps())), True, (255, 255, 255))
    surface.blit(caption, (x, y))

    caption = font.render(str(player.rect.center), True, (255, 255, 255))
    surface.blit(caption, (x + 32, y))

    y += 32
    caption = font.render(str(realm.region_coord_from_pixel_position(player.rect.center)), True, (255, 255, 255))
    surface.blit(caption, (x, y))

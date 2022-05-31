import threading
from random import randint

import pygame
from pygame.rect import Rect

from dungeoneer import intro
from dungeoneer import items
from dungeoneer import sprite_effects
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
    def __init__(self, display_surface, groups, position=(0, 0)):
        super().__init__()
        self.display_surface = display_surface
        self.offset = -1 * pygame.math.Vector2(position)
        self.groups = list(groups)

    def draw_all(self):
        for group in self.groups:
            for sprite in group.sprites():
                offset_pos = sprite.rect.topleft + self.offset
                self.display_surface.blit(sprite.image, offset_pos)

    def move(self, by_vector):
        if by_vector:
            self.offset.update(self.offset + by_vector)


class DungeoneerGame:
    def __init__(self, screen_size: tuple[int, int], tile_size=(40, 40), realm_size=(10, 10)):
        pygame.mixer.pre_init(frequency=44100)
        pygame.init()
        pygame.mixer.init(frequency=44100)
        self.clock = pygame.time.Clock()
        screen_flags = pygame.DOUBLEBUF  # | pygame.FULLSCREEN
        self.screen = pygame.display.set_mode(screen_size, screen_flags)
        self.region_size = screen_size[0] // tile_size[0], screen_size[1] // tile_size[1]
        self.realm = Realm(realm_size, tile_size, self.region_size)
        self.region = None
        self.background = None
        self.player = None
        self.camera = Camera(self.screen, [])
        self.key_event_dispatcher = KeyEventDispatcher()
        self.message_store = Messages()
        self.static_sprites = pygame.sprite.Group()
        self.fps = 40

    def initialise_realm(self):
        self.realm.generate_map()
        self.background = self.realm.render_tiles()

    def place_player(self, in_region):
        self.region = self.realm.region(in_region)
        x, y = in_region[0] * self.region.pixel_width, in_region[1] * self.region.pixel_height
        region_offset = (self.region.pixel_width // 2, self.region.pixel_height // 2)
        self.player = create_player(self.region, (x + region_offset[0], y + region_offset[1]))
        world = self.region.groups
        # When the player moves, the rest of the world moves (blitted with an offset).
        # All the groups that need to move are included here
        scrolling_groups = (world.player, world.monster, world.missile, world.player_missile,
                            world.items)
        # Some things don't move but are still visible. They are in included static_sprites
        self.camera = Camera(self.screen, scrolling_groups, position=(x, y))

        add_demo_items(self.region.groups, (x, y))
        make_monster_sprite(MonsterType.ZOMBIE_GENERATOR, x + 200, y + randint(0, self.screen.get_height()), world)
        make_monster_sprite(MonsterType.ZOMBIE_GENERATOR, x + 800, y + randint(0, self.screen.get_height()), world)

    def place_static_items(self):
        create_health_bar(self.player, self.region.groups)

        InventoryView(self.player.inventory, SCREEN_WIDTH - 80, 200, sprite_groups=[self.static_sprites])
        self.key_event_dispatcher.register(InventoryController(self.player.inventory, self.player))

    def game_loop(self):
        while True:
            handle_events(self.key_event_dispatcher, self.player, self.message_store)
            move_vector = self.player.move(self.realm)
            self.camera.move(move_vector)

            # Move actors in current region and neighbouring regions
            for region in self.realm.neighbouring_regions_from_pixel_position(self.player.rect.center):
                world = self.realm.region_from_pixel_position(self.player.rect.center).groups

                monster: Monster
                for monster in world.monster:
                    monster.target_enemy(self.player)
                    monster.move(self.realm)
                    monster.do_actions(world)
                check_bounds(world.missile)

                handle_missile_collisions(world)

            self.player.handle_item_pickup(world)

            self.screen.blit(self.background, dest=self.camera.offset)
            self.camera.draw_all()

            self.static_sprites.update()
            self.static_sprites.draw(self.screen)
            display_debug(self.screen, (0, 0), self.clock, self.player, self.realm)
            pygame.display.flip()
            self.clock.tick(self.fps)


def play():
    game = DungeoneerGame((SCREEN_WIDTH, SCREEN_HEIGHT))
    thread = threading.Thread(target=game.initialise_realm)
    thread.start()
    intro.play(game.screen)

    thread.join()
    game.place_player((5, 5))
    game.place_static_items()

    start_music("Dragon_and_Toast.mp3")

    game.game_loop()


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


def display_debug(surface, position, clock, player, realm):
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

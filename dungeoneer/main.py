import threading
from contextlib import suppress

import pygame
from pygame.rect import Rect

from dungeoneer import intro
from dungeoneer import items
from dungeoneer import screen
from dungeoneer import sprite_effects
from dungeoneer.actors import Player, Monster
from dungeoneer.camera import Camera
from dungeoneer.characters import Character, PlayerCharacterType
from dungeoneer.event_dispatcher import KeyEventDispatcher
from dungeoneer.events import WARNING_EVENT
from dungeoneer.fonts import make_font
from dungeoneer.game_assets import image_file, make_sprite_sheet
from dungeoneer.interfaces import Item
from dungeoneer.inventory_controller import InventoryController
from dungeoneer.inventory_view import InventoryView
from dungeoneer.item_sprites import make_item_sprite
from dungeoneer.messages import Messages
from dungeoneer.realms import Realm, handle_missile_collisions
from dungeoneer.regions import Region, NoFreeSpaceFound
from dungeoneer.score_bar import ScoreBar, NumericScoreBar
from dungeoneer.sound_effects import start_music
from dungeoneer.spritesheet import SpriteSheet

GENERATOR_EVENT = pygame.USEREVENT + 1


class GameInterrupt(RuntimeError):
    """Raised to signal game end"""


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
        self.camera = Camera(self.screen, self.realm)
        self.key_event_dispatcher = KeyEventDispatcher()
        self.message_store = Messages()
        self.static_sprites = pygame.sprite.Group()
        self.fps = 40

    def initialise_realm(self):
        self.realm.generate_map()
        self.background = self.realm.render_tiles()

    def place_player(self, in_region):
        self.region = self.realm.region(in_region)
        x, y = self.region.pixel_base
        region_offset = (self.region.pixel_width // 2, self.region.pixel_height // 2)
        self.player = create_player(self.realm, (x + region_offset[0], y + region_offset[1]))
        self.camera = Camera(self.screen, self.realm, position=(x, y))
        self.player.add_observer(self.realm, "move")
        # make_monster_sprite(MonsterType.ZOMBIE_GENERATOR, x + 200, y + randint(0, self.screen.get_height()), self.realm)
        # make_monster_sprite(MonsterType.ZOMBIE_GENERATOR, x + 800, y + randint(0, self.screen.get_height()), self.realm)

    def place_static_items(self):
        create_health_bar(self.player, self.static_sprites)
        create_gold_score(self.player, self.static_sprites)
        InventoryView(self.player.inventory, screen.WIDTH - 80, 200, sprite_groups=[self.static_sprites])
        self.key_event_dispatcher.register(InventoryController(self.player.inventory, self.player))

    def game_loop(self):
        while True:
            handle_events(self.key_event_dispatcher, self.player, self.message_store)
            move_vector = self.player.move()
            self.camera.move(move_vector)
            active_regions = self.realm.neighbouring_regions_from_pixel_position(self.player.rect.center)
            self.move_monsters(active_regions)

            world = self.realm.region_from_pixel_position(self.player.rect.center).groups
            self.realm.check_bounds(world.missile)
            self.realm.groups.player_missile.update()
            handle_missile_collisions(self.realm)
            self.realm.groups.effects.update()
            self.player.handle_item_pickup(world)

            self.screen.blit(self.background, dest=self.camera.offset)
            self.camera.draw_all(active_regions)

            pygame.draw.rect(self.screen, (0, 0, 0), Rect(0, 0, screen.WIDTH, 50))
            self.static_sprites.update()
            self.static_sprites.draw(self.screen)
            self.display_debug(self.screen, (0, 0))
            pygame.display.flip()
            self.clock.tick(self.fps)

    def move_monsters(self, active_regions):
        # Move monsters in current region and neighbouring regions
        for region in active_regions:
            world = region.groups

            monster: Monster
            for monster in world.monster:
                if monster.character.sleeping:
                    continue
                monster.target_enemy(self.player)
                monster.move()
                self.realm.update_monster_group(monster, region)
                monster.do_actions(self.realm)

    def display_debug(self, surface, position):
        line_spacing = 15
        font = make_font("Times New Roman", 15)
        pygame.draw.rect(surface, (0, 0, 0), Rect(0, 50, 160, 100))
        x, y = position

        region = self.realm.region_from_pixel_position(self.player.rect.center)
        caption = font.render(str(region.name), True, (255, 255, 255))
        surface.blit(caption, (x, y))

        y += line_spacing
        fps = int(self.clock.get_fps())
        fps_colour = (50, 255, 50) if fps > self.fps * 0.9 else (255, 50, 50)
        caption = font.render(str(fps), True, fps_colour)
        surface.blit(caption, (x, y))

        caption = font.render(str(self.player.rect.center), True, (255, 255, 255))
        surface.blit(caption, (x + 32, y))

        y += line_spacing
        caption = font.render(str(self.realm.region_coord_from_pixel_position(self.player.rect.center)), True,
                              (255, 255, 255))
        surface.blit(caption, (x, y))

        # neighbours = self.realm.neighbouring_regions_from_pixel_position(self.player.rect.center)
        #
        # for n in neighbours:
        #     y += line_spacing
        #     caption = font.render(str(n), True, (100, 100, 255))
        #     surface.blit(caption, (x, y))

        y += line_spacing
        caption = font.render(str(self.camera.visible_sprite_count), True, (100, 100, 255))
        surface.blit(caption, (x, y))


def play():
    game = DungeoneerGame((screen.WIDTH, screen.HEIGHT))
    thread = threading.Thread(target=game.initialise_realm)
    thread.start()
    intro.play(game.screen)

    thread.join()
    game.place_player((5, 5))
    arrows = items.ammo["arrow"]
    arrows.count = 20
    game.player.inventory.add_item(arrows, slot=2)
    add_demo_items(game.region, (10, 10))

    game.place_static_items()

    start_music("Dragon_and_Toast.mp3")

    game.game_loop()


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


def add_demo_items(region: Region, position):
    col, row = position
    arrows: Item = items.ammo["arrow"]
    arrows.count = 15
    with suppress(NoFreeSpaceFound):
        p = region.nearest_free_space(col, row, 20)
        x, y = region.pixel_position(p)
        arrow_sprite = make_item_sprite(arrows, x, y)
        region.groups.items.add(arrow_sprite)

    # for i, item in enumerate(items.all_items.values()):
    #     col, row = 10 + i % 8, 10 + i // 8
    #     try:
    #         p = region.nearest_free_space(col, row, 20)
    #     except NoFreeSpaceFound:
    #         print("Couldn't place demo item sprite")
    #         continue
    #     x, y = region.pixel_position(p)
    #     item_sprite = make_item_sprite(item, x, y)
    #     dx, dy = randint(-15, 15), randint(-15, 15)  # subtile variance in position
    #     item_sprite.rect.topleft = x + dx, y + dy
    #     region.groups.items.add(item_sprite)


def create_player(realm: Realm, pixel_position) -> Player:
    player_character = Character(PlayerCharacterType.TOBY)
    x, y = pixel_position
    region = realm.region_from_pixel_position(pixel_position)
    player = Player(x, y, player_character, realm)
    pos = region.coordinate_from_absolute_position(x, y)
    empty_space = region.nearest_free_space(*pos, 10)
    player.rect.center = region.pixel_position(empty_space, align="center")
    realm.groups.player.add(player)
    return player


def create_health_bar(player, group):
    heart = pygame.image.load(image_file("heart.png"))
    heart_filmstrip = SpriteSheet(heart, 1, 1).filmstrip(scale=0.1)
    throbbing_heart = sprite_effects.throbbing(heart_filmstrip[0])
    health_bar = ScoreBar(screen.WIDTH - 500, 20, throbbing_heart, 100, 10, frame_length=50)
    group.add(health_bar)
    player.add_observer(health_bar, "vitality")


def create_gold_score(player, group):
    gold_icon = make_sprite_sheet("gold pieces").filmstrip(scale=0.5)
    score_bar = NumericScoreBar(screen.WIDTH - 100, 20, gold_icon, 0, font_size=30)
    group.add(score_bar)
    player.add_observer(score_bar, "gold")
    score_bar.on_update("gold", Item("gold", count=player.gold))

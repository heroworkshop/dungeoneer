import unittest

import pygame
from assertpy import assert_that

from dungeoneer import actors
from dungeoneer.actors import Player
from dungeoneer.characters import MonsterType, Character, PlayerCharacterType
from dungeoneer.interfaces import SpriteGroups, Item
from dungeoneer.inventory import Inventory
from dungeoneer.realms import Realm
from dungeoneer.regions import Region


class TestZombie(unittest.TestCase):
    def setUp(self):
        self.realm = Realm(size=(10, 10), tile_size=(40, 40))

    def test_make_monster_withZombie(self):
        zombie = actors.make_monster_sprite(MonsterType.ZOMBIE, 0, 0, self.realm)
        self.assertEqual(3, len(zombie.filmstrips.walk_south))

    def test_monsters_have_unlimited_ammo(self):
        zombie = actors.make_monster_sprite(MonsterType.ZOMBIE, 0, 0, self.realm)
        ammo = zombie.ammo
        self.assertGreater(ammo, 0)
        zombie.expend_ammo()
        self.assertEqual(ammo, zombie.ammo)


class TestGenerator(unittest.TestCase):
    def setUp(self):
        self.realm = Realm(size=(10, 10), tile_size=(40, 40))
        self.groups = self.realm.region((0, 0)).groups
        player_character = Character(PlayerCharacterType.TOBY)
        self.player = Player(50, 50, player_character, self.realm)


    def test_generator_withOneGenerator_produceMonsters(self):
        generator = actors.make_monster_sprite(MonsterType.ZOMBIE_GENERATOR, 0, 0, self.realm)
        generator.targeted_enemy = self.player
        self.assertEqual(1, len(self.groups.solid))
        generator.do_actions(self.realm)
        self.assertEqual(2, len(self.groups.solid))

    def test_generator_withTwoGenerators_produceTwoMonsters(self):
        generators = [actors.make_monster_sprite(MonsterType.ZOMBIE_GENERATOR, 0, 0, self.realm),
                      actors.make_monster_sprite(MonsterType.ZOMBIE_GENERATOR, 100, 100, self.realm)]

        self.assertEqual(2, len(self.groups.solid))
        for g in generators:
            g.targeted_enemy = self.player
            g.do_actions(self.realm)
        self.assertEqual(4, len(self.groups.solid))

    def test_generator_withTime_producesMonstersAtRateOfFire(self):
        pygame.time.Clock()
        generators = [actors.make_monster_sprite(MonsterType.ZOMBIE_GENERATOR, 0, 0, self.realm),
                      actors.make_monster_sprite(MonsterType.ZOMBIE_GENERATOR, 100, 100, self.realm)]

        self.assertEqual(2, len(self.groups.solid))
        for g in generators:
            g.targeted_enemy = self.player
            g.actions[0].rate_of_fire = 10
            g.do_actions(self.realm)
        self.assertEqual(4, len(self.groups.solid))
        t = pygame.time.get_ticks()
        while True:
            for g in generators:
                g.do_actions(self.realm)
            if t + 150 < pygame.time.get_ticks():
                break
        self.assertEqual(6, len(self.groups.solid))


class TestPlayerMovement(unittest.TestCase):
    def setUp(self):
        self.realm = Realm((4, 4), tile_size=(50, 50), region_size=(20, 20))
        self.region = self.realm.region((0, 0))
        self.world = self.region.groups
        player_character = Character(PlayerCharacterType.TOBY)
        self.player = Player(500, 500, player_character, self.region)
        self.player.collide_ratio = 1

    def test_moveRight_withNoObstruction_movesSpeedPixels(self):
        self.player.direction.update(1, 0)
        self.player.move(self.realm)
        expected_x = 500 + self.player.speed
        self.assertEqual(expected_x, self.player.rect.centerx)
        self.assertEqual(500, self.player.rect.centery)

    def test_moveLeft_withNoObstruction_movesSpeedPixels(self):
        self.player.direction.update(-1, 0)
        self.player.move(self.realm)
        expected_x = 500 - self.player.speed
        self.assertEqual(expected_x, self.player.rect.centerx)
        self.assertEqual(500, self.player.rect.centery)

    def test_moveDiagonal_withNoObstruction_movesSpeedResolvedInXandYPixels(self):
        self.player.direction.update(1, -1)
        self.player.speed = 6
        self.player.move(self.realm)
        expected_x = int(500 + 4)  # 6sin(45) = 4.2
        expected_y = int(500 - 4)  # 6cos(45) = 4.2
        self.assertEqual(expected_x, self.player.rect.centerx)
        self.assertEqual(expected_y, self.player.rect.centery)

    def test_moveRight_withWallDirectlyRight_doesNotMove(self):
        block = pygame.sprite.Sprite()
        block.rect = pygame.Rect(self.player.rect.right, 450, 100, 100)
        self.world.solid.add(block)
        self.player.direction.update(1, 0)
        self.player.move(self.realm)
        self.assertEqual(500, self.player.rect.centerx)

    @unittest.skip("As an optimisation, we don't bother about these pixels")
    def test_moveRight_withWall2PixelsLeft_Moves2Pixels(self):
        block = pygame.sprite.Sprite()
        block.rect = pygame.Rect(self.player.rect.right + 2, 450, 100, 100)
        self.world.solid.add(block)
        self.player.direction.update(1, 0)
        self.player.move(self.realm)
        self.assertEqual(502, self.player.rect.centerx)

    def test_moveLeft_withDirectlyLeft_doesNotMove(self):
        block = pygame.sprite.Sprite()
        block.rect = pygame.Rect(self.player.rect.left - 100, 450, 100, 100)
        self.world.solid.add(block)
        self.player.direction.update(-1, 0)
        self.player.move(self.realm)
        self.assertEqual(500, self.player.rect.centerx)

    def test_moveDiagonalRight_withWallToRight_MovesAlongWall(self):
        block = pygame.sprite.Sprite()
        block.rect = pygame.Rect(self.player.rect.right, 450, 100, 100)
        self.world.solid.add(block)
        self.player.direction.update(1, -1)
        self.player.move(self.realm)
        self.assertEqual(500, self.player.rect.centerx)
        self.assertEqual(496, self.player.rect.centery)

    def test_moveDiagonalLeft_withWallToLeft_MovesAlongWall(self):
        block = pygame.sprite.Sprite()
        block.rect = pygame.Rect(self.player.rect.left - 100, 450, 100, 100)
        self.world.solid.add(block)
        self.player.direction.update(-1, -1)
        self.player.move(self.realm)
        assert_that(self.player.rect.center).is_equal_to((500, 496))


class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.realm = Realm(size=(10, 10), tile_size=(20, 20))
        player_character = Character(PlayerCharacterType.TOBY)
        self.player = Player(500, 500, player_character, self.realm)

    def test_player_ammo_depletes(self):
        self.player.inventory.add_item(Item("arrow"), slot=Inventory.AMMO)
        self.player.expend_ammo()
        self.assertEqual(0, self.player.ammo)

    def test_player_ammo_neverDropsBelowZero(self):
        self.player.expend_ammo()
        self.assertEqual(0, self.player.ammo)

    def test_drop_withItem_addsItemSpriteToWorld(self):
        item = Item("arrow")
        item_sprite = self.player.drop(item)
        self.assertEqual(1, len(self.player.region.groups.items))
        self.assertIn(item_sprite, self.player.region.groups.items)
        self.assertIn(item_sprite, self.player.region.groups.effects)

    def test_drop_withItem_addsItemSpriteToPlayerRecentlyDroppedItems(self):
        item = Item("arrow")
        item_sprite = self.player.drop(item)
        self.assertIn(item_sprite, self.player.recently_dropped_items)


if __name__ == '__main__':
    unittest.main()

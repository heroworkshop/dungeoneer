import unittest

import pygame

from dungeoneer.actors import Player
from dungeoneer.characters import MonsterType, Character, PlayerCharacterType
from dungeoneer.interfaces import SpriteGroups, Item
from dungeoneer import actors
from dungeoneer.inventory import Inventory
from dungeoneer.regions import Region


class TestZombie(unittest.TestCase):
    def test_make_monster_withZombie(self):
        world = SpriteGroups()
        zombie = actors.make_monster_sprite(MonsterType.ZOMBIE, 0, 0, world)
        self.assertEqual(3, len(zombie.filmstrips.walk_south))

    def test_monsters_have_unlimited_ammo(self):
        world = SpriteGroups()
        zombie = actors.make_monster_sprite(MonsterType.ZOMBIE, 0, 0, world)
        ammo = zombie.ammo
        self.assertGreater(ammo, 0)
        zombie.expend_ammo()
        self.assertEqual(ammo, zombie.ammo)


class TestGenerator(unittest.TestCase):
    def test_generator_withOneGenerator_produceMonsters(self):
        world = SpriteGroups()
        player_character = Character(PlayerCharacterType.TOBY)
        player = Player(500, 500, player_character, world)
        generator = actors.make_monster_sprite(MonsterType.ZOMBIE_GENERATOR, 0, 0, world)
        generator.targeted_enemy = player
        self.assertEqual(1, len(world.solid))
        generator.do_actions(world)
        self.assertEqual(2, len(world.solid))

    def test_generator_withTwoGenerators_produceTwoMonsters(self):
        world = SpriteGroups()
        self.assertEqual(0, len(world.solid))
        player_character = Character(PlayerCharacterType.TOBY)
        player = Player(500, 500, player_character, world)
        generators = [actors.make_monster_sprite(MonsterType.ZOMBIE_GENERATOR, 0, 0, world),
                      actors.make_monster_sprite(MonsterType.ZOMBIE_GENERATOR, 100, 100, world)]

        self.assertEqual(2, len(world.solid))
        for g in generators:
            g.targeted_enemy = player
            g.do_actions(world)
        self.assertEqual(4, len(world.solid))

    def test_generator_withTime_producesMonstersAtRateOfFire(self):
        pygame.time.Clock()
        world = SpriteGroups()
        player_character = Character(PlayerCharacterType.TOBY)
        player = Player(500, 500, player_character, world)
        generators = [actors.make_monster_sprite(MonsterType.ZOMBIE_GENERATOR, 0, 0, world),
                      actors.make_monster_sprite(MonsterType.ZOMBIE_GENERATOR, 100, 100, world)]

        self.assertEqual(2, len(world.solid))
        for g in generators:
            g.targeted_enemy = player
            g.actions[0].rate_of_fire = 10
            g.do_actions(world)
        self.assertEqual(4, len(world.solid))
        t = pygame.time.get_ticks()
        while True:
            for g in generators:
                g.do_actions(world)
            if t + 150 < pygame.time.get_ticks():
                break
        self.assertEqual(6, len(world.solid))


class TestPlayerMovement(unittest.TestCase):
    def setUp(self):
        self.world = SpriteGroups()
        player_character = Character(PlayerCharacterType.TOBY)
        self.player = Player(500, 500, player_character, self.world)
        self.player.collide_ratio = 1

    def test_moveRight_withNoObstruction_movesSpeedPixels(self):
        self.player.direction.update(1, 0)
        self.player.move([self.world.solid])
        expected_x = 500 + self.player.speed
        self.assertEqual(expected_x, self.player.rect.centerx)
        self.assertEqual(500, self.player.rect.centery)

    def test_moveLeft_withNoObstruction_movesSpeedPixels(self):
        self.player.direction.update(-1, 0)
        self.player.move([self.world.solid])
        expected_x = 500 - self.player.speed
        self.assertEqual(expected_x, self.player.rect.centerx)
        self.assertEqual(500, self.player.rect.centery)

    def test_moveDiagonal_withNoObstruction_movesSpeedResolvedInXandYPixels(self):
        self.player.direction.update(1, -1)
        self.player.speed = 6
        self.player.move([self.world.solid])
        expected_x = int(500 + 4)  # 6sin(45) = 4.2
        expected_y = int(500 - 4)  # 6cos(45) = 4.2
        self.assertEqual(expected_x, self.player.rect.centerx)
        self.assertEqual(expected_y, self.player.rect.centery)

    def test_moveRight_withWallDirectlyRight_doesNotMove(self):
        block = pygame.sprite.Sprite()
        block.rect = pygame.Rect(self.player.rect.right, 450, 100, 100)
        self.world.solid.add(block)
        self.player.direction.update(1, 0)
        self.player.move([self.world.solid])
        self.assertEqual(500, self.player.rect.centerx)

    @unittest.skip("As an optimisation, we don't bother about these pixels")
    def test_moveRight_withWall2PixelsLeft_Moves2Pixels(self):
        block = pygame.sprite.Sprite()
        block.rect = pygame.Rect(self.player.rect.right+2, 450, 100, 100)
        self.world.solid.add(block)
        self.player.direction.update(1, 0)
        self.player.move([self.world.solid])
        self.assertEqual(502, self.player.rect.centerx)

    def test_moveLeft_withDirectlyLeft_doesNotMove(self):
        block = pygame.sprite.Sprite()
        block.rect = pygame.Rect(self.player.rect.left - 100, 450, 100, 100)
        self.world.solid.add(block)
        self.player.direction.update(-1, 0)
        self.player.move([self.world.solid])
        self.assertEqual(500, self.player.rect.centerx)

    def test_moveDiagonalRight_withWallToRight_MovesAlongWall(self):
        block = pygame.sprite.Sprite()
        block.rect = pygame.Rect(self.player.rect.right, 450, 100, 100)
        self.world.solid.add(block)
        self.player.direction.update(1, -1)
        self.player.move([self.world.solid])
        self.assertEqual(500, self.player.rect.centerx)
        self.assertEqual(496, self.player.rect.centery)

    def test_moveDiagonalLeft_withWallToLeft_MovesAlongWall(self):
        block = pygame.sprite.Sprite()
        block.rect = pygame.Rect(self.player.rect.left - 100, 450, 100, 100)
        self.world.solid.add(block)
        self.player.direction.update(-1, -1)
        self.player.move([self.world.solid])
        self.assertEqual(500, self.player.rect.centerx)
        self.assertEqual(496, self.player.rect.centery)


class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.region = Region((20, 20))
        player_character = Character(PlayerCharacterType.TOBY)
        self.player = Player(500, 500, player_character, self.region)

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
        self.assertIn(item_sprite, self.player.region.groups.all)

    def test_drop_withItem_addsItemSpriteToPlayerRecentlyDroppedItems(self):
        item = Item("arrow")
        item_sprite = self.player.drop(item)
        self.assertIn(item_sprite, self.player.recently_dropped_items)


if __name__ == '__main__':
    unittest.main()

import unittest
from dungeoneer.characters import Character, MonsterType, PlayerCharacterType


class TestCharacter(unittest.TestCase):
    def test_character_withMonsterTemplate(self):
        zombie = Character(MonsterType.ZOMBIE)
        self.assertEqual(10, zombie.vitality)
        self.assertEqual(10, zombie.template.treasure)

    def test_character_withPlayerCharacterTemplate(self):
        player = Character(PlayerCharacterType.TOBY)
        self.assertEqual(150, player.vitality)
        self.assertEqual(1.5, player.rate_of_fire)


if __name__ == '__main__':
    unittest.main()

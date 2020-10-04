import unittest

from dungeoneer.realms import Realm
from dungeoneer.regions import Region


class TestRealm(unittest.TestCase):
    def test_Realm_withSize5by5_has25Regions(self):
        realm = Realm((5, 5))
        self.assertEqual(25, len(realm))
        self.assertIsInstance(realm.region((0, 0)), Region)
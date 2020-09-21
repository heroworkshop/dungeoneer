import unittest
import pygame

from dungeoneer.event_dispatcher import KeyEventDispatcher
from dungeoneer.interfaces import KeyObserver


class MyKeyObserver(KeyObserver):
    def __init__(self):
        self.key_down_history = []
        self.key_up_history = []

    def on_key_down(self, key):
        self.key_down_history.append(key)

    def on_key_up(self, key):
        self.key_up_history.append(key)

    def observes_keys(self):
        del self  # unusued
        return {pygame.K_3, pygame.K_4}


class TestKeyEventDispatcher(unittest.TestCase):
    def test_on_event_withKeyDownEvent_notifiesObservers(self):
        dispatcher = KeyEventDispatcher()
        observer = MyKeyObserver()
        dispatcher.register(observer, {pygame.K_1})
        dispatcher.event(pygame.KEYDOWN, pygame.K_1)
        self.assertEqual(observer.key_down_history, [pygame.K_1])

    def test_on_event_withKeyUpEvent_notifiesObservers(self):
        dispatcher = KeyEventDispatcher()
        observer = MyKeyObserver()
        dispatcher.register(observer, {pygame.K_1})
        dispatcher.event(pygame.KEYUP, pygame.K_1)
        self.assertEqual(observer.key_up_history, [pygame.K_1])

    def test_on_event_withKeyUpEvent_notifiesOnlyNotifiesObserversWhoRegisteredForThatKey(self):
        dispatcher = KeyEventDispatcher()
        observer = MyKeyObserver()
        dispatcher.register(observer, {pygame.K_2})
        dispatcher.event(pygame.KEYUP, pygame.K_1)
        self.assertEqual(observer.key_up_history, [])

    def test_on_event_withMultipleKeyDownEvents_notifiesObservers(self):
        dispatcher = KeyEventDispatcher()
        observer = MyKeyObserver()
        dispatcher.register(observer, {pygame.K_1, pygame.K_2})
        dispatcher.event(pygame.KEYDOWN, pygame.K_1)
        dispatcher.event(pygame.KEYDOWN, pygame.K_2)
        self.assertEqual(observer.key_down_history, [pygame.K_1, pygame.K_2])

    def test_on_event_withMultipleRegistrationsForSameKey_notifiesObserversOnlyOnce(self):
        dispatcher = KeyEventDispatcher()
        observer = MyKeyObserver()
        dispatcher.register(observer, [pygame.K_1, pygame.K_1])
        dispatcher.event(pygame.KEYDOWN, pygame.K_1)
        self.assertEqual(observer.key_down_history, [pygame.K_1])

    def test_on_event_withEmptyKeyList_usesObservesKeyMethod(self):
        dispatcher = KeyEventDispatcher()
        observer = MyKeyObserver()
        dispatcher.register(observer)
        dispatcher.event(pygame.KEYDOWN, pygame.K_3)
        self.assertEqual(observer.key_down_history, [pygame.K_3])


if __name__ == '__main__':
    unittest.main()

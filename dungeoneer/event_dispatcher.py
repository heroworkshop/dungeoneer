from collections import defaultdict
from typing import List, DefaultDict

import pygame


class KeyEventDispatcher:
    def __init__(self):
        # match an event id to a list of observers
        self.observers_by_key_id: DefaultDict[int, List] = defaultdict(list)

    def register(self, observer, key_ids: set = None):
        key_ids = key_ids or observer.observes_keys()
        for key_id in set(key_ids):
            self.observers_by_key_id[key_id].append(observer)

    def event(self, event_type, key_id):
        for observer in self.observers_by_key_id[key_id]:
            if event_type == pygame.KEYDOWN:
                observer.on_key_down(key_id)
            elif event_type == pygame.KEYUP:
                observer.on_key_up(key_id)

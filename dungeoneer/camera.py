import pygame
from pygame import Surface

from dungeoneer.realms import Realm


class Camera:
    def __init__(self, display_surface: Surface, realm: Realm, position=(0, 0)):
        super().__init__()
        self.display_surface = display_surface
        self.offset = -1 * pygame.math.Vector2(position)
        self.realm = realm
        self.visible_sprite_count = 0

    @staticmethod
    def draw_groups(groups):
        return (groups.player, groups.monster, groups.missile, groups.player_missile,
                groups.items, groups.effects)

    def draw_all(self, active_regions):
        """Draw all drawable groups in each nearby region plus in the realm's global group"""
        position = -1 * self.offset
        all_groups = [region.groups for region in active_regions]
        all_groups.append(self.realm.groups)
        self.visible_sprite_count = 0
        for groups in all_groups:
            for group in self.draw_groups(groups):
                for sprite in group.sprites():
                    offset_pos = sprite.rect.topleft + self.offset
                    self.display_surface.blit(sprite.image, offset_pos)
                    self.visible_sprite_count += 1

    def move(self, by_vector):
        if by_vector:
            self.offset.update(self.offset + by_vector)

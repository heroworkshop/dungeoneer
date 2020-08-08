from typing import List

import pygame


def throbbing(base_image: pygame.Surface) -> List[pygame.Surface]:
    """Take the base image and build a filmstrip with a 'throbbing' effect,
    like a heartbeat. The first few frames will just be the base image but then
    the image will shrink and then re-enlarge"""
    scale_factors = [1] * 15
    scale_factors.extend([.90, .80, .70, .80, .90, 1.00])
    return scaling_effect(base_image, scale_factors)


def scaling_effect(base_image, scale_factors):
    result = list()
    base_width, base_height = base_image.get_size()
    for scale in scale_factors:
        width, height = (int(x * scale) for x in (base_width, base_height))
        scaled = pygame.transform.smoothscale(base_image, (width, height))
        frame = pygame.Surface((base_width, base_height), flags=pygame.SRCALPHA)
        dx = (base_width - scaled.get_width()) // 2
        dy = (base_height - scaled.get_height()) // 2
        frame.blit(scaled, (dx, dy))
        result.append(frame)
    return result

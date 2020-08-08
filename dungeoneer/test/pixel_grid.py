import pygame


def make_pixel_grid(cols, rows):
    surface = pygame.Surface((cols, rows))
    colour = 0
    for y in range(rows):
        for x in range(cols):
            surface.set_at((x, y), (colour, 0, 0))
            colour += 1
    return surface
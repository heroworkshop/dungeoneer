import sys
from contextlib import suppress

import pygame


def debug_filmstrips(screen, actors):
    screen.fill((0, 0, 0))
    all_filmstrips = []
    print(f"found {len(actors)} actors")
    valid_actors = []
    for a in actors:
        with suppress(AttributeError):
            for filmstrip in a.filmstrips.__dict__.values():
                all_filmstrips.append(filmstrip)
            valid_actors.append(a)
    longest = max([len(f) for f in all_filmstrips])
    print(f"longest is {longest} frames")
    padding = 20
    scale = 2

    y = 50
    for actor in valid_actors:
        for name, filmstrip in actor.filmstrips.__dict__.items():
            print(f"Drawing {name} at {y}")
            x = 0
            max_height = 0
            for i, frame in enumerate(filmstrip):
                width = frame.get_width() * scale
                height = frame.get_height() * scale
                max_height = max(max_height, height)
                print(f"Scaling to ({width} x {height})")
                frame = pygame.transform.scale(frame, (width, height))
                print(f"Draw at ({x}, {y})")
                screen.blit(frame, (x, y))
                x += width + padding
            y += 20 + max_height
            pygame.draw.line(screen, (255, 255, 255), (0, y - 10), (screen.get_width(), y - 10))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

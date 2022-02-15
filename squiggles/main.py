import pygame

from dungeoneer import GameInterrupt
from squiggles.game_assets import make_sprite_sheet
from squiggles.squiggly import Throbber, Wobbler, Jaggedy, Squiggly

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

SCREEN_BOUNDS = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)


def background(surf, rect):
    color = 0, 0, 0
    surf.fill(color, rect)


def play():
    pygame.mixer.pre_init(frequency=44100)
    pygame.init()
    pygame.mixer.init(frequency=44100)
    clock = pygame.time.Clock()
    screen_flags = pygame.DOUBLEBUF  # | pygame.FULLSCREEN
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), screen_flags)

    devious = Wobbler(300, 300, make_filmstrip("devious"), velocity=(2, 0), amplitude=15)
    rage = Throbber(1200, 600, make_filmstrip("rage"), velocity=(-6, 0))
    psychopath = Jaggedy(150, 700, make_filmstrip("psychopath"), velocity=(2, -1), frequency=5)
    plagiarism = Squiggly(150, 150, make_filmstrip("plagiarism"), velocity=(2, 2))
    peachy = Throbber(500, 500, make_filmstrip("peachy"), velocity=(1, 0))
    visible_group = pygame.sprite.Group(devious, rage, psychopath, plagiarism, peachy)
    solid_group = pygame.sprite.Group(devious, rage, psychopath, peachy)

    while True:
        handle_events()
        visible_group.clear(screen, background)
        visible_group.update()
        spr: Squiggly
        for spr in visible_group:
            spr.move(solid_group, SCREEN_BOUNDS)
        visible_group.draw(screen)
        pygame.display.flip()
        clock.tick(30)


def make_filmstrip(name):
    filmstrip = make_sprite_sheet(name).filmstrip(scale=0.4)

    return filmstrip


def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise GameInterrupt
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                raise GameInterrupt


if __name__ == "__main__":
    try:
        play()
    except GameInterrupt:
        pass
    finally:
        pygame.quit()

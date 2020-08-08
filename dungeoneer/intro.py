import os
import pygame
import sys
from pygame.locals import *

from dungeoneer import fonts


def start_music():
    song = "The-Castle-Beyond-the-Forest.mp3"
    this_module = os.path.dirname(os.path.abspath(__file__))
    pygame.mixer.music.load(os.path.join(this_module, "music", song))
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play()


def play(screen):
    clock = pygame.time.Clock()
    start_music()
    x = 100
    y = screen.get_height() * 0.8
    caption = fonts.FadeInCaption("Dungeoneer", fonts.make_font("Times New Roman", 60), screen, (x, y), step=2)

    while caption.update():
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                return
        clock.tick(50)
        screen.fill((0, 0, 0))

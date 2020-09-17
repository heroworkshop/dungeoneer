import os
import pygame
import sys
from pygame.locals import *

from dungeoneer import fonts, interfaces, tiles
from dungeoneer.floorplan import create_objects


def start_music():
    song = "af.mp3"
    this_module = os.path.dirname(os.path.abspath(__file__))
    pygame.mixer.music.load(os.path.join(this_module, "music", song))
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play()


def play(screen):
    clock = pygame.time.Clock()
    start_music()
    world = plot_blocks(dungeoneer_pattern)

    while True:
        world.all.update()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                return
        clock.tick(50)
        world.all.draw(screen)


dungeoneer_pattern = """
        ###  # # #  #  ##  ###  ##  #  # ### ### ## 
        #  # # # ## # #    #   #  # ## # #   #   # #
        #  # # # # ## # ## ### #  # # ## ### ### ## 
        #  # # # #  # #  # #   #  # #  # #   #   # #
        ###  ### #  #  ### ###  ##  #  # ### ### #  #
"""


def plot_blocks(pattern):

    world = interfaces.SpriteGroups()
    create_objects([pattern], 0, world, (-150, 200))

    return world

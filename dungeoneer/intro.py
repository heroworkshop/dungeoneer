import sys

import pygame
from pygame.locals import *

from dungeoneer import interfaces
from dungeoneer.events import WARNING_EVENT
from dungeoneer.floorplan import create_objects
from dungeoneer.sound_effects import start_music


def play(screen):
    clock = pygame.time.Clock()
    start_music("af.mp3")
    world = plot_blocks(dungeoneer_pattern)

    while True:
        world.effects.update()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                return
            if event.type == WARNING_EVENT:
                print(event.message)
        clock.tick(50)
        world.effects.draw(screen)


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

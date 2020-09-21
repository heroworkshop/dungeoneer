#!/usr/bin/env python3
import pygame
from dungeoneer import play, GameInterrupt

try:
    play()
except GameInterrupt:
    pass
finally:
    pygame.quit()

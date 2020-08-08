#!/usr/bin/env python3
import pygame
from dungeoneer import play

try:
    play()
finally:
    pygame.quit()

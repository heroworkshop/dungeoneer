import pygame


def main():
    initialise(1000, 600)
    game_loop()


def game_loop():
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()

        clock.tick(60)


def initialise(width, height):
    pygame.init()
    pygame.display.set_mode((width, height))


if __name__ == "__main__":
    main()

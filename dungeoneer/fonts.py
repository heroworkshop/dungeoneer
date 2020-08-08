import pygame


def make_font(fonts, size):
    """Find a font matching one of the requested fonts. If none of the requested fonts are available then use the
    system font.
    Args:
        fonts (Iterable): names of fonts to look for in priority order
        size (int): point size of font to make
    Return:
        Pygame font object
    """
    available = pygame.font.get_fonts()
    # get_fonts() returns a list of lowercase spaceless font names 
    choices = map(lambda x: x.lower().replace(' ', ''), fonts)
    for choice in choices:
        if choice in available:
            return pygame.font.SysFont(choice, size)
    return pygame.font.Font(None, size)


class FadeInCaption:
    def __init__(self, caption, font, screen, position, peak_colour=(255, 255, 255), step=1):
        self.caption = caption
        self.screen = screen
        self.font = font
        self.position = position
        self.r, self.g, self.b = peak_colour
        self.step = 0
        self.direction = step

    def update(self):
        self.step += self.direction
        if self.step < 0:
            return False
        if self.step > 255:
            self.step = 255
            self.direction = -self.direction
        f = self.step / 255
        red, green, blue = [int(c * f) for c in (self.r, self.g, self.b)]
        caption = self.font.render(self.caption, True, (red, green, blue))
        self.screen.blit(caption, self.position)
        return True

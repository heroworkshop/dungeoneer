from dataclasses import dataclass
from typing import NamedTuple

import pygame

from dungeoneer.fonts import make_font
from dungeoneer.interfaces import Observer, Observable


class Message(NamedTuple):
    type: str
    text: str


class Messages(Observable):
    def __init__(self):
        super().__init__()
        self.types = ("warning", "information", "noises")
        self.messages = list()

    def send(self, message_type: str, text: str):
        self.messages.append(Message(message_type, text))
        self.notify_observers(message_type)

    def attribute(self, attribute_id):
        return [message for message in self.messages if attribute_id == message.type]


@dataclass
class Margin:
    top: int
    right: int
    bottom: int
    left: int


class MessagesView(Observer):
    """Shows messages in a scrollable window"""

    def __init__(self, messages, rect: pygame.rect, screen):
        self.messages = messages
        self.screen = screen
        self.rect = rect or pygame.Rect(50, 50, 400, 200)
        self.surface = pygame.Surface((self.rect.width, self.rect.height))
        self.background = (0, 0, 0)
        self.border = (255, 255, 0)
        self.border_width = 5
        self.margin = Margin(10, 10, 10, 10)
        self._font_size = 14
        self.font = make_font("Times New Roman", self._font_size)
        self.text_colour = (180, 180, 180)
        self.line_spacing = 0.1
        for t in messages.types:
            messages.add_observer(self, t)

    def on_update(self, attribute, value):
        self.draw(self.screen)

    def draw(self, screen):

        self.surface.fill(self.background)

        if self.messages.messages:
            x = self.rect.x + self.border_width + self.margin.left
            y = self.rect.top + self.border_width + self.margin.top
            text = self.messages.messages[-1].text
            caption = self.font.render(text, True, self.text_colour, self.background)
            self.surface.blit(caption, (x, y))

        pygame.draw.rect(self.surface,
                         rect=pygame.Rect(0, 0, self.rect.width, self.rect.height),
                         color=self.border, width=2)
        screen.blit(self.surface, self.rect)

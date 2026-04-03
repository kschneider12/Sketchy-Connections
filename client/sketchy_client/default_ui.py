"""
Stores all types of generic UI, such as images and the player display
"""
import pygame

from .paths import resolve_asset_path
from .paths import asset_path

class DefaultUI:
    """The parent and building block for UI- stores positioning and
    can draw to the screen appropriately"""
    def __init__(self, position, size, img, z = 0):
        self.z = z
        self.init_y = position[1]
        self.pos = position
        self.width = size[0]
        self.height = size[1]
        if img:
            self.img = pygame.image.load(resolve_asset_path(img))
            self.img = pygame.transform.scale(self.img, size)

    def draw(self, screen, curr_color = None):
        """draws the ui on the screen"""
        screen.blit(self.img, (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2))

class MouseStick(DefaultUI):
    """Extending DefaultUI, this UI moves on the mouse for drawing, such as paint bucket
    or paintbrush"""
    def __init__(self, size, img):
        self.visible = False
        DefaultUI.__init__(self, [0,0], size, img, 3)

    def behave(self, mouse_pos):
        """Moves the position on top of the mouse"""
        if self.visible:
            self.pos = [mouse_pos[0], mouse_pos[1]]

class TransparentUI(DefaultUI):
    """Extending DefaultUI, this UI is a semitransparent background. Used as an
    overlay for settings or options"""
    def __init__(self, position, size, color, transparency, z = 0):
        self.color = color
        DefaultUI.__init__(self, position, size, None, z)
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA) # pylint: disable=no-member
        self.surface.fill((color[0], color[1], color[2], transparency))

    def draw(self, screen, curr_color=None):
        """draws the ui on the screen"""
        screen.blit(self.surface, (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2))

class TextUI(DefaultUI):
    """Extending DefaultUI, this UI is plain text on the background."""
    def __init__(self, position, size, text, color, z = 0):
        self.text = text
        self.font = pygame.font.Font(asset_path("fonts", "MoreSugar-Regular.ttf"), int(size[1]))
        self.color = color
        DefaultUI.__init__(self, position, size, None, z)

    def draw(self, screen, curr_color=None):
        """Overrides DefaultUI.draw, and creates the text surface before drawing."""
        text_surface = self.font.render(self.text, True, self.color)
        screen.blit(text_surface, (self.pos[0] - self.font.size(self.text)[0] / 2,
                                   self.pos[1] - self.height / 2))

class PlayerDisplay(DefaultUI):
    """Extending DefaultUI, this UI is specifically for the player listing in the lobby.
    This is its own UI due to the unique behavior of added players, as well
    as light and name alignment"""
    def __init__(self, pos, size, screen_size, active_players):
        DefaultUI.__init__(self, pos, size, "assets/textures/players_tab.png")
        self.screen_size = screen_size
        self.light = pygame.image.load(resolve_asset_path("assets/textures/player_light.png"))
        self.light = pygame.transform.scale(self.light, (size[0] * 0.7,size[0] * 0.7))
        self.active_players = active_players
        self.font = pygame.font.Font(asset_path("fonts", "MoreSugar-Regular.ttf"),
                                     int(size[0] * 0.7))

    def set_active_players(self, active_players):
        """sets the local active players to the players in the lobby"""
        self.active_players = active_players

    def draw(self, screen, curr_color=None):
        """Overrides DefaultUI.draw, showing not only the graphics
        but text too, in the appropriate position."""
        screen.blit(self.img, (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2))
        for i, name in enumerate(self.active_players):
            screen.blit(self.light,
                        (self.pos[0] - self.width / 2.5,
                         self.pos[1] - (self.height / 2) +
                         self.ns(0,26)[1] + i * self.ns(0,69.8)[1]))
            text_surface = self.font.render(name.name, True, (0,0,0))
            screen.blit(text_surface,
                        (self.pos[0] + self.width / 2,
                         self.pos[1] - (self.height / 2) +
                         self.ns(0,26)[1] + i * self.ns(0,69.8)[1]))

    def ns(self, x, y):
        """clone of ns in Engine, to be accessed here for scale normalization."""
        return x * self.screen_size[0] / 1000, y * self.screen_size[1] / 1000 * 16/10

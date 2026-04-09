"""
Stores all types of generic UI, such as images and the player display
"""
import pygame
from pygame.mixer import Sound

from .sound_manager import SoundManager
from .paths import resolve_asset_path
from .paths import asset_path

class DefaultUI:
    """The parent and building block for UI- stores positioning and
    can draw to the screen appropriately"""
    def __init__(self, position, size, img, z = 0, draggable = False, rotate=0):
        self.z = z
        self.draggable = draggable
        self.init_y = position[1]
        self.pos = [position[0], position[1]]
        self.width = size[0]
        self.height = size[1]
        if img:
            self.img = pygame.image.load(resolve_asset_path(img))
            self.img = pygame.transform.scale(self.img, size)
            self.img = pygame.transform.rotate(self.img, rotate)

    def draw(self, screen, curr_color = None):
        """draws the ui on the screen"""
        screen.blit(self.img, (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2))

class MouseStick(DefaultUI):
    """Extending DefaultUI, this UI moves on the mouse for drawing, such as paint bucket
    or paintbrush"""
    def __init__(self, size):
        self.state = "brush"
        DefaultUI.__init__(self, [0,0], size, resolve_asset_path("assets/textures/pen_mouse.png"), 100)
        self.offset = -1 * self.width / 2, self.height / 2

    def behave(self, mouse_pos, pen_state):
        """Moves the position on top of the mouse"""
        if self.state != pen_state:
            match pen_state:
                case "brush":
                    self.img = pygame.image.load(resolve_asset_path("assets/textures/pen_mouse.png"))
                    self.img = pygame.transform.scale(self.img, (self.width,self.height))
                    self.offset = -1 * self.width / 2, self.height / 2
                    self.state = "brush"
                case "eraser":
                    self.img = pygame.image.load(resolve_asset_path("assets/textures/eraser_mouse.png"))
                    self.img = pygame.transform.scale(self.img, (self.width, self.height))
                    self.offset = 0, 0
                    self.state = "eraser"
                case "fill":
                    self.img = pygame.image.load(resolve_asset_path("assets/textures/fill_mouse.png"))
                    self.img = pygame.transform.scale(self.img, (self.width, self.height))
                    self.offset = self.width / 3, 0
                    self.state = "fill"
        self.pos = [mouse_pos[0] - self.offset[0], mouse_pos[1] - self.offset[1]]

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
    def __init__(self, position, size, text, color, z = 0,
                 draggable = False, animate=False, dynamic_size = 0,
                 wrapping = 0):
        self.text = text
        self.font = pygame.font.Font(asset_path("fonts", "MoreSugar-Regular.ttf"), int(size[1]))
        self.color = color
        self.wrapping = wrapping
        self.animate = (not animate) * len(self.text)
        self.dynamic_size = dynamic_size
        DefaultUI.__init__(self, position, size, None, z, draggable=draggable)

    def draw(self, screen, curr_color=None):
        """Overrides DefaultUI.draw, and creates the text surface before drawing."""
        if self.animate != len(self.text):
            txt = self.text[:self.animate]
            self.animate += 1
        else:
            txt = self.text

        text_surface = self.font.render(txt, True, self.color)
        if self.dynamic_size != 0:
            #need to resize to size of screen!
            while text_surface.get_width() > self.dynamic_size:
                self.height -= 1
                self.font = pygame.font.Font(asset_path("fonts", "MoreSugar-Regular.ttf"), int(self.height))
                text_surface = self.font.render(txt, True, self.color)
                if self.height == 0:
                    break
        if self.wrapping:
            if text_surface.get_width() > self.wrapping:
                texts = self.wrap_text(txt)
                screen.blit(texts[0], (self.pos[0],
                                  self.pos[1] - self.height * 1.2))
                screen.blit(texts[1], (self.pos[0],
                                  self.pos[1]))

            else:
                screen.blit(text_surface, (self.pos[0],
                                       self.pos[1]))
        else:
            screen.blit(text_surface, (self.pos[0] - self.font.size(self.text)[0] / 2,
                                        self.pos[1] - self.height / 2))

    def wrap_text(self, text):
        words = text.split()
        text_surface = self.font.render(text, True, self.color)
        can_split = True
        count = len(words)
        #print(f'WORDS: {words}')
        new_string = ""
        while text_surface.get_width() > self.wrapping:
            new_string = ""
            for word in words[:count]:
                new_string += word + " "
            text_surface = self.font.render(new_string, True, self.color)
            #print(text_surface.get_width() > self.wrapping)
            #print(text_surface.get_width())
            #print(self.wrapping)
            count -= 1
            if count == 0:
                can_split = False
                #print("Can't split the text")
                break
        if can_split:
            #print("SUCCESSFUL SPLIT!")
            second_string = ""
            for word in words[count + 1:]:
                second_string += word + " "
            return [text_surface, self.font.render(second_string, True, self.color)]
        return [self.font.render(text[:17] + "-", True, self.color),
                self.font.render(text[17:], True, self.color)]

class PlayerDisplay(DefaultUI):
    """Extending DefaultUI, this UI is specifically for the player listing in the lobby.
    This is its own UI due to the unique behavior of added players, as well
    as light and name alignment"""
    def __init__(self, pos, size, screen_size, active_players, abbrev = False):
        DefaultUI.__init__(self, pos, size, "assets/textures/players_tab.png")
        self.screen_size = screen_size
        self.light = pygame.image.load(resolve_asset_path("assets/textures/player_light.png"))
        self.light = pygame.transform.scale(self.light, (size[0] * 0.7,size[0] * 0.7))
        self.blue_light = pygame.image.load(resolve_asset_path("assets/textures/player_light_blue.png"))
        self.blue_light = pygame.transform.scale(self.blue_light, (size[0] * 0.7, size[0] * 0.7))
        self.active_players = active_players
        self.abbrev = abbrev
        self.font = pygame.font.Font(asset_path("fonts", "MoreSugar-Regular.ttf"),
                                     int(size[0] * 0.7))
        self.blue_player = None

    def set_active_players(self, active_players):
        """sets the local active players to the players in the lobby"""
        if self.active_players != active_players:
            SoundManager.get_instance().play_sfx(resolve_asset_path("assets/audio/plop.mp3"))
        self.active_players = active_players

    def make_blue(self, player):
        self.blue_player = player

    def draw(self, screen, curr_color=None):
        """Overrides DefaultUI.draw, showing not only the graphics
        but text too, in the appropriate position."""
        screen.blit(self.img, (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2))
        for i, name2 in enumerate(self.active_players):
            name = name2.name
            if self.abbrev:
                name = name[:3].upper()
            if self.blue_player == name2.id:
                screen.blit(self.blue_light,
                            (self.pos[0] - self.width / 2.5,
                             self.pos[1] - (self.height / 2) +
                             self.ns(0, 26)[1] + i * self.ns(0, 69.8)[1]))
            else:
                screen.blit(self.light,
                            (self.pos[0] - self.width / 2.5,
                             self.pos[1] - (self.height / 2) +
                             self.ns(0,26)[1] + i * self.ns(0,69.8)[1]))

            text_surface = self.font.render(name, True, (0,0,0))
            screen.blit(text_surface,
                        (self.pos[0] + self.width / 2,
                         self.pos[1] - (self.height / 2) +
                         self.ns(0,26)[1] + i * self.ns(0,69.8)[1]))

    def ns(self, x, y):
        """clone of ns in Engine, to be accessed here for scale normalization."""
        return x * self.screen_size[0] / 1000, y * self.screen_size[1] / 1000 * 16/10

"""
ColorButton is a child of Button which is for simple color selection
by the user while drawing
"""
import pygame

from .button import Button
from .paths import resolve_asset_path

COLORS = {
    'background': (240, 240, 240),
    'black' : (0, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'purple': (128, 0, 128),
    'red': (255, 0, 0),
    'orange': (255, 128, 0),
    'yellow': (255, 255, 0),
    'grey': (128, 128, 128),
    'sky_blue': (135, 206, 235),
    'brown': (139, 69, 19),
    'white': (255, 255, 255),
    'eraser': (240, 240, 240)
}

class ColorButton(Button):
    """
    Initializes ColorButton, storing the color as well
    """
    def __init__(self,  position, size, funct, color):
        self.color = COLORS[color]
        img = 'assets/textures/color_button.png'
        super().__init__(position, size, img, funct)
        self.img_select = pygame.image.load(
            resolve_asset_path('assets/textures/color_button_select.png'))
        self.img_select = pygame.transform.scale(self.img_select, size[:2])

    def behave(self, mouse_pos, just_clicked, keystrokes, mouse_state, paused):
        """
        Overrides Button.behave, overriding the return to include button color
        """
        if not paused or self.pause_override:
            if self.hovering(mouse_pos):
                self.curr_hover = True
            else:
                self.curr_hover = False
            if self.clicked(mouse_pos, just_clicked):
                return [self.command, self.color]
        return False

    def draw(self, screen, curr_color):
        """Overrides Button.draw, including the
        selection and color behavior"""
        #extra data is colorID
        if self.curr_hover:
            image = self.hover_img
        else:
            image = self.img
        if curr_color == self.color:
            image = self.img_select
        pygame.draw.rect(screen, self.color,
                         pygame.Rect(self.pos[0] - self.width / 2,
                                     self.pos[1] - self.height / 2,
                                     self.width, self.height))
        screen.blit(image, (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2))

    def resize(self, wid, ht):
        """Overrides Button.resize, including the
        selection and color behavior"""
        super().resize(wid, ht)
        self.img_select = pygame.image.load(
            resolve_asset_path('assets/textures/color_button_select.png'))
        self.img_select = pygame.transform.scale(self.img_select, (self.width, self.height))


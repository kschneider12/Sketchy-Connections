"""
PenTypeButton is a child of button, and is a selectable
thickness or fill tool. Same behavior but unique draw function.
"""
import pygame
from .paths import resolve_asset_path
from .button import Button

class PenTypeButton(Button):
    """This returns the type of pen the user uses, and is its own
    class due to its behavior and communication with other buttons"""
    def __init__(self, position, size, img, funct, selection):
        super().__init__(position,size,img,funct)
        self.selection = selection
        self.curr_selection = 1
        self.select_path = resolve_asset_path(img[:-4] + "_select.png")
        self.select_img = pygame.image.load(self.select_path)
        self.select_img = pygame.transform.scale(self.select_img, size[:2])

    def draw(self, screen, curr_color):
        """
        draw is how buttons are drawn on screen, depending on multiple textures or not.
        """
        if self.curr_hover:
            image = self.hover_img
        else:
            image = self.img
        if self.curr_selection == self.selection:
            image = self.select_img
        screen.blit(image, (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2))

    def set_selection(self, selection):
        """
        sets the current selection to the selection on screen
        """
        self.curr_selection = selection

    def resize(self, wid, ht):
        super().resize(wid, ht)
        self.select_img = pygame.image.load(self.select_path)
        self.select_img = pygame.transform.scale(self.select_img, (self.width, self.height))

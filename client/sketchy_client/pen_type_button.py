"""
PenTypeButton is a child of button, and is a selectable
thickness or fill tool. Same behavior but unique draw function.
"""
import pygame
from .paths import resolve_asset_path
from sketchy_client.button import Button


class PenTypeButton(Button):
    def __init__(self, position, size, img, funct, selection):
        super().__init__(position,size,img,funct)
        self.selection = selection
        self.curr_selection = 1
        select_path = resolve_asset_path(img[:-4] + "_select.png")
        self.select_img = pygame.image.load(select_path)
        self.select_img = pygame.transform.scale(self.select_img, size)
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

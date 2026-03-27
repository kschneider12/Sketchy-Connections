from .Button import Button
from .DefaultUI import DefaultUI
import pygame

class BrightnessSlider(Button):
    def __init__(self,  position, size, funct):
        self.selected = False
        self.min = 0
        self.rel_pos = [position[0], position[1] - size[1] / 2]
        self.max = 1
        self.bkg_size = size
        self.dragging = False
        self.accum = 0
        img = 'assets/textures/brightness_bar.png'
        self.bkg = DefaultUI(position, size, 'assets/textures/brightness_box.png')
        self.bkg2 = DefaultUI(position, size, 'assets/textures/brightness_overlay.png')
        super().__init__(position, (0.44 * size[0] * 2.5, 0.09 * size[0] * 2.5), img, funct)
        self.bounds = [self.pos[1] + self.bkg_size[1] / 2 - self.height / 2,
                       self.pos[1] - self.bkg_size[1] / 2 + self.height / 2]

    def behave(self, mouse_pos, just_clicked, keystrokes, mouse_status):
        if self.hovering_bar(mouse_pos):
            self.curr_hover = True
        else:
            self.curr_hover = False
        if self.hovering(mouse_pos) and just_clicked[0]:
            # convert mouse pos to 0-1 for position
            self.dragging = True
        if self.dragging:
            self.rel_pos[1] = mouse_pos[1]
        if mouse_status[0] == 0 and self.dragging:
            self.dragging = False
        if self.rel_pos[1] > self.bounds[0]:
           self.rel_pos[1] = self.bounds[0]
        if self.rel_pos[1] < self.bounds[1]:
           self.rel_pos[1] = self.bounds[1]
        return [self.command, 1 - ((self.max - (self.rel_pos[1] - self.bounds[1]) * (self.max - self.min) / (
                    self.bounds[1] - self.bounds[0])) - 1)]

    def draw(self, screen, curr_color):
        pygame.draw.rect(screen, curr_color, pygame.Rect(self.pos[0] - self.bkg_size[0] / 2, self.pos[1] - self.bkg_size[1] / 2, self.bkg_size[0], self.bkg_size[1]))
        self.bkg.draw(screen)
        self.bkg2.draw(screen)
        if self.curr_hover or self.dragging:
            image = self.hover_img
        else:
            image = self.img
        screen.blit(image, (self.rel_pos[0] - self.width / 2, self.rel_pos[1] - self.height / 2))
        #screen.blit(image, (self.rel_pos[0], self.rel_pos[1]))


    def hovering_bar(self, mouse_pos):
        return abs(mouse_pos[0] - self.rel_pos[0]) <= self.width / 2 and abs(mouse_pos[1] - self.rel_pos[1]) <= self.height / 2

    def hovering(self, mouse_pos):
        return abs(mouse_pos[0] - self.pos[0]) <= self.bkg_size[0] / 2 and abs(mouse_pos[1] - self.pos[1]) <= self.bkg_size[1] / 2

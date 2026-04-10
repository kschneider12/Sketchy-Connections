"""
BrightnessSlider is a type of button that is used for precise
color selection, as it changes the brightness of a preexisting
RGB value.
"""

import pygame
from .button import Button
from .default_ui import DefaultUI
from .paths import resolve_asset_path


class BrightnessSlider(Button):
    """BrightnessSlider initializer, storing the min and max values and unique
    elements to BrightnessSlider that Button does not have."""
    def __init__(self,  position, size, funct):
        self.selected = False
        self.min = 0
        self.rel_pos = [position[0], position[1] - size[1] / 2]
        self.max = 1
        self.bkg_size = size
        self.dragging = False
        self.accum = 0
        img = 'assets/textures/brightness_bar.png'
        self.bkg = DefaultUI(position, size, resolve_asset_path
        ('assets/textures/brightness_box.png'))
        self.bkg2 = DefaultUI(position, size, resolve_asset_path
        ('assets/textures/brightness_overlay.png'))
        super().__init__(position, (0.44 * size[0] * 2.5,
                                    0.035 * size[1] * 2.5, size[2]), img, funct)
        self.bounds = [self.pos[1] + self.bkg_size[1] / 2 - self.height / 2,
                       self.pos[1] - self.bkg_size[1] / 2 + self.height / 2]

    def behave(self, mouse_pos, just_clicked, keystrokes, mouse_state, paused):
        """Override of button behave function. Manages sliding bar and alternate return type"""
        if not paused or self.pause_override:
            if self.hovering_bar(mouse_pos):
                self.curr_hover = True
            else:
                self.curr_hover = False
            if self.hovering(mouse_pos) and just_clicked[0]:
                # convert mouse pos to 0-1 for position
                self.dragging = True
            if self.dragging:
                self.rel_pos[1] = mouse_pos[1]
            if mouse_state[0] == 0 and self.dragging:
                self.dragging = False
            if self.rel_pos[1] > self.bounds[0]:
                self.rel_pos[1] = self.bounds[0]
            if self.rel_pos[1] < self.bounds[1]:
                self.rel_pos[1] = self.bounds[1]
        return [self.command, 1 - ((self.max - (self.rel_pos[1] - self.bounds[1])
                                    * (self.max - self.min) / (
                    self.bounds[1] - self.bounds[0])) - 1)]

    def draw(self, screen, curr_color):
        """Overrides the draw function, including the bar and its positioning"""
        pygame.draw.rect(screen, curr_color,
                         pygame.Rect(self.pos[0] - self.bkg_size[0] / 2,
                                     self.pos[1] - self.bkg_size[1] / 2,
                                     self.bkg_size[0], self.bkg_size[1]))
        self.bkg.draw(screen)
        self.bkg2.draw(screen)
        if self.curr_hover or self.dragging:
            image = self.hover_img
        else:
            image = self.img
        screen.blit(image, (self.rel_pos[0] - self.width / 2,
                            self.rel_pos[1] - self.height / 2))
        #screen.blit(image, (self.rel_pos[0], self.rel_pos[1]))


    def hovering_bar(self, mouse_pos):
        """Returns if the mouse is hovering over the bar"""
        return (abs(mouse_pos[0] - self.rel_pos[0]) <= self.width / 2
                and abs(mouse_pos[1] - self.rel_pos[1]) <= self.height / 2)

    def hovering(self, mouse_pos):
        """Returns if the mouse is only hovering over the ball"""
        return (abs(mouse_pos[0] - self.pos[0]) <= self.bkg_size[0] / 2
                and abs(mouse_pos[1] - self.pos[1]) <= self.bkg_size[1] / 2)

    def resize(self, wid, ht):
        """resizes the brightness slider to the correct scale"""

        #between 0 and 1
        value = ((self.max - (self.rel_pos[1] - self.bounds[1])
              * (self.max - self.min) / (
                      self.bounds[1] - self.bounds[0])) - 1)

        self.pos = [int(self.init_pos[0] * wid / 100),
                    int(self.init_pos[1] * ht / 100)]

        self.width, self.height = (self.init_size[0] * wid / 1000,
                                   self.init_size[1] * ht / 1000 * 16 / 10)
        self.width *= 0.44 * 2.5
        self.height *= 0.035 * 2.5

        self.init_y = self.pos[1]
        hover_path = resolve_asset_path(self.img_path[:-4] + "_hover.png")
        self.hover_img = pygame.image.load(hover_path)
        self.hover_img = pygame.transform.scale(self.hover_img, (self.width, self.height))
        image_path = resolve_asset_path(self.img_path)
        self.img = pygame.image.load(image_path)
        self.img = pygame.transform.scale(self.img, (self.width, self.height))

        self.bkg.resize(wid, ht)
        self.bkg2.resize(wid, ht)
        self.bkg_size = self.bkg.width, self.bkg.height
        self.bounds = [self.pos[1] + self.bkg_size[1] / 2 - self.height / 2,
                       self.pos[1] - self.bkg_size[1] / 2 + self.height / 2]
        self.rel_pos[0] = self.pos[0]

        self.rel_pos[1] = self.bkg.pos[1] - self.bkg_size[1] / 2 + (self.bkg_size[1] * value)

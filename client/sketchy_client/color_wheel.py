"""
ColorWheel is a type of Button, which enables nearly any RGB value to be selected.
This is for complex colors, which enables any color during the drawing phase.
"""
import math
import pygame

from .button import Button
from .default_ui import DefaultUI

class ColorWheel(Button):
    """
    Initializes the ColorWheel class, storing the current color, positioning of
    the ball, and the textures.
    """
    def __init__(self,  position, size, funct):
        self.rel_pos = [position[0], position[1]]
        self.bkg_size = size
        self.dragging = False
        self.color = [255,255,255]
        img = 'assets/textures/slider_ball.png'
        self.bkg2 = DefaultUI(position, size, 'assets/textures/colorwheel_bkg.png')
        super().__init__(position, (size[0] / 20, size[1] / 20), img, funct)

    def behave(self, mouse_pos, just_clicked, keystrokes, mouse_state):
        """
        Overrides Button.behave, moving the ball around based on mouse position and
        calculating the color at that position, returning it.
        """
        self.curr_hover = self.hovering(mouse_pos)
        if self.get_rad(mouse_pos) <= self.bkg_size[0] / 2 and just_clicked[0]:
            self.dragging = True
        if self.dragging:
            self.rel_pos = [mouse_pos[0], mouse_pos[1]]
        if self.get_rad(self.rel_pos) > self.bkg_size[0] / 2:
            self.set_rad_pos()
        if mouse_state[0] == 0 and self.dragging:
            self.dragging = False

        #get color:
        angle = math.degrees(self.get_angle()) + 180
        rel_angle = int(angle) % 60
        match angle // 60:
            case 0:
                self.color = [255, 0 + rel_angle * 255/60, 0]
            case 1:
                self.color = [255 - rel_angle * 255 / 60, 255, 0]
            case 2:
                self.color = [0, 255, 0 + rel_angle * 255/60]
            case 3:
                self.color = [0, 255 - rel_angle * 255 / 60, 255]
            case 4:
                self.color = [rel_angle * 255/60, 0, 255]
            case 5:
                self.color = [255, 0, 255 - rel_angle * 255 / 60]
        rad = self.get_rad(self.rel_pos)
        #normalize from 0 to 1
        rad = 1 - rad / self.bkg_size[0] * 2
        for i in range(3):
            self.color[i] += int((255 - self.color[i]) * rad)
        return [self.command, self.color]

    def draw(self, screen, curr_color):
        """
        Overrides Button.draw, including to draw the ball and background together.
        """
        self.bkg2.draw(screen)
        if self.curr_hover or self.dragging:
            image = self.hover_img
        else:
            image = self.img
        screen.blit(image, (self.rel_pos[0] - self.width / 2, self.rel_pos[1] - self.height / 2))
        pygame.draw.rect(screen, self.color, pygame.Rect(self.pos[0] / 2, self.pos[1], 50, 50))


    def hovering(self, mouse_pos):
        """Returns if the mouse is hovering over the ball"""
        return (abs(mouse_pos[0] - self.rel_pos[0]) <= self.width / 2
                and abs(mouse_pos[1] - self.rel_pos[1]) <= self.height / 2)

    def get_rad(self, param):
        """returns the radius of the button"""
        return math.sqrt(abs(self.pos[0] - param[0]) ** 2 + abs(self.pos[1] - param[1]) ** 2)

    def set_rad_pos(self):
        """sets the ball to the edge of the circle if the mouse drags it outside"""
        angle = self.get_angle()
        self.rel_pos[0] = -1 * (math.cos(angle) * self.bkg_size[0] / 2) + self.pos[0]
        self.rel_pos[1] = (math.sin(angle) * self.bkg_size[1] / 2) + self.pos[1]

    def get_angle(self):
        """returns the angle of the mouse to the center of the button"""
        return math.atan2(-1 * (self.pos[1] - self.rel_pos[1]), self.pos[0] - self.rel_pos[0])

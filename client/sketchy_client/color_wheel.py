"""
ColorWheel is a type of Button, which enables nearly any RGB value to be selected.
This is for complex colors, which enables any color during the drawing phase.
"""
import math
import pygame

from .button import Button
from .default_ui import DefaultUI
from .paths import resolve_asset_path


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
        self.rad = 0
        self.angle = 0
        self.saved_positions = {}
        img = 'assets/textures/slider_ball.png'
        self.bkg2 = DefaultUI(position, size, resolve_asset_path
        ('assets/textures/colorwheel_bkg.png'))
        super().__init__(position, (size[0] / 20, size[1] / 20, size[2]), img, funct)

    def behave(self, mouse_pos, just_clicked, keystrokes, mouse_state, paused):
        """
        Overrides Button.behave, moving the ball around based on mouse position and
        calculating the color at that position, returning it.
        """
        if not paused or self.pause_override:
            self.curr_hover = self.hovering(mouse_pos)
            if self.get_rad(mouse_pos) <= 0.5 and just_clicked[0]:
                self.dragging = True
            if self.dragging:
                self.rel_pos = [mouse_pos[0], mouse_pos[1]]
            if self.get_rad(self.rel_pos) > 0.5:
                self.set_rad_pos()

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
            rad = 1 - self.get_rad(self.rel_pos) * 2
            #normalize from 0 to 1
            #rad = 1 - rad / self.bkg_size[0] * 2
            for i in range(3):
                self.color[i] += int((255 - self.color[i]) * rad)

            if mouse_state[0] == 0 and self.dragging:
                # save color and position
                self.saved_positions[(int(self.color[0]),
                                      int(self.color[1]),
                                      int(self.color[2]))] = self.rel_pos
                self.dragging = False

            return [self.command, self.color]
        return False

    def set_color(self, color):
        for col, val in self.saved_positions.items():
            if (col[0] in range(color[0]-2, color[0]+2) and
                col[1] in range(color[1]-2, color[1]+2) and
                col[2] in range(color[2]-2, color[2]+2)):
                corr_val = [0,0,0]
                for elem in range(len(col)):
                    for c in range(color[elem]-2, color[elem]+2):
                        if col[elem] == c:
                            corr_val[elem] = c
                self.rel_pos = self.saved_positions[(corr_val[0], corr_val[1], corr_val[2])]
                break

    def draw(self, screen, curr_color):
        """
        Overrides Button.draw, including to draw the ball and background together.
        """
        self.bkg2.draw(screen)
        #screen.blit(self.img, self.pos[:2])
        if self.curr_hover or self.dragging:
            image = self.hover_img
        else:
            image = self.img
        screen.blit(image, (self.rel_pos[0] - self.width / 2, self.rel_pos[1] - self.height / 2))
        try:
            pygame.draw.rect(screen, self.color, pygame.Rect(self.pos[0] / 2, self.pos[1], 50, 50))
        except:
            pygame.draw.rect(screen, (255,255,255),
                             pygame.Rect(self.pos[0] / 2, self.pos[1], 50, 50))



    def hovering(self, mouse_pos):
        """Returns if the mouse is hovering over the ball"""
        return (abs(mouse_pos[0] - self.rel_pos[0]) <= self.width / 2
                and abs(mouse_pos[1] - self.rel_pos[1]) <= self.height / 2)

    def get_rad(self, param):
        """returns the radius of the button"""
        return math.sqrt(((self.pos[0] - param[0]) / self.bkg_size[0])
                         ** 2 + (((self.pos[1] - param[1]) / self.bkg_size[1]) ** 2))

    def set_rad_pos(self):
        """sets the ball to the edge of the circle if the mouse drags it outside"""
        angle = self.get_angle()
        self.rel_pos[0] = -1 * (math.cos(angle) * self.bkg_size[0] / 2) + self.pos[0]
        self.rel_pos[1] = (math.sin(angle) * self.bkg_size[1] / 2) + self.pos[1]

    def get_angle(self, data = None):
        """returns the angle of the mouse to the center of the button"""
        if data:
            return math.atan2(-1 * (self.pos[1] - data[1]), self.pos[0] - data[0])
        return math.atan2(-1 * (self.pos[1] - self.rel_pos[1]), self.pos[0] - self.rel_pos[0])

    def resize(self, wid, ht):
        #store angle from center, and radius? (For ball position?)
        angle = self.get_angle()
        rad = self.get_rad(self.rel_pos)
        angles = []
        rads = []
        for elem in self.saved_positions.items():
            angles.append(self.get_angle(elem[1]))
            rads.append(self.get_rad(elem[1]))
        self.bkg2.resize(wid, ht)
        self.bkg_size = self.bkg2.width, self.bkg2.height
        self.pos = self.bkg2.pos
        self.width, self.height = (self.init_size[0] * wid / 1000,
                                   self.init_size[1] * ht / 1000 * 16 / 10)
        self.width /= 20
        self.height /= 20
        self.init_y = self.pos[1]
        hover_path = resolve_asset_path(self.img_path[:-4] + "_hover.png")
        self.hover_img = pygame.image.load(hover_path)
        self.hover_img = pygame.transform.scale(self.hover_img, (self.width, self.height))
        image_path = resolve_asset_path(self.img_path)
        self.img = pygame.image.load(image_path)
        self.img = pygame.transform.scale(self.img, (self.width, self.height))
        #need to calculate position from color?

        #unnormalize radius
        self.rel_pos = [self.pos[0] - math.cos(angle) * rad * self.bkg_size[0],
                        self.pos[1] + math.sin(angle) * rad* self.bkg_size[1]]
        for x, elem in enumerate(self.saved_positions.items()):
            angle = angles[x]
            rad = rads[x]
            val = [self.pos[0] - math.cos(angle) * rad * self.bkg_size[0],
                   self.pos[1] + math.sin(angle) * rad * self.bkg_size[1]]
            self.saved_positions[elem[0]] = val
        #rad = self.get_rad(self.rel_pos) / self.bkg_size[0] * 2

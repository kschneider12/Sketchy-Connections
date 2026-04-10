import pygame
from .button import Button
from .paths import resolve_asset_path

class SlideDownButton(Button):
    def __init__(self, pos, y_bounds, size, funct, z=1):
        y_bounds2 = [y_bounds[0][1], y_bounds[1][1]]
        img = 'assets/textures/slide_down_bar.png'
        self.dragging = False
        self.bounds = [y_bounds2[0] + size[1] / 2, y_bounds2[1] - size[1] / 2]
        self.init_y_bounds = [y_bounds[0][2][1], y_bounds[1][2][1]]
        super().__init__([pos[0],y_bounds2[1] - size[1] / 2, pos[2]] , size, img, funct, z=z)

    def behave(self, mouse_pos, just_clicked, keystrokes, mouse_state, paused):
        if not paused or self.pause_override:
            if self.hovering(mouse_pos):
                self.curr_hover = True
            else:
                self.curr_hover = False
            #if we are holding it
            if self.clicked(mouse_pos, just_clicked):
                self.dragging = True

            if self.dragging:
                self.pos[1] = mouse_pos[1]
            else:
                self.pos[1] += (mouse_state[2] * 5)

            if self.pos[1] < self.bounds[0]:
                self.pos[1] = self.bounds[0]
            elif self.pos[1] > self.bounds[1]:
                self.pos[1] = self.bounds[1]

            if not mouse_state[0]:
                self.dragging = False
            #return offset positioning for objects that it applies to (make an optional parameter meaning slide)
            #print((self.pos[1] - self.bounds[0]) / (self.bounds[1] - self.bounds[0]))
        return [self.command, (-1 * (self.pos[1] - self.bounds[0]) / (self.bounds[1] - self.bounds[0]) + 1) * 1.0]

    def resize(self, wid, ht):
        rel_pos = (self.pos[1] - self.bounds[0]) / (self.bounds[1] - self.bounds[0])
        self.width, self.height = self.init_size[0] * wid / 1000, self.init_size[1] * ht / 1000 * 16 / 10
        self.pos[0] = int(self.init_pos[0] * wid / 100)

        hover_path = resolve_asset_path(self.img_path[:-4] + "_hover.png")
        self.hover_img = pygame.image.load(hover_path)
        self.hover_img = pygame.transform.scale(self.hover_img, (self.width, self.height))
        image_path = resolve_asset_path(self.img_path)
        self.img = pygame.image.load(image_path)
        self.img = pygame.transform.scale(self.img, (self.width, self.height))

        new_bounds = self.init_y_bounds[0] * ht / 100, self.init_y_bounds[1] * ht / 100
        self.bounds = [new_bounds[0] + self.height / 2, new_bounds[1] - self.height / 2]
        self.pos[1] = rel_pos * (self.bounds[1] - self.bounds[0]) + self.bounds[0]


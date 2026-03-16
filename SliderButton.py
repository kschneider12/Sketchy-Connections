from Button import Button
from DefaultUI import DefaultUI

class SliderButton(Button):
    def __init__(self,  position, size, mn, mx, funct):
        self.selected = False
        self.min = mn
        self.rel_pos = [position[0], position[1]]
        self.max = mx
        self.bkg_size = size
        self.dragging = False
        self.accum = 0
        img = 'assets/textures/slider_ball.png'
        self.bkg = DefaultUI(position, size, 'assets/textures/slider_bar.png')
        super().__init__(position, (size[1], size[1]), img, funct)
        self.bounds = [self.pos[0] + self.bkg_size[0] / 2 - self.width / 2, self.pos[0] - self.bkg_size[0] / 2 + self.width / 2]

    def behave(self, mouse_pos, just_clicked, keystrokes, mouse_status):
        if self.hovering(mouse_pos):
            self.curr_hover = True
        else:
            self.curr_hover = False
        if self.hovering(mouse_pos) and just_clicked[0]:
            #convert mouse pos to 0-1 for position
            self.dragging = True
        if self.dragging:
            self.rel_pos[0] = mouse_pos[0]
        if mouse_status[0] == 0 and self.dragging:
            self.dragging = False
        if self.rel_pos[0] > self.bounds[0]:
            self.rel_pos[0] = self.bounds[0]
        if self.rel_pos[0] < self.bounds[1]:
            self.rel_pos[0] = self.bounds[1]
        return [self.command, self.max - (self.rel_pos[0] - self.bounds[0]) * (self.max - self.min) / (self.bounds[1] - self.bounds[0])]

    def draw(self, screen, curr_color):
        self.bkg.draw(screen)
        if self.curr_hover or self.dragging:
            image = self.hover_img
        else:
            image = self.img
        screen.blit(image, (self.rel_pos[0] - self.width / 2, self.rel_pos[1] - self.height / 2))

    def hovering(self, mouse_pos):
        return abs(mouse_pos[0] - self.rel_pos[0]) <= self.width / 2 and abs(mouse_pos[1] - self.rel_pos[1]) <= self.height / 2


"""
SliderButton is a type of button that enables fluid
transition between two values. Mainly utilized for volume bar,
it can also be used for any float variable modification mid-game.
"""
from .button import Button
from .default_ui import DefaultUI
from .paths import resolve_asset_path


class SliderButton(Button):
    """
    SliderButton initializer, storing the min and max values and unique
    elements to SliderButton that Button does not have. Similar to BrightnessSlidier
    """

    def __init__(self,  position, size, mn, mx, funct, val = 0, z = 0, pause_override = False):
        self.selected = False
        self.min = mn
        self.rel_pos = [position[0], position[1]]
        self.max = mx
        self.bkg_size = size[:2]
        self.dragging = False
        self.accum = 0
        self.val = val
        img = resolve_asset_path('assets/textures/slider_ball.png')
        self.bkg = DefaultUI(position, size, resolve_asset_path('assets/textures/slider_bar.png'))
        super().__init__(position, (size[1], size[1], (size[2][1], size[2][1])), img, funct, z=z, pause_override=pause_override)
        self.bounds = [self.pos[0] + self.bkg_size[0] / 2 - self.width / 2,
                       self.pos[0] - self.bkg_size[0] / 2 + self.width / 2]

        self.rel_pos[0] = ((self.max - val) * (self.bounds[1] - self.bounds[0])
                           / (self.max - self.min) + self.bounds[0])

    def behave(self, mouse_pos, just_clicked, keystrokes, mouse_state, paused):
        """
        Override of button behave function. Manages sliding bar and value with function return
        """
        if not paused or self.pause_override:
            if self.hovering(mouse_pos):
                self.curr_hover = True
            else:
                self.curr_hover = False
            if self.hovering(mouse_pos) and just_clicked[0]:
                #convert mouse pos to 0-1 for position
                self.dragging = True
            if self.dragging:
                self.rel_pos[0] = mouse_pos[0]
            if mouse_state[0] == 0 and self.dragging:
                self.dragging = False
            if self.rel_pos[0] > self.bounds[0]:
                self.rel_pos[0] = self.bounds[0]
            if self.rel_pos[0] < self.bounds[1]:
                self.rel_pos[0] = self.bounds[1]
            self.val = (self.max - (self.rel_pos[0] - self.bounds[0])
                        * (self.max - self.min) / (self.bounds[1] - self.bounds[0]))
            return [self.command, self.max - (self.rel_pos[0] - self.bounds[0])
                    * (self.max - self.min) / (self.bounds[1] - self.bounds[0])]
        return False

    def draw(self, screen, curr_color):
        """
        Override of button draw function. Draws slider ball on screen in addition to
        background UI.
        """
        self.bkg.draw(screen)
        if self.curr_hover or self.dragging:
            image = self.hover_img
        else:
            image = self.img
        screen.blit(image, (self.rel_pos[0] - self.width / 2, self.rel_pos[1] - self.height / 2))

    def hovering(self, mouse_pos):
        """
        Returns if the mouse is hovering over the ball or not
        """
        return (abs(mouse_pos[0] - self.rel_pos[0]) <= self.width / 2
                and abs(mouse_pos[1] - self.rel_pos[1]) <= self.height / 2)

    def resize(self,wid, ht):
        super().resize(wid,ht)
        self.bkg.resize(wid,ht)
        self.bkg_size = self.bkg.width, self.bkg.height

        self.bounds = [self.pos[0] + self.bkg_size[0] / 2 - self.width / 2,
                       self.pos[0] - self.bkg_size[0] / 2 + self.width / 2]

        #THIS IS ISSUE!
        self.rel_pos[0] = ((self.max - self.val) * (self.bounds[1] - self.bounds[0])
                            / (self.max - self.min) + self.bounds[0])
        self.rel_pos[1] =self.pos[1]

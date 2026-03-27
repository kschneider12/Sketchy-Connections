"""
CheckboxButton is a child of button, and is a toggleable trigger
for certain settings, such as complex colors or not.
"""
import pygame
from .button import Button
from .paths import resolve_asset_path

FONT_PATH = resolve_asset_path("assets/fonts/MoreSugar-Regular.ttf")

class CheckboxButton(Button):
    """
    creates new variables such as active, and creates the texture for the check
    within the box. Also creates text for what the button is utilized for.
    """
    def __init__(self, position, size, funct, text, active = False):
        self.active = active
        super().__init__(position, size, 'assets/textures/play.png', funct)
        self.check_img = pygame.image.load(resolve_asset_path('assets/textures/colorwheel_bkg.png'))
        self.check_img = pygame.transform.scale(self.check_img, size)
        self.font = pygame.font.Font(FONT_PATH, int(self.height * 0.8))
        self.text = text
        self.text_surface = self.font.render(self.text, True, (0,0,0))


    def behave(self, mouse_pos, just_clicked, keystrokes, mouse_state):
        """
        Overrides Button.behave, toggling on or off this button.
        """
        if self.hovering(mouse_pos):
            self.curr_hover = True
        else:
            self.curr_hover = False
        if self.clicked(mouse_pos, just_clicked):
            self.active = not self.active
            return [self.command, self.active]
        return False

    def draw(self, screen, curr_color):
        """
        Overrides Button.draw, displaying the check if the box is checked too.
        """
        if self.curr_hover:
            image = self.hover_img
        else:
            image = self.img
        screen.blit(image, (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2))
        if self.active:
            screen.blit(self.check_img, (self.pos[0] - self.width / 2,
                                         self.pos[1] - self.height / 2))
        screen.blit(self.text_surface, (self.pos[0] + self.width / 1.5,
                                        self.pos[1] - self.height / 2))

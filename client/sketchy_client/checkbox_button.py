"""
CheckboxButton is a child of button, and is a toggleable trigger
for certain settings, such as complex colors or not.
"""
import pygame
from .sound_manager import SoundManager
from .button import Button
from .paths import resolve_asset_path

FONT_PATH = resolve_asset_path("assets/fonts/MoreSugar-Regular.ttf")

class CheckboxButton(Button):
    """
    creates new variables such as active, and creates the texture for the check
    within the box. Also creates text for what the button is utilized for.
    """
    def __init__(self, position, size, funct, text, on = False, texture = None):
        self.active = True
        self.on = on
        if not texture:
            texture = 'assets/textures/checkbox_button.png'
            tick_texture = 'assets/textures/checkbox_tick.png'
        else:
            tick_texture = resolve_asset_path(texture[:-4] + "_select.png")
        self.texture = texture
        self.tick_texture = tick_texture
        super().__init__(position, size, texture, funct)
        self.check_img = pygame.image.load(resolve_asset_path(tick_texture))
        self.check_img = pygame.transform.scale(self.check_img, size[:2])
        self.font = pygame.font.Font(FONT_PATH, int(self.height * 0.8))
        self.text = text
        self.text_surface = self.font.render(self.text, True, (0,0,0))


    def behave(self, mouse_pos, just_clicked, keystrokes, mouse_state, paused):
        """
        Overrides Button.behave, toggling on or off this button.
        """
        if not paused or self.pause_override:
            if self.hovering(mouse_pos):
                self.curr_hover = True
            else:
                self.curr_hover = False
            if self.clicked(mouse_pos, just_clicked):
                self.on = not self.on
                SoundManager.get_instance().play_sfx("assets/audio/click.mp3")
                return [self.command, self.on]
        if self.text == "":
            return [self.command, self.on]
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
        if self.on:
            screen.blit(self.check_img, (self.pos[0] - self.width / 2,
                                         self.pos[1] - self.height / 2))
        screen.blit(self.text_surface, (self.pos[0] + self.width / 1.5,
                                        self.pos[1] - self.height / 2))

    def resize(self, wid, ht):
        super().resize(wid, ht)
        self.check_img = pygame.image.load(resolve_asset_path(self.tick_texture))
        self.check_img = pygame.transform.scale(self.check_img, (self.width, self.height))
        self.font = pygame.font.Font(FONT_PATH, int(self.height * 0.8))
        self.text_surface = self.font.render(self.text, True, (0,0,0))

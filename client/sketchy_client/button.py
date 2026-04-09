"""
Button is the parent class to a multitude of button types
including checkbox, choices, color wheel, slider, type box, color, brightness
slider, etc. It is the core foundation of interaction within the program.
"""
import pygame
from .sound_manager import SoundManager
from .paths import resolve_asset_path


class Button:
    """
    Initializes elements such as position, size, texture, depth,
    what function it is connected to, and if it has a different texture when it is
    hovered over.
    """
    def __init__(self, position, size, img, funct, multi_texture = True, z = 0, draggable = False, pause_override = False):
        self.pos = position
        self.pause_override = pause_override
        self.z = z
        self.draggable = draggable
        self.width = size[0]
        self.height = size[1]
        self.init_y = position[1]
        self.init_size = size[2]
        self.init_pos = position[2]
        image_path = resolve_asset_path(img)
        self.img = pygame.image.load(image_path)
        self.img_path = img
        self.curr_hover = False
        self.img = pygame.transform.scale(self.img, size[:2])
        self.command = funct
        self.active = True
        self.sounds = []
        if multi_texture:
            hover_path = resolve_asset_path(img[:-4] + "_hover.png")
            self.hover_img = pygame.image.load(hover_path)
            self.hover_img = pygame.transform.scale(self.hover_img, size[:2])
        else:
            self.hover_img = None

    def behave(self, mouse_pos, just_clicked, keystrokes, mouse_state, paused):
        """
        Called every frame, behave handles the default behavior of a button.
        Contains some unnecessary parameters, but they are for specific children that override
        this behavior.
        """
        if not paused or self.pause_override:
            if self.hovering(mouse_pos):
                self.curr_hover = True
            else:
                self.curr_hover = False
            if self.clicked(mouse_pos, just_clicked):
                SoundManager.get_instance().play_sfx("assets/audio/click.mp3")
                return self.command
        return False

    def draw(self, screen, curr_color):
        self.sounds = []
        """
        draw is how buttons are drawn on screen, depending on multiple textures or not.
        """
        if self.curr_hover and self.hover_img:
            image = self.hover_img
        else:
            image = self.img
        screen.blit(image, (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2))

    def clicked(self, mouse_pos, just_clicked):
        """
        returns if the button is clicked
        """
        return self.hovering(mouse_pos) and just_clicked[0]

    def unclicked(self, mouse_pos, just_clicked):
        """
        returns when a button is not being clicked
        """
        return not self.hovering(mouse_pos) and just_clicked[0]

    def hovering(self, mouse_pos):
        """
        returns if a button is hovered over by the mouse
        """
        return (abs(mouse_pos[0] - self.pos[0]) <= self.width / 2
                and abs(mouse_pos[1] - self.pos[1]) <= self.height / 2)

    def replace_texture(self, img, multi_texture=True):
        """switches the texture of a button"""
        self.img = pygame.image.load(resolve_asset_path(img))
        self.img = pygame.transform.scale(self.img, (self.width, self.height))
        if multi_texture:
            hover_path = resolve_asset_path(img[:-4] + "_hover.png")
            self.hover_img = pygame.image.load(hover_path)
            self.hover_img = pygame.transform.scale(self.hover_img, (self.width, self.height))

    def resize(self, wid, ht):
        """resizes the button ui on screen"""
        self.pos = [int(self.init_pos[0] * wid / 100), int(self.init_pos[1] * ht / 100)]
        self.width, self.height = self.init_size[0] * wid / 1000, self.init_size[1] * ht / 1000 * 16 / 10
        self.init_y = self.pos[1]
        if self.hover_img:
            hover_path = resolve_asset_path(self.img_path[:-4] + "_hover.png")
            self.hover_img = pygame.image.load(hover_path)
            self.hover_img = pygame.transform.scale(self.hover_img, (self.width, self.height))
        if self.img:
            image_path = resolve_asset_path(self.img_path)
            self.img = pygame.image.load(image_path)
            self.img = pygame.transform.scale(self.img, (self.width, self.height))

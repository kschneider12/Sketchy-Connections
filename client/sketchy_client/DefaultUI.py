import pygame

from .paths import resolve_asset_path


class DefaultUI:
    def __init__(self, position, size, img, z = 0):
        self.z = z
        self.pos = position
        self.width = size[0]
        self.height = size[1]
        if img:
            self.img = pygame.image.load(resolve_asset_path(img))
            self.img = pygame.transform.scale(self.img, size)

    def draw(self, screen, curr_color = None):
        screen.blit(self.img, (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2))

class MouseStick(DefaultUI):
    def __init__(self, size, img):
        self.visible = False
        DefaultUI.__init__(self, [0,0], size, img, 3)

    def behave(self, mouse_pos):
        if self.visible:
            self.pos = [mouse_pos[0], mouse_pos[1]]

class TransparentUI(DefaultUI):
    def __init__(self, position, size, color, transparency, z = 0):
        self.color = color
        DefaultUI.__init__(self, position, size, None, z)
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.surface.fill((color[0], color[1], color[2], transparency))

    def draw(self, screen, curr_color = None):
        screen.blit(self.surface, (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2))
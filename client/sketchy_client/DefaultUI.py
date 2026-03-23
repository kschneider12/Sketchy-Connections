import pygame

from .paths import resolve_asset_path


class DefaultUI:
    def __init__(self, position, size, img):
        self.pos = position
        self.width = size[0]
        self.height = size[1]
        self.img = pygame.image.load(resolve_asset_path(img))
        self.img = pygame.transform.scale(self.img, size)

    def draw(self, screen):
        screen.blit(self.img, (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2))

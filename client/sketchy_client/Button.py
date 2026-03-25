import pygame

from .paths import resolve_asset_path


class Button:
    def __init__(self, position, size, img, funct, multi_texture = True, z = 0):
        self.pos = position
        self.z = z
        self.width = size[0]
        self.height = size[1]
        image_path = resolve_asset_path(img)
        self.img = pygame.image.load(image_path)
        self.curr_hover = False
        self.img = pygame.transform.scale(self.img, size)
        self.command = funct
        self.active = True
        if multi_texture:
            hover_path = resolve_asset_path(img[:-4] + "_hover.png")
            self.hover_img = pygame.image.load(hover_path)
            self.hover_img = pygame.transform.scale(self.hover_img, size)
        else:
            self.hover_img = self.img

    def behave(self, mouse_pos, just_clicked, keystrokes, mouse_state):
        if self.hovering(mouse_pos):
            self.curr_hover = True
        else:
            self.curr_hover = False
        if self.clicked(mouse_pos, just_clicked):
            return self.command
        else:
            return False

    def draw(self, screen, curr_color):
        if self.curr_hover:
            image = self.hover_img
        else:
            image = self.img
        screen.blit(image, (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2))

    def clicked(self, mouse_pos, just_clicked):
        return self.hovering(mouse_pos) and just_clicked[0]

    def unclicked(self, mouse_pos, just_clicked):
        return not self.hovering(mouse_pos) and just_clicked[0]

    def hovering(self, mouse_pos):
        return abs(mouse_pos[0] - self.pos[0]) <= self.width / 2 and abs(mouse_pos[1] - self.pos[1]) <= self.height / 2

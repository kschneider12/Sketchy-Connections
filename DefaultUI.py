import pygame

class DefaultUI:
    def __init__(self, position, size, img):
        self.pos = position
        self.width = size[0]
        self.height = size[1]
        self.img = pygame.image.load(img)
        self.img = pygame.transform.scale(self.img, size)

    def draw(self, screen):
        screen.blit(self.img, (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2))

class MouseStick(DefaultUI):
    def __init__(self, size, img):
        self.visible = False
        DefaultUI.__init__(self, [0,0], size, img)

    def behave(self, mouse_pos):
        if self.visible:
            self.pos = [mouse_pos[0], mouse_pos[1]]




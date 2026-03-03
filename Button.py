import pygame

class Button:
    def __init__(self, position, size, img, funct, multi_texture = True):
        self.pos = position
        self.width = size[0]
        self.height = size[1]
        self.img = pygame.image.load(img)
        self.curr_hover = False
        self.img = pygame.transform.scale(self.img, size)
        self.command = funct
        if multi_texture:
            self.hover_img = pygame.image.load(img[:-4] + "_hover.png")
            self.hover_img = pygame.transform.scale(self.hover_img, size)
        else:
            self.hover_img = self.img

    def behave(self, mouse_pos, just_clicked, keystrokes):
        if self.hovering(mouse_pos):
            self.curr_hover = True
        else:
            self.curr_hover = False
            #self.img = pygame.transform.scale(self.img, (self.width + 10, self.height + 10))
        #else:
            #self.img = pygame.transform.scale(self.img, (self.width, self.height))
        if self.clicked(mouse_pos, just_clicked):
            print("CLICKED!")
            return self.command
        else:
            return False

    def draw(self, screen):
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



import pygame

class Button:
    def __init__(self, position, size, img, funct):
        self.pos = position
        self.width = size[0]
        self.height = size[1]
        self.img = pygame.image.load(img)
        self.img = pygame.transform.scale(self.img, size)
        self.command = funct

    def behave(self, mouse_pos, just_clicked, keystrokes):
        #if self.hovering(mouse_pos):
            #self.img = pygame.transform.scale(self.img, (self.width + 10, self.height + 10))
        #else:
            #self.img = pygame.transform.scale(self.img, (self.width, self.height))
        if self.clicked(mouse_pos, just_clicked):
            print("CLICKED!")
            return self.command
        else:
            return False

    def draw(self, screen):
        screen.blit(self.img, (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2))
        #pygame.draw.rect(screen, (100, 255, 0), pygame.Rect(self.pos[0] - self.width / 2, self.pos[1] - self.height / 2, self.width, self.height))

    def clicked(self, mouse_pos, just_clicked):
        return self.hovering(mouse_pos) and just_clicked[0]

    def unclicked(self, mouse_pos, just_clicked):
        return not self.hovering(mouse_pos) and just_clicked[0]

    def hovering(self, mouse_pos):
        return abs(mouse_pos[0] - self.pos[0]) <= self.width / 2 and abs(mouse_pos[1] - self.pos[1]) <= self.height / 2



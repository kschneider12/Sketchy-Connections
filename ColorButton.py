from Button import Button
import pygame

COLORS = {
    'background': (240, 240, 240),
    'black' : (0, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'purple': (128, 0, 128),
    'red': (255, 0, 0),
    'orange': (255, 128, 0),
    'yellow': (255, 255, 0),
    'grey': (128, 128, 128),
    'sky_blue': (135, 206, 235),
    'brown': (139, 69, 19),
    'white': (255, 255, 255),
    'eraser': (240, 240, 240)
}

class ColorButton(Button):
    def __init__(self,  position, size, funct, color):
        self.rel_pos = [position[0], position[1]]
        self.bkg_size = size
        self.dragging = False
        self.color = COLORS[color]
        img = 'assets/textures/color_button.png'
        super().__init__(position, size, img, funct)
        self.img_select = pygame.image.load('assets/textures/color_button_select.png')
        self.img_select = pygame.transform.scale(self.img_select, size)

    def behave(self, mouse_pos, just_clicked, keystrokes, mouse_status):
        if self.hovering(mouse_pos):
            self.curr_hover = True
        else:
            self.curr_hover = False
        if self.clicked(mouse_pos, just_clicked):
            return [self.command, self.color]
        else:
            return False

    def draw(self, screen, curr_color):
        #extra data is colorID
        if self.curr_hover:
            image = self.hover_img
        else:
            image = self.img
        if curr_color == self.color:
            image = self.img_select
        pygame.draw.rect(screen, self.color, pygame.Rect(self.pos[0] - self.width / 2, self.pos[1] - self.height / 2, self.width, self.height))
        screen.blit(image, (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2))


import pygame
from Button import Button

class TypeBox(Button):
    def __init__(self,  position, size):
        self.selected = False
        self.curr_string = ""
        img = "assets/textures/default_texture.png"
        funct = 0
        super().__init__(position, size, img, funct)

    def behave(self, mouse_pos, just_clicked, keystrokes):
        if self.clicked(mouse_pos, just_clicked):
            self.selected = True

        if self.unclicked(mouse_pos, just_clicked):
            self.selected = False

        if self.selected:
            for char in keystrokes:
                if char == pygame.K_KP_ENTER or char == pygame.K_ESCAPE:
                    self.selected = False
                if char == pygame.K_BACKSPACE:
                    print("Backspace")
                    self.curr_string = self.curr_string[:-1]
                else:
                    self.curr_string += char

        if not self.selected:
            return self.curr_string






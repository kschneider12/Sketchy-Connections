import pygame
from Button import Button
FONT_PATH = f"assets/fonts/MoreSugar-Regular.ttf"


class ChoicesButton(Button):
    def __init__(self, pos, size, funct, choices, start_choice = -1):

        self.choices = choices
        if start_choice == -1:
            self.curr_choice = choices[0]
        else:
            self.curr_choice = start_choice

        super().__init__(pos, size, 'assets/textures/play.png', funct, False)
        self.left = Button((pos[0] + size[0] / 1.2, pos[1]), (size[1],size[1]), 'assets/textures/host.png', True)
        self.right = Button((pos[0] - size[0] / 1.2, pos[1]), (size[1],size[1]), 'assets/textures/host.png', True)
        self.font = pygame.font.Font(FONT_PATH, int(self.height * 0.7))

    def behave(self, mouse_pos, just_clicked, keystrokes, mouse_state):
        if self.left.behave(mouse_pos, just_clicked, keystrokes, mouse_state) and self.curr_choice != self.choices[-1]:
            for i, val in enumerate(self.choices):
                if val == self.curr_choice:
                    self.curr_choice = self.choices[i + 1]
                    break
        if self.right.behave(mouse_pos, just_clicked, keystrokes, mouse_state) and self.curr_choice != self.choices[0]:
            for i, val in enumerate(self.choices):
                if val == self.curr_choice:
                    self.curr_choice = self.choices[i - 1]
                    break
        print(self.curr_choice)
        return self.command, self.curr_choice

    def draw(self, screen, curr_color):
        self.left.draw(screen, curr_color)
        self.right.draw(screen, curr_color)
        screen.blit(self.img, (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2))
        text = str(self.curr_choice)
        scale = self.font.size(text)
        text_surface = self.font.render(text, True, (0, 0, 0))
        screen.blit(text_surface, (self.pos[0] - scale[0] / 2, self.pos[1] - scale[1] / 2))


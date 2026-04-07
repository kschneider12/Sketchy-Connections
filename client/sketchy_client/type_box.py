"""
TypeBox is a type of Button, but is more complex for its typing functionality.
It behaves nearly exactly like text boxes in other programs.
"""
import pygame

from .button import Button
from .paths import asset_path


FONT_PATH = asset_path("fonts", "MoreSugar-Regular.ttf")

class TypeBox(Button):
    """
    Initializes TypeBox, including all type-related elements
    that the normal button class does not require.
    """
    def __init__(self,  position, size, img, funct, default_message = "",
                 character_limit = 40, z = 0):
        self.selected = False
        self.character_limit = character_limit
        self.accum = 0
        self.backspace_hold = 0
        self.curr_string = ""
        self.color = (0,0,0)
        self.default_message = default_message
        super().__init__(position, size, img, funct, False, z)
        self.text_size = int(self.height * 2/3.3)
        self.font = pygame.font.Font(FONT_PATH, self.text_size)

    def behave(self, mouse_pos, just_clicked, keystrokes, mouse_state, paused):
        """
        Overrides Button.behave, enabling typing in the box,
        box selection, backspace, return and character management.
        """
        if self.active and (not paused or self.pause_override):
            if self.clicked(mouse_pos, just_clicked):
                self.selected = True

            if self.unclicked(mouse_pos, just_clicked):
                self.selected = False
                self.accum = 0

            if self.selected:
                self.accum += 1
                if 'backspace' not in keystrokes:
                    self.backspace_hold = 0
                for elem in keystrokes:
                    if elem == "enter":
                        self.selected = False
                        self.accum = 0
                    elif elem == "backspace":
                        if self.backspace_hold == 0:
                            self.curr_string = self.curr_string[:-1]
                        else:
                            #NOW THAT BACKSPACE ISN'T 0, WAIT A BIT THEN START DELETING
                            if self.backspace_hold > 30:
                                if (self.backspace_hold // 500) % 2 == 0:
                                    self.curr_string = self.curr_string[:-1]
                        self.backspace_hold += 1
                    else:
                        self.curr_string += elem
        if (self.accum // 30) % 2 == 1:
            bonus = "|"
        else:
            bonus = ""
        if len(self.curr_string) > self.character_limit:
            self.curr_string = self.curr_string[:self.character_limit]
        if self.curr_string == "" and not self.selected:
            # return default gray message
            return [self.default_message,  # written text
                    (self.pos[0] - self.width / 2.2, self.pos[1] - self.height / 3),
                    self.font,
                    (100,100,100),
                    self.character_limit,
                    (self.pos[0] + self.width / 2) - self.font.size("00")[0] - 10,
                    # position for top corner counter
                    "",
                    self.command]
        # return appropriate text

        #Handle staying inside the textbox:
        lim = 0
        while self.font.size(self.curr_string[lim:])[0] >= self.width * 9/10:
            lim += 1
        return [self.curr_string[lim:] + bonus, # written text
                (self.pos[0] - self.width / 2.2, self.pos[1] - self.height / 3), #pos for main
                self.font, # font
                self.color, # color
                self.character_limit,
                (self.pos[0] + self.width / 2) - self.font.size("00")[0] - 10, # pos for corner
                self.curr_string,
                self.command]

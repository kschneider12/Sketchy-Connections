"""
TimeBar is a child of DefaultUI, but has its own file due to its complexity.
It tracks time in many phases of the game, and counts down, returning True when the
time runs out.
"""
import pygame
import time as t

from .default_ui import DefaultUI
from. sound_manager import SoundManager
from .paths import resolve_asset_path

class TimeBar(DefaultUI):
    """
    Initializer of TimeBar, storing the time, textures, and positioning.
    """
    def __init__(self, position, size, time):
        img = "assets/textures/time_bar.png"
        self.bar_pos = position
        self.start_time = time
        self.end_time = t.time() + time
        self.beep = 3
        self.time = self.start_time
        print(self.time)
        self.returned = False
        super().__init__(position, size, img)
        self.bar_img = pygame.image.load(resolve_asset_path("assets/textures/time_line.png"))
        self.bar_img = pygame.transform.scale(self.bar_img, (size[0] * 9/10, size[0] * 2/10))


    def draw(self, screen, curr_color = None):
        """
        Overrides DefaultUI.draw, including the correct height of the bar and the
        colorful pygame Rect to fill in the space.
        """
        self.bar_pos =  (self.pos[0] - self.width / 2.3,
                         self.pos[1] - self.height / 2.08 + (self.start_time - self.time)
                         * (self.height / self.start_time * 0.964))

        color = (255 - int(255 * self.time / self.start_time), int(255 * self.time / self.start_time), 0)
        for val in color:
            if val < 0 or val > 255:
                color = (0,0,0)
        #pygame.draw.rect(screen, color,
                         #pygame.Rect(self.pos[0] - self.width / 2.17, self.bar_pos[1] + self.height * 0.02,
                                     #self.width * 9/10, self.height - self.bar_pos[1] + self.height / 4.2))
        pygame.draw.rect(screen, color,
                         pygame.Rect(self.pos[0] - self.width / 2.17, self.bar_pos[1] + self.bar_img.get_height() / 2.0,
                                     self.width * 9 / 10, ((self.pos[1] + self.height / 2.0) - self.bar_pos[1]) - self.bar_img.get_height()))
        screen.blit(self.bar_img, self.bar_pos)
        screen.blit(self.img, (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2))


        screen.blit(self.bar_img, self.bar_pos)

    def time_up(self):
        """
        returns True when the time reaches 0, and else otherwise.
        """
        if not self.returned:
            self.time = self.end_time - t.time()
            if self.beep > self.time:
                self.beep-= 1
                if self.beep >= 0:
                    SoundManager.get_instance().play_sfx("assets/audio/ding.mp3")
            if self.end_time <= t.time():
                self.returned = True
                return True
        return False

"""
TimeBar is a child of DefaultUI, but has its own file due to its complexity.
It tracks time in many phases of the game, and counts down, returning True when the
time runs out.
"""
import pygame

from .default_ui import DefaultUI
from .paths import resolve_asset_path

class TimeBar(DefaultUI):
    """
    Initializer of TimeBar, storing the time, textures, and positioning.
    """
    def __init__(self, position, size, time):
        img = "assets/textures/time_bar.png"
        self.bar_pos = position
        self.time = time * 60
        self.start_time = self.time
        super().__init__(position, size, img)
        self.bar_img = pygame.image.load(resolve_asset_path("assets/textures/time_line.png"))
        self.bar_img = pygame.transform.scale(self.bar_img, (size[0] * 9/10, 10))


    def draw(self, screen, curr_color = None):
        """
        Overrides DefaultUI.draw, including the correct height of the bar and the
        colorful pygame Rect to fill in the space.
        """
        self.bar_pos =  (self.pos[0] - self.width / 2.15,
                         self.pos[1] - self.height / 2.05 + (self.start_time - self.time)
                         * (self.height / self.start_time * 0.964))
        color = (255 - 255 * self.time / self.start_time, 255 * self.time / self.start_time, 0)
        for val in color:
            if val < 0 or val > 255:
                color = (0,0,0)
        pygame.draw.rect(screen, color,
                         pygame.Rect(self.pos[0] - self.width / 2.15, self.bar_pos[1] + 5,
                                     self.width * 9/10, self.height * 1.245 - self.bar_pos[1] + 5))
        screen.blit(self.bar_img, self.bar_pos)
        screen.blit(self.img, (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2))


        screen.blit(self.bar_img, self.bar_pos)

    def time_up(self):
        """
        returns True when the time reaches 0, and else otherwise.
        """
        if self.time == 0:
            return True
        self.time -= 1
        return False

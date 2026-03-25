import pygame

from .DefaultUI import DefaultUI
from .paths import resolve_asset_path

class TimeBar(DefaultUI):
    def __init__(self, position, size, time):
        img = "assets/textures/time_bar.png"
        self.bar_pos = position
        self.time = time * 60
        print(time)
        self.start_time = self.time
        super().__init__(position, size, img)
        self.bar_img = pygame.image.load(resolve_asset_path("assets/textures/time_line.png"))
        self.bar_img = pygame.transform.scale(self.bar_img, (size[0] * 9/10, 10))


    def draw(self, screen, curr_color = None):
        self.bar_pos =  (self.pos[0] - self.width / 2.15, self.pos[1] - self.height / 2.05 + (self.start_time - self.time) * (self.height / self.start_time * 0.964))
        #self.bar_pos =  (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2 + (self.start_time - self.time) * (self.height / self.start_time * 0.965) + 5)
        #screen.blit(self.bar_img, ((self.pos[0] - self.width / 2) + 5, self.bar_pos))
        color = (255 - 255 * self.time / self.start_time, 255 * self.time / self.start_time, 0)
        for val in color:
            if val < 0 or val > 255:
                color = (0,0,0)
        pygame.draw.rect(screen, color, pygame.Rect(self.pos[0] - self.width / 2.15, self.bar_pos[1] + 5, self.width * 9/10, self.height * 1.245 - self.bar_pos[1] + 5))
        screen.blit(self.bar_img, self.bar_pos)
        screen.blit(self.img, (self.pos[0] - self.width / 2, self.pos[1] - self.height / 2))


        screen.blit(self.bar_img, self.bar_pos)

    def time_up(self):
        if self.time == 0:
            return True
        else:
            self.time -= 1
        return False

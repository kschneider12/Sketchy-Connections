from .button import Button

class SlideDownButton(Button):
    def __init__(self, pos, y_bounds, size, funct):
        y_bounds = (y_bounds[0][1], y_bounds[1][1])
        img = 'assets/textures/play.png'
        self.dragging = False
        self.bounds = (y_bounds[0] + size[1] / 2, y_bounds[1] - size[1] / 2)
        super().__init__([pos[0],y_bounds[1] - size[1] / 2] , size, img, funct)

    def behave(self, mouse_pos, just_clicked, keystrokes, mouse_state, paused):
        if not paused or self.pause_override:
            if self.hovering(mouse_pos):
                self.curr_hover = True
            else:
                self.curr_hover = False
            #if we are holding it
            if self.clicked(mouse_pos, just_clicked):
                self.dragging = True

            if self.dragging:
                self.pos[1] = mouse_pos[1]
            else:
                self.pos[1] += (mouse_state[2] * 5)

            if self.pos[1] < self.bounds[0]:
                self.pos[1] = self.bounds[0]
            elif self.pos[1] > self.bounds[1]:
                self.pos[1] = self.bounds[1]

            if not mouse_state[0]:
                self.dragging = False
            #return offset positioning for objects that it applies to (make an optional parameter meaning slide)
            #print((self.pos[1] - self.bounds[0]) / (self.bounds[1] - self.bounds[0]))
        return [self.command, (self.pos[1] - self.bounds[0]) / (self.bounds[1] - self.bounds[0])]


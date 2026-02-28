import pygame
from pygame.constants import K_KP_ENTER, K_BACKSPACE, K_RETURN

from Button import Button
from TypeBox import TypeBox, CHARACTER_LIMIT

SCREEN_LEN = 1920
SCREEN_HT = 1080

class Engine():
    def __init__(self):
        # flags
        self.exit = False

        #pygame info
        self.screen = pygame.display.set_mode((SCREEN_LEN, SCREEN_HT))
        pygame.display.set_caption("Sketchy Connections")
        self.clock = pygame.time.Clock()

        # Input management
        self.scene = "welcome"
        self.key_status = {
            pygame.K_s: False,
            pygame.K_w: False,
            pygame.K_SPACE: False,
            pygame.K_BACKSPACE: False,
            pygame.K_RETURN: False,
            pygame.K_ESCAPE: False
        }
        self.mouse_buttons = [False, False]
        self.mouse_buttons_last_frame = [False, False]
        self.mouse_pos = [0, 0]
        self.keystrokes = []
        self.type_text_draws = []

        # UI Management
        self.active_buttons = []


    def run(self):
        while True:
            self.type_text_draws = []
            self.mouse_buttons_last_frame[0] = self.mouse_buttons[0]
            self.mouse_buttons_last_frame[1] = self.mouse_buttons[1]
            self.getInputs()
            self.manageButtons()

            # Behaviors depending on scene
            match self.scene:
                case "welcome":
                    self.welcome()
                case "draw":
                    self.draw()
                case "guess":
                    self.guess()
                case "game_over":
                    self.game_over()
            if self.exit:
                pygame.quit()
                break
            # Update the Screen
            self.drawUI()
            pygame.display.flip()
            self.clock.tick(60)

    def getInputs(self):
        self.keystrokes = []
        self.key_status[K_KP_ENTER] = False
        #self.key_status[K_BACKSPACE] = False
        self.mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit = True
            if event.type == pygame.TEXTINPUT:
                self.keystrokes.append(event.text)
            elif event.type == pygame.KEYDOWN:
                if event.key in self.key_status:
                    self.key_status[event.key] = True
            elif event.type == pygame.KEYUP:
                if event.key in self.key_status:
                    self.key_status[event.key] = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_buttons[0] = True
                elif event.button == 3:
                    self.mouse_buttons[1] = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_buttons[0] = False
                elif event.button == 3:
                    self.mouse_buttons[1] = False
        if self.key_status[pygame.K_RETURN]:
            self.keystrokes.append("enter")
        if self.key_status[pygame.K_BACKSPACE]:
            self.keystrokes.append("backspace")
        if self.key_status[pygame.K_ESCAPE]:
            self.exit = True

    def drawUI(self):
        self.screen.fill((50, 100, 100))
        for button in self.active_buttons:
            button.draw(self.screen)
        for data in self.type_text_draws:
            # NEED TO SEPARATE FROM NORMAL DRAWS! TWO DIFFERENT VECTORS
            self.drawTypingText(data)

    def manageButtons(self):
        just_clicked = [not self.mouse_buttons_last_frame[0] and self.mouse_buttons[0],
                        not self.mouse_buttons_last_frame[1] and self.mouse_buttons[1]]
        for button in self.active_buttons:
            output = button.behave(self.mouse_pos, just_clicked, self.keystrokes)
            if isinstance(output, list):
                #output[:-1] is the return value- store when the submit button is pressed
                self.type_text_draws.append(output)
            if callable(output):
                output()


    def welcome(self):
        # This is the game loop for the welcome screen
        if self.key_status[pygame.K_SPACE]:
            print("Draw!")
            self.scene = "draw"
            self.active_buttons = [Button((100,100), (50,30), "assets/textures/default_texture.png", self.switchToGuessing),
                                   Button((250,100), (100,100), "assets/textures/default_texture.png", self.switchToWelcome),
                                   TypeBox((SCREEN_LEN / 2, SCREEN_HT - 200), (1300, 70), "assets/textures/text_box_5.png", "Type A Response"),
                                   TypeBox((300, 300), (200, 50),"assets/textures/text_box_4.png")]

    def draw(self):
        #print("DRAWING!")
        '''
        Notes on data structure:
            [[index, colorID], [],[],...] in order of pixels added
            index is 0 -> length*width
            -----------------
            -0              -
            -               -
            -            255-
            -----------------
            Keep brush type as a settable variable for easy switching when buttons implemented (including eraser)
        '''
        # This is the game loop for the drawing screen
        return

    def guess(self):
        if self.key_status[pygame.K_s]:
            print("Welcome!")
            self.scene = "welcome"        # This is the game loop for the guessing screen
        return

    def game_over(self):
        # This is the game loop for the game over screen
        return


#------------------------------------------------------------------------------------------------
#Button Commands listed below (Nothing else under this line!)
#------------------------------------------------------------------------------------------------

    def switchToGuessing(self):
        self.scene = "guess"
        self.active_buttons = []

    def switchToWelcome(self):
        self.scene = "welcome"
        self.active_buttons = []

    def drawText(self, vec):
        if len(vec) == 4:
            text = vec[0]
            pos = vec[1]
            font = vec[2]
            color = vec[3]
            text_surface = font.render(text, True, color)
            # SO I NEED TO KNOW THE SIZE OF THE TEXT BEFORE I BLIT IT, BUT AFTER I MAKE IT???!!
            self.screen.blit(text_surface, pos)

    def drawTypingText(self, vec):
        if (len(vec[-1]) > 0):
            self.drawText([str(CHARACTER_LIMIT - len(vec[-1])), (vec[-2], vec[1][1]), vec[2], (100,100,100)])

        self.drawText(vec[:-2])
        #(self.pos[0] - self.width / 2.2, self.pos[1] - self.height / 3)
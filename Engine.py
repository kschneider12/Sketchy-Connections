import pygame


class Engine():
    def __init__(self):
        # Init Pygame and Audio
        self.clock = pygame.time.Clock()
        self.scene = "welcome"
        self.key_status = {
            pygame.K_s: False,
            pygame.K_w: False,
            pygame.K_SPACE: False
        }
        self.mouse_buttons = [False, False]
        self.mouse_pos = [0, 0]
        # Import images and sounds
        # quack = pygame.mixer.Sound("assets\sounds\Quack Sound Effect.mp3")

    def run(self):
        while True:
            #Get Inputs
            self.getInputs()

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

            # Update the Screen
            pygame.display.flip()
            self.clock.tick(60)

    def getInputs(self):
        self.mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:

                # MAKE THIS A FLAG FOR END OF LOOP!
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key in self.key_status:
                    self.key_status[event.key] = True
            elif event.type == pygame.KEYUP:
                if event.key in self.key_status:
                    self.key_status[event.key] = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 0:
                    self.mouse_buttons[event.button] = True
                elif event.button == 1:
                    self.mouse_buttons[event.button] = True

    def welcome(self):
        # This is the game loop for the welcome screen
        print("WELCOMING!")
        if self.key_status[pygame.K_SPACE]:
            self.scene = "draw"

    def draw(self):
        print("DRAWING!")
        # This is the game loop for the drawing screen
        if self.key_status[pygame.K_w]:
            self.scene = "guess"
        return

    def guess(self):
        print("GUESSING!")
        if self.key_status[pygame.K_s]:
            self.scene = "welcome"
        # This is the game loop for the guessing screen
        return

    def game_over(self):
        # This is the game loop for the game over screen
        return

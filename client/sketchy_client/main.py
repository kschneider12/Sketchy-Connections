# Sketchy Connections
# CS3050 Final Project
# Kent Schneider, Mathew Neves, James LeMahieu, Joe Liotta
import pygame

from .Engine import Engine

# We will need plenty of other screens, but this is a proof of concept for simple structure
'''
Other screens may include: Naming a user, selecting host or join for multiplayer, options, stats,
store, creating prompts, voting, etc. Many of which could be late game, but by having this global
variable that enables a scene switch, it could be super easy to add new screens! (It won't switch to a new
screen until that particular screen tells it to, because that's the only loop getting called)
Also, many screens will reuse code, so we will absolutely have different functions called from multiple game loops.
But I still think the core loop should be independent for each screen because they need to behave differently,
and for organizational purposes.
'''
def main():
    # Init Pygame
    pygame.init()
    pygame.mixer.init()

    # Create and run game
    engine = Engine()
    engine.run()


if __name__ == '__main__':
    main()

    '''
    PYGAME DOCUMENTATION:
    
        loading an image:
       player_img = pygame.image.load("assets\sprites\\player.png")
       
       putting image on screen:
            screen.blit(player_img, (player_x,player_y))

       
       Fills backdrop:
            screen.fill((255, 255, 255))
    
    Drawing rectangle objects:
        
        create rectangle
            ground = pygame.Rect(0, 400, 960, 50) 
        
        in game loop:
            pygame.draw.rect(screen, (100, 255, 0), ground)
            
    Text:
        font = pygame.font.Font(f"{FILEPATH}\\fonts\\nameOfFont.ttf", 20) < font size

         text_surface = font.render(f"",True, (255, 0, 0))
         
         V These work on rectangles too, with .center for positioning (also corner!)
        text_rect = text_surface.get_rect()
        text_rect.center = (778, 265)
        
    Audio:
    The mixer is already initialized, so it super straightforward.
    quack = pygame.mixer.Sound("assets\sounds\Quack Sound Effect.mp3")
    quack.play()
        
    
    
    
    
    
    '''

# Sketchy Connections
# CS3050 Final Project
# Kent Schneider, Mathew Neves, James LeMahieu, Joe Liotta
"""
Main file for the program
"""
import pygame

from .engine import Engine

def main():
    """
    main function that holds and begins Engine
    """
    # Init Pygame
    pygame.init() # pylint: disable=no-member
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

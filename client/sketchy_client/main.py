# Sketchy Connections
# CS3050 Final Project
# Kent Schneider, Mathew Neves, James LeMahieu, Joe Liotta
"""
Main file for the program
"""
import sys
import os
import pygame
if hasattr(sys, '_MEIPASS'):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

sys.path.append(os.path.join(BASE_DIR, "client"))
sys.path.append(os.path.join(BASE_DIR, "shared"))
try:
    # Package execution path (python -m sketchy_client.main)
    from .engine import Engine
except ImportError:
    # Script/frozen execution path (e.g. PyInstaller bootloader)
    from sketchy_client.engine import Engine
def main():
    """
    main function that holds and begins Engine
    """
    # Init Pygame
    pygame.init() # pylint: disable=no-member

    # Create and run game
    engine = Engine()
    engine.run()


if __name__ == '__main__':
    main()

    '''
    MAC:
    pyinstaller --onefile --windowed \
    --paths client \
    --paths shared \
    --add-data "client/assets:assets" \
    --icon=client/assets/textures/desktop_icon.icns \
    client/sketchy_client/main.py
    
    WINDOWS:
    pyinstaller --onefile --windowed ^
    --icon=client\assets\textures\desktop_icon.ico ^
    --paths client ^
    --paths shared ^
    --add-data "client/assets;assets" ^
    client\sketchy_client\main.py
    '''
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

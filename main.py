# Sketchy Connections
# CS3050 Final Project
# Kent Schneider, Mathew Neves, James LeMahieu, Joe Liotta
import pygame
from Engine import Engine

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
if __name__ == '__main__':
    # Init Pygame
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Sketchy Connections")

    # Create and run game
    engine = Engine()
    engine.run()


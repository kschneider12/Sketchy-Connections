# Sketchy Connections
# CS3050 Final Project
# Kent Schneider, Mathew Neves, James LeMahieu, Joe Liotta

global screen

# Testing - Mat added

import pygame

DRAWING_GRID_HEIGHT = 256
DRAWING_GRID_WIDTH = 256
GRID_SQUARE = 1
PIXEL_HEIGHT = DRAWING_GRID_HEIGHT * GRID_SQUARE
PIXEL_WIDTH = DRAWING_GRID_WIDTH * GRID_SQUARE

COLORS = {
    'pen' : (0, 0, 0),
    'window' : (252, 252, 252)
}

# A cell in a grid - allows it to be drawn?
class GridCell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.color = COLORS['window']
        self.neighbors = []

    def position(self):
        return self.row, self.col

    def draw(self, window):
        pygame.draw.rect(window, self.color,
                         (self.row, self.col, GRID_SQUARE, GRID_SQUARE))

    def update(self, grid):
        pass

# Needed to build grid
class Grid:
    def __init__(self):
        pass


# Legacy - Kent added


def welcome():
    #This is the game loop for the welcome screen
    return

def draw():
    #This is the game loop for the drawing screen
    return

def guess():
    #This is the game loop for the guessing screen
    return

def game_over():
    #This is the game loop for the game over screen
    return

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
    screen = "welcome"
    while True:
        #MAIN GAME LOOP
        #Global var storing which phase of the game we are in
        match screen:
            case "welcome":
                welcome()
            case "draw":
                draw()
            case "guess":
                guess()
            case "game_over":
                game_over()


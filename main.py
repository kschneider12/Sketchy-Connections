# Sketchy Connections
# CS3050 Final Project
# Kent Schneider, Mathew Neves, James LeMahieu, Joe Liotta

global screen

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


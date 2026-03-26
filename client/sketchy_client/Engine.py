import pygame
import pyautogui
from pygame.constants import K_KP_ENTER

from .Button import Button
from .CheckboxButton import CheckboxButton
from .ChoicesButton import ChoicesButton
from .BrightnessSlider import BrightnessSlider
from .DefaultUI import DefaultUI, TransparentUI, TextUI
from .TimeBar import TimeBar
from .ColorButton import ColorButton
from .draw_window import Grid
from sketchy_shared.types import GamePhase, GameStateData, PlayerData, BookData, RoomPhase, RoomData, EntryData, EntryType
from .network_client import NetworkClient, NetworkClientError
from .TypeBox import TypeBox
from .SliderButton import SliderButton
from .draw_window import DrawingWindow, AnimationWindow
from .ColorWheel import ColorWheel
# from draw_window import AnimationWindow

SCREEN_LEN = pyautogui.size()[0] / 2
SCREEN_HT = pyautogui.size()[1] / 2

class Engine:
    def __init__(self):
        # flags
        self.exit = False
        self.drawing = False

        #pygame info
        self.screen = pygame.display.set_mode((SCREEN_LEN, SCREEN_HT))
        pygame.display.set_caption("Sketchy Connections")
        self.clock = pygame.time.Clock()

        # Input management
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
        self.mouse_pos = (0, 0)
        self.keystrokes = []
        self.type_text_draws = []

        # UI Management
        self.scene = "welcome"
        self.draw_order = []
        self.active_ui = []
        self.active_buttons = []
        self.active_animations = []
        self.active_drawings = []
        self.frame = 0
        self.curr_color = [120,250,250]
        self.curr_shade = [0,0,0]
        self.curr_brush = 1
        self.brush_index = 0
        self.curr_tool = "brush"
        self.tool_index = 0
        self.curr_name = None
        self.curr_guess = None
        self.curr_prompt = None
        self.room_code_attempt = None

        # Backend game state management
        self.network: NetworkClient = NetworkClient()
        self.room: RoomData = RoomData()
        self.player: PlayerData = PlayerData()
        self.network_error = None
        self.last_submission = ""


    def run(self):
        self.switchToWelcome()
        while True:
            if self.room.game:
                print(self.room.game.phase)

            self.room = self.network.room
            if self.network_error is not None:
                print(self.network_error)
                self.network_error = None
            self.frame += 1
            if self.frame > 65535:
                self.frame = 0
            self.type_text_draws = []
            self.mouse_buttons_last_frame[0] = self.mouse_buttons[0]
            self.mouse_buttons_last_frame[1] = self.mouse_buttons[1]
            self.getInputs()
            self.manageButtons()

            if self.room.phase == RoomPhase.PLAYING:
                if self.scene != self.room.game.phase:
                    match self.room.game.phase:
                        case 'writing':
                            self.switchToWriting()
                        case 'drawing':
                            self.switchToDraw()
                        case 'guessing':
                            self.switchToGuessing()

            # Behaviors depending on scene
            match self.scene:
                case "welcome":
                    self.welcome()
                case "lobby":
                    self.lobby()
                case "writing":
                    self.writing()
                case "drawing":
                    self.draw()
                case "guessing":
                    self.guess()
                case "results":
                    self.results()
            if self.exit:
                self.network.close()
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

            # added by Mat for drawing window
            if self.scene == "draw":
                for drawing_win in self.active_drawings:
                    drawing_win.handle_clicks(event)

        if self.key_status[pygame.K_RETURN]:
            self.keystrokes.append("enter")
        if self.key_status[pygame.K_BACKSPACE]:
            self.keystrokes.append("backspace")
        if self.key_status[pygame.K_ESCAPE]:
            self.exit = True

    def drawUI(self):
        self.screen.fill((50, 100, 100))
        for elem in self.draw_order:
            if isinstance(elem, TimeBar):
                if elem.time_up():
                    print("time up!")
                    self.submit()
            elem.draw(self.screen, self.curr_color)
        for data in self.type_text_draws:
            # NEED TO SEPARATE FROM NORMAL DRAWS! TWO DIFFERENT VECTORS
            self.drawTypingText(data)

    #TODO: SETTINGS NEED TO BE PRESERVED WHEN BUTTONS DIE! (STORE IN ENGINE AND IMPORT UPON CREATION!)
    def manageButtons(self):
        just_clicked = [not self.mouse_buttons_last_frame[0] and self.mouse_buttons[0],
                        not self.mouse_buttons_last_frame[1] and self.mouse_buttons[1]]
        for button in self.active_buttons:
            if button.active or isinstance(button, TypeBox):
                output = button.behave(self.mouse_pos, just_clicked, self.keystrokes, self.mouse_buttons)
                if isinstance(output, list):
                    if len(output) == 2:
                        #slider bar
                        output[0](output[1])
                    else:
                        #output[:-1] is the return value- store when the submit button is pressed
                        output[-1](output[-2])
                        self.type_text_draws.append(output[:-1])
                if callable(output):
                    output()


    def welcome(self):
        # This is the game loop for the welcome screen
        return

    def lobby(self):
        return

    def writing(self):
        return

    def draw(self):
        # added by Mat for drawing window
        keys = pygame.key.get_pressed()
        for drawing_win in self.active_drawings:
            drawing_win.update(
                self.mouse_pos,
                self.mouse_buttons[0],
                self.curr_shade,
                self.curr_brush,
                self.curr_tool
            )

    def guess(self):
        return

    def results(self):
        # This is the game loop for the game over screen
        for animation in self.active_animations:
            animation.update(False)


    # When any timer in the game runs out, figure out which timer it was and behave accordingly
    def time_up(self):
        match self.scene:
            case "write":
                self.switchToDraw()
            case "draw":
                self.switchToGuessing()
            case "guess":
                # Switching to do animation debug
                self.switchToResults()

    # normalize position as a percent (0-100) for distance across screen
    def np(self, x, y):
        return int(x * SCREEN_LEN / 100), int(y * SCREEN_HT / 100)
    # normalize scale in relation to screen size
    def ns(self, x, y):
        return x * SCREEN_LEN / 1000, y * SCREEN_HT / 1000 * 16/10

#------------------------------------------------------------------------------------------------
#Button Commands listed below
#------------------------------------------------------------------------------------------------
    def switchToWelcome(self):
        self.scene = "welcome"
        self.active_ui = [DefaultUI(self.np(50, 30), self.ns(169 * 3.5, 97 * 3.5), "assets/textures/title.png")]
        self.active_buttons = [
            Button(self.np(30, 70), (self.ns(115 * 2.2, 51 * 2.2)), "assets/textures/host.png", self._start_room),
            #Button(self.np(30, 70), (self.ns(115 * 2.2, 51 * 2.2)), "assets/textures/host.png", self.switchToLobby),

            Button(self.np(70, 70), (self.ns(115 * 2.2, 51 * 2.2)), "assets/textures/join.png", self.enableRoomCode),
            TypeBox(self.np(50, 90), self.ns(1300 * 0.6, 110 * 0.6), "assets/textures/text_box_5.png", self.setName,"Enter A Name",25)]
            #CheckboxButton(self.np(50,50), self.ns(40, 40), self.checkBoxTest, "HIII"),
            #ChoicesButton(self.np(70,50), self.ns(80,40), self.checkBoxTest, [0,1,'NICO','RYAN','KENT','LAUREL', 'SOPHIE'])]
        self.active_drawings = []
        self.draw_order = self.active_buttons + self.active_drawings + self.active_ui + self.active_animations

    def switchToLobby(self):
        self.scene = "lobby"
        self.active_animations = []
        self.active_ui = [DefaultUI(self.np(10, 5), self.ns(130 * 1.5, 50 * 1), "assets/textures/players.png"),
                          DefaultUI(self.np(80, 18), self.ns(169 * 2.0, 97 * 2.0), "assets/textures/title.png"),
                          DefaultUI(self.np(4, 55), self.ns(30 * 2.4, 241 * 2.4), "assets/textures/players_tab.png"),
                          TextUI(self.np(80, 40), self.ns(0, 50), "Room Code:", (0, 0, 0)),
                          TextUI(self.np(80, 50), self.ns(0, 50), self.network.room.room_id, (0,0,0))]
        if self.player.is_host:
            self.active_buttons = [
                Button(self.np(88, 90), (self.ns(115 * 1.8, 51 * 1.8)), "assets/textures/play.png", self.startGame),
                Button(self.np(65, 90), (self.ns(115 * 1.8, 51 * 1.8)), "assets/textures/options.png", self.startGame)]
        else:
            self.active_buttons = []
        self.active_drawings = []
        self.draw_order = self.active_buttons + self.active_drawings + self.active_ui + self.active_animations


    def switchToWriting(self):
        self.scene = "writing"
        self.active_ui = [TimeBar(self.np(92,50), self.ns(60 * 1.5, 270 * 1.5), 10),
                          TextUI(self.np(50, 10), self.ns(100,100), "PROMPT: GET PREVIOUS PROMPT HERE", (0,0,0))]
        self.active_buttons = [TypeBox(self.np(45,50), self.ns(1300 * 0.6, 110 * 0.6), "assets/textures/text_box_5.png", self.setCurrPrompt, "Enter A Prompt"),
                               Button(self.np(50,90), (self.ns(140 * 2.2, 51 * 2.2)), "assets/textures/submit.png", self.submit),
                               SliderButton(self.np(20, 20), self.ns(300,30),0, 100, self.setSoundEffectsVolume)]
        self.draw_order = self.active_buttons + self.active_drawings + self.active_ui + self.active_animations

    def switchToGuessing(self):
        self.scene = "guessing"
        self.active_ui = [TimeBar(self.np(92,50), self.ns(60 * 1.5, 270 * 1.5), 10)]
        self.active_buttons = [TypeBox(self.np(50, 80), self.ns(1300 * 0.6, 70 * 0.6), "assets/textures/text_box_5.png", self.setCurrGuess,"Type A Response")]
        self.draw_order = self.active_buttons + self.active_drawings + self.active_ui + self.active_animations

    def switchToDraw(self):
        # note from Mat - this makes the drawing window displayable, but it does not fully work...it is just there for now.
        self.scene = "drawing"
        self.active_ui = [TimeBar(self.np(92,50), self.ns(60 * 1.5, 270 * 1.5), 10)]
        self.active_buttons = [
            ColorWheel(self.np(50, 85), (self.ns(180, 180)), self.setColor),
            BrightnessSlider(self.np(70, 80), (self.ns(1 * 50, 4 * 50)), self.setBrightness),
        #   ColorButton(self.np(10, 80), self.ns(40, 40), self.setColor, "red"),
        #   ColorWheel(self.np(50,85), (self.ns(180,180)), self.setColor)
            Button(self.np(80, 95), self.ns(60, 60), "assets/textures/submit.png", self.setBrushThickness),
            Button(self.np(90, 95), self.ns(60, 60), "assets/textures/submit.png", self.setCurrentTool)]
        # Mat changed this line
        self.active_drawings = [DrawingWindow(self.np(50,50), self.ns(845 * 0.5, 455 * 0.5))]
        self.draw_order = self.active_buttons + self.active_drawings + self.active_ui + self.active_animations

    def switchToResults(self):
        self.scene = "results"
        self.active_ui = []
        self.active_buttons = [
            Button(self.np(80, 95), (self.ns(140 * 2.2, 51 * 2.2)), "assets/textures/submit.png", self.switchToLobby)

        ]
        pixels = []
        if self.active_drawings:
            pixels = self.active_drawings[0].get_drawn_pixels()

        self.active_animations = [
            AnimationWindow(self.np(50, 50), self.ns(845, 455), pixels)
        ]
        self.active_drawings = []
        self.draw_order = self.active_buttons + self.active_drawings + self.active_ui + self.active_animations

    def enableRoomCode(self):
        if self.curr_name:
            for button in self.active_buttons:
                button.active = False
            self.active_ui.append(TransparentUI(self.np(50,50),self.ns(SCREEN_LEN * 2,SCREEN_HT * 2), (0,0,0), 150))

            self.active_buttons.append(Button(self.np(60, 60), (self.ns(140 * 1.2, 51 * 1.2)), "assets/textures/join.png", self._join_room, z=2))
            self.active_buttons.append(Button(self.np(40, 60), (self.ns(140 * 1.2, 51 * 1.2)), "assets/textures/join.png", self.disableRoomCode, z=2))
            self.active_buttons.append(TypeBox(self.np(50, 40), (self.ns(150 * 1, 64 * 1)), "assets/textures/text_box_4.png", self.setRoomCode, "CODE", 4, 2))

            self.draw_order = self.active_buttons + self.active_drawings + self.active_ui + self.active_animations
            self.draw_order = sorted(self.draw_order, key=lambda elem: elem.z)

    def disableRoomCode(self):
        self.active_ui.pop()
        self.active_buttons.pop()
        self.active_buttons.pop()
        self.active_buttons.pop()
        self.draw_order = self.active_buttons + self.active_drawings + self.active_ui + self.active_animations
        self.draw_order = sorted(self.draw_order, key=lambda elem: elem.z)
        for button in self.active_buttons:
            button.active = True
            #TODO: generate box to get room code, including button

    def startGame(self):
        self.network.start_game()
        return

    def drawText(self, vec):
        if len(vec) == 4:
            text = vec[0]
            pos = vec[1]
            font = vec[2]
            color = vec[3]
            text_surface = font.render(text, True, color)
            self.screen.blit(text_surface, pos)

    def drawTypingText(self, vec):
        if len(vec[-1]) > 0 and vec[4] - len(vec[-1]) < vec[4] / 2 + 1: # ONLY SHOWS UP IF YOU'RE CLOSE
            self.drawText([str(vec[4] - len(vec[-1])), (vec[-2], vec[1][1]), vec[2], (100,100,100)])

        self.drawText(vec[:-3])
        #(self.pos[0] - self.width / 2.2, self.pos[1] - self.height / 3)

    def _start_room(self):
        #would be nice to have index passed in too, so client already knows what their ID is, to easily access themselves inside Room
        player_name = self.curr_name.strip()
        if not player_name:
            self.network_error = "Enter a name first."
            return
        try:
            self.network.create_room(player_name)
        except NetworkClientError as exc:
            self.network_error = str(exc)
            return

        self.room = self.network.room
        self.player = self.network.player

        print(f"ROOM STARTED BY {self.player.name} ({self.room.room_id})")
        self.switchToLobby()

    def _join_room(self):
        if self.room_code_attempt and len(self.room_code_attempt) == 4:
            room_code = self.room_code_attempt.strip()
            name = self.curr_name.strip()
            if not room_code:
                self.network_error = "Enter a code first."
                return
            try:
                #TODO: Replace with entered name
                self.network.join_room(name, room_code)
            except NetworkClientError as exc:
                self.network_error = str(exc)
                return

            self.room = self.network.room
            self.player = self.network.player

            print(f"ROOM {self.room.room_id} JOINED BY {self.player.name}")
            self.switchToLobby()

    #------------------------------------------------------------------------------------------------
    #Animation and Audio listed below
    #------------------------------------------------------------------------------------------------
    # Will figure out how to send animation soon

    def setSoundEffectsVolume(self, volume):
        return

    def setMusicVolume(self, volume):
        return

    def setGlobalVolume(self, volume):
        return

    def setColor(self, color):
        self.curr_color = color

    def setBrightness(self, val):
        self.curr_shade[0] = self.curr_color[0] * val
        self.curr_shade[1] = self.curr_color[1] * val
        self.curr_shade[2] = self.curr_color[2] * val

    def checkBoxTest(self, val):
        print(self.last_submission)
        self.player_name = val
        print(self.player_name)

    def setBrushThickness(self):
        thickness = [1, 2, 4]
        self.brush_index = (self.brush_index + 1) % len(thickness)
        self.curr_brush = thickness[self.brush_index]
        print("Brush thickness:", self.curr_brush)

    def setCurrentTool(self):
        tools = ["brush", "fill"]
        self.tool_index = (self.tool_index + 1) % len(tools)
        self.curr_tool = tools[self.tool_index]
        print("Current tool:", self.curr_tool)

    def setName(self, name):
        self.curr_name = name

    def setCurrPrompt(self, prompt):
        self.curr_prompt = prompt

    def setCurrGuess(self, guess):
        self.curr_guess = guess

    def setRoomCode(self, code):
        self.room_code_attempt = code.upper()

    def submit(self):
        if self.scene == "writing":
            self.network.submit_entry(self.curr_prompt)
        if self.scene == "drawing":
            self.network.submit_entry(self.active_drawings[0].drawn_pixels)
        self.network.sync()

    #Kent's to-dos
    #DONE: COLOR BUTTONS
    #DONE: COLOR WHEEL
    #TODO: COLOR BRIGHTNESS BAR
    #TODO: LIST PLAYERS UI FIX
    #TODO: PEN SIZE BUTTONS
    #DONE: SLIDER SETTINGS BUTTON TYPE
    #TODO: SELECT OPTIONS TYPE OF BUTTON (SETTINGS)
    #TODO: REARRANGE BUTTONS ON SCREEN
    #TODO: SLIDER WITH SCROLL WHEEL FOR RESULTS
    #TODO: RESULTS DEFAULT DATA
    #TODO: SOUND BOARD/SFX/MUSIC
    #TODO: MORE ART
    #TODO: OPTIONS MENU COMPLETE
    #TODO: SHOP OPTIONS/SCORING
    #TODO: VOTING UI?

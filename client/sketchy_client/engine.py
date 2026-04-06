"""
handles all client-side interface logic, including all
elements for the player. All other elements pass through
Engine, as it is the connector between frontend and
backend
"""
import pygame
import pyautogui
import csv
import random
from pygame.constants import K_KP_ENTER # pylint: disable=no-name-in-module

from sketchy_shared.types import PlayerData, RoomPhase, RoomData, BookData, EntryData, EntryType
from .button import Button
from .checkbox_button import CheckboxButton
from .paths import resolve_asset_path
from .slide_down_button import SlideDownButton
from .pen_type_button import PenTypeButton
from .brightness_slider import BrightnessSlider
from .default_ui import DefaultUI, TransparentUI, TextUI, PlayerDisplay, MouseStick
from .sound_manager import SoundManager
from .time_bar import TimeBar
#from .ColorButton import ColorButton
#from .draw_window import Grid
from .network_client import NetworkClient, NetworkClientError
from .type_box import TypeBox
from .slider_button import SliderButton
from .draw_window import DrawingWindow, AnimationWindow
from .color_wheel import ColorWheel
from .choices_button import ChoicesButton
# from draw_window import AnimationWindow
SCREEN_LEN = pyautogui.size()[0] / 2
SCREEN_HT = pyautogui.size()[1] / 2

PROMPT_TIMES = [10, 20, 30, 60]
DRAW_TIMES = [30, 60, 120, 180, 300]

class Engine:
    """Initialization of Engine, including the screen, UI elements,
    vectors that store UI data, input collection, and server
    connectivity elements"""
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
            pygame.K_s: False,  # pylint: disable=no-member
            pygame.K_w: False,  # pylint: disable=no-member
            pygame.K_SPACE: False,  # pylint: disable=no-member
            pygame.K_BACKSPACE: False,  # pylint: disable=no-member
            pygame.K_RETURN: False, # pylint: disable=no-member
            pygame.K_ESCAPE: False  # pylint: disable=no-member
        }
        self.mouse_buttons = [False, False, 0]
        self.mouse_buttons_last_frame = [False, False]
        self.mouse_pos = (0, 0)
        self.keystrokes = []
        self.type_text_draws = []

        # Sound management
        self.sfx_volume = 100
        self.music_volume = 100

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
        self.brightness = 1
        self.curr_brush = 1
        self.brush_index = 0
        self.curr_tool = "brush"
        self.tool_index = 0
        self.curr_name = None
        self.curr_guess = None
        self.curr_prompt = None
        self.room_code_attempt = None
        self.tool_text = "brush"
        self.background = DefaultUI(self.np(50, 50),
                                     (SCREEN_LEN, SCREEN_HT),
                                     "assets/textures/background.png")

        self.simple_colors = False
        self.prompt_length = 20
        self.draw_length = 120

        # Backend game state management
        self.network: NetworkClient = NetworkClient()
        self.room: RoomData = RoomData()
        self.player: PlayerData = PlayerData()
        self.current_entry: EntryData | None = None # Safe to access after first prompt, look at impl for fields
        self.current_entry_type: EntryType = EntryType.PROMPT # When drawing this has type PROMPT, when guessing this has type DRAWING
        self.books: list[BookData] | None = None # This only gets set when we have reached results!!
        self.network_error = None
        self.submitted = False
        self.last_submission = ""
        self.paused = False

        # Results page
        self.results_height = 0


    def run(self):
        """main game loop. Updates the game, manages inputs, buttons,
        draws UI, handles special loop cases, and maintains the game clock"""
        self.switch_to_welcome()
        while True:
            self.update_room()
            if self.network_error is not None:
                print(self.network_error)
                self.network_error = None
            self.frame += 1
            if self.frame > 65535:
                self.frame = 0
            self.type_text_draws = []
            self.mouse_buttons_last_frame[0] = self.mouse_buttons[0]
            self.mouse_buttons_last_frame[1] = self.mouse_buttons[1]
            self.get_inputs()
            self.manage_buttons()

            if self.room.phase == RoomPhase.PLAYING:
                if self.room.game and self.scene != self.room.game.phase:
                    self.submitted = False
                    match self.room.game.phase:
                        case 'writing':
                            self.switch_to_writing()
                        case 'drawing':
                            self.switch_to_draw()
                        case 'guessing':
                            self.switch_to_guessing()
            elif self.room.phase == RoomPhase.RESULTS:
                if self.room.game.books and self.scene != self.room.phase:
                    self.books = self.room.game.books
                    self.switch_to_results()
            # Behaviors depending on scene
            if self.scene == "drawing":
                self.draw()
            elif self.scene == "results":
                self.results()
            if self.exit:
                self.network.close()
                pygame.quit()
                break

            # Update the Screen
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)

    def update_room(self):
        self.room = self.network.room

        if self.room.game:
            if self.room.game.current_prompt:
                self.current_entry = self.room.game.current_prompt
                self.current_entry_type = self.current_entry.type
            if self.room.game.books:
                self.books = self.room.game.books

    def get_inputs(self):
        """Collects all inputs from the user every frame, and stores it
        within Engine to be accessed by any other functions."""
        self.keystrokes = []
        self.mouse_buttons[2] = 0
        self.key_status[K_KP_ENTER] = False
        #self.key_status[K_BACKSPACE] = False
        self.mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # pylint: disable=no-member
                self.exit = True
            if event.type == pygame.TEXTINPUT: # pylint: disable=no-member
                self.keystrokes.append(event.text)
            elif event.type == pygame.KEYDOWN: # pylint: disable=no-member
                if event.key in self.key_status:
                    self.key_status[event.key] = True
                    if event.key == pygame.K_ESCAPE: # pylint: disable=no-member
                        self.pause_client(True)
            elif event.type == pygame.KEYUP: # pylint: disable=no-member
                if event.key in self.key_status:
                    self.key_status[event.key] = False
            elif event.type == pygame.MOUSEBUTTONDOWN: # pylint: disable=no-member
                if event.button == 1:
                    self.mouse_buttons[0] = True
                elif event.button == 3:
                    self.mouse_buttons[1] = True
            elif event.type == pygame.MOUSEBUTTONUP: # pylint: disable=no-member
                if event.button == 1:
                    self.mouse_buttons[0] = False
                elif event.button == 3:
                    self.mouse_buttons[1] = False
            elif event.type == pygame.MOUSEWHEEL:
                self.mouse_buttons[2] = event.y

            # added by Mat for drawing window
            if self.scene == "draw":
                for drawing_win in self.active_drawings:
                    drawing_win.handle_clicks(event)

        if self.key_status[pygame.K_RETURN]: # pylint: disable=no-member
            self.keystrokes.append("enter")
        if self.key_status[pygame.K_BACKSPACE]: # pylint: disable=no-member
            self.keystrokes.append("backspace")

    def draw_ui(self):
        """UI manager that draws UI to the screen. Also
        handles TimeBar, as this is where the UI TimeBar is
        accessed every frame."""
        self.screen.fill((50, 100, 100))
        self.background.draw(self.screen)
        for elem in self.draw_order:
            if isinstance(elem, TimeBar):
                if elem.time_up():
                    print("time up!")
                    self.submit(True)
            elif isinstance(elem, PlayerDisplay):
                elem.set_active_players(self.network.room.players)
            elif isinstance(elem, PenTypeButton):
                elem.set_selection(self.curr_brush)
            elif isinstance(elem, MouseStick):
                elem.behave(self.mouse_pos, self.get_pen_state())
            elem.draw(self.screen, self.curr_color)
        if not self.paused: #THIS IS BETTER THAN RECONFIGURING HOW THIS TEXT IS DRAWN!
            for data in self.type_text_draws:
                self.draw_typing_text(data)
        if self.scene == "drawing":
            if self.curr_shade == [240, 240, 240] and \
                self.curr_tool == "fill":
                self.tool_text.text = "eraser fill"
            elif self.curr_shade == [240, 240, 240] and \
                    self.curr_tool == "brush":
                self.tool_text.text = "eraser brush"
            else:
                self.tool_text.text = "draw " + self.curr_tool

    def manage_buttons(self):
        """manages all active buttons on screen, running behavior
        and handling any output in any variation"""
        just_clicked = [not self.mouse_buttons_last_frame[0] and self.mouse_buttons[0],
                        not self.mouse_buttons_last_frame[1] and self.mouse_buttons[1]]
        for button in self.active_buttons:
            if button.active or isinstance(button, TypeBox):
                output = button.behave(self.mouse_pos, just_clicked,
                                       self.keystrokes, self.mouse_buttons, self.paused)
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
            if self.paused and not button.pause_override:
                button.curr_hover = False

    def draw(self):
        """game loop for drawing screen"""
        # added by Mat for drawing window
        #keys = pygame.key.get_pressed()
        if not self.submitted and not self.paused:
            for drawing_win in self.active_drawings:
                drawing_win.update(
                    self.mouse_pos,
                    self.mouse_buttons[0],
                    self.curr_shade,
                    self.curr_brush,
                    self.curr_tool
                )

    def results(self):
        """game loop for the game over screen"""
        for animation in self.active_animations:
            animation.update(False)

    def time_up(self):
        """accessed when any timer runs out, this manages logic
        when time runs out"""
        match self.scene:
            case "write":
                self.switch_to_draw()
            case "draw":
                self.switch_to_guessing()
            case "guess":
                # Switching to do animation debug
                self.switch_to_results()

    # normalize position as a percent (0-100) for distance across screen
    def np(self, x, y):
        """short for normalize position, this normalizes UI elements
        regardless of screen size"""
        return [int(x * SCREEN_LEN / 100), int(y * SCREEN_HT / 100)]

    # normalize scale in relation to screen size
    def ns(self, x, y):
        """short for normalize scale, this normalizes UI elements
        regardless of screen size"""
        return x * SCREEN_LEN / 1000, y * SCREEN_HT / 1000 * 16/10

    def nl(self, x):
        """short for normalize length, this normalizes draw window length
        regardless of screen size"""
        return x * SCREEN_LEN / 1000.0, x * SCREEN_LEN / 1000.0 * 175/325.0

    #TODO: Drawing only starts when you click on canvas

#------------------------------------------------------------------------------------------------
#Button Commands listed below
#------------------------------------------------------------------------------------------------
    def switch_to_welcome(self):
        """switches the scene to welcome, initializing the UI."""
        self.scene = "welcome"
        self.active_ui = [DefaultUI(self.np(50, 30), self.ns(169 * 3.5, 97 * 3.5),
                                    "assets/textures/title.png")]
        self.active_buttons = [
            Button(self.np(30, 70), (self.ns(115 * 2.2, 51 * 2.2)),
                   "assets/textures/host.png", self._start_room),
            #Button(self.np(30, 70),
            #(self.ns(115 * 2.2, 51 * 2.2)), "assets/textures/host.png", self.switch_to_lobby),

            Button(self.np(70, 70), (self.ns(115 * 2.2, 51 * 2.2)),
                   "assets/textures/join.png", self.enable_room_code),
            Button(self.np(97, 4), (self.ns(50, 50)),
                   "assets/textures/exit.png", self.quit_game),
            TypeBox(self.np(50, 90), self.ns(1300 * 0.6, 110 * 0.6),
                    "assets/textures/text_box_5.png", self.set_name,"Enter A Name",15)]
        #SlideDownButton(self.np(90, 0), (self.np(0, 20), self.np(0,80)), self.ns(10,50), self.slider_control)
        self.active_drawings = []
        self.draw_order = self.active_buttons + self.active_drawings +\
                          self.active_ui + self.active_animations
        self.pause_client()
        SoundManager.get_instance().play_music("assets/audio/RadioMartini.mp3")

    def switch_to_lobby(self):
        """switches the scene to lobby, initializing the UI."""
        self.scene = "lobby"
        self.active_animations = []
        self.active_ui = [DefaultUI(self.np(10, 5), self.ns(130 * 1.5, 50 * 1),
                                    "assets/textures/players.png"),
                          DefaultUI(self.np(80, 18), self.ns(169 * 2.0, 97 * 2.0),
                                    "assets/textures/title.png"),
                          PlayerDisplay(self.np(4, 55), self.ns(30 * 2.4, 241 * 2.4),
                                        (SCREEN_LEN, SCREEN_HT), self.network.room.players),
                          DefaultUI(self.np(35, 5), self.ns(65 * 2, 23 * 2),
                                    "assets/textures/code.png"),
                          #DefaultUI(self.np(50, 5.5), self.ns(160, 60),
                                    #"assets/textures/text_box_4.png"),
                          TextUI(self.np(50, 5), self.ns(0, 60),
                                 self.network.room.room_id.lower(), (0,0,0))]
        if self.player.is_host:
            self.active_buttons = [
                Button(self.np(88, 90), (self.ns(115 * 1.8, 51 * 1.8)),
                       "assets/textures/play.png", self.start_game),
                CheckboxButton(self.np(70, 76), self.ns(40, 40),
                               self.simple_color_select, "Simple Colors", False),
                ChoicesButton(self.np(79.5, 55), self.ns(90, 40),
                              self.prompt_time_length, PROMPT_TIMES, 20),
                ChoicesButton(self.np(79.5,68), self.ns(90,40),
                                  self.draw_time_length, DRAW_TIMES, 120)

            ]
            self.active_ui.append(DefaultUI(self.np(80, 41), self.ns(240, 49),
                                "assets/textures/text_box_4.png"))
            self.active_ui.append(
                DefaultUI(self.np(80, 41), self.ns(173, 43),
                          "assets/textures/options_txt.png"))
            self.active_ui.append(
                TextUI(self.np(80, 49), self.ns(0, 30),
                       "Write Time", (0, 0, 0)))
            self.active_ui.append(
                TextUI(self.np(80, 62), self.ns(0, 30),
                       "Draw Time", (0, 0, 0)))
        else:
            self.active_buttons = []
        self.active_drawings = []
        self.draw_order = self.active_buttons + self.active_drawings +\
                          self.active_ui + self.active_animations
        self.pause_client()

        SoundManager.get_instance().play_music("assets/audio/KoolKats.mp3")



    def switch_to_writing(self):
        """switches the scene to writing, initializing the UI."""
        self.scene = "writing"
        self.active_ui = [TimeBar(self.np(92,50), self.ns(60 * 1.5, 270 * 1.5), self.prompt_length),
                          TextUI(self.np(50, 10), self.ns(100,100),
                                 "Create a Prompt!", (0,0,0))]
        self.active_buttons = [TypeBox(self.np(45,50), self.ns(1300 * 0.6, 110 * 0.6),
                                       "assets/textures/text_box_5.png",
                                       self.set_curr_prompt, "Enter A Prompt"),
                               Button(self.np(50,90), (self.ns(140 * 2.2, 51 * 2.2)),
                                      "assets/textures/submit.png", self.submit),
                               # SliderButton(self.np(20, 20), self.ns(300,30),
                               #           0, 100, self.set_sound_effects_volume)
                                      ]
        self.draw_order = self.active_buttons + self.active_drawings +\
                          self.active_ui + self.active_animations
        self.pause_client()

        SoundManager.get_instance().play_music("assets/audio/Hackbeat.mp3")

    def switch_to_guessing(self):
        """switches the scene to guessing, initializing the UI."""
        self.scene = "guessing"
        pygame.mouse.set_visible(True)
        self.active_ui = [TimeBar(self.np(92,43), self.ns(60 * 1.5, 270 * 1.5), self.prompt_length),
                          DefaultUI(self.np(36, 43), self.ns(650, 400),
                                    "assets/textures/color_button.png")
        ]
        self.active_buttons = [TypeBox(self.np(50, 86), self.ns(1550 * 0.6, 70 * 0.6),
                                       "assets/textures/text_box_5.png",
                                       self.set_curr_guess,"Type A Response")]

        pixels = []
        if self.room.game.current_prompt:
            pixels = self.room.game.current_prompt.content

        self.active_animations = [
            AnimationWindow(self.np(36, 43), self.ns(845, 455), pixels)
        ]
        self.active_drawings = []
        self.draw_order = self.active_buttons + self.active_ui + \
                          self.active_drawings + self.active_animations
        self.pause_client()

    def switch_to_draw(self):
        pygame.mouse.set_visible(False)
        """switches the scene to drawing, initializing the UI."""
        # note from Mat - this makes the drawing window displayable, not fully functional
        self.scene = "drawing"
        self.tool_text = TextUI(self.np(60, 95), self.ns(20, 20),
                                 "Current: " + self.curr_tool, (0, 0, 0))
        self.active_ui = [TimeBar(self.np(94,58), self.ns(60 * 1.5, 320 * 1.5), self.draw_length),
                          # TextUI(self.np(50, 10), self.ns(100, 100),
                          #      "Prompt: " + self.room.game.current_prompt.content, (0, 0, 0)),
                          TextUI(self.np(60, 90), self.ns(20, 20),
                                 "Current Tool: ", (0, 0, 0)),
                          self.tool_text,
                          DefaultUI(self.np(36, 53), self.nl(660),
                                "assets/textures/color_button.png"),
                          MouseStick(self.ns(20, 20))]
        self.active_buttons = [
            ColorWheel(self.np(79, 36), (self.ns(180, 180)), self.set_color),
            BrightnessSlider(self.np(85, 69), (self.ns(1.2 * 50, 4 * 50)), self.set_brightness),
            #ColorButton(self.np(10, 80), self.ns(40, 40), self.set_color, "red"),
            PenTypeButton(self.np(75, 57), self.ns(100, 40),
                   "assets/textures/thickness_1.png", lambda: self.set_brush_thickness(1), 1),
            PenTypeButton(self.np(75, 65), self.ns(100, 40),
                   "assets/textures/thickness_2.png", lambda: self.set_brush_thickness(2), 2),
            PenTypeButton(self.np(75, 73), self.ns(100, 40),
                   "assets/textures/thickness_3.png", lambda: self.set_brush_thickness(4), 4),
            PenTypeButton(self.np(75, 81), self.ns(100, 40),
                   "assets/textures/thickness_4.png", lambda: self.set_brush_thickness(8), 8),
            #Button(self.np(74, 92), self.ns(80, 60),
                   #"assets/textures/submit.png", lambda: self.set_eraser()),
            PenTypeButton(self.np(84, 92), self.ns(80, 51),
                    "assets/textures/fill_button.png", self.set_fill_tool, 0),
            CheckboxButton(self.np(74, 92), self.ns(115, 51),
                           self.set_eraser, "", False,
                           "assets/textures/eraser_button.png"),
            Button(self.np(36, 92.5), (self.ns(140 * 1.8, 51 * 1.8)),
                  "assets/textures/submit.png", self.submit)]
        # Mat changed this line
        #TODO: MAT- self.nl works- I use it for the colorbutton texture you put behind
        #TODO: the drawing window for reference. Mess around with DrawingWindow and change 680.
        #TODO: See how it snaps? The calculation for size of drawing window is not consistent with
        #TODO: the other UI elements- please look at this and solve it, as it's out of my scope now.
        #TODO: The objective is that it can be ANY size- especially for the results page.
        self.active_drawings = [DrawingWindow(self.np(36,53), self.nl(680))]
        self.draw_order = self.active_buttons + self.active_ui +\
                          self.active_drawings + self.active_animations
        self.draw_order = sorted(self.draw_order, key=lambda elem: elem.z)
        self.pause_client()

    def switch_to_results(self):
        """switches the scene to results, initializing the UI"""
        self.scene = "results"
        self.active_ui = []
        self.active_buttons = [
            Button(self.np(80, 95), (self.ns(140 * 2.2, 51 * 2.2)),
                   "assets/textures/submit.png", self.switch_to_lobby)

        ]
        pixels = []
        if self.active_drawings:
            pixels = self.active_drawings[0].get_drawn_pixels()

        self.active_animations = [
            AnimationWindow(self.np(50, 50), self.ns(845, 455), pixels)
        ]
        self.active_drawings = []
        self.draw_order = self.active_buttons + self.active_drawings +\
                          self.active_ui + self.active_animations
        self.pause_client()

    def enable_room_code(self):
        """Enables UI for asking for room code"""
        if self.curr_name:
            for button in self.active_buttons:
                button.active = False
            self.active_ui.append(TransparentUI(self.np(50,50),
                                                self.ns(SCREEN_LEN * 2,SCREEN_HT * 2),
                                                (0,0,0), 150))
            self.active_buttons.append(Button(self.np(62, 60), (self.ns(140 * 1.5, 51 * 1.5)),
                                              "assets/textures/go.png", self._join_room, z=2))
            self.active_buttons.append(Button(self.np(38, 60), (self.ns(140 * 1.5, 51 * 1.5)),
                                              "assets/textures/back.png",
                                              self.disable_room_code, z=2))
            self.active_buttons.append(TypeBox(self.np(50, 40), (self.ns(150 * 1.4, 64 * 1.4)),
                                               "assets/textures/text_box_4.png", self.set_room_code,
                                               "CODE", 4, 2))

            self.draw_order = self.active_buttons + self.active_drawings +\
                              self.active_ui + self.active_animations
            self.draw_order = sorted(self.draw_order, key=lambda elem: elem.z)
            self.draw_order.append(TextUI(self.np(50, 68),
                                         self.ns(0, 20),
                                     "", (255, 255, 255)))

    def disable_room_code(self):
        """Turns off the room code popup and returns
        to main welcome screen"""
        self.active_ui.pop()
        self.active_buttons.pop()
        self.active_buttons.pop()
        self.active_buttons.pop()
        self.draw_order = self.active_buttons + self.active_drawings +\
                          self.active_ui + self.active_animations
        self.draw_order = sorted(self.draw_order, key=lambda elem: elem.z)
        for button in self.active_buttons:
            button.active = True

    def start_game(self):
        """starts the game by calling network.
        Used when play button pressed."""
        self.network.start_game()

    def draw_text(self, vec):
        """Draws text on screen from draw_typing_text"""
        if len(vec) == 4:
            text = vec[0]
            pos = vec[1]
            font = vec[2]
            color = vec[3]
            text_surface = font.render(text, True, color)
            self.screen.blit(text_surface, pos)

    def draw_typing_text(self, vec):
        """Used by TypeBox button, draws typed text on screen"""
        #only show up if you're close
        if len(vec[-1]) > 0 and vec[4] - len(vec[-1]) < vec[4] / 2 + 1:
            self.draw_text([str(vec[4] - len(vec[-1])),
                            (vec[-2], vec[1][1]), vec[2], (100,100,100)])
        self.draw_text(vec[:-3])
        #(self.pos[0] - self.width / 2.2, self.pos[1] - self.height / 3)

    def _start_room(self):
        """creates a room and makes the user the host.
         Verifies server is active and sets self.player and self.room"""
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
        self.switch_to_lobby()

    def _join_room(self):
        """Joins the room, accessing the room code and joining it if it exists.
        Supports error with multiple error checks. Sets self.player and self.room"""
        if not self.room_code_attempt:
            self.draw_order[-1] = TextUI(self.np(50, 68),
                                         self.ns(0, 20),
                                     "Enter a code to join", (255, 255, 255))
        if self.room_code_attempt:
            room_code = self.room_code_attempt.strip()
            name = self.curr_name.strip()
            if not room_code:
                self.network_error = "Enter a code first."
                return
            try:
                self.network.join_room(name, room_code)
            except NetworkClientError as exc:
                self.network_error = str(exc)
                self.draw_order[-1] = TextUI(self.np(50, 68),
                                             self.ns(0, 20),
                                             "Invalid Room Code", (255, 255, 255))
                return

            self.room = self.network.room
            self.player = self.network.player

            print(f"ROOM {self.room.room_id} JOINED BY {self.player.name}")
            self.switch_to_lobby()

    #------------------------------------------------------------
    #Animation and Audio listed below
    #------------------------------------------------------------
    # Will figure out how to send animation soon

    def set_sound_effects_volume(self, volume):
        """sets the sound effects volume. Primarily used by buttons"""
        self.sfx_volume = volume
        SoundManager.get_instance().change_volume(self.sfx_volume, "sfx")

    def set_music_volume(self, volume):
        """sets the music volume. Primarily used by buttons"""
        self.music_volume = volume
        SoundManager.get_instance().change_volume(self.music_volume, "music")

    def set_color(self, color):
        """sets the RGB color while drawing. Primarily used by buttons"""
        self.curr_color = color
        self.curr_shade = [
            color[0] * self.brightness,
            color[1] * self.brightness,
            color[2] * self.brightness]

    def set_brightness(self, val):
        """sets brightness of the RGB value while drawing.
        Utilized by BrightnessSlider object exclusively"""
        self.brightness = val
        self.curr_shade = [
            self.curr_color[0] * val,
            self.curr_color[1] * val,
            self.curr_color[2] * val]

    def check_box_test(self, val):
        """temporary test empty function"""
        return

    def set_brush_thickness(self, num):
        """sets the brush thickness while drawing. Primarily used by buttons"""
        self.curr_brush = num
        self.curr_tool = "brush"
        # print("Brush thickness:", self.curr_brush)

    def set_fill_tool(self):
        """sets the tool to fill. Primarily used by buttons"""
        self.curr_brush = 0
        self.curr_tool = "fill"
        # print("Current tool:", self.curr_tool)

    def set_brush_tool(self):
        """Sets tool to brush"""
        self.curr_tool = "brush"
        # print("Current tool:", self.curr_tool)

    def set_eraser(self, enabled):
        """Sets the current color to eraser values. Primarily used by buttons"""
        if enabled:
            #self.curr_color = [240, 240, 240]
            self.curr_shade = [240, 240, 240]

    def set_name(self, name):
        """sets the name of the user. Primarily used by buttons"""
        self.curr_name = name

    def set_curr_prompt(self, prompt):
        """sets the current prompt. Primarily used by buttons"""
        self.curr_prompt = prompt

    def set_curr_guess(self, guess):
        """sets the current guess. Primarily used by buttons"""
        self.curr_guess = guess

    def set_room_code(self, code):
        """sets the room code. Primarily used by buttons"""
        self.room_code_attempt = code.upper()

    def simple_color_select(self, enabled):
        """Sets simple_colors to true"""
        self.simple_colors = True

    def prompt_time_length(self, selected_value):
        """Sets timer length for prompt/guess phase. Primarily used by buttons"""
        self.prompt_length = selected_value

    def draw_time_length(self, selected_value):
        """Sets timer length for draw phase. Primarily used by buttons"""
        self.draw_length = selected_value

    def get_pen_state(self):
        if self.curr_shade == [240, 240, 240]:
            return "eraser"
        return self.curr_tool

    def submit(self, time_up = False):
        """refers to server that a user has made a submission, and submits it"""
        if not time_up:
            SoundManager.get_instance().play_sfx("assets/audio/yay.mp3")
        if self.scene == "writing" and not self.submitted:
            if not self.curr_prompt:
                self.curr_prompt = f"{self.player.name} didn't submit!"
            self.network.submit_entry(self.curr_prompt)
            self.submitted = True
            # disable buttons and present close screen
            self.submit_ui()
        elif self.scene == "drawing" and not self.submitted:
            # disable buttons and present close screen
            self.network.submit_entry(self.active_drawings[0].drawn_pixels)
            print(self.network.room.to_dict())
            self.submitted = True
            self.submit_ui()

    def submit_ui(self):
        """creates the overlay when you submit something"""
        for button in self.active_buttons:
            button.active = False
        if self.paused:
            index = -3
        else:
            index = -1
        self.draw_order.insert(index, TransparentUI(self.np(50, 50),
                                            self.ns(SCREEN_LEN * 2, SCREEN_HT * 2),
                                            (0, 0, 0), 150))
        if self.scene == "writing":
            with open(resolve_asset_path("assets/guess_prompts.csv"), mode='r', newline='') as file:
                text = random.choice(list(csv.reader(file)))
            print(text)
            self.draw_order.insert(index, TextUI(self.np(50, 40),
                                     self.ns(0, 80),
                                 text[0], (255, 255, 255)))
        elif self.scene == "drawing":
            with open(resolve_asset_path("assets/draw_prompts.csv"), mode='r', newline='') as file:
                text = random.choice(list(csv.reader(file)))
            self.draw_order.insert(index, TextUI(self.np(50, 35),
                                         self.ns(0, 80),
                                     text[0], (255, 255, 255)))

    def slider_control(self, offset):
        """Controls the slide bar, moving items up and down
        based on the offset from the UI element"""
        # compare results height to the height of the window: A constant for now.
        # The excess height is
        results_window_ht = self.ns(0, 500) #random value for now, proof of concept complete!
        mult =  self.results_height - results_window_ht[1]
        if mult < 0:
            mult = 0
        for element in self.draw_order:
            if not isinstance(element, SlideDownButton) and element.draggable:
                element.pos[1] = element.init_y - offset * mult

    def quit_game(self):
        """closes the program"""
        self.exit = True

    def leave_room(self):
        # TODO: LEAVE ROOM!
        self.network.close()
        self.switch_to_welcome()
        self.pause_client(True)

    def pause_client(self, pause = False):
        """Pauses the client game, organizing UI and its logic"""
        if (not self.paused and pause) or (self.paused and not pause):
            pygame.mouse.set_visible(True)
            self.paused = True
            self.active_buttons.append(SliderButton(self.np(30, 50),
                                                    self.ns(200,30),0, 1,
                                                    self.set_sound_effects_volume,
                                                    self.sfx_volume, 10))
            self.active_buttons.append(SliderButton(self.np(70, 50),
                                                    self.ns(200, 30), 0,1,
                                                    self.set_music_volume,
                                                    self.music_volume, 10))
            if self.scene != "welcome":
                self.active_buttons.append(Button(self.np(50, 70), (self.ns(140 * 1.8, 51 * 1.8)),
                                                  "assets/textures/quit.png",
                                                  self.leave_room, z=5, pause_override=True))
            else:
                self.active_buttons.append(Button(self.np(50, 70), (self.ns(140 * 1.8, 51 * 1.8)),
                                                  "assets/textures/quit.png",
                                                  self.quit_game, z=5, pause_override=True))

            self.draw_order.append(TransparentUI(self.np(50, 50),
                          self.ns(SCREEN_LEN * 2, SCREEN_HT * 2),
                          (0, 0, 0), 100))
            self.draw_order.append(DefaultUI(self.np(50, 50),
                                                 self.ns(520 * 1.5, 300 * 1.5),
                                                 "assets/textures/pause_screen.png"))
            self.draw_order += self.active_buttons[-3:]

        elif self.paused and pause:
            self.paused = False
            self.active_buttons.pop()
            self.active_buttons.pop()
            self.active_buttons.pop()
            self.draw_order = self.draw_order[:-5]
            if self.scene == "drawing":
                pygame.mouse.set_visible(False)

import pygame

GRID_CELL_SIZE = 4
GRID_WIDTH = 325
GRID_HEIGHT = 175
PIXEL_WIDTH = GRID_CELL_SIZE * GRID_WIDTH
PIXEL_HEIGHT = GRID_CELL_SIZE * GRID_HEIGHT

COLORS = {
    'background': (240, 240, 240),
    'black_pen' : (0, 0, 0),
    'green_pen': (0, 255, 0),
    'blue_pen': (0, 0, 255),
    'purple_pen': (128, 0, 128),
    'red_pen': (255, 0, 0),
    'orange_pen': (255, 128, 0),
    'yellow_pen': (255, 255, 0),
    'grey_pen': (128, 128, 128),
    'sky_blue_pen': (135, 206, 235),
    'brown_pen': (139, 69, 19),
    'white_pen': (255, 255, 255),
    'eraser': (240, 240, 240)
}


# cells on the grid
class GridCell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = col * GRID_CELL_SIZE
        self.y = row * GRID_CELL_SIZE
        self.color = COLORS['background']

    def get_position(self):
        return self.row, self.col

    def drawing(self, color):
        self.color = color


# the grid for the drawing window
class Grid:
    def __init__(self, pos, size, pixel_size):
        self.pos = pos
        self.size = size
        self.pixel_size = pixel_size
        self.cells = self._create_cells()
        # for optimization
        self.surface = pygame.Surface((GRID_WIDTH * GRID_CELL_SIZE, GRID_HEIGHT * GRID_CELL_SIZE))
        self.surface.fill(COLORS['background'])

        self.brush_cache = {}
        for r in [1, 2, 4]:
            self.brush_cache[r] = self.brush_offsets(r)

    @staticmethod
    def _create_cells():
        return [[GridCell(row, col) for col in range(GRID_WIDTH)] for row in range(GRID_HEIGHT)]

    def get_cell(self, row, col):
        if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
            return self.cells[row][col]
        return None

    def set_pixel(self, row, col, color):
        if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
            self.cells[row][col].color = color
            pygame.draw.rect(self.surface, color,
                        (col * GRID_CELL_SIZE, row * GRID_CELL_SIZE,
                            GRID_CELL_SIZE, GRID_CELL_SIZE))

    def brush_offsets(self, radius):
        offsets = []
        for r in range(-radius, radius + 1):
            for c in range(-radius, radius + 1):
                if r * r + c * c <= radius * radius:
                    offsets.append((r, c))
        return offsets

    def draw_brush(self, row, col, color, radius=1):
        drawn_pixels =[]

        offsets = self.brush_cache[radius]

        for dr, dc in offsets:
            r = row + dr
            c = col + dc
            if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                self.set_pixel(r, c, color)
                drawn_pixels.append((r, c, color))

        return drawn_pixels

    def draw_line_cells(self, start, end, color, radius=2):
        drawn_pixels = []
        x1, y1 = start
        x2, y2 = end

        steps = max(abs(x1 - x2), abs(y1 - y2))
        if steps == 0:
            return self.draw_brush(y1 // GRID_CELL_SIZE, x1 // GRID_CELL_SIZE, color, radius)

        for i in range(steps + 1):
            t = i / steps if steps != 0 else 0
            x = int(x1 + t * (x2 - x1))
            y = int(y1 + t * (y2 - y1))
            row = y // GRID_CELL_SIZE
            col = x // GRID_CELL_SIZE
            drawn_pixels += self.draw_brush(row, col, color, radius)

        return drawn_pixels

    # fill tool!
    def fill_tool(self, start_row, start_col, new_color):
        drawn_pixels = []
        visited = set()
        start_cell = self.get_cell(start_row, start_col)
        if not start_cell:
            return drawn_pixels

        target_color = start_cell.color

        if target_color == new_color:
            return drawn_pixels

        update_stack = [(start_row, start_col)]

        while update_stack:
            row, col = update_stack.pop()

            if (row, col) in visited:
                continue
            visited.add((row, col))

            cell = self.get_cell(row, col)

            if cell and cell.color == target_color:
                self.set_pixel(row, col, new_color)

                drawn_pixels.append((row, col, new_color))

                update_stack.append((row + 1, col))
                update_stack.append((row - 1, col))
                update_stack.append((row, col + 1))
                update_stack.append((row, col - 1))

        return drawn_pixels

    def draw(self, window):
        window.blit(self.surface, self.pos)


# for rendering the drawing window in engine
class DrawingWindow:
    def __init__(self, pos):
        self.grid = Grid(pos, (0, 0), 2)
        self.pos = pos
        self.brush_radius = 1
        self.current_color = COLORS['black_pen']
        self.current_tool = "brush"
        self.last_pos = None
        self.last_mouse = False
        self.font = pygame.font.SysFont("Consolas", 18)
        self.pen_colors = [
            ("Black", COLORS['black_pen']),
            ("Green", COLORS['green_pen']),
            ("Blue", COLORS['blue_pen']),
            ("Purple", COLORS['purple_pen']),
            ("Red", COLORS['red_pen']),
            ("Orange", COLORS['orange_pen']),
            ("Yellow", COLORS['yellow_pen']),
            ("Grey", COLORS['grey_pen']),
            ("Sky Blue", COLORS['sky_blue_pen']),
            ("Brown", COLORS['brown_pen']),
            ("White", COLORS['white_pen']),
            ("Erasing", COLORS['eraser'])
        ]
        self.color_index = 0

    def update(self, mouse_pos, mouse_pressed, key_pressed):
        this_x = mouse_pos[0] - self.pos[0]
        this_y = mouse_pos[1] - self.pos[1]

        if this_x < 0 or this_y < 0:
            return

        row = this_y // GRID_CELL_SIZE
        col = this_x // GRID_CELL_SIZE

        if mouse_pressed:
            if self.current_tool == "brush":
                if self.last_pos and (this_x, this_y) != self.last_pos:
                    self.grid.draw_line_cells(
                        self.last_pos,
                        (this_x, this_y),
                        self.current_color,
                        self.brush_radius)
                else:
                    self.grid.draw_brush(row, col, self.current_color, self.brush_radius)
                self.last_pos = (this_x, this_y)
            elif self.current_tool == "fill":
                if not self.last_mouse:
                    self.grid.fill_tool(row, col, self.current_color)
        else:
            self.last_pos = None

        self.last_mouse = mouse_pressed

    def draw(self, screen):
        self.grid.draw(screen)

        font = self.font

        text_surface = font.render(f"Brush size (press 1-4 to change): {self.brush_radius}", True, (0, 0, 0))
        text_surface2 = font.render(f"Color (press TAB to cycle): {self.color_index}", True, (0, 0, 0))
        text_surface3 = font.render(f"Brush type (press f or b to cycle): {self.current_tool}", True, (0, 0, 0))

        screen.blit(text_surface, (10, 10))
        screen.blit(text_surface2, (10, 20))
        screen.blit(text_surface3, (10, 30))

    def color_switch(self):
        self.color_index = (self.color_index +1) % len(self.pen_colors)
        name, color = self.pen_colors[self.color_index]
        self.current_color = color

    def handle_clicks(self, click):
        if click.type == pygame.KEYDOWN:
            if click.key == pygame.K_TAB:
                self.color_switch()
            elif click.key == pygame.K_1:
                self.brush_radius = 1
            elif click.key == pygame.K_2:
                self.brush_radius = 2
            elif click.key == pygame.K_3:
                self.brush_radius = 4
            elif click.key == pygame.K_f:
                self.current_tool = "fill"
            elif click.key == pygame.K_b:
                self.current_tool = "brush"

# may replace soon
def get_clicked_pos(position):
    x, y = position
    col = x // GRID_CELL_SIZE
    row = y // GRID_CELL_SIZE
    return row, col

# runs the window for debug
def run_drawing(window):
    # pen colors
    pen_colors = [
        ("Black", COLORS['black_pen']),
        ("Green", COLORS['green_pen']),
        ("Blue", COLORS['blue_pen']),
        ("Purple", COLORS['purple_pen']),
        ("Red", COLORS['red_pen']),
        ("Orange", COLORS['orange_pen']),
        ("Yellow", COLORS['yellow_pen']),
        ("Grey", COLORS['grey_pen']),
        ("Sky Blue", COLORS['sky_blue_pen']),
        ("Brown", COLORS['brown_pen']),
        ("White", COLORS['white_pen']),
        ("Erasing", COLORS['eraser'])
    ]
    # variables to get started
    grid = Grid((0,0), (0,0), 2)
    run = True
    last_pos = None
    brush_radius = 1
    color = None
    drawn_pixels = []

    # font variables
    pygame.font.init()
    font = pygame.font.SysFont('Consola', 18)

    # color variables
    color_index = 0
    current_color_name, current_color = pen_colors[color_index]

    # brush type variables
    current_tool = "brush"

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # brush width
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    brush_radius = 1
                if event.key == pygame.K_2:
                    brush_radius = 2
                if event.key == pygame.K_3:
                    brush_radius = 4

            # change color
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    color_index = (color_index + 1) % len(pen_colors)
                    current_color_name, current_color = pen_colors[color_index]

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    current_tool = "fill"
                if event.key == pygame.K_b:
                    current_tool = "brush"

            # draw if clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = pygame.mouse.get_pos()
                    row, col = get_clicked_pos(pos)

                    if current_tool == "brush":
                        drawing = grid.draw_brush(row, col, current_color, brush_radius)
                        drawn_pixels.append(("pixels", drawing))
                        last_pos = pos
                    elif current_tool == "fill":
                        drawing = grid.fill_tool(row, col, current_color)
                        drawn_pixels.append(("fill", drawing))

            # draw when held
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()

                if last_pos:
                    drawing = grid.draw_line_cells(last_pos, pos, current_color, radius=brush_radius)
                    drawn_pixels.append(("pixels", drawing))
                last_pos = pos
            else:
                last_pos= None

        window.fill(COLORS['background'])
        grid.draw(window)

        # debugging text boxes
        text_surface = font.render(f"Brush size (press 1-4 to change): {brush_radius}", True, (0, 0, 0))
        text_surface2 = font.render(f"Color (press TAB to cycle): {current_color_name}", True, (0, 0, 0))
        text_surface3 = font.render(f"Brush type (press f or b to cycle): {current_tool}", True, (0, 0, 0))

        window.blit(text_surface, (10, 10))
        window.blit(text_surface2, (10, 20))
        window.blit(text_surface3, (10, 30))

        pygame.display.update()

    return drawn_pixels

# animates the window for debug
def run_animation(window, drawn_pixels):
    grid = Grid((0,0), (0,0), 2)
    clock = pygame.time.Clock()

    total_pixels = len(drawn_pixels)
    if total_pixels == 0:
        return

    # trying to fix animation timing - it is still slow
    max_seconds = 3
    fps = 120
    total_pixels = len(drawn_pixels)

    pixels_per_frame = max(5, total_pixels // (fps * max_seconds))

    index = 0
    running = True

    while running:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        for i in range(pixels_per_frame):
            if index >= total_pixels:
                running = False
                break

            action_type, pixel_list = drawn_pixels[index]

            if action_type == "fill":
                for row, col, color in pixel_list:
                    grid.set_pixel(row, col, color)
                index += 1

            else:
                for row, col, color in pixel_list:
                    grid.set_pixel(row, col, color)
                index += 1

        window.fill(COLORS['background'])
        grid.draw(window)
        pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False


if __name__ == '__main__':
    w = pygame.display.set_mode((PIXEL_WIDTH, PIXEL_HEIGHT))
    try:
        pixels = run_drawing(w)
        run_animation(w, pixels)
    finally: pygame.quit()

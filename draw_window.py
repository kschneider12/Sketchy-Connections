import pygame

GRID_CELL_SIZE = 4
GRID_WIDTH = 256
GRID_HEIGHT = 128
PIXEL_WIDTH = GRID_CELL_SIZE * GRID_WIDTH
PIXEL_HEIGHT = GRID_CELL_SIZE * GRID_HEIGHT

COLORS = {
    'background': (250, 250, 250),
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
    'eraser': (250, 250, 250)

}

# cells on the grid
class GridCell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = col * GRID_CELL_SIZE
        self.y = row * GRID_CELL_SIZE
        self.color = COLORS['background']
        self.neighbors = []

    def get_position(self):
        return self.row, self.col

    # Could be used to help with saving drawn pixels
    def is_drawn(self):
        return self.color == COLORS['pen']

    # Could be used to help with saving erased pixels
    def is_erased(self):
        return self.color == COLORS['background']

    def erasing(self):
        self.color = COLORS['background']

    def drawing(self, color):
        self.color = color

    def draw(self, win):
        pygame.draw.rect(win,
                         self.color,
                         (self.x, self.y, GRID_CELL_SIZE, GRID_CELL_SIZE))

    def update_cells(self):
        self.neighbors = []

# the grid for the drawing window
class Grid:
    def __init__(self):
        self.cells = self._create_cells()

    @staticmethod
    def _create_cells():
        return [[GridCell(row, col) for col in range(GRID_WIDTH)] for row in range(GRID_HEIGHT)]

    def get_cell(self, row, col):
        if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
            return self.cells[row][col]
        return None

    def draw_brush(self, row, col, color, radius=1):
        for r in range(row - radius, row + radius + 1):
            for c in range(col - radius, col + radius + 1):
                cell = self.get_cell(r, c)
                if cell:
                    cell.drawing(color)

    def draw_line_cells(self, start, end, color, radius=2):
        x1, y1 = start
        x2, y2 = end

        steps = max(abs(x1 - x2), abs(y1 - y2))

        for i in range(steps + 1):
            t = i / steps if steps != 0 else 0
            x = int(x1 + t * (x2 - x1) * t)
            y = int(y1 + t * (y2 - y1) * t)
            row, col = get_clicked_pos((x, y))
            self.draw_brush(row, col, color, radius)

    def update_cells(self):
        for row in self.cells:
            for cell in row:
                cell.update_cells(self)

    def draw(self, window):
        for row in self.cells:
            for cell in row:
                cell.draw(window)

    def erasing(self):
        self.cells = self._create_cells()

def get_clicked_pos(position):
    x, y = position
    col = x // GRID_CELL_SIZE
    row = y // GRID_CELL_SIZE
    return row, col

# runs the window
def run(window):
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
    grid = Grid()
    run = True
    last_pos = None
    brush_radius = 1
    color = None
    pygame.font.init()
    font = pygame.font.SysFont('Consola', 18)
    color_index = 0
    current_color_name, current_color = pen_colors[color_index]

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    brush_radius = 1
                if event.key == pygame.K_2:
                    brush_radius = 2
                if event.key == pygame.K_3:
                    brush_radius = 4
                if event.key == pygame.K_4:
                    brush_radius = 8
                if event.key == pygame.K_5:
                    brush_radius = 16

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    color_index = (color_index + 1) % len(pen_colors)
                    current_color_name, current_color = pen_colors[color_index]

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()

                if last_pos:
                    grid.draw_line_cells(last_pos, pos, current_color, radius=brush_radius)
                last_pos = pos
            else:
                last_pos= None

        window.fill(COLORS['background'])
        grid.draw(window)

        text_surface = font.render(f"Brush size: {brush_radius}", True, (0, 0, 0))
        text_surface2 = font.render(f"Color: {current_color_name}", True, (0, 0, 0))

        window.blit(text_surface, (10, 10))
        window.blit(text_surface2, (10, 20))

        pygame.display.update()

if __name__ == '__main__':
    w = pygame.display.set_mode((PIXEL_WIDTH, PIXEL_HEIGHT))
    try:
        run(w)
    finally:
        pygame.quit()

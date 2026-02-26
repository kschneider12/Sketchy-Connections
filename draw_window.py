import pygame

GRID_CELL_SIZE = 8
GRID_WIDTH = 256
GRID_HEIGHT = 128
PIXEL_WIDTH = GRID_CELL_SIZE * GRID_WIDTH
PIXEL_HEIGHT = GRID_CELL_SIZE * GRID_HEIGHT

COLORS = {
    'background': (250, 250, 250),
    'pen' : (0, 0, 0)
}

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

    def drawing(self):
        self.color = COLORS['pen']

    def draw(self, window):
        pygame.draw.rect(window,
                         self.color,
                         (self.x, self.y, GRID_CELL_SIZE * 2, GRID_CELL_SIZE * 2))

    def update_cells(self):
        self.neighbors = []

class Grid:
    def __init__(self, rows, cols):
        self.cells = self._create_cells()

        @staticmethod
        def _create_cells():
            return [[GridCell(x, y)
                     for y in range(GRID_WIDTH) for x in range(GRID_HEIGHT)]]

        def get_cell(self, row, col):
            if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
                return self.cells[row][col]
            return None

        # def update





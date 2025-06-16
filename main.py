import pygame
import sys
import random
import os

# Initialize Pygame
pygame.init()

def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller bundle
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

icon = pygame.image.load(resource_path(r'images\unclicked-bomb.png'))
icon = pygame.transform.scale(icon, (32, 32))
pygame.display.set_icon(icon)

FONT = pygame.font.SysFont(None, 48)
BUTTON_FONT = pygame.font.SysFont(None, 36)
BG_COLOR = (255, 255, 255)  # White background (same as your fill color)

def draw_text_center(text, y):
    text_surface = FONT.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, y))
    screen.blit(text_surface, text_rect)

def draw_button(text, rect):
    pygame.draw.rect(screen, (0, 120, 215), rect)  # Blue button
    pygame.draw.rect(screen, (0, 0, 0), rect, 2)   # Black border
    button_text = BUTTON_FONT.render(text, True, (255, 255, 255))
    button_rect = button_text.get_rect(center=rect.center)
    screen.blit(button_text, button_rect)

# Constants
WIDTH, HEIGHT = 400, 600
WINDOW_TITLE = "Minesweeper"
ROWS, COLS = 15, 10
CELL_SIZE = 40
NUM_BOMBS = 20


# Load images
EMPTY_BLOCK = pygame.image.load(resource_path(r'images\empty-block.png'))
BOMB_BLOCK = pygame.image.load(resource_path(r'images\empty-block.png'))
REVEALED_TILES = {
    i: pygame.image.load(resource_path(fr'images\{i}.png')) for i in range(9)
}
REVEALED_TILES[9] = pygame.image.load(resource_path(r'images\bomb-at-clicked-block.png'))
FLAG_IMAGE = pygame.image.load(resource_path(r'images\flag.png'))

# Scale celulas
for key in REVEALED_TILES:
    REVEALED_TILES[key] = pygame.transform.scale(REVEALED_TILES[key], (CELL_SIZE, CELL_SIZE))
EMPTY_BLOCK = pygame.transform.scale(EMPTY_BLOCK, (CELL_SIZE, CELL_SIZE))
BOMB_BLOCK = pygame.transform.scale(BOMB_BLOCK, (CELL_SIZE, CELL_SIZE))
FLAG_IMAGE = pygame.transform.scale(FLAG_IMAGE, (CELL_SIZE, CELL_SIZE))

# Grid
grid_width = COLS * CELL_SIZE
grid_height = ROWS * CELL_SIZE
start_x = (WIDTH - grid_width) // 2
start_y = (HEIGHT - grid_height) // 2

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)


grid = [[None for _ in range(COLS)] for _ in range(ROWS)]

def place_bombs():
    # colaca bomba aleatoriamente
    bomb_positions = set()
    while len(bomb_positions) < NUM_BOMBS:
        r = random.randint(0, ROWS - 1)
        c = random.randint(0, COLS - 1)
        if (r, c) not in bomb_positions:
            bomb_positions.add((r, c))
            grid[r][c] = 9  # bomba -- 9

    # contador de bombas a volta da celulas
    for row in range(ROWS):
        for col in range(COLS):
            if grid[row][col] == 9:
                continue  # skipa as bombas
            bomb_count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS:
                        if grid[nr][nc] == 9:
                            bomb_count += 1
            grid[row][col] = bomb_count

# Draw the grid
def draw_grid():
    for row in range(ROWS):
        for col in range(COLS):
            x = start_x + col * CELL_SIZE
            y = start_y + row * CELL_SIZE

            if revealed[row][col]:
                value = grid[row][col]
                screen.blit(REVEALED_TILES[value], (x, y))
            elif flagged[row][col]:
                screen.blit(FLAG_IMAGE, (x, y))
            else:
                screen.blit(EMPTY_BLOCK, (x, y))


revealed = [[False for _ in range(COLS)] for _ in range(ROWS)]
flagged = [[False for _ in range(COLS)] for _ in range(ROWS)]

def save_grid_to_file(filename="grid_layout.txt"):
    with open(filename, 'w') as f:
        for row in grid:
            line = ''.join([str(cell) for cell in row])
            f.write(line + '\n')

def flood_fill(row, col):
    # Base case: if out of bounds or already revealed
    if not (0 <= row < ROWS and 0 <= col < COLS):
        return
    if revealed[row][col]:
        return

    revealed[row][col] = True

    if grid[row][col] == 0:
        # Continue flood fill in all 8 directions
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                flood_fill(row + dr, col + dc)

def check_win():
    for row in range(ROWS):
        for col in range(COLS):
            if grid[row][col] != 9 and not revealed[row][col]:
                return False
    return True

def reset_game():
    global grid, revealed, flagged
    grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
    revealed = [[False for _ in range(COLS)] for _ in range(ROWS)]
    flagged = [[False for _ in range(COLS)] for _ in range(ROWS)]
    place_bombs()


# Main game loop
def main():
    clock = pygame.time.Clock()
    place_bombs()
    save_grid_to_file()

    running = True
    game_over = False
    win = False

    # Button rectangle
    button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 50)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not game_over and not win:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = event.pos
                    col = (mouse_x - start_x) // CELL_SIZE
                    row = (mouse_y - start_y) // CELL_SIZE

                    if 0 <= row < ROWS and 0 <= col < COLS:
                        if not flagged[row][col]:
                            if grid[row][col] == 9:
                                revealed[row][col] = True
                                game_over = True
                            elif grid[row][col] == 0:
                                flood_fill(row, col)
                            else:
                                revealed[row][col] = True

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Right click
                    mouse_x, mouse_y = event.pos
                    col = (mouse_x - start_x) // CELL_SIZE
                    row = (mouse_y - start_y) // CELL_SIZE

                    if 0 <= row < ROWS and 0 <= col < COLS:
                        if not revealed[row][col]:
                            flagged[row][col] = not flagged[row][col]

                # Check win condition
                if check_win():
                    win = True

            else:
                # Game over or win screen
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if button_rect.collidepoint(event.pos):
                        # Restart game
                        reset_game()
                        game_over = False
                        win = False

        screen.fill(BG_COLOR)

        if game_over:
            draw_text_center("Game Over!", HEIGHT // 2 - 20)
            draw_button("Restart", button_rect)
        elif win:
            draw_text_center("You Win!", HEIGHT // 2 - 20)
            draw_button("Restart", button_rect)
        else:
            draw_grid()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

main()
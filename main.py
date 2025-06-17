import pygame
import sys
import random
import os

# Inicializa o Pygame
pygame.init()

# Estado inicial do jogo
state = "menu"  # opções possíveis: menu, difficulty, credits, game

# Configurações iniciais
DEFAULT_WIDTH, DEFAULT_HEIGHT = 400, 600
WIDTH, HEIGHT = DEFAULT_WIDTH, DEFAULT_HEIGHT
WINDOW_TITLE = "Minesweeper"
CELL_SIZE = 40
BG_COLOR = (255, 255, 255)

# Definições actuais do jogo
current_settings = {
    "rows": 15,
    "cols": 10,
    "bombs": 20
}

ROWS = current_settings["rows"]
COLS = current_settings["cols"]
NUM_BOMBS = current_settings["bombs"]

# Função para obter o caminho para os recursos (compatível com PyInstaller)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Fonte principal usada no jogo
FONT = pygame.font.SysFont(None, 48)
BUTTON_FONT = pygame.font.SysFont(None, 36)

# Criação da janela principal
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(WINDOW_TITLE)
icon = pygame.image.load(resource_path(r'images\unclicked-bomb.png'))
pygame.display.set_icon(pygame.transform.scale(icon, (32, 32)))

# Carregamento das imagens usadas no jogo
EMPTY_BLOCK = pygame.image.load(resource_path(r'images\empty-block.png'))
BOMB_BLOCK = pygame.image.load(resource_path(r'images\unclicked-bomb.png'))  # unclicked bomb
WRONG_FLAG = pygame.image.load(resource_path(r'images\wrong-flag.png'))      # wrong flag
FLAG_IMAGE = pygame.image.load(resource_path(r'images\flag.png'))

REVEALED_TILES = {i: pygame.image.load(resource_path(fr'images\{i}.png')) for i in range(9)}
REVEALED_TILES[9] = pygame.image.load(resource_path(r'images\bomb-at-clicked-block.png'))  # clicked bomb



# Redimensionamento das imagens para o tamanho das células
for key in REVEALED_TILES:
    REVEALED_TILES[key] = pygame.transform.scale(REVEALED_TILES[key], (CELL_SIZE, CELL_SIZE))
EMPTY_BLOCK = pygame.transform.scale(EMPTY_BLOCK, (CELL_SIZE, CELL_SIZE))
BOMB_BLOCK = pygame.transform.scale(BOMB_BLOCK, (CELL_SIZE, CELL_SIZE))
FLAG_IMAGE = pygame.transform.scale(FLAG_IMAGE, (CELL_SIZE, CELL_SIZE))

# Cálculo de posições e dimensões da grelha
grid_width = COLS * CELL_SIZE
grid_height = ROWS * CELL_SIZE
start_x = (WIDTH - grid_width) // 2
start_y = (HEIGHT - grid_height) // 2

# Inicialização das estruturas de dados da grelha
grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
revealed = [[False for _ in range(COLS)] for _ in range(ROWS)]
flagged = [[False for _ in range(COLS)] for _ in range(ROWS)]

# ---------- Funções de interface ----------
def draw_text_center(text, y):
    # Desenha texto centrado na horizontal
    text_surface = FONT.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, y))
    screen.blit(text_surface, text_rect)

def draw_button(text, rect):
    # Desenha um botão com texto
    pygame.draw.rect(screen, (0, 120, 215), rect)
    pygame.draw.rect(screen, (0, 0, 0), rect, 2)
    button_text = BUTTON_FONT.render(text, True, (255, 255, 255))
    button_rect = button_text.get_rect(center=rect.center)
    screen.blit(button_text, button_rect)

def draw_text_with_background(text, y, alpha=180, font_size=40):
    font = pygame.font.Font(None, font_size)
    text_surf = font.render(text, True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=(WIDTH // 2, y))

    # Create semi-transparent surface
    padding = 4
    bg_width = text_rect.width + padding
    bg_height = text_rect.height + padding
    bg_surf = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)

    # Draw rounded rectangle on the surface
    rect = pygame.Rect(0, 0, bg_width, bg_height)
    pygame.draw.rect(bg_surf, (255, 255, 255, alpha), rect, border_radius=10)

    # Position the background centered behind the text
    bg_rect = bg_surf.get_rect(center=text_rect.center)

    # Blit background and text
    screen.blit(bg_surf, bg_rect)
    screen.blit(text_surf, text_rect)




def draw_grid(offset_y=0):
    # Desenha a grelha de jogo com o estado atual das células
    for row in range(current_settings["rows"]):
        for col in range(current_settings["cols"]):
            x = start_x + col * CELL_SIZE
            y = row * CELL_SIZE + offset_y

            if revealed[row][col]:
                value = grid[row][col]
                screen.blit(REVEALED_TILES[value], (x, y))
            elif flagged[row][col]:
                screen.blit(FLAG_IMAGE, (x, y))
            else:
                screen.blit(EMPTY_BLOCK, (x, y))


# ---------- Funções do jogo ----------
def reset_game():
    # Reinicia o estado do jogo (nova grelha, sem revelações nem bandeiras)
    global grid, revealed, flagged
    r, c = current_settings["rows"], current_settings["cols"]
    grid = [[None for _ in range(c)] for _ in range(r)]
    revealed = [[False for _ in range(c)] for _ in range(r)]
    flagged = [[False for _ in range(c)] for _ in range(r)]

def place_bombs_safe(start_row, start_col):
    # Coloca as bombas aleatoriamente, garantindo que a primeira célula clicada é segura
    r, c, b = current_settings["rows"], current_settings["cols"], current_settings["bombs"]
    bomb_positions = set()

    # Zona segura: célula inicial e as 8 adjacentes
    safe_zone = {
        (start_row + dr, start_col + dc)
        for dr in [-1, 0, 1]
        for dc in [-1, 0, 1]
        if 0 <= start_row + dr < r and 0 <= start_col + dc < c
    }

    while len(bomb_positions) < b:
        row = random.randint(0, r - 1)
        col = random.randint(0, c - 1)
        if (row, col) not in bomb_positions and (row, col) not in safe_zone:
            bomb_positions.add((row, col))
            grid[row][col] = 9

    # Calcula o número de bombas adjacentes para cada célula
    for row in range(r):
        for col in range(c):
            if grid[row][col] == 9:
                continue
            count = sum(
                1 for dr in [-1, 0, 1] for dc in [-1, 0, 1]
                if 0 <= row + dr < r and 0 <= col + dc < c and grid[row + dr][col + dc] == 9
            )
            grid[row][col] = count

def flood_fill(row, col):
    # Revela automaticamente células vazias e as suas vizinhas recursivamente
    r, c = current_settings["rows"], current_settings["cols"]
    if not (0 <= row < r and 0 <= col < c) or revealed[row][col]:
        return
    revealed[row][col] = True
    if grid[row][col] == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr or dc:
                    flood_fill(row + dr, col + dc)

def check_win():
    # Verifica se o jogador ganhou (todas as células não-bomba estão reveladas)
    r, c = current_settings["rows"], current_settings["cols"]
    return all(
        grid[row][col] == 9 or revealed[row][col]
        for row in range(r) for col in range(c)
    )

# ---------- Telas ----------
def main_menu():
    global WIDTH, HEIGHT, screen
    WIDTH, HEIGHT = DEFAULT_WIDTH, DEFAULT_HEIGHT
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    new_game_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 30, 200, 50)
    credits_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 50)
    exit_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 110, 200, 50)

    while True:
        screen.fill(BG_COLOR)
        draw_text_center("Minesweeper", HEIGHT//2 - 100)
        draw_button("Novo Jogo", new_game_rect)
        draw_button("Creditos", credits_rect)
        draw_button("Sair", exit_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if new_game_rect.collidepoint(event.pos): return "difficulty"
                if credits_rect.collidepoint(event.pos): return "credits"
                if exit_rect.collidepoint(event.pos): return pygame.EXIT

def difficulty_screen():
    offset_x = -30
    slider_width = 200
    slider_height = 10
    knob_radius = 10

    # Slider ranges
    ranges = {
        "rows": (8, 20),
        "cols": (8, 25),
    }

    # Initial values
    values = {
        "rows": current_settings["rows"],
        "cols": current_settings["cols"],
        "bombs": current_settings["bombs"],
    }

    dragging = {"rows": False, "cols": False, "bombs": False}

    # Positions for sliders
    slider_y_positions = {
        "rows": HEIGHT//2 - 60,
        "cols": HEIGHT//2,
        "bombs": HEIGHT//2 + 60,
    }

    start_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 130, 200, 50)
    error_message = ""

    def draw_slider(name, min_val, max_val, value, y):
        # Draw line
        x = WIDTH // 2 + offset_x
        pygame.draw.line(screen, (200, 200, 200), (x, y), (x + slider_width, y), slider_height)

        # Position knob
        knob_x = int(x + ((value - min_val) / (max_val - min_val)) * slider_width)
        pygame.draw.circle(screen, (100, 100, 250), (knob_x, y), knob_radius)

        # Draw label
        label = f"{labels[name]}: {value}"
        label_surface = BUTTON_FONT.render(label, True, (0, 0, 0))
        screen.blit(label_surface, (x - label_surface.get_width() - 15, y - 10))

        return pygame.Rect(knob_x - knob_radius, y - knob_radius, knob_radius * 2, knob_radius * 2)

    labels = {"rows": "Linhas", "cols": "Colunas", "bombs": "Bombas"}

    while True:
        screen.fill(BG_COLOR)
        draw_text_center("Dificuldade", HEIGHT//2 - 160)

        # Calculate min and max bombs based on current rows and cols
        min_bombs = max(5, int(values["rows"] * values["cols"] * 0.08))
        max_bombs = max(min_bombs, (values["rows"] * values["cols"]) // 3)

        # Clamp bombs value within new min and max bombs
        values["bombs"] = max(min_bombs, min(values["bombs"], max_bombs))

        knob_rects = {}
        for key in ["rows", "cols"]:
            knob_rects[key] = draw_slider(key, ranges[key][0], ranges[key][1], values[key], slider_y_positions[key])
        knob_rects["bombs"] = draw_slider("bombs", min_bombs, max_bombs, values["bombs"], slider_y_positions["bombs"])

        if error_message:
            err_surf = BUTTON_FONT.render(error_message, True, (200, 0, 0))
            screen.blit(err_surf, (WIDTH//2 - err_surf.get_width()//2, HEIGHT//2 + 100))

        draw_button("Começar", start_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for key, rect in knob_rects.items():
                        if rect.collidepoint(event.pos):
                            dragging[key] = True
                    if start_rect.collidepoint(event.pos):
                        rows, cols, bombs = values["rows"], values["cols"], values["bombs"]
                        min_bombs_check = max(5, int(rows * cols * 0.08))
                        if not (ranges["rows"][0] <= rows <= ranges["rows"][1]):
                            error_message = f"Linhas: {ranges['rows'][0]} a {ranges['rows'][1]}"
                            continue
                        if not (ranges["cols"][0] <= cols <= ranges["cols"][1]):
                            error_message = f"Colunas: {ranges['cols'][0]} a {ranges['cols'][1]}"
                            continue
                        if not (min_bombs_check <= bombs <= (rows * cols) // 2):
                            error_message = f"Bombas: mínimo {min_bombs_check}"
                            continue
                        current_settings.update(rows=rows, cols=cols, bombs=bombs)
                        return "game"

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    for key in dragging:
                        dragging[key] = False

            elif event.type == pygame.MOUSEMOTION:
                if any(dragging.values()):
                    mx = event.pos[0]
                    x_start = WIDTH // 2 + offset_x
                    for key in dragging:
                        if dragging[key]:
                            if key == "bombs":
                                min_val, max_val = min_bombs, max_bombs
                            else:
                                min_val, max_val = ranges[key]
                            relative_x = max(0, min(mx - x_start, slider_width))
                            ratio = relative_x / slider_width
                            new_value = int(min_val + round((max_val - min_val) * ratio))
                            values[key] = new_value

def credits_screen():
    back_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 80, 200, 50)
    while True:
        screen.fill(BG_COLOR)
        draw_text_center("Gonçalo Araújo", HEIGHT//2 - 40)
        draw_text_center("2025", HEIGHT//2)
        draw_button("Voltar", back_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return "menu"

# ---------- Execução principal ----------
def run_game():
    global state, screen, start_x, start_y, ROWS, COLS, WIDTH, HEIGHT

    TOP_BAR_HEIGHT = 30
    ROWS, COLS = current_settings["rows"], current_settings["cols"]
    WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE + TOP_BAR_HEIGHT
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    start_x = 0
    start_y = 0

    reset_game()
    bombs_placed = False
    start_time = None
    flags_used = 0
    final_time = None

    game_over, win = False, False
    reveal_time = None  # NEW: Track when game ends to delay showing UI

    restart_rect = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 + 40, 100, 50)
    main_menu_rect = pygame.Rect(WIDTH // 2 + 10, HEIGHT // 2 + 40, 100, 50)

    while True:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not game_over and not win:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos

                    if my < TOP_BAR_HEIGHT:
                        continue

                    col, row = mx // CELL_SIZE, (my - TOP_BAR_HEIGHT) // CELL_SIZE
                    if 0 <= row < ROWS and 0 <= col < COLS:
                        if not bombs_placed:
                            place_bombs_safe(row, col)
                            bombs_placed = True
                            start_time = pygame.time.get_ticks()

                        if event.button == 1 and not flagged[row][col]:
                            if grid[row][col] == 9:
                                revealed[row][col] = True
                                game_over = True
                                reveal_time = current_time  # Record when game ends
                            elif grid[row][col] == 0:
                                flood_fill(row, col)
                            else:
                                revealed[row][col] = True
                        elif event.button == 3 and not revealed[row][col]:
                            flagged[row][col] = not flagged[row][col]
                            flags_used += 1 if flagged[row][col] else -1

                        if check_win():
                            win = True
                            reveal_time = current_time  # Record when game ends

            elif reveal_time and current_time - reveal_time >= 1000:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if restart_rect.collidepoint(event.pos):
                        reset_game()
                        return
                    if main_menu_rect.collidepoint(event.pos):
                        reset_game()
                        state = "menu"
                        return

        # Timer display
        if start_time and not (game_over or win):
            elapsed_sec = (current_time - start_time) // 1000
        elif (game_over or win) and final_time is None:
            final_time = (current_time - start_time) // 1000
            elapsed_sec = final_time
        else:
            elapsed_sec = final_time if final_time is not None else 0

        # DRAW
        screen.fill(BG_COLOR)

        pygame.draw.rect(screen, (220, 220, 220), (0, 0, WIDTH, TOP_BAR_HEIGHT))
        bombs_left = current_settings["bombs"] - flags_used
        bomb_text = BUTTON_FONT.render(f"Bombas: {bombs_left}", True, (0, 0, 0))
        screen.blit(bomb_text, (10, 5))
        time_text = BUTTON_FONT.render(f"Tempo: {elapsed_sec}s", True, (0, 0, 0))
        screen.blit(time_text, (WIDTH - time_text.get_width() - 10, 5))

        if (game_over or win) and reveal_time and current_time - reveal_time < 1000:
            # Show full grid for 1 second
            for r in range(ROWS):
                for c in range(COLS):
                    revealed[r][c] = True
            draw_grid(offset_y=TOP_BAR_HEIGHT)

        elif game_over and reveal_time and current_time - reveal_time >= 1000:
            draw_grid(offset_y=TOP_BAR_HEIGHT)
            draw_text_with_background("Perdeste!", HEIGHT // 2 - 40, font_size=80)

            draw_button("Denovo", restart_rect)
            draw_button("Menu", main_menu_rect)

        elif win and reveal_time and current_time - reveal_time >= 1000:
            draw_grid(offset_y=TOP_BAR_HEIGHT)
            draw_text_with_background("Ganhaste!", HEIGHT // 2 - 40, font_size=80)
            if final_time is not None:
                time_finish_text = BUTTON_FONT.render(f"Tempo final: {final_time}s", True, (0, 0, 0))
                screen.blit(time_finish_text, ((WIDTH - time_finish_text.get_width()) // 2, HEIGHT // 2))
            draw_button("Denovo", restart_rect)
            draw_button("Menu", main_menu_rect)

        else:
            draw_grid(offset_y=TOP_BAR_HEIGHT)

        pygame.display.flip()


def main():
    global state
    clock = pygame.time.Clock()
    while True:
        if state == "menu": state = main_menu()
        elif state == "difficulty": state = difficulty_screen()
        elif state == "credits": state = credits_screen()
        elif state == "game": run_game()
        clock.tick(60)

main()
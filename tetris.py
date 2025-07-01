import pygame
import random
import json

# --- Globals ---
# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
PLAY_WIDTH = 300  # 300 // 10 = 30 width per block
PLAY_HEIGHT = 600 # 600 // 20 = 20 height per block
BLOCK_SIZE = 30

# Top left position of the play area
TOP_LEFT_X = (SCREEN_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = SCREEN_HEIGHT - PLAY_HEIGHT - 50

# --- Shape Formats ---
S = [['.....', '.....', '..00.', '.00..', '.....'], ['.....', '..0..', '..00.', '...0.', '.....']]
Z = [['.....', '.....', '.00..', '..00.', '.....'], ['.....', '..0..', '.00.', '.0...', '.....']]
I = [['..0..', '..0..', '..0..', '..0..', '.....'], ['.....', '0000.', '.....', '.....', '.....']]
O = [['.....', '.....', '.00..', '.00..', '.....']]
J = [['.....', '.0...', '.000.', '.....', '.....'], ['.....', '..00.', '..0..', '..0..', '.....'], ['.....', '.....', '.000.', '...0.', '.....'], ['.....', '..0..', '..0..', '.00..', '.....']]
L = [['.....', '...0.', '.000.', '.....', '.....'], ['.....', '..0..', '..0..', '..00.', '.....'], ['.....', '.....', '.000.', '.0...', '.....'], ['.....', '..00.', '..0..', '..0..', '.....']]
T = [['.....', '..0..', '.000.', '.....', '.....'], ['.....', '..0..', '..00.', '..0..', '.....'], ['.....', '.....', '.000.', '..0..', '.....'], ['.....', '..0..', '.00..', '..0..', '.....']]

SHAPES = [S, Z, I, O, J, L, T]
SHAPE_COLORS = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]

# --- Themes & Settings ---
THEMES = {
    'Dark': { 'background': (20, 20, 20), 'text': (255, 255, 255), 'grid': (70, 70, 70), 'border': (150, 150, 150), 'button_bg': (50, 50, 50), 'button_hover': (80, 80, 80), 'button_text': (255, 255, 255) },
    'Light': { 'background': (230, 230, 230), 'text': (10, 10, 10), 'grid': (180, 180, 180), 'border': (100, 100, 100), 'button_bg': (200, 200, 200), 'button_hover': (170, 170, 170), 'button_text': (10, 10, 10) },
    'Synthwave': { 'background': (29, 25, 43), 'text': (255, 0, 255), 'grid': (0, 255, 255), 'border': (255, 255, 0), 'button_bg': (40, 35, 63), 'button_hover': (60, 55, 83), 'button_text': (0, 255, 255) },
    'Retro': { 'background': (218, 212, 181), 'text': (54, 44, 43), 'grid': (120, 110, 90), 'border': (94, 84, 83), 'button_bg': (180, 172, 141), 'button_hover': (150, 142, 111), 'button_text': (54, 44, 43) },
    'Pink': { 'background': (255, 192, 203), 'text': (139, 0, 139), 'grid': (255, 182, 193), 'border': (219, 112, 147), 'button_bg': (255, 105, 180), 'button_hover': (238, 98, 168), 'button_text': (255, 255, 255) }
}
current_theme_name = 'Dark'
current_theme = THEMES[current_theme_name]
grid_opacity = 100 # Default opacity

# --- Classes ---
class Piece:
    def __init__(self, x, y, shape):
        self.x = x; self.y = y; self.shape = shape; self.color = SHAPE_COLORS[SHAPES.index(shape)]; self.rotation = 0

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height); self.text = text; self.font = pygame.font.SysFont('comicsans', 35, bold=True)

    def draw(self, surface):
        text_color, bg_color, hover_bg_color = current_theme['button_text'], current_theme['button_bg'], current_theme['button_hover']
        mouse_pos = pygame.mouse.get_pos()
        color = hover_bg_color if self.rect.collidepoint(mouse_pos) else bg_color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

# --- Functions ---

def load_settings():
    global current_theme_name, current_theme, grid_opacity
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
            theme_name = settings.get('theme', 'Dark')
            if theme_name in THEMES:
                current_theme_name = theme_name; current_theme = THEMES[theme_name]
            grid_opacity = settings.get('grid_opacity', 100)
    except (FileNotFoundError, json.JSONDecodeError):
        save_settings()

def save_settings():
    with open('settings.json', 'w') as f:
        settings = {'theme': current_theme_name, 'grid_opacity': grid_opacity}
        json.dump(settings, f)

def load_high_score():
    try:
        with open('scores.txt', 'r') as f: return int(f.read())
    except (FileNotFoundError, ValueError): return 0

def save_high_score(score):
    high_score = load_high_score()
    if score > high_score:
        with open('scores.txt', 'w') as f: f.write(str(score))

def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if (x, y) in locked_positions: grid[y][x] = locked_positions[(x, y)]
    return grid

def convert_shape_format(piece):
    positions = []
    fmt = piece.shape[piece.rotation % len(piece.shape)]
    for i, line in enumerate(fmt):
        for j, col in enumerate(list(line)):
            if col == '0': positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions

def valid_space(piece, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]
    formatted = convert_shape_format(piece)
    for pos in formatted:
        if pos not in accepted_pos and pos[1] > -1: return False
    return True

def check_lost(positions):
    for pos in positions:
        if pos[1] < 1: return True
    return False

def get_shape():
    return Piece(5, 0, random.choice(SHAPES))

def draw_text(surface, text, size, color, x, y, center=True):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)
    if center:
        surface.blit(label, (x - label.get_width()/2, y - label.get_height()/2))
    else:
        surface.blit(label, (x, y))
    return label

def draw_grid_lines(surface):
    if grid_opacity == 0:
        return
    
    # Create a transparent surface to draw the lines on
    grid_surface = pygame.Surface((PLAY_WIDTH, PLAY_HEIGHT), pygame.SRCALPHA)
    
    # Calculate alpha from 0-100 opacity to 0-255 alpha
    alpha = int((grid_opacity / 100) * 255)
    grid_color = current_theme['grid']
    line_color = (grid_color[0], grid_color[1], grid_color[2], alpha)

    for i in range(21): # 20 rows
        pygame.draw.line(grid_surface, line_color, (0, i * BLOCK_SIZE), (PLAY_WIDTH, i * BLOCK_SIZE))
    for j in range(11): # 10 columns
        pygame.draw.line(grid_surface, line_color, (j * BLOCK_SIZE, 0), (j * BLOCK_SIZE, PLAY_HEIGHT))
    
    surface.blit(grid_surface, (TOP_LEFT_X, TOP_LEFT_Y))

def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid)-1, -1, -1):
        if (0,0,0) not in grid[i]:
            inc += 1; ind = i
            for j in range(len(grid[i])):
                try: del locked[(j, i)]
                except: continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind: locked[(x, y + inc)] = locked.pop(key)
    return inc

def draw_next_shape(piece, surface):
    sx = TOP_LEFT_X + PLAY_WIDTH + 50; sy = TOP_LEFT_Y + PLAY_HEIGHT/2 - 100
    draw_text(surface, 'Next Shape', 30, current_theme['text'], sx + 10, sy - 30, center=False)
    fmt = piece.shape[piece.rotation % len(piece.shape)]
    for i, line in enumerate(fmt):
        for j, col in enumerate(list(line)):
            if col == '0': pygame.draw.rect(surface, piece.color, (sx + j*BLOCK_SIZE, sy + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

def draw_window(surface, grid, score=0, high_score=0):
    surface.fill(current_theme['background'])
    draw_text(surface, 'TETRIS', 60, current_theme['text'], TOP_LEFT_X + PLAY_WIDTH/2, 60)
    
    sx = TOP_LEFT_X + PLAY_WIDTH + 50; sy = TOP_LEFT_Y + PLAY_HEIGHT/2 - 100
    draw_text(surface, f'Score: {score}', 30, current_theme['text'], sx + 20, sy + 160, center=False)
    draw_text(surface, f'High Score: {high_score}', 30, current_theme['text'], TOP_LEFT_X + 20, TOP_LEFT_Y + 30, center=False)
    
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (TOP_LEFT_X + j*BLOCK_SIZE, TOP_LEFT_Y + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    
    draw_grid_lines(surface) # This function now handles opacity
    pygame.draw.rect(surface, current_theme['border'], (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 5)

def main_game(win):
    high_score = load_high_score(); locked_positions = {}; grid = create_grid(locked_positions)
    change_piece = False; run = True; current_piece = get_shape(); next_piece = get_shape()
    clock = pygame.time.Clock(); fall_time = 0; fall_speed = 0.27; level_time = 0; score = 0

    while run:
        grid = create_grid(locked_positions); fall_time += clock.get_rawtime(); level_time += clock.get_rawtime(); clock.tick()
        if level_time/1000 > 5 and fall_speed > 0.12: level_time = 0; fall_speed -= 0.005
        if fall_time/1000 > fall_speed:
            fall_time = 0; current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0: current_piece.y -= 1; change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False; pygame.display.quit(); quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: run = False
                elif event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid): current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid): current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid): current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid): current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)
                elif event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid): current_piece.y += 1
                    current_piece.y -= 1; change_piece = True

        shape_pos = convert_shape_format(current_piece)
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1: grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos: locked_positions[(pos[0], pos[1])] = current_piece.color
            current_piece = next_piece; next_piece = get_shape(); change_piece = False
            rows_cleared = clear_rows(grid, locked_positions)
            score += [0, 10, 30, 50, 80][rows_cleared] # Better scoring
        
        draw_window(win, grid, score, high_score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        if check_lost(locked_positions):
            save_high_score(score)
            draw_text(win, "YOU LOST!", 80, (255,255,255), SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
            pygame.display.update(); pygame.time.delay(2000); run = False

def settings_screen(win):
    global current_theme_name, current_theme, grid_opacity
    run = True; button_w, button_h = 220, 50
    
    y_start = 120
    theme_buttons = [Button(SCREEN_WIDTH/2 - button_w/2, y_start + i*60, button_w, button_h, theme) for i, theme in enumerate(THEMES)]
    
    # Opacity controls setup
    opacity_y = y_start + len(THEMES)*60 + 40
    opacity_dec_button = Button(SCREEN_WIDTH/2 - 70, opacity_y, 50, 50, "<")
    opacity_inc_button = Button(SCREEN_WIDTH/2 + 20, opacity_y, 50, 50, ">")
    
    back_button = Button(SCREEN_WIDTH/2 - button_w/2, opacity_y + 80, button_w, button_h, "Back")
    
    while run:
        win.fill(current_theme['background'])
        draw_text(win, 'Settings', 70, current_theme['text'], SCREEN_WIDTH/2, 60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: run = False
            
            for button in theme_buttons:
                if button.is_clicked(event):
                    current_theme_name = button.text; current_theme = THEMES[current_theme_name]
            
            if opacity_dec_button.is_clicked(event): grid_opacity = max(0, grid_opacity - 10)
            if opacity_inc_button.is_clicked(event): grid_opacity = min(100, grid_opacity + 10)
            if back_button.is_clicked(event): run = False
        
        # Draw all buttons
        for button in theme_buttons: button.draw(win)
        opacity_dec_button.draw(win); opacity_inc_button.draw(win); back_button.draw(win)
        
        # Draw text labels and the opacity value
        draw_text(win, 'Theme', 30, current_theme['text'], SCREEN_WIDTH/2, y_start - 25)
        draw_text(win, 'Grid Opacity', 30, current_theme['text'], SCREEN_WIDTH/2, opacity_y - 25)
        draw_text(win, f"{grid_opacity}%", 35, current_theme['text'], SCREEN_WIDTH/2, opacity_y + 25)

        pygame.display.update()

    save_settings() # Save settings when leaving the screen

def home_screen(win):
    run = True
    start_button = Button(SCREEN_WIDTH/2-110, 300, 220, 60, "Start Game")
    settings_button = Button(SCREEN_WIDTH/2-110, 380, 220, 60, "Settings")
    quit_button = Button(SCREEN_WIDTH/2-110, 460, 220, 60, "Quit")

    while run:
        win.fill(current_theme['background'])
        high_score = load_high_score()
        draw_text(win, 'PYTHON TETRIS', 90, current_theme['text'], SCREEN_WIDTH/2, 150)
        draw_text(win, f'High Score: {high_score}', 40, current_theme['text'], SCREEN_WIDTH/2, 240)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False
            if start_button.is_clicked(event): main_game(win)
            if settings_button.is_clicked(event): settings_screen(win)
            if quit_button.is_clicked(event): run = False
        
        start_button.draw(win); settings_button.draw(win); quit_button.draw(win)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    pygame.font.init()
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Python Tetris')
    load_settings()
    home_screen(win)
import array
import math
import os
import random
import sys
import pygame

os.environ['SDL_VIDEO_FULLSCREEN_DISPLAY'] = '0'

pygame.init()

# Audio initialization
sound_jump = None
sound_tick = None
sound_win = None

try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)

    def create_tone(freq, duration, volume=0.3):
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        buf = array.array('h')
        for i in range(n_samples):
            val = int(math.sin(2.0 * math.pi * freq * (i / sample_rate)) * 32767 * volume)
            buf.append(val)
        return pygame.mixer.Sound(buffer=buf)

    def create_fanfare():
        sample_rate = 22050
        notes = [(440, 0.12), (554, 0.12), (659, 0.12), (880, 0.35)]
        buf = array.array('h')
        for freq, duration in notes:
            n_samples = int(sample_rate * duration)
            for i in range(n_samples):
                val = int(math.sin(2.0 * math.pi * freq * (i / sample_rate)) * 32767 * 0.4)
                buf.append(val)
        return pygame.mixer.Sound(buffer=buf)

    sound_tick = create_tone(850, 0.03, 0.2)
    sound_jump = create_tone(380, 0.15, 0.35)
    sound_win = create_fanfare()
except Exception:
    pass

def play_sfx(s):
    try:
        if s:
            s.play()
    except Exception:
        pass

info = pygame.display.Info()
device_w = info.current_w
device_h = info.current_h

if device_w < device_h:
    REAL_W, REAL_H = device_h, device_w
else:
    REAL_W, REAL_H = device_w, device_h

real_screen = pygame.display.set_mode((REAL_W, REAL_H), pygame.FULLSCREEN)
pygame.display.set_caption("THE SPEED RUN - 500 LEVELS")

V_WIDTH = 960
V_HEIGHT = 540
screen = pygame.Surface((V_WIDTH, V_HEIGHT))

clock = pygame.time.Clock()
font_logo = pygame.font.Font(None, 110)
font_title = pygame.font.Font(None, 65)
font_text = pygame.font.Font(None, 30)
font_small = pygame.font.Font(None, 24)
font_coin = pygame.font.Font(None, 20)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
GROUND_COLOR = (34, 139, 34)
ROAD_BORDER = (20, 90, 20)
PLATFORM_COLOR = (110, 75, 45)
PLATFORM_TOP = (160, 110, 60)
OBSTACLE_COLOR = (204, 0, 0)
OVERHEAD_COLOR = (139, 0, 0)
DANGER_BALL_COLOR = (220, 20, 60)
GOLD = (255, 215, 0)
GREEN_BTN = (46, 204, 113)
BLUE_BTN = (52, 152, 219)
GRAY = (180, 180, 180)
DARK_GRAY = (50, 50, 50)
PURPLE_CARD = (142, 68, 173)
ORANGE_CARD = (230, 126, 34)
SHIELD_GLOW = (52, 152, 219)
CYAN = (0, 255, 255)

ground_y = 420
upper_path_y = 260

player_x = 120
player_width = 36
player_height = 56
player_y = ground_y - player_height

is_jumping = False
jump_velocity = 13.5
gravity = 1.35
velocity_y = 0

obstacle_width = 28
obstacles = []
overhead_obstacles = []
overhead_width = 45
overhead_height = 45

upper_platforms = []
danger_ball_radius = 15
platform_queue = 0
platform_milestone_spawned = -1

coins = []
coin_radius = 15
track_stars = []
star_radius = 18

n_cards = []
b_cards = []
card_width = 34
card_height = 45

shield_timer = 0
speed_timer = 0

run_anim_frame = 0
tick_sound_timer = 0

distance_meters = 0.0
total_coins = 0

current_level = 1
max_levels = 500
unlocked_levels = 1
level_stars = {i: 0 for i in range(1, max_levels + 1)}
target_distance = 1000.0
stars_collected_in_run = 0
finish_line_x = None

star1_spawned = False
star2_spawned = False

level_page = 0

game_state = "SPLASH"
loading_progress = 0.0

bonus_claimed_milestone = 0
bonus_msg_timer = 0
n_card_spawned_milestone = -1
b_card_spawned_milestone = -1

skins = [
    {"name": "Classic", "type": "human", "price": 0, "unlocked": True, "body": (0, 102, 204), "head": (255, 218, 185), "accent": None},
    {"name": "Dino", "type": "dino", "price": 100, "unlocked": False, "body": (46, 139, 87), "head": (46, 139, 87), "accent": (34, 100, 60)},
    {"name": "Chicken", "type": "bird", "price": 130, "unlocked": False, "body": (255, 255, 255), "head": (255, 255, 255), "accent": (220, 20, 60)},
    {"name": "Duck", "type": "duck", "price": 160, "unlocked": False, "body": (255, 215, 0), "head": (255, 215, 0), "accent": (255, 140, 0)},
    {"name": "Cap America", "type": "human", "price": 200, "unlocked": False, "body": (25, 55, 150), "head": (255, 218, 185), "accent": (200, 20, 20)},
    {"name": "Robin", "type": "human", "price": 240, "unlocked": False, "body": (220, 20, 60), "head": (255, 218, 185), "accent": (46, 204, 113)},
    {"name": "Thor", "type": "human", "price": 280, "unlocked": False, "body": (70, 75, 80), "head": (255, 218, 185), "accent": (180, 20, 20)},
    {"name": "Hulk", "type": "human", "price": 320, "unlocked": False, "body": (40, 140, 40), "head": (35, 120, 35), "accent": (100, 40, 130)},
    {"name": "Wolf", "type": "quad", "price": 360, "unlocked": False, "body": (120, 120, 125), "head": (100, 100, 105), "accent": (40, 40, 45)},
    {"name": "Fox", "type": "quad", "price": 400, "unlocked": False, "body": (220, 90, 20), "head": (220, 90, 20), "accent": (255, 255, 255)},
    {"name": "Lion", "type": "quad", "price": 450, "unlocked": False, "body": (218, 165, 32), "head": (180, 115, 20), "accent": (139, 69, 19)},
    {"name": "Tiger", "type": "quad", "price": 500, "unlocked": False, "body": (230, 110, 25), "head": (230, 110, 25), "accent": (20, 20, 20)},
    {"name": "Leopard", "type": "quad", "price": 550, "unlocked": False, "body": (230, 180, 34), "head": (230, 180, 34), "accent": (40, 30, 10)},
    {"name": "Panda", "type": "quad", "price": 600, "unlocked": False, "body": (240, 240, 240), "head": (240, 240, 240), "accent": (20, 20, 20)},
    {"name": "Eagle", "type": "eagle", "price": 650, "unlocked": False, "body": (100, 60, 30), "head": (245, 245, 245), "accent": (255, 180, 0)},
    {"name": "Falcon", "type": "eagle", "price": 700, "unlocked": False, "body": (70, 70, 75), "head": (50, 50, 55), "accent": (255, 140, 0)},
    {"name": "Flash", "type": "human", "price": 750, "unlocked": False, "body": (210, 20, 20), "head": (210, 20, 20), "accent": (255, 215, 0)},
    {"name": "Spider-Man", "type": "human", "price": 800, "unlocked": False, "body": (180, 20, 20), "head": (180, 20, 20), "accent": (20, 40, 160)},
    {"name": "Panther", "type": "human", "price": 850, "unlocked": False, "body": (25, 25, 30), "head": (25, 25, 30), "accent": (190, 190, 200)},
    {"name": "Batman", "type": "human", "price": 900, "unlocked": False, "body": (30, 30, 35), "head": (20, 20, 25), "accent": (255, 215, 0)},
    {"name": "Wolverine", "type": "human", "price": 950, "unlocked": False, "body": (230, 190, 20), "head": (20, 20, 25), "accent": (20, 35, 140)},
    {"name": "Deadpool", "type": "human", "price": 1000, "unlocked": False, "body": (190, 25, 25), "head": (190, 25, 25), "accent": (20, 20, 20)},
    {"name": "Venom", "type": "human", "price": 1050, "unlocked": False, "body": (15, 15, 20), "head": (15, 15, 20), "accent": (255, 255, 255)},
    {"name": "Iron Man", "type": "human", "price": 1100, "unlocked": False, "body": (178, 34, 34), "head": (212, 175, 55), "accent": (0, 255, 255)},
    {"name": "Cyborg", "type": "human", "price": 1150, "unlocked": False, "body": (160, 165, 175), "head": (160, 165, 175), "accent": (255, 40, 40)},
    {"name": "Doctor Strange", "type": "human", "price": 1200, "unlocked": False, "body": (20, 45, 130), "head": (255, 218, 185), "accent": (190, 20, 20)},
    {"name": "Ghost Rider", "type": "human", "price": 1300, "unlocked": False, "body": (20, 20, 20), "head": (255, 120, 0), "accent": (255, 200, 0)},
    {"name": "Godzilla", "type": "dino", "price": 1380, "unlocked": False, "body": (40, 45, 50), "head": (40, 45, 50), "accent": (0, 180, 255)},
    {"name": "Golden King", "type": "human", "price": 1450, "unlocked": False, "body": (255, 215, 0), "head": (255, 215, 0), "accent": (255, 255, 255)},
    {"name": "Omni God", "type": "human", "price": 1500, "unlocked": False, "body": (230, 235, 255), "head": (255, 255, 255), "accent": (0, 255, 255)}
]
selected_skin = 0
store_page = 0

def draw_star(surface, cx, cy, r, color, outline=True):
    points = []
    for i in range(10):
        angle = i * (math.pi / 5) - (math.pi / 2)
        radius = r if i % 2 == 0 else r * 0.45
        px = cx + radius * math.cos(angle)
        py = cy + radius * math.sin(angle)
        points.append((px, py))
    pygame.draw.polygon(surface, color, points)
    if outline:
        pygame.draw.polygon(surface, BLACK, points, 2)

def get_level_distance(lvl):
    return 1000.0 + (lvl - 1) * 500.0

def spawn_ground_obstacles():
    min_gap = max(130, 220 - int(current_level * 0.2))
    start_x = V_WIDTH + random.randint(40, 90)
    
    if len(overhead_obstacles) > 0:
        last_oh = max(oh["x"] for oh in overhead_obstacles)
        if start_x < last_oh + 170:
            start_x = last_oh + 170

    if current_level < 15:
        return [{"x": start_x, "h": 34}]

    roll = random.random()
    if roll < 0.35 + (current_level * 0.0008):
        return [{"x": start_x, "h": 36}, {"x": start_x + min_gap, "h": 38}]
    elif roll < 0.60 + (current_level * 0.0006):
        return [{"x": start_x, "h": 36}, {"x": start_x + min_gap, "h": 36}, {"x": start_x + (min_gap * 2), "h": 38}]
    else:
        return [{"x": start_x, "h": random.choice([36, 40])}]

def spawn_overhead_obstacle():
    start_x = V_WIDTH + random.randint(90, 160)
    if len(obstacles) > 0:
        last_ground = max(obs["x"] for obs in obstacles)
        if start_x < last_ground + 180:
            start_x = last_ground + 180
    return {"x": start_x, "y": ground_y - 120}

def spawn_upper_platform(start_x):
    length = random.randint(340, 450)
    has_danger = random.random() < 0.6
    danger_x = start_x + length // 2 if has_danger else None
    return {"x": start_x, "y": upper_path_y, "width": length, "height": 20, "danger_x": danger_x}

def spawn_ground_coins():
    new_coins = []
    start_x = V_WIDTH + random.randint(80, 180)
    valid_pos = False
    attempts = 0
    while not valid_pos and attempts < 10:
        attempts += 1
        valid_pos = True
        for obs in obstacles:
            if abs(start_x - obs["x"]) < 60 or abs((start_x + 160) - obs["x"]) < 60:
                start_x += 75
                valid_pos = False
                break

    for i in range(5):
        new_coins.append({"x": start_x + (i * 38), "y": ground_y - 28})
    return new_coins

def spawn_platform_coins(plat_x, plat_len, danger_x):
    new_coins = []
    for i in range(5):
        cx = plat_x + 40 + (i * 50)
        if danger_x is None or abs(cx - danger_x) > 30:
            new_coins.append({"x": cx, "y": upper_path_y - 24})
    return new_coins

def reset_game():
    global player_y, is_jumping, velocity_y, obstacles, overhead_obstacles, upper_platforms
    global coins, track_stars, n_cards, b_cards, distance_meters, shield_timer, speed_timer
    global platform_queue, platform_milestone_spawned, n_card_spawned_milestone, b_card_spawned_milestone
    global bonus_claimed_milestone, bonus_msg_timer, target_distance, stars_collected_in_run, finish_line_x
    global star1_spawned, star2_spawned, tick_sound_timer
    
    player_y = ground_y - player_height
    is_jumping = False
    velocity_y = 0
    distance_meters = 0.0
    shield_timer = 0
    speed_timer = 0
    tick_sound_timer = 0
    bonus_claimed_milestone = 0
    bonus_msg_timer = 0
    stars_collected_in_run = 0
    finish_line_x = None
    star1_spawned = False
    star2_spawned = False
    
    target_distance = get_level_distance(current_level)
    platform_queue = 0
    platform_milestone_spawned = -1
    n_card_spawned_milestone = -1
    b_card_spawned_milestone = -1
    obstacles = spawn_ground_obstacles()
    overhead_obstacles = []
    upper_platforms = []
    coins = spawn_ground_coins()
    track_stars = []
    n_cards = []
    b_cards = []

reset_game()

# HOME SCREEN BUTTONS
start_play_btn = pygame.Rect(V_WIDTH // 2 - 105, 185, 210, 50)
start_levels_btn = pygame.Rect(V_WIDTH // 2 - 105, 255, 210, 50)
start_store_btn = pygame.Rect(V_WIDTH // 2 - 105, 325, 210, 50)

# GAMEOVER BUTTONS
gameover_restart_btn = pygame.Rect(V_WIDTH // 2 - 120, 290, 240, 50)
gameover_home_btn = pygame.Rect(V_WIDTH // 2 - 120, 360, 240, 50)

win_next_btn = pygame.Rect(V_WIDTH // 2 - 120, 300, 240, 50)
win_menu_btn = pygame.Rect(V_WIDTH // 2 - 120, 370, 240, 50)

back_btn_rect = pygame.Rect(40, 20, 100, 40)
next_page_btn = pygame.Rect(V_WIDTH - 140, V_HEIGHT - 60, 110, 38)
prev_page_btn = pygame.Rect(40, V_HEIGHT - 60, 110, 38)

level_button_rects = []
grid_start_x = 90
grid_start_y = 80
cell_w = 140
cell_h = 75
gap_x = 20
gap_y = 15

for row in range(4):
    for col in range(5):
        rx = grid_start_x + col * (cell_w + gap_x)
        ry = grid_start_y + row * (cell_h + gap_y)
        level_button_rects.append(pygame.Rect(rx, ry, cell_w, cell_h))

skin_cards = [
    pygame.Rect(80, 85, 240, 175),
    pygame.Rect(360, 85, 240, 175),
    pygame.Rect(640, 85, 240, 175),
    pygame.Rect(80, 280, 240, 175),
    pygame.Rect(360, 280, 240, 175),
    pygame.Rect(640, 280, 240, 175)
]

def draw_lock_icon(surface, cx, cy):
    pygame.draw.rect(surface, (140, 140, 140), (cx - 10, cy - 2, 20, 16), border_radius=3)
    pygame.draw.arc(surface, (140, 140, 140), (cx - 7, cy - 14, 14, 16), 0, math.pi, 3)
    pygame.draw.circle(surface, BLACK, (cx, cy + 4), 2)
    pygame.draw.line(surface, BLACK, (cx, cy + 5), (cx, cy + 9), 2)

def draw_animated_character(x, y, skin_idx, leg_offset):
    skin = skins[skin_idx]
    stype = skin["type"]

    if shield_timer > 0:
        pygame.draw.ellipse(screen, SHIELD_GLOW, (x - 8, y - 10, player_width + 16, player_height + 15), 3)

    if stype == "human":
        body_h = 28
        head_r = 10
        pygame.draw.rect(screen, skin["body"], (x + 6, y + 10, player_width - 12, body_h))
        pygame.draw.circle(screen, skin["head"], (int(x) + player_width // 2, int(y) + 4), head_r)

        if skin["name"] == "Iron Man":
            pygame.draw.circle(screen, skin["accent"], (int(x) + player_width // 2, int(y) + 24), 4)
            pygame.draw.rect(screen, (178, 34, 34), (int(x) + 10, int(y) - 4, 16, 4))
        elif skin["name"] == "Omni God":
            pygame.draw.circle(screen, skin["accent"], (int(x) + player_width // 2, int(y) + 22), 6)
            pygame.draw.circle(screen, GOLD, (int(x) + player_width // 2, int(y) + 4), head_r + 2, 2)
        elif skin["name"] == "Cap America":
            pygame.draw.rect(screen, WHITE, (int(x) + 10, int(y) + 18, 16, 4))
            pygame.draw.circle(screen, skin["accent"], (int(x) + 4, int(y) + 26), 9, 2)
        elif skin["name"] == "Thor":
            pygame.draw.rect(screen, skin["accent"], (int(x) - 4, int(y) + 10, 8, 30))
        elif skin["name"] == "Hulk":
            pygame.draw.rect(screen, skin["accent"], (int(x) + 6, int(y) + 25, player_width - 12, 15))
        elif skin["name"] == "Panther":
            pygame.draw.rect(screen, skin["accent"], (int(x) + 10, int(y) + 16, 16, 3))
            pygame.draw.circle(screen, WHITE, (int(x) + player_width // 2 - 4, int(y) + 4), 2)
            pygame.draw.circle(screen, WHITE, (int(x) + player_width // 2 + 4, int(y) + 4), 2)
        elif skin["name"] == "Spider-Man":
            pygame.draw.rect(screen, skin["accent"], (int(x) + 6, int(y) + 14, 5, 20))
            pygame.draw.rect(screen, skin["accent"], (int(x) + player_width - 11, int(y) + 14, 5, 20))
        elif skin["name"] in ("Ghost Rider", "Deadpool", "Batman", "Flash", "Venom"):
            pygame.draw.rect(screen, skin["accent"], (int(x) + 10, int(y) + 18, 16, 8))

        leg1_x = x + 12 + leg_offset
        leg2_x = x + player_width - 12 - leg_offset
        pygame.draw.line(screen, BLACK, (x + 12, y + 38), (leg1_x, y + player_height), 4)
        pygame.draw.line(screen, BLACK, (x + player_width - 12, y + 38), (leg2_x, y + player_height), 4)

    elif stype == "dino":
        pygame.draw.rect(screen, skin["body"], (x + 4, y + 12, player_width - 4, 25), border_radius=5)
        pygame.draw.rect(screen, skin["head"], (x + player_width - 8, y + 4, 16, 17), border_radius=4)
        pygame.draw.polygon(screen, skin["accent"], [(x + 4, y + 20), (x - 12, y + 28), (x + 4, y + 33)])
        pygame.draw.circle(screen, WHITE, (int(x + player_width + 1), int(y + 8)), 2)
        leg1_x = x + 10 + leg_offset
        leg2_x = x + player_width - 6 - leg_offset
        pygame.draw.line(screen, skin["accent"], (x + 12, y + 36), (leg1_x, y + player_height), 5)
        pygame.draw.line(screen, skin["accent"], (x + player_width - 4, y + 36), (leg2_x, y + player_height), 5)

    elif stype in ("bird", "duck", "eagle"):
        pygame.draw.ellipse(screen, skin["body"], (x, y + 12, player_width, 28))
        pygame.draw.circle(screen, skin["head"], (int(x + player_width - 4), int(y + 14)), 10)
        if stype == "bird":
            pygame.draw.polygon(screen, (255, 140, 0), [(x + player_width + 4, y + 14), (x + player_width + 18, y + 18), (x + player_width + 4, y + 22)])
            pygame.draw.polygon(screen, skin["accent"], [(x + player_width - 6, y + 4), (x + player_width - 2, y - 4), (x + player_width + 2, y + 4)])
        elif stype == "duck":
            pygame.draw.polygon(screen, (255, 140, 0), [(x + player_width + 4, y + 14), (x + player_width + 18, y + 18), (x + player_width + 4, y + 22)])
        else:
            pygame.draw.polygon(screen, skin["accent"], [(x + player_width + 4, y + 15), (x + player_width + 16, y + 18), (x + player_width + 4, y + 24)])
        pygame.draw.circle(screen, BLACK, (int(x + player_width - 2), int(y + 12)), 2)
        leg1_x = x + 12 + leg_offset
        leg2_x = x + 22 - leg_offset
        pygame.draw.line(screen, (255, 140, 0), (x + 12, y + 40), (leg1_x, y + player_height), 3)
        pygame.draw.line(screen, (255, 140, 0), (x + 22, y + 40), (leg2_x, y + player_height), 3)

    elif stype == "quad":
        pygame.draw.rect(screen, skin["body"], (x, y + 16, player_width + 6, 20), border_radius=5)
        pygame.draw.circle(screen, skin["head"], (int(x + player_width + 4), int(y + 16)), 12)
        if skin["name"] == "Lion":
            pygame.draw.circle(screen, skin["accent"], (int(x + player_width + 4), int(y + 16)), 15, 3)
        elif skin["name"] == "Tiger":
            pygame.draw.line(screen, skin["accent"], (x + 12, y + 16), (x + 12, y + 36), 2)
            pygame.draw.line(screen, skin["accent"], (x + 22, y + 16), (x + 22, y + 36), 2)
            pygame.draw.line(screen, skin["accent"], (x + 32, y + 16), (x + 32, y + 36), 2)
        elif skin["name"] == "Panda":
            pygame.draw.circle(screen, skin["accent"], (int(x + player_width + 6), int(y + 13)), 3)
            pygame.draw.rect(screen, skin["accent"], (x + 8, y + 20, 14, 16))
        else:
            pygame.draw.circle(screen, skin["accent"], (int(x + 8), int(y + 22)), 2)
            pygame.draw.circle(screen, skin["accent"], (int(x + 20), int(y + 26)), 2)
            pygame.draw.circle(screen, skin["accent"], (int(x + 32), int(y + 21)), 2)
        l1 = x + 5 + leg_offset
        l2 = x + 14 - leg_offset
        l3 = x + player_width - 4 + leg_offset
        l4 = x + player_width + 4 - leg_offset
        pygame.draw.line(screen, skin["body"], (x + 5, y + 36), (l1, y + player_height), 3)
        pygame.draw.line(screen, skin["body"], (x + 14, y + 36), (l2, y + player_height), 3)
        pygame.draw.line(screen, skin["body"], (x + player_width - 4, y + 36), (l3, y + player_height), 3)
        pygame.draw.line(screen, skin["body"], (x + player_width + 4, y + 36), (l4, y + player_height), 3)

running = True
while running:
    clock.tick(60)

    cur_w, cur_h = real_screen.get_size()
    if cur_w < cur_h:
        real_screen = pygame.display.set_mode((cur_h, cur_w), pygame.FULLSCREEN)
        REAL_W, REAL_H = cur_h, cur_w
    elif cur_w != REAL_W or cur_h != REAL_H:
        REAL_W, REAL_H = cur_w, cur_h

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

        if event.type == pygame.VIDEORESIZE:
            REAL_W, REAL_H = event.w, event.h

        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
            rx, ry = event.pos if event.type == pygame.MOUSEBUTTONDOWN else (event.x * REAL_W, event.y * REAL_H)
            vx = int(rx * V_WIDTH / REAL_W)
            vy = int(ry * V_HEIGHT / REAL_H)

            if game_state == "START":
                if start_play_btn.collidepoint((vx, vy)):
                    reset_game()
                    game_state = "PLAYING"
                elif start_levels_btn.collidepoint((vx, vy)):
                    level_page = (current_level - 1) // 20
                    game_state = "LEVEL_SELECT"
                elif start_store_btn.collidepoint((vx, vy)):
                    game_state = "STORE"

            elif game_state == "LEVEL_SELECT":
                if back_btn_rect.collidepoint((vx, vy)):
                    game_state = "START"
                elif next_page_btn.collidepoint((vx, vy)) and (level_page + 1) * 20 < max_levels:
                    level_page += 1
                elif prev_page_btn.collidepoint((vx, vy)) and level_page > 0:
                    level_page -= 1
                else:
                    for i, rect in enumerate(level_button_rects):
                        lvl_num = level_page * 20 + i + 1
                        if lvl_num <= max_levels and rect.collidepoint((vx, vy)):
                            if lvl_num <= unlocked_levels:
                                current_level = lvl_num
                                reset_game()
                                game_state = "PLAYING"

            elif game_state == "STORE":
                if back_btn_rect.collidepoint((vx, vy)):
                    game_state = "START"
                elif next_page_btn.collidepoint((vx, vy)) and (store_page + 1) * 6 < len(skins):
                    store_page += 1
                elif prev_page_btn.collidepoint((vx, vy)) and store_page > 0:
                    store_page -= 1
                else:
                    for i, card in enumerate(skin_cards):
                        idx = store_page * 6 + i
                        if idx < len(skins) and card.collidepoint((vx, vy)):
                            if skins[idx]["unlocked"]:
                                selected_skin = idx
                            elif total_coins >= skins[idx]["price"]:
                                total_coins -= skins[idx]["price"]
                                skins[idx]["unlocked"] = True
                                selected_skin = idx

            elif game_state == "GAMEOVER":
                if gameover_restart_btn.collidepoint((vx, vy)):
                    reset_game()
                    game_state = "PLAYING"
                elif gameover_home_btn.collidepoint((vx, vy)):
                    game_state = "START"

            elif game_state == "LEVEL_COMPLETE":
                if win_next_btn.collidepoint((vx, vy)):
                    if current_level < max_levels:
                        current_level += 1
                    reset_game()
                    game_state = "PLAYING"
                elif win_menu_btn.collidepoint((vx, vy)):
                    game_state = "START"

            elif game_state == "PLAYING":
                if not is_jumping:
                    is_jumping = True
                    velocity_y = -jump_velocity
                    play_sfx(sound_jump)

    if game_state == "SPLASH":
        loading_progress += 1.2
        if loading_progress >= 100.0:
            loading_progress = 100.0
            game_state = "START"

        screen.fill((15, 15, 20))
        logo_surf = font_logo.render("MNR", True, CYAN)
        screen.blit(logo_surf, (V_WIDTH // 2 - logo_surf.get_width() // 2, 160))

        sub_surf = font_small.render("G A M E  S T U D I O S", True, (160, 180, 200))
        screen.blit(sub_surf, (V_WIDTH // 2 - sub_surf.get_width() // 2, 260))

        bar_w = 420
        bar_h = 16
        bar_x = V_WIDTH // 2 - bar_w // 2
        bar_y = 350
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_w, bar_h), border_radius=8)

        fill_w = int((loading_progress / 100.0) * bar_w)
        if fill_w > 0:
            pygame.draw.rect(screen, CYAN, (bar_x, bar_y, fill_w, bar_h), border_radius=8)

        pct_text = font_text.render(f"Loading... {int(loading_progress)}%", True, WHITE)
        screen.blit(pct_text, (V_WIDTH // 2 - pct_text.get_width() // 2, bar_y + 30))

    elif game_state == "PLAYING":
        run_anim_frame += 0.4

        if not is_jumping:
            tick_sound_timer += 1
            if tick_sound_timer >= 15:
                play_sfx(sound_tick)
                tick_sound_timer = 0
        else:
            tick_sound_timer = 0

        current_floor_y = ground_y
        for plat in upper_platforms:
            if plat["x"] <= player_x + player_width and plat["x"] + plat["width"] >= player_x:
                if player_y + player_height <= plat["y"] + 15 and velocity_y >= 0:
                    current_floor_y = plat["y"]

        if is_jumping or player_y + player_height < current_floor_y:
            player_y += velocity_y
            velocity_y += gravity

            if player_y >= current_floor_y - player_height:
                player_y = current_floor_y - player_height
                is_jumping = False
                velocity_y = 0
        else:
            player_y = current_floor_y - player_height

        if player_y + player_height > upper_path_y and current_floor_y == ground_y and player_y < ground_y - player_height:
            is_jumping = True

        if shield_timer > 0:
            shield_timer -= 1

        if speed_timer > 0:
            speed_timer -= 1

        level_speed_add = min(20.0, current_level * 0.1)
        current_speed = 65.0 + level_speed_add + int(distance_meters // 100)

        if speed_timer > 0:
            effective_speed = current_speed * 1.5
        else:
            effective_speed = current_speed

        distance_meters += effective_speed / 60.0
        current_meters = int(distance_meters)

        p1 = target_distance * 0.33
        p2 = target_distance * 0.66
        if distance_meters >= p1 and not star1_spawned:
            track_stars.append({"x": V_WIDTH + 80, "y": ground_y - 35})
            star1_spawned = True
        if distance_meters >= p2 and not star2_spawned:
            track_stars.append({"x": V_WIDTH + 80, "y": ground_y - 35})
            star2_spawned = True

        if distance_meters >= target_distance and finish_line_x is None:
            finish_line_x = V_WIDTH + 150

        if current_meters >= 1000:
            m_stage = (current_meters // 1000) * 1000
            if m_stage > bonus_claimed_milestone:
                bonus_claimed_milestone = m_stage
                total_coins += 100
                bonus_msg_timer = 90

        obstacle_speed = (effective_speed / 65.0) * 10.0

        if len(overhead_obstacles) == 0 and len(upper_platforms) == 0 and finish_line_x is None:
            can_spawn_oh = True
            for obs in obstacles:
                if abs(V_WIDTH - obs["x"]) < 200:
                    can_spawn_oh = False
                    break
            if can_spawn_oh and random.random() < 0.012:
                overhead_obstacles.append(spawn_overhead_obstacle())

        if current_meters >= 2000 and finish_line_x is None:
            m_target = 2000 + max(0, ((current_meters - 2000) // 2000)) * 2000
            if current_meters >= m_target and platform_milestone_spawned != m_target:
                platform_queue = random.randint(2, 3)
                platform_milestone_spawned = m_target

        if platform_queue > 0:
            if len(upper_platforms) == 0 or (upper_platforms[-1]["x"] + upper_platforms[-1]["width"] < V_WIDTH - 150):
                new_start_x = V_WIDTH + 80
                new_p = spawn_upper_platform(new_start_x)
                upper_platforms.append(new_p)
                coins.extend(spawn_platform_coins(new_p["x"], new_p["width"], new_p["danger_x"]))
                platform_queue -= 1

        if current_meters >= 500 and finish_line_x is None:
            b_target = (current_meters // 500) * 500
            if b_card_spawned_milestone != b_target:
                b_cards.append({"x": V_WIDTH + 80, "y": ground_y - 40})
                b_card_spawned_milestone = b_target

        if current_meters >= 1000 and finish_line_x is None:
            n_target = (current_meters // 1000) * 1000
            if n_card_spawned_milestone != n_target:
                n_cards.append({"x": V_WIDTH + 80, "y": ground_y - 40})
                n_card_spawned_milestone = n_target

        for obs in obstacles:
            obs["x"] -= obstacle_speed

        if obstacles[-1]["x"] < -obstacle_width and finish_line_x is None:
            obstacles = spawn_ground_obstacles()

        for obs in overhead_obstacles[:]:
            obs["x"] -= obstacle_speed
            if obs["x"] < -overhead_width:
                overhead_obstacles.remove(obs)

        for plat in upper_platforms:
            plat["x"] -= obstacle_speed
            if plat["danger_x"] is not None:
                plat["danger_x"] -= obstacle_speed

        if len(upper_platforms) > 0 and upper_platforms[0]["x"] + upper_platforms[0]["width"] < -80:
            upper_platforms.pop(0)

        if finish_line_x is not None:
            finish_line_x -= obstacle_speed
            if player_x >= finish_line_x:
                stars_collected_in_run = min(3, stars_collected_in_run + 1)
                level_stars[current_level] = max(level_stars[current_level], stars_collected_in_run)
                if current_level == unlocked_levels and unlocked_levels < max_levels:
                    unlocked_levels += 1
                play_sfx(sound_win)
                game_state = "LEVEL_COMPLETE"

        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

        for coin in coins[:]:
            coin["x"] -= obstacle_speed
            coin_rect = pygame.Rect(coin["x"] - coin_radius, coin["y"] - coin_radius, coin_radius * 2, coin_radius * 2)
            if player_rect.colliderect(coin_rect):
                total_coins += 1
                coins.remove(coin)
            elif coin["x"] < -coin_radius:
                coins.remove(coin)

        for st in track_stars[:]:
            st["x"] -= obstacle_speed
            st_rect = pygame.Rect(st["x"] - star_radius, st["y"] - star_radius, star_radius * 2, star_radius * 2)
            if player_rect.colliderect(st_rect):
                stars_collected_in_run += 1
                track_stars.remove(st)
            elif st["x"] < -star_radius:
                track_stars.remove(st)

        if len(coins) < 4 and finish_line_x is None:
            coins.extend(spawn_ground_coins())

        for card in n_cards[:]:
            card["x"] -= obstacle_speed
            card_rect = pygame.Rect(card["x"], card["y"], card_width, card_height)
            if player_rect.colliderect(card_rect):
                shield_timer = 1800
                n_cards.remove(card)
            elif card["x"] < -card_width:
                n_cards.remove(card)

        for card in b_cards[:]:
            card["x"] -= obstacle_speed
            card_rect = pygame.Rect(card["x"], card["y"], card_width, card_height)
            if player_rect.colliderect(card_rect):
                speed_timer = 480
                b_cards.remove(card)
            elif card["x"] < -card_width:
                b_cards.remove(card)

        for obs in obstacles:
            obs_rect = pygame.Rect(obs["x"], ground_y - obs["h"], obstacle_width, obs["h"])
            if player_rect.colliderect(obs_rect):
                if shield_timer <= 0:
                    game_state = "GAMEOVER"

        for obs in overhead_obstacles:
            oh_rect = pygame.Rect(obs["x"], obs["y"], overhead_width, overhead_height)
            if player_rect.colliderect(oh_rect):
                if shield_timer <= 0:
                    game_state = "GAMEOVER"

        for plat in upper_platforms:
            if plat["danger_x"] is not None:
                ball_rect = pygame.Rect(plat["danger_x"] - danger_ball_radius, upper_path_y - danger_ball_radius * 2, danger_ball_radius * 2, danger_ball_radius * 2)
                if player_rect.colliderect(ball_rect):
                    if shield_timer <= 0:
                        game_state = "GAMEOVER"

    if game_state not in ("SPLASH", "LEVEL_SELECT"):
        screen.fill(SKY_BLUE)
        pygame.draw.rect(screen, GROUND_COLOR, (0, ground_y, V_WIDTH, V_HEIGHT - ground_y))
        pygame.draw.line(screen, ROAD_BORDER, (0, ground_y), (V_WIDTH, ground_y), 5)

        for plat in upper_platforms:
            pygame.draw.rect(screen, PLATFORM_COLOR, (plat["x"], plat["y"], plat["width"], plat["height"]), border_radius=4)
            pygame.draw.rect(screen, PLATFORM_TOP, (plat["x"], plat["y"], plat["width"], 4), border_radius=3)
            if plat["danger_x"] is not None:
                pygame.draw.circle(screen, DANGER_BALL_COLOR, (int(plat["danger_x"]), upper_path_y - danger_ball_radius), danger_ball_radius)
                pygame.draw.circle(screen, BLACK, (int(plat["danger_x"]), upper_path_y - danger_ball_radius), danger_ball_radius, 2)

    if game_state == "START":
        title_text = font_title.render("THE SPEED RUN", True, BLACK)
        screen.blit(title_text, (V_WIDTH // 2 - title_text.get_width() // 2, 50))

        lvl_disp = font_text.render(f"Current Level: {current_level} / {max_levels}", True, (20, 20, 100))
        screen.blit(lvl_disp, (V_WIDTH // 2 - lvl_disp.get_width() // 2, 115))
        
        goal_disp = font_small.render(f"Level Target: {int(target_distance)} Meters", True, DARK_GRAY)
        screen.blit(goal_disp, (V_WIDTH // 2 - goal_disp.get_width() // 2, 145))

        pygame.draw.rect(screen, GREEN_BTN, start_play_btn, border_radius=14)
        pygame.draw.rect(screen, BLACK, start_play_btn, 3, border_radius=14)
        play_lbl = font_text.render("PLAY", True, WHITE)
        screen.blit(play_lbl, (start_play_btn.centerx - play_lbl.get_width() // 2, start_play_btn.centery - play_lbl.get_height() // 2))

        pygame.draw.rect(screen, BLUE_BTN, start_levels_btn, border_radius=14)
        pygame.draw.rect(screen, BLACK, start_levels_btn, 3, border_radius=14)
        lvl_btn_lbl = font_text.render("LEVELS", True, WHITE)
        screen.blit(lvl_btn_lbl, (start_levels_btn.centerx - lvl_btn_lbl.get_width() // 2, start_levels_btn.centery - lvl_btn_lbl.get_height() // 2))

        pygame.draw.rect(screen, GOLD, start_store_btn, border_radius=14)
        pygame.draw.rect(screen, BLACK, start_store_btn, 3, border_radius=14)
        store_lbl = font_text.render("STORE", True, BLACK)
        screen.blit(store_lbl, (start_store_btn.centerx - store_lbl.get_width() // 2, start_store_btn.centery - store_lbl.get_height() // 2))

        coin_txt = font_text.render(f"M Coins: {total_coins}", True, (180, 130, 0))
        screen.blit(coin_txt, (V_WIDTH - coin_txt.get_width() - 25, 25))

        preview_x = V_WIDTH - 170
        preview_y = ground_y - player_height
        draw_animated_character(preview_x, preview_y, selected_skin, 0)
        skin_name_lbl = font_small.render(skins[selected_skin]["name"], True, BLACK)
        screen.blit(skin_name_lbl, (preview_x + player_width // 2 - skin_name_lbl.get_width() // 2, preview_y - 25))

    elif game_state == "LEVEL_SELECT":
        screen.fill((235, 240, 245))

        title_text = font_title.render(f"SELECT LEVEL ({level_page * 20 + 1} - {min(max_levels, (level_page + 1) * 20)})", True, BLACK)
        screen.blit(title_text, (V_WIDTH // 2 - title_text.get_width() // 2, 20))

        pygame.draw.rect(screen, DARK_GRAY, back_btn_rect, border_radius=8)
        back_txt = font_small.render("BACK", True, WHITE)
        screen.blit(back_txt, (back_btn_rect.centerx - back_txt.get_width() // 2, back_btn_rect.centery - back_txt.get_height() // 2))

        if (level_page + 1) * 20 < max_levels:
            pygame.draw.rect(screen, BLUE_BTN, next_page_btn, border_radius=8)
            nxt_txt = font_small.render("NEXT >", True, WHITE)
            screen.blit(nxt_txt, (next_page_btn.centerx - nxt_txt.get_width() // 2, next_page_btn.centery - nxt_txt.get_height() // 2))

        if level_page > 0:
            pygame.draw.rect(screen, BLUE_BTN, prev_page_btn, border_radius=8)
            prv_txt = font_small.render("< PREV", True, WHITE)
            screen.blit(prv_txt, (prev_page_btn.centerx - prv_txt.get_width() // 2, prev_page_btn.centery - prv_txt.get_height() // 2))

        for i, rect in enumerate(level_button_rects):
            lvl_num = level_page * 20 + i + 1
            if lvl_num <= max_levels:
                is_unlocked = lvl_num <= unlocked_levels
                is_cur = (lvl_num == current_level)

                card_bg = WHITE if is_unlocked else (210, 210, 215)
                border_color = (0, 180, 0) if is_cur else (BLACK if is_unlocked else (160, 160, 160))
                border_w = 3 if is_cur else 2

                pygame.draw.rect(screen, card_bg, rect, border_radius=10)
                pygame.draw.rect(screen, border_color, rect, border_w, border_radius=10)

                if is_unlocked:
                    stars = level_stars.get(lvl_num, 0)
                    for s in range(3):
                        star_x = rect.centerx - 22 + (s * 22)
                        star_y = rect.y + 18
                        c = GOLD if s < stars else (190, 190, 195)
                        draw_star(screen, star_x, star_y, 7, c, outline=True)

                    num_surf = font_text.render(f"Level {lvl_num}", True, BLACK)
                    screen.blit(num_surf, (rect.centerx - num_surf.get_width() // 2, rect.bottom - 36))
                else:
                    num_surf = font_small.render(f"Level {lvl_num}", True, (130, 130, 130))
                    screen.blit(num_surf, (rect.centerx - num_surf.get_width() // 2, rect.y + 12))
                    draw_lock_icon(screen, rect.centerx, rect.bottom - 24)

    elif game_state == "STORE":
        screen.fill((240, 240, 240))
        total_store_pages = (len(skins) + 5) // 6
        title_text = font_title.render(f"STORE (Page {store_page + 1}/{total_store_pages})", True, BLACK)
        screen.blit(title_text, (V_WIDTH // 2 - title_text.get_width() // 2, 20))

        coin_txt = font_text.render(f"Your M Coins: {total_coins}", True, (180, 130, 0))
        screen.blit(coin_txt, (V_WIDTH - coin_txt.get_width() - 30, 25))

        pygame.draw.rect(screen, DARK_GRAY, back_btn_rect, border_radius=8)
        back_txt = font_small.render("BACK", True, WHITE)
        screen.blit(back_txt, (back_btn_rect.centerx - back_txt.get_width() // 2, back_btn_rect.centery - back_txt.get_height() // 2))

        if (store_page + 1) * 6 < len(skins):
            pygame.draw.rect(screen, BLUE_BTN, next_page_btn, border_radius=8)
            nxt_txt = font_small.render("NEXT >", True, WHITE)
            screen.blit(nxt_txt, (next_page_btn.centerx - nxt_txt.get_width() // 2, next_page_btn.centery - nxt_txt.get_height() // 2))

        if store_page > 0:
            pygame.draw.rect(screen, BLUE_BTN, prev_page_btn, border_radius=8)
            prv_txt = font_small.render("< PREV", True, WHITE)
            screen.blit(prv_txt, (prev_page_btn.centerx - prv_txt.get_width() // 2, prev_page_btn.centery - prv_txt.get_height() // 2))

        for i, card in enumerate(skin_cards):
            idx = store_page * 6 + i
            if idx < len(skins):
                skin = skins[idx]
                is_sel = (idx == selected_skin)
                border_c = (0, 150, 0) if is_sel else (100, 100, 100)

                pygame.draw.rect(screen, WHITE, card, border_radius=10)
                pygame.draw.rect(screen, border_c, card, 3 if is_sel else 1, border_radius=10)

                name_t = font_small.render(skin["name"], True, BLACK)
                screen.blit(name_t, (card.centerx - name_t.get_width() // 2, card.y + 12))

                draw_animated_character(card.centerx - player_width // 2, card.y + 55, idx, 0)

                if is_sel:
                    status_t = font_small.render("EQUIPPED", True, (0, 150, 0))
                elif skin["unlocked"]:
                    status_t = font_small.render("SELECT", True, BLACK)
                else:
                    status_t = font_small.render(f"{skin['price']} M Coins", True, (160, 30, 30))
                screen.blit(status_t, (card.centerx - status_t.get_width() // 2, card.bottom - 28))

    elif game_state == "PLAYING":
        leg_offset = 0 if is_jumping else int(math.sin(run_anim_frame) * 7)
        draw_animated_character(player_x, player_y, selected_skin, leg_offset)

        for obs in obstacles:
            pygame.draw.rect(screen, OBSTACLE_COLOR, (obs["x"], ground_y - obs["h"], obstacle_width, obs["h"]))

        for obs in overhead_obstacles:
            ox, oy = obs["x"], obs["y"]
            pygame.draw.rect(screen, OVERHEAD_COLOR, (ox, oy, overhead_width, overhead_height - 12), border_radius=4)
            pygame.draw.line(screen, DARK_GRAY, (ox + overhead_width // 2, 0), (ox + overhead_width // 2, oy), 3)
            pygame.draw.polygon(screen, OVERHEAD_COLOR, [(ox + 4, oy + overhead_height - 12), (ox + overhead_width // 2, oy + overhead_height), (ox + overhead_width - 4, oy + overhead_height - 12)])

        if finish_line_x is not None:
            pygame.draw.rect(screen, GOLD, (finish_line_x, ground_y - 140, 16, 140))
            pygame.draw.rect(screen, GOLD, (finish_line_x + 70, ground_y - 140, 16, 140))
            pygame.draw.rect(screen, (220, 20, 60), (finish_line_x, ground_y - 135, 86, 35), border_radius=4)
            f_txt = font_small.render("FINISH", True, WHITE)
            screen.blit(f_txt, (finish_line_x + 12, ground_y - 127))

        for coin in coins:
            pygame.draw.circle(screen, GOLD, (int(coin["x"]), int(coin["y"])), coin_radius)
            pygame.draw.circle(screen, BLACK, (int(coin["x"]), int(coin["y"])), coin_radius, 2)
            m_txt = font_coin.render("M", True, BLACK)
            screen.blit(m_txt, (coin["x"] - m_txt.get_width() // 2, coin["y"] - m_txt.get_height() // 2))

        for st in track_stars:
            draw_star(screen, int(st["x"]), int(st["y"]), star_radius, GOLD, outline=True)

        for card in n_cards:
            pygame.draw.rect(screen, PURPLE_CARD, (card["x"], card["y"], card_width, card_height), border_radius=5)
            pygame.draw.rect(screen, WHITE, (card["x"], card["y"], card_width, card_height), 2, border_radius=5)
            n_txt = font_small.render("N", True, WHITE)
            screen.blit(n_txt, (card["x"] + card_width // 2 - n_txt.get_width() // 2, card["y"] + card_height // 2 - n_txt.get_height() // 2))

        for card in b_cards:
            pygame.draw.rect(screen, ORANGE_CARD, (card["x"], card["y"], card_width, card_height), border_radius=5)
            pygame.draw.rect(screen, WHITE, (card["x"], card["y"], card_width, card_height), 2, border_radius=5)
            b_txt = font_small.render("B", True, WHITE)
            screen.blit(b_txt, (card["x"] + card_width // 2 - b_txt.get_width() // 2, card["y"] + card_height // 2 - b_txt.get_height() // 2))

        lvl_t = font_text.render(f"Level: {current_level}/{max_levels}", True, BLACK)
        dist_t = font_small.render(f"Distance: {int(distance_meters)} / {int(target_distance)} m", True, BLACK)
        coin_t = font_text.render(f"M Coins: {total_coins}", True, (180, 130, 0))

        screen.blit(lvl_t, (25, 20))
        screen.blit(dist_t, (25, 55))
        screen.blit(coin_t, (V_WIDTH - coin_t.get_width() - 25, 20))

        for s in range(3):
            sx = V_WIDTH // 2 - 35 + (s * 35)
            sy = 30
            c = GOLD if s < stars_collected_in_run else (190, 190, 195)
            draw_star(screen, sx, sy, 12, c, outline=True)

        if bonus_msg_timer > 0:
            bonus_msg_timer -= 1
            bonus_txt = font_text.render("+100 M-COINS BONUS!", True, GOLD)
            screen.blit(bonus_txt, (V_WIDTH // 2 - bonus_txt.get_width() // 2, 75))

        if shield_timer > 0:
            remaining_sec = (shield_timer // 60) + 1
            shield_txt = font_small.render(f"SHIELD: {remaining_sec}s", True, (0, 102, 204))
            screen.blit(shield_txt, (25, 85))

        if speed_timer > 0:
            speed_sec = (speed_timer // 60) + 1
            boost_txt = font_small.render(f"SPEED BOOST: {speed_sec}s", True, (220, 80, 0))
            screen.blit(boost_txt, (V_WIDTH // 2 - boost_txt.get_width() // 2, 60))

    elif game_state == "LEVEL_COMPLETE":
        win_title = font_title.render("LEVEL COMPLETED!", True, (0, 150, 0))
        screen.blit(win_title, (V_WIDTH // 2 - win_title.get_width() // 2, 60))

        for s in range(3):
            sx = V_WIDTH // 2 - 70 + (s * 70)
            sy = 160
            c = GOLD if s < stars_collected_in_run else (190, 190, 195)
            draw_star(screen, sx, sy, 26, c, outline=True)

        dist_info = font_text.render(f"Distance Reached: {int(distance_meters)} m", True, BLACK)
        coins_info = font_text.render(f"Total M Coins: {total_coins}", True, (180, 130, 0))
        screen.blit(dist_info, (V_WIDTH // 2 - dist_info.get_width() // 2, 220))
        screen.blit(coins_info, (V_WIDTH // 2 - coins_info.get_width() // 2, 255))

        pygame.draw.rect(screen, GREEN_BTN, win_next_btn, border_radius=12)
        pygame.draw.rect(screen, BLACK, win_next_btn, 3, border_radius=12)
        next_lbl = font_text.render("NEXT LEVEL", True, WHITE)
        screen.blit(next_lbl, (win_next_btn.centerx - next_lbl.get_width() // 2, win_next_btn.centery - next_lbl.get_height() // 2))

        pygame.draw.rect(screen, DARK_GRAY, win_menu_btn, border_radius=12)
        pygame.draw.rect(screen, BLACK, win_menu_btn, 3, border_radius=12)
        menu_lbl = font_text.render("MAIN MENU", True, WHITE)
        screen.blit(menu_lbl, (win_menu_btn.centerx - menu_lbl.get_width() // 2, win_menu_btn.centery - menu_lbl.get_height() // 2))

    elif game_state == "GAMEOVER":
        gameover_text = font_title.render("GAME OVER", True, (200, 0, 0))
        final_score_text = font_text.render(f"Level {current_level} Failed at {int(distance_meters)} m", True, BLACK)
        coins_collected_text = font_text.render(f"Total M Coins: {total_coins}", True, (180, 130, 0))

        screen.blit(gameover_text, (V_WIDTH // 2 - gameover_text.get_width() // 2, 70))
        screen.blit(final_score_text, (V_WIDTH // 2 - final_score_text.get_width() // 2, 150))
        screen.blit(coins_collected_text, (V_WIDTH // 2 - coins_collected_text.get_width() // 2, 190))

        pygame.draw.rect(screen, GREEN_BTN, gameover_restart_btn, border_radius=12)
        pygame.draw.rect(screen, BLACK, gameover_restart_btn, 3, border_radius=12)
        restart_lbl = font_text.render("TRY AGAIN", True, WHITE)
        screen.blit(restart_lbl, (gameover_restart_btn.centerx - restart_lbl.get_width() // 2, gameover_restart_btn.centery - restart_lbl.get_height() // 2))

        pygame.draw.rect(screen, BLUE_BTN, gameover_home_btn, border_radius=12)
        pygame.draw.rect(screen, BLACK, gameover_home_btn, 3, border_radius=12)
        home_lbl = font_text.render("HOME", True, WHITE)
        screen.blit(home_lbl, (gameover_home_btn.centerx - home_lbl.get_width() // 2, gameover_home_btn.centery - home_lbl.get_height() // 2))

    scaled_surface = pygame.transform.scale(screen, (REAL_W, REAL_H))
    real_screen.blit(scaled_surface, (0, 0))
    pygame.display.flip()

pygame.quit()

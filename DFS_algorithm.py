import pygame
import random
import time
import heapq
import math

# ================= CONFIG =================
ROWS = 30
COLS = 30
CELL_SIZE = 26

PANEL_HEIGHT = 120
WIDTH = COLS * CELL_SIZE + 2  # +2 for border
HEIGHT = ROWS * CELL_SIZE + PANEL_HEIGHT + 2

# ── Dark terminal / neon theme ──
BG_COLOR        = (10, 12, 20)
PANEL_COLOR     = (16, 18, 30)
WALL_COLOR      = (25, 28, 45)
PATH_COLOR      = (22, 25, 40)
GRID_COLOR      = (30, 35, 55)

VISITED_COLOR   = (0, 180, 140)   # teal
VISITED_DARK    = (0, 100, 80)
PATH_COLOR_DRAW = (255, 210, 0)   # gold path
START_COLOR     = (0, 200, 255)   # cyan
GOAL_COLOR      = (255, 60, 100)  # hot pink

BTN_BASE        = (28, 32, 52)
BTN_HOVER       = (40, 46, 72)
BTN_ACTIVE      = (55, 62, 95)
BTN_BORDER      = (60, 70, 110)
BTN_BORDER_SEL  = (0, 220, 180)
BTN_TEXT        = (180, 190, 220)
BTN_TEXT_SEL    = (0, 255, 200)

INFO_COLOR      = (120, 130, 170)
WHITE           = (255, 255, 255)
BLACK           = (0, 0, 0)

WALL = 1
PATH = 0

# ─── Ripple effect storage ───
ripples = []   # list of {x, y, t, max_t}

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("✦ Qidiruv algoritmlari")

try:
    font_large = pygame.font.SysFont("Consolas", 19, bold=True)
    font_med   = pygame.font.SysFont("Consolas", 15)
    font_small = pygame.font.SysFont("Consolas", 13)
except:
    font_large = pygame.font.SysFont("monospace", 19, bold=True)
    font_med   = pygame.font.SysFont("monospace", 15)
    font_small = pygame.font.SysFont("monospace", 13)

# ================= MAZE =================
def generate_maze():
    maze = [[PATH if random.random() < 0.68 else WALL for _ in range(COLS)] for _ in range(ROWS)]
    start = (random.randint(1, ROWS-2), random.randint(1, COLS-2))
    goal  = (random.randint(1, ROWS-2), random.randint(1, COLS-2))
    while abs(start[0]-goal[0]) + abs(start[1]-goal[1]) < 10:
        goal = (random.randint(1, ROWS-2), random.randint(1, COLS-2))
    maze[start[0]][start[1]] = PATH
    maze[goal[0]][goal[1]]   = PATH
    return maze, start, goal

# ================= DRAW =================
def lerp_color(c1, c2, t):
    return tuple(int(c1[k] + (c2[k]-c1[k])*t) for k in range(3))

def draw_cell(surface, rect, color, border_color=None, border=0):
    pygame.draw.rect(surface, color, rect, border_radius=3)
    if border_color and border:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=3)

def draw_maze(maze, visited, path, start, goal, anim_tick):
    # Background
    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, PANEL_COLOR, (0, ROWS*CELL_SIZE+2, WIDTH, PANEL_HEIGHT))
    # thin separator
    pygame.draw.line(screen, BTN_BORDER, (0, ROWS*CELL_SIZE+2), (WIDTH, ROWS*CELL_SIZE+2), 1)

    # Cells
    for i in range(ROWS):
        for j in range(COLS):
            x = j * CELL_SIZE + 1
            y = i * CELL_SIZE + 1
            rect = pygame.Rect(x, y, CELL_SIZE-1, CELL_SIZE-1)
            node = (i, j)

            if maze[i][j] == WALL:
                draw_cell(screen, rect, WALL_COLOR)
            elif node in visited:
                # pulsing visited glow
                pulse = 0.82 + 0.18 * math.sin(anim_tick * 0.05 + i * 0.3 + j * 0.2)
                col = lerp_color(VISITED_DARK, VISITED_COLOR, pulse)
                draw_cell(screen, rect, col)
            else:
                draw_cell(screen, rect, PATH_COLOR)

            # grid line
            pygame.draw.rect(screen, GRID_COLOR, rect, 1, border_radius=3)

    # Drawn path (gold)
    for idx, node in enumerate(path):
        x = node[1] * CELL_SIZE + 1
        y = node[0] * CELL_SIZE + 1
        rect = pygame.Rect(x, y, CELL_SIZE-1, CELL_SIZE-1)
        draw_cell(screen, rect, PATH_COLOR_DRAW, (255, 240, 120), 1)
        # small dot
        cx, cy = x + (CELL_SIZE-1)//2, y + (CELL_SIZE-1)//2
        pygame.draw.circle(screen, (255, 255, 200), (cx, cy), 3)

    # Start cell
    sx = start[1]*CELL_SIZE+1; sy = start[0]*CELL_SIZE+1
    sr = pygame.Rect(sx, sy, CELL_SIZE-1, CELL_SIZE-1)
    draw_cell(screen, sr, START_COLOR, (150, 240, 255), 2)
    lbl = font_small.render("S", True, BG_COLOR)
    screen.blit(lbl, (sx+(CELL_SIZE-1-lbl.get_width())//2, sy+(CELL_SIZE-1-lbl.get_height())//2))

    # Goal cell
    gx = goal[1]*CELL_SIZE+1; gy = goal[0]*CELL_SIZE+1
    gr = pygame.Rect(gx, gy, CELL_SIZE-1, CELL_SIZE-1)
    draw_cell(screen, gr, GOAL_COLOR, (255, 150, 180), 2)
    lbl2 = font_small.render("G", True, WHITE)
    screen.blit(lbl2, (gx+(CELL_SIZE-1-lbl2.get_width())//2, gy+(CELL_SIZE-1-lbl2.get_height())//2))

    # Ripples
    global ripples
    new_ripples = []
    for rp in ripples:
        rp['t'] += 1
        if rp['t'] < rp['max_t']:
            prog = rp['t'] / rp['max_t']
            alpha = int(200 * (1 - prog))
            radius = int(prog * 50)
            rip_surf = pygame.Surface((radius*2+4, radius*2+4), pygame.SRCALPHA)
            pygame.draw.circle(rip_surf, (0, 220, 180, alpha), (radius+2, radius+2), radius, 2)
            screen.blit(rip_surf, (rp['x'] - radius - 2, rp['y'] - radius - 2))
            new_ripples.append(rp)
    ripples = new_ripples

# ================= BUTTON CLASS =================
class Button:
    def __init__(self, text, x, y, w, h, tag=None):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.tag  = tag
        self.hovered  = False
        self.pressed  = False   # for click animation
        self.press_t  = 0       # timer
        self.selected = False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.press_t > 0:
            self.press_t -= 1
            self.pressed = True
        else:
            self.pressed = False

    def trigger_press(self):
        self.press_t = 8   # frames of "pressed" state
        # add ripple at center
        cx = self.rect.centerx
        cy = self.rect.centery
        ripples.append({'x': cx, 'y': cy, 't': 0, 'max_t': 22})

    def draw(self):
        # color logic
        if self.pressed:
            bg = BTN_ACTIVE
        elif self.hovered:
            bg = BTN_HOVER
        else:
            bg = BTN_BASE

        border = BTN_BORDER_SEL if self.selected else BTN_BORDER
        border_w = 2 if self.selected else 1

        # slight scale-down when pressed
        rect = self.rect.inflate(-4 if self.pressed else 0, -4 if self.pressed else 0)
        rect.center = self.rect.center

        pygame.draw.rect(screen, bg, rect, border_radius=6)
        pygame.draw.rect(screen, border, rect, border_w, border_radius=6)

        # glow behind selected buttons
        if self.selected:
            glow = pygame.Surface((rect.w+12, rect.h+12), pygame.SRCALPHA)
            pygame.draw.rect(glow, (0, 220, 180, 30), (0, 0, rect.w+12, rect.h+12), border_radius=9)
            screen.blit(glow, (rect.x-6, rect.y-6))

        col = BTN_TEXT_SEL if self.selected else BTN_TEXT
        txt = font_med.render(self.text, True, col)
        screen.blit(txt, (rect.x + (rect.w - txt.get_width())//2,
                          rect.y + (rect.h - txt.get_height())//2))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)

# ================= SEARCH =================
def neighbors(node, maze):
    i, j = node
    result = []
    for ni, nj in [(i-1,j),(i+1,j),(i,j-1),(i,j+1)]:
        if 0 <= ni < ROWS and 0 <= nj < COLS and maze[ni][nj] == PATH:
            result.append((ni, nj))
    return result

def reconstruct(parent, start, goal):
    path, node = [], goal
    while node != start:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path

def dfs(maze, start, goal):
    stack, visited, parent, steps = [start], set(), {}, 0
    while stack:
        node = stack.pop()
        if node in visited: continue
        visited.add(node)
        steps += 1
        if node == goal:
            return visited, reconstruct(parent, start, goal), steps
        for n in neighbors(node, maze):
            if n not in visited:
                parent[n] = node
                stack.append(n)
        yield visited, [], steps
    return visited, [], steps

def bfs(maze, start, goal):
    queue, visited, parent, steps = [start], {start}, {}, 0
    while queue:
        node = queue.pop(0)
        steps += 1
        if node == goal:
            return visited, reconstruct(parent, start, goal), steps
        for n in neighbors(node, maze):
            if n not in visited:
                visited.add(n)
                parent[n] = node
                queue.append(n)
        yield visited, [], steps
    return visited, [], steps

def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar(maze, start, goal):
    open_set, g, parent, visited, steps = [], {start: 0}, {}, set(), 0
    heapq.heappush(open_set, (0, start))
    while open_set:
        _, node = heapq.heappop(open_set)
        if node in visited: continue
        visited.add(node)
        steps += 1
        if node == goal:
            return visited, reconstruct(parent, start, goal), steps
        for n in neighbors(node, maze):
            tg = g[node] + 1
            if n not in g or tg < g[n]:
                g[n] = tg
                heapq.heappush(open_set, (tg + heuristic(n, goal), n))
                parent[n] = node
        yield visited, [], steps
    return visited, [], steps

# ================= INIT =================
maze, start, goal = generate_maze()
visited, path = set(), []
steps, elapsed = 0, 0.0
algorithm  = "DFS"
search_gen = None
start_time = 0
anim_tick  = 0
status_msg = "Algoritmni tanlang va Boshlash tugmasini bosing"

PY = ROWS * CELL_SIZE + 2 + 14   # panel Y base
BH = 36                           # button height

btn_dfs   = Button("DFS",      18,  PY,    70, BH, tag="algo")
btn_bfs   = Button("BFS",      96,  PY,    70, BH, tag="algo")
btn_astar = Button("A*",       174, PY,    70, BH, tag="algo")
btn_start = Button("Boshlash", 262, PY,   110, BH)
btn_new   = Button("Yangi labirint",   382, PY,   100, BH)
btn_exit  = Button("Yopish",  490, PY,    90, BH)

btn_dfs.selected = True

algo_btns = [btn_dfs, btn_bfs, btn_astar]
all_btns  = [btn_dfs, btn_bfs, btn_astar, btn_start, btn_new, btn_exit]

clock   = pygame.time.Clock()
running = True

# ================= MAIN LOOP =================
while running:
    clock.tick(60)
    anim_tick += 1
    mouse_pos = pygame.mouse.get_pos()

    for btn in all_btns:
        btn.update(mouse_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            # Algorithm buttons
            for btn, name in zip(algo_btns, ["DFS","BFS","A*"]):
                if btn.clicked(pos):
                    btn.trigger_press()
                    algorithm = name
                    for b in algo_btns:
                        b.selected = False
                    btn.selected = True
                    status_msg = f"{name} selected"

            # New Maze
            if btn_new.clicked(pos):
                btn_new.trigger_press()
                maze, start, goal = generate_maze()
                visited, path = set(), []
                search_gen = None
                steps, elapsed = 0, 0.0
                status_msg = "Yangi labirint tuzildi"

            # Exit
            if btn_exit.clicked(pos):
                btn_exit.trigger_press()
                running = False

            # Start
            if btn_start.clicked(pos):
                btn_start.trigger_press()
                visited, path = set(), []
                steps, elapsed = 0, 0.0
                start_time = time.time()
                status_msg = f"{algorithm} ishga tushirildi..."
                if algorithm == "DFS":
                    search_gen = dfs(maze, start, goal)
                elif algorithm == "BFS":
                    search_gen = bfs(maze, start, goal)
                else:
                    search_gen = astar(maze, start, goal)

    # Step generator (multiple steps per frame for speed)
    if search_gen:
        for _ in range(3):   # advance 3 steps per frame
            try:
                result = next(search_gen)
                if isinstance(result, tuple):
                    visited, path, steps = result
            except StopIteration as e:
                if e.value:
                    visited, path, steps = e.value
                elapsed = time.time() - start_time
                search_gen = None
                found = len(path) > 0
                status_msg = (f"Bajarildi! Yo'l: {len(path)} qadam  |  Ko'rib chiqildi: {len(visited)}  |  Vaqt: {elapsed:.4f}s"
                              if found else f"Yo'l topilmadi  |  Ko'rib chiqildi: {len(visited)}  |  Vaqt: {elapsed:.4f}s")
                break

    # ─── DRAW ───
    draw_maze(maze, visited, path, start, goal, anim_tick)

    # Buttons
    for btn in all_btns:
        btn.draw()

    # Info bar
    info_y = PY + BH + 10
    # draw subtle divider
    pygame.draw.line(screen, BTN_BORDER,
                     (18, info_y - 4), (WIDTH - 18, info_y - 4), 1)

    # Status
    status_surf = font_small.render(status_msg, True, INFO_COLOR)
    screen.blit(status_surf, (18, info_y))

    # Live stats on right
    stat_str = f"ALGO: {algorithm}  |  Qadamlar: {steps}  |  Yo'l: {len(path)}"
    stat_surf = font_small.render(stat_str, True, (80, 100, 140))
    screen.blit(stat_surf, (WIDTH - stat_surf.get_width() - 18, info_y))

    # Legend dots
    legend_y = info_y + 20
    items = [
        (START_COLOR,     "Boshlash"),
        (GOAL_COLOR,      "Nishon"),
        (VISITED_COLOR,   "Ko'rib chiqildi"),
        (PATH_COLOR_DRAW, "Yo'l"),
    ]
    lx = 18
    for col, label in items:
        pygame.draw.circle(screen, col, (lx+5, legend_y+6), 5)
        lbl = font_small.render(label, True, (80, 95, 130))
        screen.blit(lbl, (lx+14, legend_y))
        lx += 14 + lbl.get_width() + 16

    pygame.display.flip()

pygame.quit()
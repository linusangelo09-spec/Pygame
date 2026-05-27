import pygame
import sys
import math

# ==============================================================================
# INIT
# ==============================================================================

pygame.init()
try:
    pygame.mixer.init()
except Exception:
    pass

# ==============================================================================
# CONSTANTS
# ==============================================================================

# Screen
WIDTH = 600
HEIGHT = 800

# Colors
BG_COLOR      = (30,  30,  30)
BUTTON_COLOR  = (70,  130, 180)
HOVER_COLOR   = (100, 170, 220)
TEXT_COLOR    = (255, 255, 255)

# Player
PLAYER_SIZE  = 40
PLAYER_SPEED = 5

# Bullets
BULLET_WIDTH  = 4
BULLET_HEIGHT = 10
BULLET_SPEED  = 12
BULLET_DAMAGE = 1

# Normal enemies
ENEMY_W       = 25
ENEMY_H       = 15
ENEMY_SPEED   = 3
ENEMY_DROP    = 20
ENEMY_HP      = 1
ENEMY_SCORE   = 10

# Special enemies (red, 2 HP)
SPECIAL_W     = 30
SPECIAL_H     = 20
SPECIAL_SPEED = 3
SPECIAL_DROP  = 20
SPECIAL_HP    = 2
SPECIAL_SCORE = 15

# Tanky enemies (green, 7 HP)
TANKY_W       = 40
TANKY_H       = 25
TANKY_SPEED   = 3
TANKY_DROP    = 20
TANKY_HP      = 7
TANKY_SCORE   = 30

# Boss enemy
BOSS_W        = 140
BOSS_H        = 100
BOSS_SPEED    = 5
BOSS_HP       = 67
BOSS_SCORE    = 100

# Enemy grid layout
ROWS      = 3
COLS      = 8
X_SPACING = 40
Y_SPACING = 40
X_PADDING = (WIDTH - ((COLS - 1) * X_SPACING + ENEMY_W)) // 2
Y_PADDING = 40

# How much speed multiplies per kill
SPEED_SCALE = 1.02

# SCREEN & CLOCK


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SpaceShooters")
clock = pygame.time.Clock()


# FONTS


font       = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 28)


# MUSIC


music_loaded  = False
music_playing = False

# Try both mp3 and ogg fallback
for music_path in ["Assets/Bad Piggies Theme - Ilmari Hakkola.mp3",
                   "Assets/Bad Piggies Theme - Ilmari Hakkola.ogg"]:
    try:
        pygame.mixer.music.load(music_path)
        music_loaded = True
        break
    except Exception:
        continue


# BUTTON CLASS


class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface):
        color = HOVER_COLOR if self.rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        text_surf = font.render(self.text, True, TEXT_COLOR)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

# Main menu buttons
main_buttons = [
    Button("Play", 200, 120, 200, 50),
    Button("Quit", 200, 190, 200, 50),
]

# Pause menu buttons
pause_buttons = [
    Button("Continue", 200, 120, 200, 50),
    Button("Menu",     200, 190, 200, 50),
    Button("Quit",     200, 260, 200, 50),
]


# GAME STATE


# State flags
menu_active = True
paused      = False
game_over   = False

# Level
start_level = 1
level       = start_level

# Score
score = 0

# Player position (reset each game)
player_x = WIDTH  // 2 - PLAYER_SIZE // 2
player_y = HEIGHT // 1.3

# Mutable speeds (scale up as enemies are killed)
enemies_speed        = ENEMY_SPEED
special_enemies_speed = SPECIAL_SPEED
tanky_enemies_speed  = TANKY_SPEED
boss_speed           = BOSS_SPEED

# Mutable widths (shrink slightly each level)
enemies_width        = ENEMY_W
special_enemies_width = SPECIAL_W

# Enemy direction: +1 = right, -1 = left
enemy_direction = 1

# Entity lists  —  each enemy: [x, y, hp, hit_flash_timer]
# normal enemy: [x, y, hp]  (no flash timer needed)
# bullet: [x, y]
bullets        = []
enemies        = []
special_enemies = []
tanky_enemies  = []
bosses         = []


# HELPER FUNCTIONS

def draw_boss_health_bar(boss, surface):
    """Draw a health bar just above the boss."""
    ratio    = max(0.0, min(boss[2] / BOSS_HP, 1.0))
    bar_x    = boss[0]
    bar_y    = boss[1] - 12
    bar_w    = BOSS_W
    bar_h    = 8
    pygame.draw.rect(surface, (120, 0,   0), (bar_x, bar_y, bar_w, bar_h))
    pygame.draw.rect(surface, (0,   200, 0), (bar_x, bar_y, int(bar_w * ratio), bar_h))
    pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 1)


def spawn_enemies():
    """
    Populate enemy lists for the current level.
    Levels 5 and 10 are boss levels.
    Every other level spawns a grid of normal/special/tanky enemies
    according to level-specific rules.
    """
    global enemies_speed, special_enemies_speed, tanky_enemies_speed
    global enemies_width, special_enemies_width

    # ── Boss levels ──────────────────────────────────────────────────────────
    if level in (5, 10):
        bosses.clear()
        bosses.append([(WIDTH - BOSS_W) // 2, Y_PADDING, BOSS_HP, 0])
        return

    # ── Per-level speed / size scaling (applied once per spawn) ──────────────
    if level >= 2:
        enemies_speed         += 0.4
        special_enemies_speed  = enemies_speed
        tanky_enemies_speed    = enemies_speed
        enemies_width          = max(10, enemies_width - 1)
        special_enemies_width  = max(10, special_enemies_width - 1)

    # ── Grid dimensions (most levels use the default COLS, level 8/9 use 9) ──
    if level in (8, 9):
        spawn_cols      = 9
        spawn_x_padding = (WIDTH - ((spawn_cols - 1) * X_SPACING + enemies_width)) // 2
    else:
        spawn_cols      = COLS
        spawn_x_padding = X_PADDING

    # Tanky column layout used by levels 7–9
    tanky_cols      = 6
    tanky_x_spacing = TANKY_W + 15
    tanky_x_padding = (WIDTH - ((tanky_cols - 1) * tanky_x_spacing + TANKY_W)) // 2

    # ── Populate grid ─────────────────────────────────────────────────────────
    for row in range(ROWS):
        for col in range(spawn_cols):

            # Level 7: bottom row only has tanky_cols tanky enemies
            if level == 7 and row == ROWS - 1 and col >= tanky_cols:
                continue

            # Base positions
            ex = spawn_x_padding + col * X_SPACING
            ey = Y_PADDING + row * Y_SPACING

            # Special enemy position (slightly larger so centre-align it)
            se_x = ex - (special_enemies_width - enemies_width) // 2
            se_y = ey + (ENEMY_H - SPECIAL_H)

            # Tanky enemy position
            tan_x = (tanky_x_padding + col * tanky_x_spacing) if level == 7 \
                    else (ex - (TANKY_W - enemies_width) // 2)
            tan_y = ey + (ENEMY_H - TANKY_H)

            # ── Level-specific spawn rules ────────────────────────────────────
            if level == 2 and row == ROWS - 1:
                special_enemies.append([se_x, se_y, SPECIAL_HP, 0])

            elif level == 3 and row in (0, ROWS - 1):
                special_enemies.append([se_x, se_y, SPECIAL_HP, 0])

            elif level == 4 and (row + col) % 2 == 0:
                special_enemies.append([se_x, se_y, SPECIAL_HP, 0])

            elif level == 6 and row in (0, 1, ROWS - 1):
                special_enemies.append([se_x, se_y, SPECIAL_HP, 0])

            elif level == 7:
                if row == ROWS - 1:
                    tanky_enemies.append([tan_x, tan_y, TANKY_HP, 0])
                else:
                    special_enemies.append([se_x, se_y, SPECIAL_HP, 0])

            elif level == 8:
                # Alternate full columns: even columns (incl. first & last) → tanky
                if col == 0 or col == spawn_cols - 1 or col % 2 == 0:
                    tanky_enemies.append([tan_x, tan_y, TANKY_HP, 0])
                else:
                    special_enemies.append([se_x, se_y, SPECIAL_HP, 0])

            elif level == 9 and (row + col) % 2 == 0:
                tanky_enemies.append([tan_x, tan_y, TANKY_HP, 0])

            else:
                enemies.append([ex, ey, ENEMY_HP])


def reset_game():
    """Reset all mutable state and spawn enemies for the chosen start level."""
    global level, score, game_over
    global enemies_speed, special_enemies_speed, tanky_enemies_speed, boss_speed
    global enemies_width, special_enemies_width
    global enemy_direction
    global player_x, player_y

    level           = start_level
    score           = 0
    game_over       = False

    enemies_speed         = ENEMY_SPEED
    special_enemies_speed = SPECIAL_SPEED
    tanky_enemies_speed   = TANKY_SPEED
    boss_speed            = BOSS_SPEED
    enemies_width         = ENEMY_W
    special_enemies_width = SPECIAL_W
    enemy_direction       = 1

    player_x = WIDTH  // 2 - PLAYER_SIZE // 2
    player_y = HEIGHT // 1.3

    bullets.clear()
    enemies.clear()
    special_enemies.clear()
    tanky_enemies.clear()
    bosses.clear()

    spawn_enemies()

# ==============================================================================
# MAIN GAME LOOP
# ==============================================================================

while True:

    # ── EVENT HANDLING ────────────────────────────────────────────────────────
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # ── Main menu clicks ──────────────────────────────────────────────────
        if menu_active:
            for btn in main_buttons:
                if btn.clicked(event):
                    if btn.text == "Play":
                        menu_active = False
                        paused      = False
                        reset_game()
                    elif btn.text == "Quit":
                        pygame.quit()
                        sys.exit()

        # ── Pause menu clicks ─────────────────────────────────────────────────
        elif paused:
            for btn in pause_buttons:
                if btn.clicked(event):
                    if btn.text == "Continue":
                        paused = False
                    elif btn.text == "Menu":
                        paused      = False
                        menu_active = True
                    elif btn.text == "Quit":
                        pygame.quit()
                        sys.exit()

        # ── Keyboard events ───────────────────────────────────────────────────
        if event.type == pygame.KEYDOWN:

            # ESC toggles pause (only during active gameplay)
            if event.key == pygame.K_ESCAPE:
                if not menu_active and not game_over:
                    paused = not paused
                continue

            if paused:
                continue

            # R restarts from the game-over screen
            if game_over:
                if event.key == pygame.K_r:
                    reset_game()
                continue

            # Number keys / arrows to pick a start level from the main menu
            if menu_active:
                if event.key in (pygame.K_UP, pygame.K_LEFT):
                    start_level = max(1, start_level - 1)
                elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
                    start_level = min(10, start_level + 1)
                else:
                    try:
                        n = int(event.unicode)
                        start_level = 10 if n == 0 else n if 1 <= n <= 9 else start_level
                    except Exception:
                        pass
                continue

            # SPACE fires a bullet
            if event.key == pygame.K_SPACE:
                bx = player_x + PLAYER_SIZE // 2 - BULLET_WIDTH // 2
                bullets.append([bx, player_y])

    # ── MUSIC CONTROL ─────────────────────────────────────────────────────────
    if music_loaded:
        should_play = not menu_active and not game_over and not paused
        if should_play and not music_playing:
            try:
                pygame.mixer.music.play(-1)
                music_playing = True
            except Exception:
                pass
        elif not should_play and music_playing:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
            music_playing = False

    # ── GAME LOGIC (only when actively playing) ───────────────────────────────
    if not game_over and not menu_active and not paused:

        # ── Move bullets & handle collisions ──────────────────────────────────
        for bullet in bullets[:]:
            bullet[1] -= BULLET_SPEED

            # Remove bullets that leave the top of the screen
            if bullet[1] < 0:
                bullets.remove(bullet)
                continue

            bullet_rect = pygame.Rect(bullet[0], bullet[1], BULLET_WIDTH, BULLET_HEIGHT)
            hit = False

            # Check special enemies first (highest priority visual)
            for se in special_enemies[:]:
                if se[2] > 0 and bullet_rect.colliderect(
                        pygame.Rect(se[0], se[1], special_enemies_width, SPECIAL_H)):
                    se[2] -= BULLET_DAMAGE
                    se[3]  = 8          # flash timer
                    if se[2] <= 0:
                        special_enemies.remove(se)
                        score += SPECIAL_SCORE
                        enemies_speed         *= SPEED_SCALE
                        special_enemies_speed *= SPEED_SCALE
                        tanky_enemies_speed   *= SPEED_SCALE
                    if bullet in bullets:
                        bullets.remove(bullet)
                    hit = True
                    break

            if hit:
                continue

            # Check tanky enemies
            for te in tanky_enemies[:]:
                if te[2] > 0 and bullet_rect.colliderect(
                        pygame.Rect(te[0], te[1], TANKY_W, TANKY_H)):
                    te[2] -= BULLET_DAMAGE
                    te[3]  = 8
                    if te[2] <= 0:
                        tanky_enemies.remove(te)
                        score += TANKY_SCORE
                        enemies_speed         *= SPEED_SCALE
                        special_enemies_speed *= SPEED_SCALE
                        tanky_enemies_speed   *= SPEED_SCALE
                    if bullet in bullets:
                        bullets.remove(bullet)
                    hit = True
                    break

            if hit:
                continue

            # Check normal enemies
            for en in enemies[:]:
                if en[2] > 0 and bullet_rect.colliderect(
                        pygame.Rect(en[0], en[1], enemies_width, ENEMY_H)):
                    en[2] -= BULLET_DAMAGE
                    if en[2] <= 0:
                        enemies.remove(en)
                        score += ENEMY_SCORE
                        enemies_speed         *= SPEED_SCALE
                        special_enemies_speed *= SPEED_SCALE
                        tanky_enemies_speed   *= SPEED_SCALE
                    if bullet in bullets:
                        bullets.remove(bullet)
                    hit = True
                    break

            if hit:
                continue

            # Check boss
            for boss in bosses[:]:
                if boss[2] > 0 and bullet_rect.colliderect(
                        pygame.Rect(boss[0], boss[1], BOSS_W, BOSS_H)):
                    boss[2] -= BULLET_DAMAGE
                    boss[3]  = 8
                    if boss[2] <= 0:
                        bosses.remove(boss)
                        score     += BOSS_SCORE
                        boss_speed *= SPEED_SCALE
                    if bullet in bullets:
                        bullets.remove(bullet)
                    break

        # ── Enemy horizontal movement & bouncing ──────────────────────────────
        # Detect if any enemy has reached a side wall
        move_left  = False
        move_right = False

        for en in enemies:
            if en[0] + enemies_width >= WIDTH: move_left  = True
            if en[0] <= 0:                     move_right = True
        for se in special_enemies:
            if se[0] + special_enemies_width >= WIDTH: move_left  = True
            if se[0] <= 0:                             move_right = True
        for te in tanky_enemies:
            if te[0] + TANKY_W >= WIDTH: move_left  = True
            if te[0] <= 0:              move_right = True
        for boss in bosses:
            if boss[0] + BOSS_W >= WIDTH: move_left  = True
            if boss[0] <= 0:             move_right = True

        # Reverse direction and drop all enemies down one step
        if move_left or move_right:
            enemy_direction *= -1
            for en   in enemies:         en[1]   += ENEMY_DROP
            for se   in special_enemies: se[1]   += SPECIAL_DROP
            for te   in tanky_enemies:   te[1]   += TANKY_DROP
            for boss in bosses:          boss[1] += 25   # boss drop

        # Apply horizontal movement
        for en   in enemies:         en[0]   += enemies_speed         * enemy_direction
        for se   in special_enemies: se[0]   += special_enemies_speed * enemy_direction
        for te   in tanky_enemies:   te[0]   += tanky_enemies_speed   * enemy_direction
        for boss in bosses:          boss[0] += boss_speed            * enemy_direction

        # ── Check if any enemy reached the player (game over) ─────────────────
        # Also triggers if enemies drop off the bottom of the screen
        player_rect = pygame.Rect(player_x, player_y, PLAYER_SIZE, PLAYER_SIZE)

        for en in enemies:
            r = pygame.Rect(en[0], en[1], enemies_width, ENEMY_H)
            if player_rect.colliderect(r) or en[1] + ENEMY_H >= HEIGHT:
                game_over = True; break

        for se in special_enemies:
            r = pygame.Rect(se[0], se[1], special_enemies_width, SPECIAL_H)
            if player_rect.colliderect(r) or se[1] + SPECIAL_H >= HEIGHT:
                game_over = True; break

        for te in tanky_enemies:
            r = pygame.Rect(te[0], te[1], TANKY_W, TANKY_H)
            if player_rect.colliderect(r) or te[1] + TANKY_H >= HEIGHT:
                game_over = True; break

        for boss in bosses:
            r = pygame.Rect(boss[0], boss[1], BOSS_W, BOSS_H)
            if player_rect.colliderect(r) or boss[1] + BOSS_H >= HEIGHT:
                game_over = True; break

        # ── Level up when all enemies are cleared ─────────────────────────────
        if not enemies and not special_enemies and not tanky_enemies and not bosses:
            level += 1
            bullets.clear()
            spawn_enemies()

        # ── Tick down hit-flash timers ─────────────────────────────────────────
        for boss in bosses:
            if boss[3] > 0: boss[3] -= 1
        for se in special_enemies:
            if se[3] > 0: se[3] -= 1
        for te in tanky_enemies:
            if te[3] > 0: te[3] -= 1

        # ── Player movement (WASD, diagonal normalised) ───────────────────────
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_d] - keys[pygame.K_a])
        dy = (keys[pygame.K_s] - keys[pygame.K_w])

        if dx != 0 and dy != 0:
            dx /= math.sqrt(2)
            dy /= math.sqrt(2)

        player_x = max(0,           min(WIDTH  - PLAYER_SIZE, player_x + dx * PLAYER_SPEED))
        player_y = max(500,         min(HEIGHT - PLAYER_SIZE, player_y + dy * PLAYER_SPEED))

    # ── DRAWING ───────────────────────────────────────────────────────────────
    screen.fill(BG_COLOR)

    if menu_active:
        # Title
        t = font.render("SpaceShooters", True, TEXT_COLOR)
        screen.blit(t, ((WIDTH - t.get_width()) // 2, 40))
        # Buttons
        for btn in main_buttons:
            btn.draw(screen)
        # Start-level selector hint
        hint = small_font.render(
            f"Start Level: {start_level}  (1-9, 0=10, arrows)", True, TEXT_COLOR)
        screen.blit(hint, ((WIDTH - hint.get_width()) // 2, 260))

    elif paused:
        t = font.render("Paused", True, TEXT_COLOR)
        screen.blit(t, ((WIDTH - t.get_width()) // 2, 40))
        for btn in pause_buttons:
            btn.draw(screen)
        hint = small_font.render("Press ESC to continue", True, TEXT_COLOR)
        screen.blit(hint, ((WIDTH - hint.get_width()) // 2, 340))

    elif game_over:
        t1 = font.render("GAME OVER", True, (255, 50, 50))
        t2 = small_font.render("Press R to restart", True, TEXT_COLOR)
        t3 = font.render(f"Score: {score}", True, TEXT_COLOR)
        screen.blit(t1, ((WIDTH - t1.get_width()) // 2, HEIGHT // 3))
        screen.blit(t3, ((WIDTH - t3.get_width()) // 2, HEIGHT // 2))
        screen.blit(t2, ((WIDTH - t2.get_width()) // 2, HEIGHT // 2 + 60))

    else:
        # ── Bullets ───────────────────────────────────────────────────────────
        for b in bullets:
            pygame.draw.rect(screen, (255, 50, 50), (b[0], b[1], BULLET_WIDTH, BULLET_HEIGHT))

        # ── Normal enemies (yellow) ───────────────────────────────────────────
        for en in enemies:
            pygame.draw.rect(screen, (200, 180, 0), (en[0], en[1], enemies_width, ENEMY_H))

        # ── Special enemies (red, flash white on hit) ─────────────────────────
        for se in special_enemies:
            color = (255, 200, 200) if se[3] > 0 else (255, 0, 0)
            pygame.draw.rect(screen, color, (se[0], se[1], special_enemies_width, SPECIAL_H))

        # ── Tanky enemies (green, flash light-green on hit) ───────────────────
        for te in tanky_enemies:
            color = (150, 255, 150) if te[3] > 0 else (0, 200, 0)
            pygame.draw.rect(screen, color, (te[0], te[1], TANKY_W, TANKY_H))

        # ── Boss (red, flash pink on hit, health bar above) ───────────────────
        for boss in bosses:
            color = (255, 100, 100) if boss[3] > 0 else (255, 0, 0)
            pygame.draw.rect(screen, color, (boss[0], boss[1], BOSS_W, BOSS_H))
            draw_boss_health_bar(boss, screen)

        # ── HUD ───────────────────────────────────────────────────────────────
        level_surf = font.render(f"Level: {level}", True, TEXT_COLOR)
        score_surf = font.render(f"Score: {score}", True, TEXT_COLOR)
        screen.blit(level_surf, (10, 10))
        screen.blit(score_surf, (WIDTH - score_surf.get_width() - 10, 10))

        # ── Player (cyan square) ──────────────────────────────────────────────
        pygame.draw.rect(screen, (0, 200, 255), (player_x, player_y, PLAYER_SIZE, PLAYER_SIZE))

    pygame.display.flip()
    clock.tick(60)
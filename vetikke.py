import pygame
import sys
import math

pygame.init()
try:
    pygame.mixer.init()
except Exception:
    pass

# try to load music, mp3 first then ogg as backup
music_loaded = False
music_playing = False
music_paths = ["Assets/Bad Piggies Theme - Ilmari Hakkola.mp3", "Assets/Bad Piggies Theme - Ilmari Hakkola.ogg"]
for mp in music_paths:
    try:
        pygame.mixer.music.load(mp)
        music_loaded = True
        break
    except Exception:
        music_loaded = False
        continue

# screen
Width = 600
height = 800
screen = pygame.display.set_mode((Width, height))
pygame.display.set_caption("SpaceShooters")

# colors
BG_COLOR = (30, 30, 30)
BUTTON_COLOR = (70, 130, 180)
HOVER_COLOR = (100, 170, 220)
TEXT_COLOR = (255, 255, 255)

Clock = pygame.time.Clock()

# fonts
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 28)

# game state
start_level = 1
level = start_level
game_over = False
menu_active = True
paused = False
score = 0


# button class, handles drawing and click detection
class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surface):
        color = HOVER_COLOR if self.rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        text_surf = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


# main menu buttons
buttons = [
    Button("Play", 200, 120, 200, 50),
    Button("Quit", 200, 190, 200, 50)
]

# pause menu buttons
buttonesc = [
    Button("Continue", 200, 120, 200, 50),
    Button("Menu", 200, 190, 200, 50),
    Button("Quit", 200, 260, 200, 50)
]

# player
player_size = 40
player_x = Width // 2 - player_size // 2
player_y = height // 1.3
speed = 5

# bullets
bullet_width = 4
bullet_height = 10
bullet_speed = 12
bullet_damage = 1
bullets = []

# normal enemies (yellow)
enemies_width = 25
enemies_height = 15
enemies_speed = 3
enemies = []
enemy_direction = 1
enemy_drop = 20
enemies_health = 1
enemies_score = 10

# special enemies (red, 2 hp)
special_enemies_width = 30
special_enemies_height = 20
special_enemies_speed = 3
special_enemies = []
special_enemy_drop = 20
special_enemies_health = 2
special_enemies_score = 15

# tanky enemies (green, 7 hp)
tanky_enemies_width = 40
tanky_enemies_height = 25
tanky_enemies_speed = 3
tanky_enemies = []
tanky_enemy_drop = 20
tanky_enemies_health = 7
tanky_enemies_score = 30

# boss
bosses_width = 140
bosses_height = 100
boss_speed = 5
boss_health = 67
boss_maxhealth = 67
bosses = []
boss_drop = 25
boss_score = 100

# enemy grid layout
rows = 3
cols = 8
x_spacing = 40
y_spacing = 40
x_padding = (Width - ((cols - 1) * x_spacing + enemies_width)) // 2
y_padding = 40


def draw_boss_health_bar(boss, surface):
    hp = boss[2]
    ratio = max(0.0, min(hp / boss_maxhealth, 1.0))
    bar_x = boss[0]
    bar_y = boss[1] - 12
    pygame.draw.rect(surface, (120, 0, 0), (bar_x, bar_y, bosses_width, 8))
    pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, int(bosses_width * ratio), 8))
    pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bosses_width, 8), 1)


def spawnEnemy():
    global enemies_speed, enemies_width, special_enemies_speed, special_enemies_width, tanky_enemies_speed

    # boss levels
    if level == 5 or level == 10:
        bosses.clear()
        bosses.append([(Width - bosses_width) // 2, y_padding, boss_health, 0])
        return

    # speed and size scaling each level
    if level >= 2:
        enemies_speed += 0.4
        special_enemies_speed = enemies_speed
        tanky_enemies_speed = enemies_speed
        enemies_width = max(10, enemies_width - 1)
        special_enemies_width = max(10, special_enemies_width - 1)

    # level 8 and 9 use a wider 9-column grid
    spawn_cols = cols
    spawn_x_padding = x_padding
    if level == 8 or level == 9:
        spawn_cols = 9
        spawn_x_padding = (Width - ((spawn_cols - 1) * x_spacing + enemies_width)) // 2

    # tanky layout (used in levels 7, 8, 9)
    tanky_cols = 6
    tanky_x_spacing = tanky_enemies_width + 15
    tanky_x_padding = (Width - ((tanky_cols - 1) * tanky_x_spacing + tanky_enemies_width)) // 2

    for row in range(rows):
        for col in range(spawn_cols):

            # level 7 bottom row only has 6 tanky enemies
            if level == 7 and row == rows - 1 and col >= tanky_cols:
                continue

            enemy_x = spawn_x_padding + col * x_spacing
            enemy_y = y_padding + row * y_spacing

            # special enemy position (a bit bigger so we center it)
            se_x = enemy_x - (special_enemies_width - enemies_width) // 2
            se_y = enemy_y + (enemies_height - special_enemies_height)

            # tanky enemy position
            if level == 7:
                tanky_x = tanky_x_padding + col * tanky_x_spacing
            else:
                tanky_x = enemy_x - (tanky_enemies_width - enemies_width) // 2
            tanky_y = enemy_y + (enemies_height - tanky_enemies_height)

            # which enemy type to spawn depends on the level and grid position
            if level == 2 and row == rows - 1:
                special_enemies.append([se_x, se_y, special_enemies_health, 0])

            elif level == 3 and (row == rows - 1 or row == 0):
                special_enemies.append([se_x, se_y, special_enemies_health, 0])

            elif level == 4 and (row + col) % 2 == 0:
                special_enemies.append([se_x, se_y, special_enemies_health, 0])

            elif level == 6 and (row == rows - 1 or row == 0 or row == 1):
                special_enemies.append([se_x, se_y, special_enemies_health, 0])

            elif level == 7:
                if row == rows - 1:
                    tanky_enemies.append([tanky_x, tanky_y, tanky_enemies_health, 0])
                else:
                    special_enemies.append([se_x, se_y, special_enemies_health, 0])

            elif level == 8:
                # even columns (and the last) are tanky, odd columns are special
                if col == 0 or col == spawn_cols - 1 or col % 2 == 0:
                    tanky_enemies.append([tanky_x, tanky_y, tanky_enemies_health, 0])
                else:
                    special_enemies.append([se_x, se_y, special_enemies_health, 0])

            elif level == 9 and (row + col) % 2 == 0:
                tanky_enemies.append([tanky_x, tanky_y, tanky_enemies_health, 0])

            else:
                enemies.append([enemy_x, enemy_y, enemies_health])


def reset_game():
    global level, enemies_speed, special_enemies_speed, enemy_direction
    global enemies_width, enemies_height, special_enemies_width, special_enemies_height
    global boss_speed, bosses_width, player_x, player_y, game_over, score

    level = start_level
    score = 0
    game_over = False
    enemy_direction = 1

    # reset speeds and sizes back to defaults
    enemies_speed = 3
    special_enemies_speed = 3
    tanky_enemies_speed = 3
    boss_speed = 5
    enemies_width = 25
    enemies_height = 15
    special_enemies_width = 30
    special_enemies_height = 20
    bosses_width = 140

    player_x = Width // 2 - player_size // 2
    player_y = height // 1.3

    enemies.clear()
    special_enemies.clear()
    tanky_enemies.clear()
    bosses.clear()
    bullets.clear()

    spawnEnemy()


# game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if menu_active:
            for button in buttons:
                if button.clicked(event):
                    if button.text == "Play":
                        menu_active = False
                        paused = False
                        reset_game()
                    elif button.text == "Quit":
                        pygame.quit()
                        sys.exit()

        elif paused:
            for button in buttonesc:
                if button.clicked(event):
                    if button.text == "Continue":
                        paused = False
                    elif button.text == "Menu":
                        paused = False
                        menu_active = True
                    elif button.text == "Quit":
                        pygame.quit()
                        sys.exit()

        if event.type == pygame.KEYDOWN:
            # esc pauses/unpauses during gameplay
            if event.key == pygame.K_ESCAPE:
                if not menu_active and not game_over:
                    paused = not paused
                continue

            if paused:
                continue

            # r restarts from game over screen
            if game_over:
                if event.key == pygame.K_r:
                    reset_game()
                continue

            # number keys and arrows to pick start level on the menu
            if menu_active:
                if event.key in (pygame.K_UP, pygame.K_LEFT):
                    start_level = max(1, start_level - 1)
                elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
                    start_level = min(10, start_level + 1)
                else:
                    try:
                        n = int(event.unicode)
                        if n == 0:
                            start_level = 10
                        elif 1 <= n <= 9:
                            start_level = n
                    except Exception:
                        pass
                continue

            # space shoots
            if event.key == pygame.K_SPACE:
                bullet_x = player_x + player_size // 2 - bullet_width // 2
                bullets.append([bullet_x, player_y])

    # music plays during gameplay only
    if music_loaded:
        if not menu_active and not game_over and not paused:
            if not music_playing:
                try:
                    pygame.mixer.music.play(-1)
                    music_playing = True
                except Exception:
                    music_playing = False
        else:
            if music_playing:
                try:
                    pygame.mixer.music.stop()
                except Exception:
                    pass
                music_playing = False

    if not game_over and not menu_active and not paused:

        # move bullets up and check if they hit anything
        for bullet in bullets[:]:
            bullet[1] -= bullet_speed
            if bullet[1] < 0:
                bullets.remove(bullet)
                continue

            bullet_rect = pygame.Rect(bullet[0], bullet[1], bullet_width, bullet_height)
            hit = False

            for special_enemy in special_enemies[:]:
                special_rect = pygame.Rect(special_enemy[0], special_enemy[1], special_enemies_width, special_enemies_height)
                if special_enemy[2] > 0 and bullet_rect.colliderect(special_rect):
                    special_enemy[2] -= bullet_damage
                    special_enemy[3] = 8  # hit flash timer
                    if special_enemy[2] <= 0:
                        special_enemies.remove(special_enemy)
                        score += special_enemies_score
                        enemies_speed *= 1.02
                        special_enemies_speed *= 1.02
                        tanky_enemies_speed *= 1.02
                    if bullet in bullets:
                        bullets.remove(bullet)
                    hit = True
                    break

            if hit:
                continue

            for tanky_enemy in tanky_enemies[:]:
                tanky_rect = pygame.Rect(tanky_enemy[0], tanky_enemy[1], tanky_enemies_width, tanky_enemies_height)
                if tanky_enemy[2] > 0 and bullet_rect.colliderect(tanky_rect):
                    tanky_enemy[2] -= bullet_damage
                    tanky_enemy[3] = 8
                    if tanky_enemy[2] <= 0:
                        tanky_enemies.remove(tanky_enemy)
                        score += tanky_enemies_score
                        enemies_speed *= 1.02
                        special_enemies_speed *= 1.02
                        tanky_enemies_speed *= 1.02
                    if bullet in bullets:
                        bullets.remove(bullet)
                    hit = True
                    break

            if hit:
                continue

            for enemy in enemies[:]:
                enemy_rect = pygame.Rect(enemy[0], enemy[1], enemies_width, enemies_height)
                if enemy[2] > 0 and bullet_rect.colliderect(enemy_rect):
                    enemy[2] -= bullet_damage
                    if enemy[2] <= 0:
                        enemies.remove(enemy)
                        score += enemies_score
                        enemies_speed *= 1.02
                        special_enemies_speed *= 1.02
                        tanky_enemies_speed *= 1.02
                    if bullet in bullets:
                        bullets.remove(bullet)
                    hit = True
                    break

            if hit:
                continue

            for boss in bosses[:]:
                boss_rect = pygame.Rect(boss[0], boss[1], bosses_width, bosses_height)
                if boss[2] > 0 and bullet_rect.colliderect(boss_rect):
                    boss[2] -= bullet_damage
                    boss[3] = 8
                    if boss[2] <= 0:
                        bosses.remove(boss)
                        score += boss_score
                        boss_speed *= 1.02
                    if bullet in bullets:
                        bullets.remove(bullet)
                    break

        # check if any enemy hit a side wall, if so flip direction and drop down
        move_left = False
        move_right = False

        for enemy in enemies:
            if enemy[0] + enemies_width >= Width:
                move_left = True
            if enemy[0] <= 0:
                move_right = True

        for special_enemy in special_enemies:
            if special_enemy[0] + special_enemies_width >= Width:
                move_left = True
            if special_enemy[0] <= 0:
                move_right = True

        for tanky_enemy in tanky_enemies:
            if tanky_enemy[0] + tanky_enemies_width >= Width:
                move_left = True
            if tanky_enemy[0] <= 0:
                move_right = True

        for boss in bosses:
            if boss[0] + bosses_width >= Width:
                move_left = True
            if boss[0] <= 0:
                move_right = True

        if move_left or move_right:
            enemy_direction *= -1
            for enemy in enemies:
                enemy[1] += enemy_drop
            for special_enemy in special_enemies:
                special_enemy[1] += special_enemy_drop
            for tanky_enemy in tanky_enemies:
                tanky_enemy[1] += tanky_enemy_drop
            for boss in bosses:
                boss[1] += boss_drop

        for enemy in enemies:
            enemy[0] += enemies_speed * enemy_direction
        for special_enemy in special_enemies:
            special_enemy[0] += special_enemies_speed * enemy_direction
        for tanky_enemy in tanky_enemies:
            tanky_enemy[0] += tanky_enemies_speed * enemy_direction
        for boss in bosses:
            boss[0] += boss_speed * enemy_direction

        # game over if player touches an enemy or an enemy reaches the bottom
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

        for enemy in enemies:
            if player_rect.colliderect(pygame.Rect(enemy[0], enemy[1], enemies_width, enemies_height)):
                game_over = True
                break
            if enemy[1] + enemies_height >= height:
                game_over = True
                break

        for special_enemy in special_enemies:
            if player_rect.colliderect(pygame.Rect(special_enemy[0], special_enemy[1], special_enemies_width, special_enemies_height)):
                game_over = True
                break
            if special_enemy[1] + special_enemies_height >= height:
                game_over = True
                break

        for tanky_enemy in tanky_enemies:
            if player_rect.colliderect(pygame.Rect(tanky_enemy[0], tanky_enemy[1], tanky_enemies_width, tanky_enemies_height)):
                game_over = True
                break
            if tanky_enemy[1] + tanky_enemies_height >= height:
                game_over = True
                break

        for boss in bosses:
            if player_rect.colliderect(pygame.Rect(boss[0], boss[1], bosses_width, bosses_height)):
                game_over = True
                break
            if boss[1] + bosses_height >= height:
                game_over = True
                break

        # if all enemies are gone, go to next level
        if not enemies and not special_enemies and not tanky_enemies and not bosses:
            level += 1
            bullets.clear()
            spawnEnemy()

        # tick down hit flash timers
        for boss in bosses:
            if boss[3] > 0:
                boss[3] -= 1
        for special_enemy in special_enemies:
            if special_enemy[3] > 0:
                special_enemy[3] -= 1
        for tanky_enemy in tanky_enemies:
            if tanky_enemy[3] > 0:
                tanky_enemy[3] -= 1

        # player movement with WASD, diagonal movement is normalized
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1

        if dx != 0 and dy != 0:
            dx /= math.sqrt(2)
            dy /= math.sqrt(2)

        player_x += dx * speed
        player_y += dy * speed

        player_x = max(0, min(Width - player_size, player_x))
        player_y = max(500, min(height - player_size, player_y))

    # drawing
    screen.fill((30, 30, 30))

    if menu_active:
        title_text = font.render("SpaceShooters", True, TEXT_COLOR)
        screen.blit(title_text, ((Width - title_text.get_width()) // 2, 40))
        for button in buttons:
            button.draw(screen)
        start_text = small_font.render("Start Level: " + str(start_level) + "  (1-9, 0 = level 10, arrows also work)", True, TEXT_COLOR)
        screen.blit(start_text, ((Width - start_text.get_width()) // 2, 260))

    elif paused:
        paused_text = font.render("Paused", True, TEXT_COLOR)
        screen.blit(paused_text, ((Width - paused_text.get_width()) // 2, 40))
        for button in buttonesc:
            button.draw(screen)
        resume_text = small_font.render("Press ESC to continue", True, TEXT_COLOR)
        screen.blit(resume_text, ((Width - resume_text.get_width()) // 2, 340))

    elif game_over:
        game_over_text = font.render("GAME OVER", True, (255, 50, 50))
        score_text = font.render("Score: " + str(score), True, (255, 255, 255))
        restart_text = small_font.render("Press R to restart", True, (255, 255, 255))
        screen.blit(game_over_text, ((Width - game_over_text.get_width()) // 2, height // 3))
        screen.blit(score_text, ((Width - score_text.get_width()) // 2, height // 2))
        screen.blit(restart_text, ((Width - restart_text.get_width()) // 2, height // 2 + 60))

    else:
        for bullet in bullets:
            pygame.draw.rect(screen, (255, 50, 50), (bullet[0], bullet[1], bullet_width, bullet_height))

        for enemy in enemies:
            pygame.draw.rect(screen, (200, 180, 0), (enemy[0], enemy[1], enemies_width, enemies_height))

        for special_enemy in special_enemies:
            color = (255, 200, 200) if special_enemy[3] > 0 else (255, 0, 0)
            pygame.draw.rect(screen, color, (special_enemy[0], special_enemy[1], special_enemies_width, special_enemies_height))

        for tanky_enemy in tanky_enemies:
            color = (150, 255, 150) if tanky_enemy[3] > 0 else (0, 200, 0)
            pygame.draw.rect(screen, color, (tanky_enemy[0], tanky_enemy[1], tanky_enemies_width, tanky_enemies_height))

        for boss in bosses:
            current_color = (255, 100, 100) if boss[3] > 0 else (255, 0, 0)
            pygame.draw.rect(screen, current_color, (boss[0], boss[1], bosses_width, bosses_height))
            draw_boss_health_bar(boss, screen)

        level_text = font.render("Level: " + str(level), True, (255, 255, 255))
        score_text = font.render("Score: " + str(score), True, (255, 255, 255))
        screen.blit(level_text, (10, 10))
        screen.blit(score_text, (Width - score_text.get_width() - 10, 10))

        pygame.draw.rect(screen, (0, 200, 255), (player_x, player_y, player_size, player_size))

    pygame.display.flip()
    Clock.tick(60)
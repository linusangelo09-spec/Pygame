import pygame
import sys
import math
import os

pygame.init()
try:
    pygame.mixer.init()
except Exception:
    pass

music_loaded = False
music_playing = False
for mp in ["Assets/Bad Piggies Theme - Ilmari Hakkola.mp3", "Assets/Bad Piggies Theme - Ilmari Hakkola.ogg"]:
    try:
        pygame.mixer.music.load(mp)
        music_loaded = True
        break
    except Exception:
        continue

Width = 600
height = 800
screen = pygame.display.set_mode((Width, height))
pygame.display.set_caption("SpaceShooters")

BUTTON_COLOR = (70, 130, 180)
HOVER_COLOR = (100, 170, 220)
TEXT_COLOR = (255, 255, 255)

Clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 28)

start_level = 1
level = start_level
game_over = False
menu_active = True
paused = False
score = 0


def load_sprite(path, w, h):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (w, h))
    except Exception:
        return None


player_size = 40
bosses_width = 140
bosses_height = 100

player_img = load_sprite("Assets/player.png", player_size, player_size)
boss_img = load_sprite("Assets/boss.png", bosses_width, bosses_height)

#--------------------------AI----------------------------
def draw_enemy_sprite(surface, x, y, w, h, kind, flash=False):
    if kind == 'normal':
        body_color = (255, 255, 255) if flash else (220, 200, 0)
        eye_color = (255, 255, 255) if flash else (50, 50, 180)
        pygame.draw.ellipse(surface, body_color, pygame.Rect(x + w // 4, y, w // 2, h // 2))
        pygame.draw.ellipse(surface, body_color, pygame.Rect(x, y + h // 3, w, h // 2))
        pygame.draw.circle(surface, eye_color, (x + w // 3, y + h // 2), max(2, h // 7))
        pygame.draw.circle(surface, eye_color, (x + 2 * w // 3, y + h // 2), max(2, h // 7))

    elif kind == 'special':
        body_color = (255, 255, 255) if flash else (220, 40, 40)
        wing_color = (255, 255, 255) if flash else (180, 20, 20)
        cock_color = (255, 255, 255) if flash else (255, 220, 80)
        pygame.draw.polygon(surface, body_color, [(x + w // 2, y), (x, y + h), (x + w, y + h)])
        pygame.draw.polygon(surface, wing_color, [(x, y + h // 2), (x - w // 4, y + h), (x + w // 3, y + h)])
        pygame.draw.polygon(surface, wing_color, [(x + w, y + h // 2), (x + w + w // 4, y + h), (x + 2 * w // 3, y + h)])
        pygame.draw.ellipse(surface, cock_color, (x + w // 3, y + h // 3, w // 3, h // 4))

    elif kind == 'tanky':
        body_color = (255, 255, 255) if flash else (30, 180, 30)
        shell_color = (255, 255, 255) if flash else (20, 130, 20)
        eye_color = (255, 255, 255) if flash else (255, 80, 80)
        pygame.draw.rect(surface, body_color, (x + w // 5, y + h // 5, 3 * w // 5, 3 * h // 5))
        pygame.draw.rect(surface, shell_color, (x, y + h // 4, w // 5, h // 2))
        pygame.draw.rect(surface, shell_color, (x, y + h // 4, w // 5 + w // 8, h // 6))
        pygame.draw.rect(surface, shell_color, (x + 4 * w // 5, y + h // 4, w // 5, h // 2))
        pygame.draw.rect(surface, shell_color, (x + 4 * w // 5 - w // 8, y + h // 4, w // 5 + w // 8, h // 6))
        pygame.draw.circle(surface, eye_color, (x + w // 3, y + h // 2), max(2, h // 8))
        pygame.draw.circle(surface, eye_color, (x + 2 * w // 3, y + h // 2), max(2, h // 8))
        pygame.draw.rect(surface, shell_color, (x + w // 3, y, w // 8, h // 5))
        pygame.draw.rect(surface, shell_color, (x + w // 2, y, w // 8, h // 5))

#--------------------------------------ai--------------------


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


buttons = [
    Button("Play", 200, 120, 200, 50),
    Button("Quit", 200, 190, 200, 50)
]

buttonesc = [
    Button("Continue", 200, 120, 200, 50),
    Button("Menu", 200, 190, 200, 50),
    Button("Quit", 200, 260, 200, 50)
]

# player
player_x = Width // 2 - player_size // 2
player_y = height // 1.3
speed = 5
player_health = 0
player_max_health = 10

# bullets
bullet_width = 4
bullet_height = 10
bullet_speed = 12
bullet_damage = 1
bullets = []

# boss bullets
boss_bullet_width = 6
boss_bullet_height = 12
boss_bullet_speed = 8
boss_bullets = []

# normal enemies
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
boss_speed = 5
boss_health = 67
boss_maxhealth = 67
bosses = []
boss_drop = 25
boss_score = 100

# enemy grid
rows = 3
cols = 8
x_spacing = 40
y_spacing = 40
x_padding = (Width - ((cols - 1) * x_spacing + enemies_width)) // 2
y_padding = 40


def draw_boss_health_bar(boss, surface):
    ratio = max(0.0, min(boss[2] / boss_maxhealth, 1.0))
    bar_x = boss[0]
    bar_y = boss[1] - 12
    pygame.draw.rect(surface, (120, 0, 0), (bar_x, bar_y, bosses_width, 8))
    pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, int(bosses_width * ratio), 8))
    pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bosses_width, 8), 1)


def draw_player_health_bar(surface):
    bar_width = 150
    bar_height = 20
    bar_x = Width - bar_width - 10
    bar_y = height - bar_height - 10
    ratio = max(0.0, min(player_health / player_max_health, 1.0))
    pygame.draw.rect(surface, (120, 0, 0), (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, int(bar_width * ratio), bar_height))
    pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
    health_text = small_font.render(f"Health: {player_health}/{player_max_health}", True, (255, 255, 255))
    surface.blit(health_text, (bar_x + 5, bar_y + 2))


def spawnEnemy():
    global enemies_speed, enemies_width, special_enemies_speed, special_enemies_width
    global tanky_enemies_speed, player_health, bullet_damage

    if level == 5 or level == 10:
        bosses.clear()
        bosses.append([(Width - bosses_width) // 2, y_padding, boss_health, 0, 0])
        player_health = player_max_health
        return

    # reset speeds after the level 5 boss so level 6 doesn't feel impossible
    if level == 6:
        enemies_speed = 3
        special_enemies_speed = 3
        tanky_enemies_speed = 3

    if level == 8 or level == 9:
        bullet_damage = 2
        enemies_speed = 4
        special_enemies_speed = 4
        tanky_enemies_speed = 4

    if level >= 2:
        enemies_speed += 0.4
        special_enemies_speed = enemies_speed
        tanky_enemies_speed = enemies_speed
        enemies_width = max(10, enemies_width - 1)
        special_enemies_width = max(10, special_enemies_width - 1)

    spawn_cols = cols
    spawn_x_padding = x_padding
    if level == 8 or level == 9:
        spawn_cols = 9
        spawn_x_padding = (Width - ((spawn_cols - 1) * x_spacing + enemies_width)) // 2

    tanky_cols = 6
    tanky_x_spacing = tanky_enemies_width + 15
    tanky_x_padding = (Width - ((tanky_cols - 1) * tanky_x_spacing + tanky_enemies_width)) // 2

    for row in range(rows):
        for col in range(spawn_cols):

            if level == 7 and row == rows - 1 and col >= tanky_cols:
                continue

            enemy_x = spawn_x_padding + col * x_spacing
            enemy_y = y_padding + row * y_spacing

            se_x = enemy_x - (special_enemies_width - enemies_width) // 2
            se_y = enemy_y + (enemies_height - special_enemies_height)

            if level == 7:
                tanky_x = tanky_x_padding + col * tanky_x_spacing
            else:
                tanky_x = enemy_x - (tanky_enemies_width - enemies_width) // 2
            tanky_y = enemy_y + (enemies_height - tanky_enemies_height)

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
                if col == 0 or col == spawn_cols - 1 or col % 2 == 0:
                    tanky_enemies.append([tanky_x, tanky_y, tanky_enemies_health, 0])
                else:
                    special_enemies.append([se_x, se_y, special_enemies_health, 0])
            elif level == 9 and (row + col) % 2 == 0:
                tanky_enemies.append([tanky_x, tanky_y, tanky_enemies_health, 0])
            else:
                enemies.append([enemy_x, enemy_y, enemies_health])


def reset_game():
    global level, enemies_speed, special_enemies_speed, tanky_enemies_speed, enemy_direction
    global enemies_width, enemies_height, special_enemies_width, special_enemies_height
    global boss_speed, bosses_width, player_x, player_y, game_over, score, bullet_damage

    level = start_level
    score = 0
    game_over = False
    enemy_direction = 1
    bullet_damage = 1

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
    boss_bullets.clear()

    spawnEnemy()


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
            if event.key == pygame.K_ESCAPE:
                if not menu_active and not game_over:
                    paused = not paused
                continue

            if paused:
                continue

            if game_over:
                if event.key == pygame.K_r:
                    reset_game()
                continue

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

            if event.key == pygame.K_SPACE:
                bullet_x = player_x + player_size // 2 - bullet_width // 2
                bullets.append([bullet_x, player_y])

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

        for bullet in bullets[:]:
            bullet[1] -= bullet_speed
            if bullet[1] < 0:
                bullets.remove(bullet)
                continue

            bullet_rect = pygame.Rect(bullet[0], bullet[1], bullet_width, bullet_height)
            hit = False

            for special_enemy in special_enemies[:]:
                if special_enemy[2] > 0 and bullet_rect.colliderect(pygame.Rect(special_enemy[0], special_enemy[1], special_enemies_width, special_enemies_height)):
                    special_enemy[2] -= bullet_damage
                    special_enemy[3] = 8
                    if special_enemy[2] <= 0:
                        special_enemies.remove(special_enemy)
                        score += special_enemies_score
                        enemies_speed *= 1.008
                        special_enemies_speed *= 1.008
                        tanky_enemies_speed *= 1.008
                    bullets.remove(bullet)
                    hit = True
                    break
            if hit:
                continue

            for tanky_enemy in tanky_enemies[:]:
                if tanky_enemy[2] > 0 and bullet_rect.colliderect(pygame.Rect(tanky_enemy[0], tanky_enemy[1], tanky_enemies_width, tanky_enemies_height)):
                    tanky_enemy[2] -= bullet_damage
                    tanky_enemy[3] = 8
                    if tanky_enemy[2] <= 0:
                        tanky_enemies.remove(tanky_enemy)
                        score += tanky_enemies_score
                        enemies_speed *= 1.02
                        special_enemies_speed *= 1.02
                        tanky_enemies_speed *= 1.02
                    bullets.remove(bullet)
                    hit = True
                    break
            if hit:
                continue

            for enemy in enemies[:]:
                if enemy[2] > 0 and bullet_rect.colliderect(pygame.Rect(enemy[0], enemy[1], enemies_width, enemies_height)):
                    enemy[2] -= bullet_damage
                    if enemy[2] <= 0:
                        enemies.remove(enemy)
                        score += enemies_score
                        enemies_speed *= 1.02
                        special_enemies_speed *= 1.02
                        tanky_enemies_speed *= 1.02
                    bullets.remove(bullet)
                    hit = True
                    break
            if hit:
                continue

            for boss in bosses[:]:
                if boss[2] > 0 and bullet_rect.colliderect(pygame.Rect(boss[0], boss[1], bosses_width, bosses_height)):
                    boss[2] -= bullet_damage
                    boss[3] = 8
                    if boss[2] <= 0:
                        bosses.remove(boss)
                        score += boss_score
                        boss_speed *= 1.02
                    bullets.remove(bullet)
                    break

        for boss_bullet in boss_bullets[:]:
            boss_bullet[1] += boss_bullet_speed
            if boss_bullet[1] > height:
                boss_bullets.remove(boss_bullet)
                continue
            bullet_rect = pygame.Rect(boss_bullet[0], boss_bullet[1], boss_bullet_width, boss_bullet_height)
            if bullet_rect.colliderect(pygame.Rect(player_x, player_y, player_size, player_size)):
                player_health -= 1
                boss_bullets.remove(boss_bullet)
                if player_health <= 0:
                    game_over = True

        for boss in bosses[:]:
            boss[4] += 1
            if level == 5:
                if boss[4] >= 30:
                    boss_bullets.append([boss[0] + bosses_width // 2 - boss_bullet_width // 2, boss[1] + bosses_height])
                    boss[4] = 0
            elif level == 10:
                if boss[4] >= 30:
                    boss_bullets.append([boss[0] + bosses_width // 3 - boss_bullet_width // 2, boss[1] + bosses_height])
                    boss_bullets.append([boss[0] + 2 * bosses_width // 3 - boss_bullet_width // 2, boss[1] + bosses_height])
                    boss[4] = 0

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

        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

        for enemy in enemies:
            if player_rect.colliderect(pygame.Rect(enemy[0], enemy[1], enemies_width, enemies_height)) or enemy[1] + enemies_height >= height:
                game_over = True
                break
        for special_enemy in special_enemies:
            if player_rect.colliderect(pygame.Rect(special_enemy[0], special_enemy[1], special_enemies_width, special_enemies_height)) or special_enemy[1] + special_enemies_height >= height:
                game_over = True
                break
        for tanky_enemy in tanky_enemies:
            if player_rect.colliderect(pygame.Rect(tanky_enemy[0], tanky_enemy[1], tanky_enemies_width, tanky_enemies_height)) or tanky_enemy[1] + tanky_enemies_height >= height:
                game_over = True
                break
        for boss in bosses:
            if player_rect.colliderect(pygame.Rect(boss[0], boss[1], bosses_width, bosses_height)) or boss[1] + bosses_height >= height:
                game_over = True
                break

        if not enemies and not special_enemies and not tanky_enemies and not bosses:
            level += 1
            bullets.clear()
            boss_bullets.clear()
            spawnEnemy()

        for boss in bosses:
            if boss[3] > 0:
                boss[3] -= 1
        for special_enemy in special_enemies:
            if special_enemy[3] > 0:
                special_enemy[3] -= 1
        for tanky_enemy in tanky_enemies:
            if tanky_enemy[3] > 0:
                tanky_enemy[3] -= 1

        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1

        if dx != 0 and dy != 0:
            dx /= math.sqrt(2)
            dy /= math.sqrt(2)

        player_x += dx * speed
        player_y += dy * speed
        player_x = max(0, min(Width - player_size, player_x))
        player_y = max(500, min(height - player_size, player_y))

    screen.fill((10, 10, 30))

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

        for bb in boss_bullets:
            pygame.draw.rect(screen, (255, 150, 50), (bb[0], bb[1], boss_bullet_width, boss_bullet_height))

        for enemy in enemies:
            draw_enemy_sprite(screen, enemy[0], enemy[1], enemies_width, enemies_height, 'normal')

        for se in special_enemies:
            draw_enemy_sprite(screen, se[0], se[1], special_enemies_width, special_enemies_height, 'special', flash=(se[3] > 0))

        for te in tanky_enemies:
            draw_enemy_sprite(screen, te[0], te[1], tanky_enemies_width, tanky_enemies_height, 'tanky', flash=(te[3] > 0))

        for boss in bosses:
            if boss_img:
                if boss[3] > 0:
                    img_copy = boss_img.copy()
                    img_copy.fill((255, 255, 255, 120), special_flags=pygame.BLEND_RGBA_ADD)
                    screen.blit(img_copy, (boss[0], boss[1]))
                else:
                    screen.blit(boss_img, (boss[0], boss[1]))
            else:
                color = (255, 100, 100) if boss[3] > 0 else (255, 0, 0)
                pygame.draw.rect(screen, color, (boss[0], boss[1], bosses_width, bosses_height))
            draw_boss_health_bar(boss, screen)

        level_text = font.render("Level: " + str(level), True, (255, 255, 255))
        score_text = font.render("Score: " + str(score), True, (255, 255, 255))
        screen.blit(level_text, (10, 10))
        screen.blit(score_text, (Width - score_text.get_width() - 10, 10))

        if player_img:
            screen.blit(player_img, (player_x, player_y))
        else:
            pygame.draw.rect(screen, (0, 200, 255), (player_x, player_y, player_size, player_size))

        if bosses:
            draw_player_health_bar(screen)

    pygame.display.flip()
    Clock.tick(60)
import pygame
import sys
import math


pygame.init()
try:
    pygame.mixer.init()
except Exception:
    pass

# Music
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

# Screen settings
Width = 600
height = 800
screen = pygame.display.set_mode((Width, height))
pygame.display.set_caption("SpaceShooters")

# Colors
BG_COLOR = (30, 30, 30)
BUTTON_COLOR = (70, 130, 180)
HOVER_COLOR = (100, 170, 220)
TEXT_COLOR = (255, 255, 255)

# Clock
Clock = pygame.time.Clock()
level = 1
game_over = False
menu_active = True

# Fonts
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 28)

# Button class
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

# Create buttons
buttons = [
    Button("Play", 200, 120, 200, 50),
    Button("Options", 200, 190, 200, 50),
    Button("Quit", 200, 260, 200, 50)
]

# Player settings
player_size = 40
player_x = Width // 2 - player_size // 2
player_y = height // 1.3
speed = 5

# Bullets
bullet_width = 4
bullet_height = 10
bullet_speed = 12
bullet_damage = 1
bullets = []

# Normal Enemies
enemies_width = 25
enemies_height = 15
enemies_speed = 3
enemies = []
enemy_direction = 1
enemy_drop = 20
enemies_health = 1

# Special Enemies
special_enemies_width = 30
special_enemies_height = 20
special_enemies_speed = 3
special_enemies = []
special_enemy_drop = 20
special_enemies_health = 2

# Boss Enemy
bosses_width = 140
bosses_height = 100
boss_speed = 5
boss_health = 67
boss_maxhealth = 67
bosses = []
boss_drop = 25

# Enemy grid settings
rows = 3
cols = 8
x_spacing = 40
y_spacing = 40
x_padding = (Width - ((cols - 1) * x_spacing + enemies_width)) // 2
y_padding = 40


def draw_boss_health_bar(boss, surface):
    hp = boss[2]
    ratio = max(0.0, min(hp / boss_maxhealth, 1.0))
    bar_width = bosses_width
    bar_height = 8
    bar_x = boss[0]
    bar_y = boss[1] - 12
    pygame.draw.rect(surface, (120, 0, 0), (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, int(bar_width * ratio), bar_height))
    pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)


def spawnEnemy():
    global enemies_speed, enemies_width, special_enemies_speed, special_enemies_width

    if level == 5 or level == 10:
        boss_x = (Width - bosses_width) // 2
        boss_y = y_padding
        bosses.clear()
        bosses.append([boss_x, boss_y, boss_health, 0])
        return

    # Apply level scaling ONCE, outside the row loop
    if level >= 2:
        enemies_speed += 1
        special_enemies_speed = enemies_speed
        enemies_width = max(10, enemies_width - 1)
        special_enemies_width = max(10, special_enemies_width - 1)

    for row in range(rows):
        for col in range(cols):
            enemy_x = x_padding + col * x_spacing
            enemy_y = y_padding + row * y_spacing
            se_x = enemy_x - (special_enemies_width - enemies_width) // 2
            se_y = enemy_y + (enemies_height - special_enemies_height)
            if level == 2 and row == rows - 1:
                special_enemies.append([se_x, se_y, special_enemies_health])
            elif level == 3 and (row == rows - 1 or row == 0):
                special_enemies.append([se_x, se_y, special_enemies_health])
            elif level == 4 and (row + col) % 2 == 0:
                special_enemies.append([se_x, se_y, special_enemies_health])
            else:
                enemies.append([enemy_x, enemy_y, enemies_health])


def reset_game():
    global level, enemies_speed, special_enemies_speed, enemy_direction
    global enemies_width, enemies_height, special_enemies_width, special_enemies_height
    global boss_speed, bosses_width, player_x, player_y, game_over

    level = 1
    enemies_speed = 3
    special_enemies_speed = 3
    enemy_direction = 1
    enemies_width = 25
    enemies_height = 15
    special_enemies_width = 30
    special_enemies_height = 20
    boss_speed = 5
    bosses_width = 140
    player_x = Width // 2 - player_size // 2
    player_y = height // 1.3
    game_over = False

    enemies.clear()
    special_enemies.clear()
    bosses.clear()
    bullets.clear()

    spawnEnemy()


# Game loop
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
                        reset_game()
                    elif button.text == "Options":
                        pass
                    elif button.text == "Quit":
                        pygame.quit()
                        sys.exit()

        if event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_r:
                    reset_game()
                continue

            if not menu_active and event.key == pygame.K_SPACE:
                bullet_x = player_x + player_size // 2 - bullet_width // 2
                bullet_y = player_y
                bullets.append([bullet_x, bullet_y])

    # Music control
    if music_loaded:
        if not menu_active and not game_over:
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

    if not game_over and not menu_active:
        # Move bullets and check collisions
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
                    if special_enemy[2] <= 0:
                        special_enemies.remove(special_enemy)
                        enemies_speed *= 1.02
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
                        enemies_speed *= 1.02
                    if bullet in bullets:
                        bullets.remove(bullet)
                    break

            for boss in bosses[:]:
                boss_rect = pygame.Rect(boss[0], boss[1], bosses_width, bosses_height)
                if boss[2] > 0 and bullet_rect.colliderect(boss_rect):
                    boss[2] -= bullet_damage
                    boss[3] = 8
                    if boss[2] <= 0:
                        bosses.remove(boss)
                        boss_speed *= 1.02
                    if bullet in bullets:
                        bullets.remove(bullet)
                    break

        # Determine movement direction based on edge collisions
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
            for boss in bosses:
                boss[1] += boss_drop

        for enemy in enemies:
            enemy[0] += enemies_speed * enemy_direction

        for special_enemy in special_enemies:
            special_enemy[0] += enemies_speed * enemy_direction

        for boss in bosses:
            boss[0] += boss_speed * enemy_direction

        # Check player collision
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

        for enemy in enemies:
            if player_rect.colliderect(pygame.Rect(enemy[0], enemy[1], enemies_width, enemies_height)):
                game_over = True
                break

        for special_enemy in special_enemies:
            if player_rect.colliderect(pygame.Rect(special_enemy[0], special_enemy[1], special_enemies_width, special_enemies_height)):
                game_over = True
                break

        for boss in bosses:
            if player_rect.colliderect(pygame.Rect(boss[0], boss[1], bosses_width, bosses_height)):
                game_over = True
                break

        # Level up when all enemies cleared
        if not enemies and not special_enemies and not bosses:
            level += 1
            bullets.clear()
            spawnEnemy()

        # Update boss hit flash timers
        for boss in bosses:
            if boss[3] > 0:
                boss[3] -= 1

        # Player movement
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

    # Drawing
    screen.fill((30, 30, 30))

    if menu_active:
        title_text = font.render("SpaceShooters", True, TEXT_COLOR)
        screen.blit(title_text, ((Width - title_text.get_width()) // 2, 40))
        for button in buttons:
            button.draw(screen)
    else:
        if game_over:
            game_over_text = font.render("GAME OVER", True, (255, 50, 50))
            restart_text = small_font.render("Press R to restart", True, (255, 255, 255))
            screen.blit(game_over_text, ((Width - game_over_text.get_width()) // 2, height // 3))
            screen.blit(restart_text, ((Width - restart_text.get_width()) // 2, height // 2))
        else:
            for bullet in bullets:
                pygame.draw.rect(screen, (255, 50, 50), (bullet[0], bullet[1], bullet_width, bullet_height))

            for enemy in enemies:
                pygame.draw.rect(screen, (200, 180, 0), (enemy[0], enemy[1], enemies_width, enemies_height))

            for special_enemy in special_enemies:
                pygame.draw.rect(screen, (255, 0, 0), (special_enemy[0], special_enemy[1], special_enemies_width, special_enemies_height))

            for boss in bosses:
                current_color = (255, 100, 100) if boss[3] > 0 else (255, 0, 0)
                pygame.draw.rect(screen, current_color, (boss[0], boss[1], bosses_width, bosses_height))
                draw_boss_health_bar(boss, screen)

            level_text = font.render("Level: " + str(level), True, (255, 255, 255))
            screen.blit(level_text, (10, 10))

            pygame.draw.rect(screen, (0, 200, 255), (player_x, player_y, player_size, player_size))

    pygame.display.flip()
    Clock.tick(60)
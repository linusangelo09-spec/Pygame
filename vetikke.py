import pygame
import sys
import math


pygame.init()

# Screen settings
Width = 600
height = 800
screen = pygame.display.set_mode((Width, height))
pygame.display.set_caption("SpaceShooters")

# Clock
Clock = pygame.time.Clock()
level = 1
game_over = False

#player settings
player_size = 40
player_x = Width // 2 - player_size // 2
player_y = height // 1.3
speed = 5

# Fonts
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 28)

# Bullets
bullet_width = 4
bullet_height = 10
bullet_speed = 8
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
special_enemies_speed = 2
special_enemies = []
special_enemy_direction = 1
special_enemy_drop = 25
special_enemies_health = 2

# Boss Enemy
bosses_width = 50
bosses_height = 30
boss_speed = 1
boss_health = 5
bosses = []
boss_drop = 25
boss_health = 50


# Create enemies in a grid similar to Galaga
rows = 3
cols = 8
x_spacing = 40
y_spacing = 40
x_padding = (Width - ((cols - 1) * x_spacing + enemies_width)) // 2
y_padding = 40

def spawnEnemy():
    global enemies_speed
    global enemies_width
    global special_enemies_speed

    for row in range(rows):
        if level >= 2:
            enemies_speed += 1
            special_enemies_speed = enemies_speed
            enemies_width -= 1

        for col in range(cols):
            enemy_x = x_padding + col * x_spacing
            enemy_y = y_padding + row * y_spacing
            if level == 2 and row == rows - 1:
                special_enemies.append([enemy_x, enemy_y, special_enemies_health])
            else:
                enemies.append([enemy_x, enemy_y, enemies_health])

def spawnSpecialEnemy():
    global special_enemies_speed
    global special_enemies_width

    for row in range(rows):
        if level >= 2:
            special_enemies_speed += 1
            special_enemies_width -= 1

            
            
        for col in range(cols):
            special_enemy_x = x_padding + col * x_spacing
            special_enemy_y = y_padding + row * y_spacing
            special_enemies.append([special_enemy_x, special_enemy_y, special_enemies_health])

def spawnBoss():
    global boss_speed
    global boss_health

    for row in range(rows):
        if level >= 2:
            boss_speed += 1
            boss_width -= 1
            
        for col in range(cols):
            boss_x = x_padding + col * x_spacing
            boss_y = y_padding + row * y_spacing
            bosses.append([boss_x, boss_y, boss_health])


spawnEnemy()
#spawnSpecialEnemy()
#spawnBoss()

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_r:
                    # Restart the game after game over
                    level = 1
                    enemies.clear()
                    special_enemies.clear()
                    bullets.clear()
                    player_x = Width // 2 - player_size // 2
                    player_y = height // 1.3
                    enemies_speed = 3
                    special_enemies_speed = 2
                    enemy_direction = 1
                    enemies_width = 25 
                    enemies_height = 15
                    special_enemies_width = 30
                    special_enemies_height = 20
                    game_over = False
                    spawnEnemy()
                continue

            if event.key == pygame.K_SPACE:
                bullet_x = player_x + player_size // 2 - bullet_width // 2
                bullet_y = player_y
                bullets.append([bullet_x, bullet_y])

    if not game_over:
        # Move bullets and collide with enemies
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
                    enemies_speed *= 1.02  # Increase speed slightly with each hit based on current speed
                    if bullet in bullets:
                        bullets.remove(bullet)
                    break
                    
            for boss in bosses[:]:
                boss_rect = pygame.Rect(boss[0], boss[1], bosses_width, bosses_height)
                if boss[2] > 0 and bullet_rect.colliderect(boss_rect):
                    boss[2] -= bullet_damage
                    if boss[2] <= 0:
                        bosses.remove(boss)
                    boss_speed *= 1.02  # Increase speed slightly with each hit based on current speed
                    if bullet in bullets:
                        bullets.remove(bullet)
                    break

        # Move enemies side to side like Galaga
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

        # Check for collision between enemies and player
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy[0], enemy[1], enemies_width, enemies_height)
            if player_rect.colliderect(enemy_rect):
                game_over = True
                break

        for special_enemy in special_enemies:
            special_rect = pygame.Rect(special_enemy[0], special_enemy[1], special_enemies_width, special_enemies_height)
            if player_rect.colliderect(special_rect):
                game_over = True
                break

        # Respawn enemies if all are destroyed
        if not enemies and not special_enemies:
            level += 1
            bullets.clear()
            spawnEnemy()

        # Key presses
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_RIGHT]:
            dx += 1
        if keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_DOWN]:
            dy += 1

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx /= math.sqrt(2)
            dy /= math.sqrt(2)

        player_x += dx * speed
        player_y += dy * speed

        # Keep square on screen
        player_x = max(0, min(Width - player_size, player_x))
        player_y = max(500, min(height - player_size, player_y))

    # Drawing
    screen.fill((30, 30, 30))

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
            pygame.draw.rect(screen, (255, 0, 0), (boss[0], boss[1], boss_width, boss_height))

        pygame.draw.rect(screen, (0, 200, 255), (player_x, player_y, player_size, player_size))

    pygame.display.flip()
    Clock.tick(60)
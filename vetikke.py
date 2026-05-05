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

#player settings
player_size = 40
player_x = Width // 2 - player_size // 2
player_y = height // 1.3
speed = 5

# Bullets
bullet_width = 4
bullet_height = 10
bullet_speed = 8
bullets = []

# Enemies
enemies_width = 25
enemies_height = 15
enemies_speed = 3
enemies = []
enemy_direction = 1
enemy_drop = 20

# Create enemies in a grid similar to Galaga
rows = 3
cols = 8
x_padding = 40
y_padding = 40
x_spacing = enemies_width + 20
y_spacing = enemies_height + 20
for row in range(rows):
    for col in range(cols):
        enemy_x = x_padding + col * x_spacing
        enemy_y = y_padding + row * y_spacing
        enemies.append([enemy_x, enemy_y])


# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet_x = player_x + player_size // 2 - bullet_width // 2
                bullet_y = player_y
                bullets.append([bullet_x, bullet_y])

    # Move bullets and collide with enemies
    for bullet in bullets[:]:
        bullet[1] -= bullet_speed
        if bullet[1] < 0:
            bullets.remove(bullet)
            continue

        for enemy in enemies[:]:
            enemy_rect = pygame.Rect(enemy[0], enemy[1], enemies_width, enemies_height)
            bullet_rect = pygame.Rect(bullet[0], bullet[1], bullet_width, bullet_height)
            if bullet_rect.colliderect(enemy_rect):
                enemies.remove(enemy)
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

    if move_left or move_right:
        enemy_direction *= -1
        for enemy in enemies:
            enemy[1] += enemy_drop

    for enemy in enemies:
        enemy[0] += enemies_speed * enemy_direction

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
    player_y = max(0, min(height - player_size, player_y))

    # Drawing
    screen.fill((30, 30, 30))

    for bullet in bullets:
        pygame.draw.rect(screen, (255, 50, 50), (bullet[0], bullet[1], bullet_width, bullet_height))

    for enemy in enemies:
        pygame.draw.rect(screen, (200, 180, 0), (enemy[0], enemy[1], enemies_width, enemies_height))

    pygame.draw.rect(screen, (0, 200, 255), (player_x, player_y, player_size, player_size))

    pygame.display.flip()
    Clock.tick(60)
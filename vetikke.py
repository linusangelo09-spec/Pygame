import pygame
import sys
import math

print ("i love femboys")

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

    # Move bullets
    for bullet in bullets[:]:
        bullet[1] -= bullet_speed
        if bullet[1] < 0:
            bullets.remove(bullet)

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

    pygame.draw.rect(screen, (0, 200, 255), (player_x, player_y, player_size, player_size))

    pygame.display.flip()
    Clock.tick(60)
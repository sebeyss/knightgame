import pygame
import random
import math

# Initialisation de Pygame
pygame.init()

# Paramètres de la fenêtre
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Knight vs Enemies")

# Chargement des images
knight_image = pygame.image.load("assets/knight.png").convert_alpha()
knight_image = pygame.transform.scale(knight_image, (128, 128))
enemy_image = pygame.image.load("assets/enemy.png").convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (64, 64))

# Polices pour le texte
font = pygame.font.SysFont(None, 74)  # Pour "Game Over"
button_font = pygame.font.SysFont(None, 48)  # Pour le bouton

# Classe pour le chevalier
class Knight:
    def __init__(self):
        self.width = 64
        self.height = 64
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT - 100
        self.speed = 5
        self.health = 100
        self.attack_cooldown = 0

    def draw(self):
        screen.blit(knight_image, (self.x, self.y))
        pygame.draw.rect(screen, (255, 0, 0), (10, 10, 100, 10))
        pygame.draw.rect(screen, (0, 255, 0), (10, 10, self.health, 10))

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WINDOW_WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < WINDOW_HEIGHT - self.height:
            self.y += self.speed

    def attack(self, enemies):
        if self.attack_cooldown <= 0:
            attack_range = 70
            knight_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            for enemy in enemies[:]:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if knight_rect.inflate(attack_range, attack_range).colliderect(enemy_rect):
                    enemy.health -= 20
                    if enemy.health <= 0:
                        enemies.remove(enemy)
            self.attack_cooldown = 30

# Classe pour les ennemis
class Enemy:
    def __init__(self, target_x, target_y, speed):
        self.width = 48
        self.height = 48
        side = random.choice(["top", "left", "right"])
        if side == "top":
            self.x = random.randint(0, WINDOW_WIDTH - self.width)
            self.y = -self.height
        elif side == "left":
            self.x = -self.width
            self.y = random.randint(0, WINDOW_HEIGHT - self.height)
        else:
            self.x = WINDOW_WIDTH
            self.y = random.randint(0, WINDOW_HEIGHT - self.height)
        self.speed = speed
        self.health = 50

    def draw(self):
        screen.blit(enemy_image, (self.x, self.y))
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 10, self.width, 5))
        pygame.draw.rect(screen, (255, 165, 0), (self.x, self.y - 10, self.width * (self.health / 50), 5))

    def move_towards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 50:
            dx, dy = dx / distance, dy / distance
            self.x += dx * self.speed * 0.8
            self.y += dy * self.speed * 0.8
        knight_rect = pygame.Rect(target_x - 32, target_y - 32, 64, 64)
        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if enemy_rect.colliderect(knight_rect):
            knight.health -= 1

# Fonction pour réinitialiser le jeu
def reset_game():
    global knight, enemies, wave, enemies_to_spawn, spawned_enemies, game_over
    knight = Knight()
    enemies = []
    wave = 0
    enemies_to_spawn = 1
    spawned_enemies = 0
    game_over = False

# Initialisation des objets
knight = Knight()
enemies = []
wave = 0
enemies_to_spawn = 1
base_speed = 1
spawned_enemies = 0
game_over = False

# Bouton Restart
button_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 50, 200, 60)
button_text = button_font.render("Restart", True, (255, 255, 255))

# Boucle principale
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and game_over:
            if button_rect.collidepoint(event.pos):
                reset_game()

    if not game_over:
        keys = pygame.key.get_pressed()
        knight.move(keys)
        
        if keys[pygame.K_SPACE]:
            knight.attack(enemies)

        if knight.attack_cooldown > 0:
            knight.attack_cooldown -= 1

        if len(enemies) == 0 and spawned_enemies == 0:
            wave += 1
            enemies_to_spawn = wave * 2 - 2 if wave > 1 else 1
            spawned_enemies = enemies_to_spawn
            current_speed = base_speed + wave * 0.2

        if spawned_enemies > 0:
            enemies.append(Enemy(knight.x, knight.y, current_speed))
            spawned_enemies -= 1

        for enemy in enemies[:]:
            enemy.move_towards(knight.x + knight.width // 2, knight.y + knight.height // 2)

        if knight.health <= 0:
            game_over = True

    # Affichage
    screen.fill((0, 0, 0))
    knight.draw()
    for enemy in enemies:
        enemy.draw()

    if game_over:
        game_over_text = font.render("Game Over", True, (255, 0, 0))
        screen.blit(game_over_text, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 40))
        # Affichage du bouton Restart
        pygame.draw.rect(screen, (0, 128, 0), button_rect)  # Fond vert
        screen.blit(button_text, (button_rect.x + 40, button_rect.y + 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
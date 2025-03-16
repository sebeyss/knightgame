import pygame
import random
import math

# Initialisation de Pygame
pygame.init()

# Paramètres de la fenêtre
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Knight vs Enemies")

# Couleur de fond verte
GRASS_COLOR = (50, 100, 50)  # Vert foncé

# Chargement des images
# Chevalier
knight_image = pygame.image.load("assets/knight.png").convert_alpha()
knight_image = pygame.transform.scale(knight_image, (64, 64))
knight_red_image = pygame.transform.scale(knight_image.copy(), (64, 64))
knight_red_image.fill((255, 50, 50, 150), special_flags=pygame.BLEND_RGBA_MULT)

# Ennemi animé
enemy_sprites = [
    pygame.transform.scale(pygame.image.load("assets/enemy_idle.png").convert_alpha(), (48, 48)),
    pygame.transform.scale(pygame.image.load("assets/enemy_walk1.png").convert_alpha(), (48, 48)),
    pygame.transform.scale(pygame.image.load("assets/enemy_walk2.png").convert_alpha(), (48, 48))
]

# Brins d'herbe
grass_sprites = [
    pygame.transform.scale(pygame.image.load("assets/grass1.png").convert_alpha(), (32, 32)),
    pygame.transform.scale(pygame.image.load("assets/grass2.png").convert_alpha(), (32, 32)),
    pygame.transform.scale(pygame.image.load("assets/grass3.png").convert_alpha(), (32, 32)),
    pygame.transform.scale(pygame.image.load("assets/grass4.png").convert_alpha(), (32, 32))
]
grass_moving_sprites = [
    pygame.transform.scale(pygame.image.load("assets/grass1_moving.png").convert_alpha(), (32, 32)),
    pygame.transform.scale(pygame.image.load("assets/grass2_moving.png").convert_alpha(), (32, 32)),
    pygame.transform.scale(pygame.image.load("assets/grass3_moving.png").convert_alpha(), (32, 32)),
    pygame.transform.scale(pygame.image.load("assets/grass4_moving.png").convert_alpha(), (32, 32))
]

# Polices
font = pygame.font.SysFont(None, 74)
button_font = pygame.font.SysFont(None, 48)
score_font = pygame.font.SysFont(None, 36)

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
        self.hit_timer = 0
        self.attack_timer = 0

    def draw(self):
        if self.attack_timer > 0:
            radius = 50
            angle_rad = math.radians(self.attack_timer * 20)
            circle_x = self.x + self.width // 2 + math.cos(angle_rad) * radius
            circle_y = self.y + self.height // 2 + math.sin(angle_rad) * radius
            pygame.draw.circle(screen, (200, 200, 200), (int(circle_x), int(circle_y)), 10, 2)
            self.attack_timer -= 1
        if self.hit_timer > 0:
            screen.blit(knight_red_image, (self.x, self.y))
            self.hit_timer -= 1
        else:
            screen.blit(knight_image, (self.x, self.y))
        pygame.draw.ellipse(screen, (0, 0, 0, 100), (self.x, self.y + self.height - 10, self.width, 20))
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 15, self.width, 10))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y - 15, self.width * (self.health / 100), 10))

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
            self.attack_timer = 20
            attack_range = 70
            knight_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            for enemy in enemies[:]:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if knight_rect.inflate(attack_range, attack_range).colliderect(enemy_rect):
                    enemy.health -= 40
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        global enemies_killed
                        enemies_killed += 1
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
        self.frame = 0

    def draw(self):
        screen.blit(enemy_sprites[int(self.frame)], (self.x, self.y))
        pygame.draw.ellipse(screen, (0, 0, 0, 100), (self.x, self.y + self.height - 10, self.width, 15))
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y - 10, self.width, 5))
        pygame.draw.rect(screen, (255, 165, 0), (self.x, self.y - 10, self.width * (self.health / 50), 5))

    def move_towards(self, target_x, target_y, enemies):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 50:
            dx, dy = dx / distance, dy / distance
            self.x += dx * self.speed * 0.8
            self.y += dy * self.speed * 0.8
            self.frame = (self.frame + 0.1) % 3
        else:
            self.frame = 0
        for other in enemies:
            if other != self:
                dist_x = self.x - other.x
                dist_y = self.y - other.y
                dist = math.sqrt(dist_x**2 + dist_y**2)
                if dist < self.width and dist > 0:
                    push_x = dist_x / dist * 0.5
                    push_y = dist_y / dist * 0.5
                    self.x += push_x
                    self.y += push_y
                    other.x -= push_x
                    other.y -= push_y
        knight_rect = pygame.Rect(target_x - 32, target_y - 32, 64, 64)
        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if enemy_rect.colliderect(knight_rect) and knight.hit_timer == 0:
            knight.health -= 0.5
            knight.hit_timer = 10

# Classe pour les brins d'herbe
class GrassBlade:
    def __init__(self, x, y, type_idx):
        self.x = x
        self.y = y
        self.type_idx = type_idx  # 0 à 3 pour choisir le sprite
        self.moved = False  # État permanent une fois déplacé

    def draw(self):
        sprite = grass_moving_sprites[self.type_idx] if self.moved else grass_sprites[self.type_idx]
        screen.blit(sprite, (self.x, self.y))

    def check_collision(self, rect):
        grass_rect = pygame.Rect(self.x, self.y, 32, 32)
        if grass_rect.colliderect(rect) and not self.moved:
            self.moved = True

# Fonction pour réinitialiser le jeu
def reset_game():
    global knight, enemies, wave, enemies_to_spawn, spawned_enemies, game_over, enemies_killed, grass_blades
    knight = Knight()
    enemies = []
    wave = 0
    enemies_to_spawn = 1
    spawned_enemies = 0
    game_over = False
    enemies_killed = 0
    grass_blades = [GrassBlade(random.randint(0, WINDOW_WIDTH - 32), random.randint(0, WINDOW_HEIGHT - 32), random.randint(0, 3)) for _ in range(200)]

# Initialisation des objets
knight = Knight()
enemies = []
wave = 0
enemies_to_spawn = 1
base_speed = 1
spawned_enemies = 0
game_over = False
enemies_killed = 0
grass_blades = [GrassBlade(random.randint(0, WINDOW_WIDTH - 32), random.randint(0, WINDOW_HEIGHT - 32), random.randint(0, 3)) for _ in range(200)]  # 200 brins

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
            enemy.move_towards(knight.x + knight.width // 2, knight.y + knight.height // 2, enemies)

        # Vérification des collisions avec l'herbe
        knight_rect = pygame.Rect(knight.x, knight.y, knight.width, knight.height)
        for blade in grass_blades:
            blade.check_collision(knight_rect)
            for enemy in enemies:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                blade.check_collision(enemy_rect)

        if knight.health <= 0:
            game_over = True

    # Affichage
    screen.fill(GRASS_COLOR)  # Fond vert uni
    for blade in grass_blades:
        blade.draw()
    knight.draw()
    for enemy in enemies:
        enemy.draw()

    # Affichage du score
    score_text = score_font.render(f"Ennemis tués : {enemies_killed}", True, (255, 255, 255))
    screen.blit(score_text, (10, 30))

    if game_over:
        game_over_text = font.render("Game Over", True, (255, 0, 0))
        screen.blit(game_over_text, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 40))
        pygame.draw.rect(screen, (0, 128, 0), button_rect)
        screen.blit(button_text, (button_rect.x + 40, button_rect.y + 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
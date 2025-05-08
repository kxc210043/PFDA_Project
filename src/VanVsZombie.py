import pygame
import random

pygame.init()

# Screen 
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Van vs Zombies")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BUTTON_COL = (100, 200, 150)
BUTTON_HOVER_COL = (150, 255, 200)
TEXT_COL = WHITE


main_menu = True
game_paused = False


font = pygame.font.SysFont("arialblack", 40)
small_font = pygame.font.SysFont("Arial", 20)


button_rect = pygame.Rect(300, 250, 200, 60)

# Game settings
van_hp = 100
van_speed = 5
zombie_speed = 3
zombie_types = ["normal", "semi_mutated", "special_mutated"]

# Helper function to draw text
def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

# Van class
class Van(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((60, 40))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.health = van_hp

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= van_speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += van_speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= van_speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += van_speed
    # Zombie class
class Zombie(pygame.sprite.Sprite):
    def __init__(self, zombie_type):
        super().__init__()
        self.zombie_type = zombie_type
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - 40)
        self.rect.y = random.randint(-150, -40)

        if self.zombie_type == "normal":
            self.damage = 5
            self.image.fill((150, 0, 0))
        elif self.zombie_type == "semi_mutated":
            self.damage = 10
            self.image.fill((255, 100, 100))
        elif self.zombie_type == "special_mutated":
            self.damage = 20
            self.image.fill((255, 0, 0))

    def update(self):
        self.rect.y += zombie_speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - 40)
            self.rect.y = random.randint(-150, -40)

# Main loop
run = True
clock = pygame.time.Clock()

# Sprites (initialized when the game starts)
all_sprites = pygame.sprite.Group()
zombies = pygame.sprite.Group()
van = None 

def start_game():
    global all_sprites, zombies, van
    all_sprites = pygame.sprite.Group()
    zombies = pygame.sprite.Group()
    van = Van()
    all_sprites.add(van)
    for _ in range(5):
        zombie_type = random.choice(zombie_types)
        zombie = Zombie(zombie_type)
        all_sprites.add(zombie)
        zombies.add(zombie)

while run:
    clock.tick(60)
    screen.fill((52, 78, 91) if main_menu else BLACK)

    if main_menu:
        # Handle menu
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, BUTTON_HOVER_COL, button_rect, border_radius=10)
            if mouse_click[0]:
                main_menu = False
                start_game()
        else:
            pygame.draw.rect(screen, BUTTON_COL, button_rect, border_radius=10)

        draw_text("START", font, TEXT_COL, button_rect.x + 50, button_rect.y + 10)
        draw_text("Van vs Zombies", font, TEXT_COL, 240, 100)

    elif game_paused:
        draw_text("Game Paused", font, TEXT_COL, 260, 250)
    else:
        # Game running
        keys = pygame.key.get_pressed()
        van.update(keys)
        zombies.update()

        # Check collisions
        collided_zombies = pygame.sprite.spritecollide(van, zombies, True)
        for zombie in collided_zombies:
            van.health -= zombie.damage

        # Draw all sprites
        all_sprites.draw(screen)

        # Health bar
        health_text = small_font.render(f"Van Health: {van.health}", True, WHITE)
        screen.blit(health_text, (10, 10))

        # Game Over check
        if van.health <= 0:
            game_over_text = font.render("Game Over!", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2))
            pygame.display.flip()
            pygame.time.delay(2000)
            main_menu = True  # Back to menu

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not main_menu:
                game_paused = not game_paused

    pygame.display.update()

pygame.quit()

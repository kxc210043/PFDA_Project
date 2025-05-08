import pygame
import random
import os

pygame.init()

# Screen setup
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
ROAD_COLOR = (50, 50, 50)


main_menu = True
game_paused = False


font = pygame.font.SysFont("arialblack", 40)
small_font = pygame.font.SysFont("Arial", 20)


button_rect = pygame.Rect(300, 250, 200, 60)


van_hp = 100
van_speed = 5
zombie_speed = 3
zombie_types = ["normal", "semi_mutated", "special_mutated"]


road_scroll = 0
line_spacing = 100

# Zombie spawn timing
zombie_spawn_delay = 1500  # milliseconds
last_zombie_spawn_time = 0


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


class Van(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

       
        if not os.path.isfile('van.png'):
            print("van.png not found!")
            pygame.quit()
            exit()

        try:
            self.image = pygame.image.load('van.png').convert_alpha()  # Load the van image
        except pygame.error as e:
            print(f"Error loading image: {e}")
            pygame.quit()
            exit()

        # Rotate the image 90 degrees clockwise
        self.image = pygame.transform.rotate(self.image, -90)  # Rotate by -90 degrees (clockwise)

        # Resize the image to make it smaller
        self.image = pygame.transform.scale(self.image, (240, 160))  # Adjust the width and height as needed

        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.health = van_hp

    def update(self, keys):
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= van_speed
        if keys[pygame.K_d] and self.rect.right < WIDTH:
            self.rect.x += van_speed
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= van_speed
        if keys[pygame.K_s] and self.rect.bottom < HEIGHT:
            self.rect.y += van_speed

# Zombie class
class Zombie(pygame.sprite.Sprite):
    def __init__(self, zombie_type):
        super().__init__()
        self.zombie_type = zombie_type
        self.image = pygame.Surface((40, 40))
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

#game loop
run = True
clock = pygame.time.Clock()


all_sprites = pygame.sprite.Group()
zombies = pygame.sprite.Group()
van = None


def start_game():
    global all_sprites, zombies, van, road_scroll, last_zombie_spawn_time
    all_sprites = pygame.sprite.Group()
    zombies = pygame.sprite.Group()
    van = Van()
    all_sprites.add(van)
    for _ in range(5):
        zombie_type = random.choice(zombie_types)
        zombie = Zombie(zombie_type)
        all_sprites.add(zombie)
        zombies.add(zombie)
    road_scroll = 0
    last_zombie_spawn_time = pygame.time.get_ticks()

# Main game loop
while run:
    clock.tick(60)

    if main_menu:
        screen.fill((52, 78, 91))
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
        screen.fill(ROAD_COLOR)

        
        if van.health > 0:
            road_scroll += 5
            if road_scroll >= line_spacing:
                road_scroll = 0

        # Draw dashed lines
        line_width = 10
        line_height = 50
        line_x = WIDTH // 2 - line_width // 2
        for y in range(-line_height, HEIGHT + line_spacing, line_spacing):
            pygame.draw.rect(screen, WHITE, (line_x, y + road_scroll, line_width, line_height))

        keys = pygame.key.get_pressed()
        if van.health > 0:
            van.update(keys)
            zombies.update()

            # Spawn new zombie
            current_time = pygame.time.get_ticks()
            if current_time - last_zombie_spawn_time > zombie_spawn_delay:
                zombie_type = random.choice(zombie_types)
                new_zombie = Zombie(zombie_type)
                all_sprites.add(new_zombie)
                zombies.add(new_zombie)
                last_zombie_spawn_time = current_time

        # Check collisions
        collided_zombies = pygame.sprite.spritecollide(van, zombies, True)
        for zombie in collided_zombies:
            van.health -= zombie.damage

        
        all_sprites.draw(screen)

        # Health
        health_text = small_font.render(f"Van Health: {van.health}", True, WHITE)
        screen.blit(health_text, (10, 10))

        # Game over
        if van.health <= 0:
            draw_text("GAME OVER!", font, RED, WIDTH // 2 - 140, HEIGHT // 2 - 20)
            pygame.display.flip()
            pygame.time.delay(2000)
            main_menu = True
            game_paused = False

    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN and not main_menu:
            if event.key == pygame.K_SPACE:
                game_paused = not game_paused

    pygame.display.update()

pygame.quit()


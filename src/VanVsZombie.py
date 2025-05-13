import pygame
import random
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Van vs Zombies")


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BUTTON_COL = (100, 200, 150)
BUTTON_HOVER_COL = (150, 255, 200)
TEXT_COL = BLACK
ROAD_COLOR = (50, 50, 50)


font = pygame.font.SysFont("arialblack", 40)
small_font = pygame.font.SysFont("Arial", 20)
high_score_font = pygame.font.SysFont("arialblack", 30)


button_rect = pygame.Rect(300, 250, 200, 60)


main_menu = True
game_paused = False
run = True
clock = pygame.time.Clock()


van_hp = 100
van_speed = 7
zombie_speed = 5
zombie_types = ["normal", "semi_mutated", "special_mutated"]
zombie_spawn_delay = 1500


road_scroll = 0
line_spacing = 100


last_zombie_spawn_time = 0
start_time = 0
high_score = 0


all_sprites = pygame.sprite.Group()
zombies = pygame.sprite.Group()
van = None


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def draw_health_bar(health, max_health, x, y, width, height):
    pygame.draw.rect(screen, RED, (x, y, width, height))
    health_width = width * (health / max_health)
    pygame.draw.rect(screen, (0, 255, 0), (x, y, health_width, height))

def draw_high_score(score, y_offset=100):
    text = f"High Score: {score}s"
    rendered = high_score_font.render(text, True, WHITE)
    rect = rendered.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(rendered, rect)

class Van(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        if not os.path.isfile('van.png'):
            print("Missing van.png")
            pygame.quit()
            exit()
        self.image = pygame.image.load('van.png').convert_alpha()
        self.image = pygame.transform.rotate(self.image, -90)
        self.image = pygame.transform.scale(self.image, (300, 220))
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.health = van_hp
        self.collision_rect = pygame.Rect(0, 0, self.rect.width // 3.5, self.rect.height // 3.5)
        self.update_collision_rect()

    def update(self, keys):
        if keys[pygame.K_a] and self.rect.x > -self.rect.width // 2:
            self.rect.x -= van_speed
        if keys[pygame.K_d] and self.rect.x < WIDTH - self.rect.width // 2:
            self.rect.x += van_speed
        if keys[pygame.K_w] and self.rect.y > -self.rect.height // 2:
            self.rect.y -= van_speed
        if keys[pygame.K_s] and self.rect.y < HEIGHT - self.rect.height // 2:
            self.rect.y += van_speed
        self.update_collision_rect()

    def update_collision_rect(self):
        self.collision_rect.center = self.rect.center

class Zombie(pygame.sprite.Sprite):
    def __init__(self, zombie_type):
        super().__init__()
        self.zombie_type = zombie_type
        self.rect = pygame.Rect(0, 0, 60, 60)
        self.rect.x = random.randint(0, WIDTH - 60)
        self.rect.y = random.randint(-150, -60)

        try:
            if zombie_type == "normal":
                self.damage = 5
                img_path = "nor_zom.png"
                size = (70, 70)
            elif zombie_type == "semi_mutated":
                self.damage = 10
                img_path = "sem_zom.png"
                size = (80, 78)
            elif zombie_type == "special_mutated":
                self.damage = 20
                img_path = "mut_zom.png"
                size = (100, 90)

            if os.path.isfile(img_path):
                self.image = pygame.image.load(img_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, size)
                self.image = pygame.transform.rotate(self.image, -90)
            else:
                raise FileNotFoundError(f"{img_path} not found")
        except Exception as e:
            print(f"Error loading zombie: {e}")
            self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
            self.image.fill((255, 0, 0))

    def update(self):
        self.rect.y += zombie_speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - 60)
            self.rect.y = random.randint(-150, -60)

def start_game():
    global all_sprites, zombies, van, road_scroll, last_zombie_spawn_time, start_time
    all_sprites.empty()
    zombies.empty()
    van = Van()
    all_sprites.add(van)

    for _ in range(5):
        zombie_type = random.choice(zombie_types)
        zombie = Zombie(zombie_type)
        zombies.add(zombie)
        all_sprites.add(zombie)

    road_scroll = 0
    last_zombie_spawn_time = pygame.time.get_ticks()
    start_time = pygame.time.get_ticks()



while run:
    clock.tick(60)

    if main_menu:
        screen.fill((52, 78, 91))
        if os.path.isfile("start.png"):
            bg = pygame.image.load("start.png").convert()
            bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
            screen.blit(bg, (0, 0))

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        pygame.draw.rect(screen, BUTTON_HOVER_COL if button_rect.collidepoint(mouse_pos) else BUTTON_COL, button_rect, border_radius=10)
        draw_text("START", font, TEXT_COL, button_rect.x + 50, button_rect.y + 10)
        draw_text("Van vs Zombies", font, TEXT_COL, 240, 100)

        if button_rect.collidepoint(mouse_pos) and mouse_click[0]:
            main_menu = False
            start_game()

    elif game_paused:
        draw_text("Game Paused", font, TEXT_COL, 260, 250)

    else:
        screen.fill(ROAD_COLOR)
        if van.health > 0:
            road_scroll = (road_scroll + 5) % line_spacing

        for y in range(-50, HEIGHT + line_spacing, line_spacing):
            pygame.draw.rect(screen, YELLOW, (WIDTH // 2 - 5, y + road_scroll, 10, 50))

        keys = pygame.key.get_pressed()
        if van.health > 0:
            van.update(keys)
            zombies.update()

            now = pygame.time.get_ticks()
            if now - last_zombie_spawn_time > zombie_spawn_delay:
                zombie = Zombie(random.choice(zombie_types))
                zombies.add(zombie)
                all_sprites.add(zombie)
                last_zombie_spawn_time = now

        for Hit in [Hit for Hit in zombies if van.collision_rect.colliderect(Hit.rect)]:
            van.health -= Hit.damage
            zombies.remove(Hit)
            all_sprites.remove(Hit)

        # Draw
        draw_health_bar(van.health, van_hp, 10, 10, 200, 20)
        time_survived = (pygame.time.get_ticks() - start_time) // 1000
        draw_text(f"Time: {time_survived}s", small_font, WHITE, WIDTH - 130, 15)

        all_sprites.draw(screen)

        if van.health <= 0:
            if time_survived > high_score:
                high_score = time_survived
            draw_text("GAME OVER!", font, RED, WIDTH // 2 - 140, HEIGHT // 2 - 40)
            draw_high_score(high_score, y_offset=20)
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



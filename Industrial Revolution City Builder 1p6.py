import pygame
import random

pygame.init()
pygame.mixer.init()

# Screen and Grid settings
WIDTH = 800
HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE  # 40
GRID_HEIGHT = HEIGHT // GRID_SIZE  # 30
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Industrial Revolution City Builder")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
DARK_GRAY = (50, 50, 50)
DARK_RED = (139, 0, 0)
LIGHT_GRAY = (200, 200, 200)
DARK_GREEN = (0, 100, 0)
BEIGE = (245, 245, 220)
DARK_BROWN = (101, 67, 33)

# Building definitions
BUILDINGS = {
    "factory": {"color": GRAY, "grid_size": (2, 2), "base_cost": 200, "current_cost": 200, "workers": 10},
    "house": {"color": BROWN, "grid_size": (1, 1), "base_cost": 50, "current_cost": 50, "workers": 0},
    "farm": {"color": YELLOW, "grid_size": (2, 2), "base_cost": 75, "current_cost": 75, "workers": 20},
    "mine": {"color": BLUE, "grid_size": (2, 2), "base_cost": 150, "current_cost": 150, "workers": 15},
    "railroad": {"color": DARK_GRAY, "grid_size": (1, 1), "base_cost": 25, "current_cost": 25, "workers": 0}
}

# Worker constants
WORKERS_PER_HOUSE = 5
WORKERS_PER_FACTORY = 10
WORKERS_PER_MINE = 15
WORKERS_PER_FARM = 20

# Production constants
FACTORY_PRODUCTION = 10
FARM_PRODUCTION = 20
MINE_PRODUCTION = 20
HOUSE_CAPACITY = 5

# Worker constants (unchanged)
HOUSE_CAPACITY = 5

# Technology effect functions
def reduce_factory_workers():
    global WORKERS_PER_FACTORY
    WORKERS_PER_FACTORY = 8

def bessemer_steel_process():
    global FACTORY_PRODUCTION
    FACTORY_PRODUCTION = 15

def increase_farm_production():
    global FARM_PRODUCTION
    FARM_PRODUCTION = 30

def mccormicks_reaper():
    global WORKERS_PER_FARM
    WORKERS_PER_FARM = 15

def increase_mine_production():
    global MINE_PRODUCTION
    MINE_PRODUCTION = 30

def dynamite():
    global WORKERS_PER_MINE
    WORKERS_PER_MINE = 12

def urban_housing():
    global HOUSE_CAPACITY
    HOUSE_CAPACITY +=2  # Increases capacity by 2 

def modern_medicine():
    global HOUSE_CAPACITY
    HOUSE_CAPACITY += 3 # Increases capacity by 3

# Technology definitions
TECHNOLOGIES = {
    "bessemer_steel_process": {
        "base_cost": 350,
        "effect": bessemer_steel_process,
        "description": "Increases factory production to 15 resources"
    },
    "factory_efficiency": {
        "base_cost": 300,
        "effect": reduce_factory_workers,
        "description": "Reduces factory worker requirement to 8"
    },
    "mccormicks_reaper": {
        "base_cost": 300,
        "effect": mccormicks_reaper,
        "description": "Reduces farm worker requirement to 15"
    },
    "advanced_farming": {
        "base_cost": 250,
        "effect": increase_farm_production,
        "description": "Increases farm production to 30 resources"
    },
    "dynamite": {
        "base_cost": 275,
        "effect": dynamite,
        "description": "Reduces mine worker requirement to 12"
    },
    "deep_mining": {
        "base_cost": 250,
        "effect": increase_mine_production,
        "description": "Increases mine production to 30 resources"
    },
    "urban_housing": {
        "base_cost": 200,
        "effect": urban_housing,
        "description": "Increases house worker capacity to 7"
    },
    "modern_medicine": {
        "base_cost": 400,
        "effect": modern_medicine,
        "description": "Increases house worker capacity to 8"
    }
}

tech_list = [
    "bessemer_steel_process", "factory_efficiency",
    "mccormicks_reaper", "advanced_farming",
    "dynamite", "deep_mining",
    "urban_housing", "modern_medicine"
]

# Load sound effects
try:
    BUILD_SOUND = pygame.mixer.Sound("build.wav")
    RESOURCE_SOUND = pygame.mixer.Sound("resource.wav")
except FileNotFoundError:
    BUILD_SOUND = None
    RESOURCE_SOUND = None

class CityBuilder:
    def __init__(self):
        self.resources = 475
        self.pollution = 0
        self.buildings = []
        self.grid = [[False for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
        self.current_building = "house"
        self.font = pygame.font.Font(None, 36)
        self.tech_font = pygame.font.Font(None, 24)
        self.last_pollution_time = pygame.time.get_ticks()
        self.last_factory_production = pygame.time.get_ticks()
        self.last_mine_production = pygame.time.get_ticks()
        self.last_farm_production = pygame.time.get_ticks()
        self.unlocked_buildings = {"house", "farm", "mine", "factory", "railroad"}
        self.researched_technologies = set()
        self.tech_menu_open = False
        self.smoke_particles = []  # For factory smoke animation
        self.last_smoke_time = pygame.time.get_ticks()

        # Starting buildings
        center_x, center_y = GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2  # (19, 15)
        farm_x, farm_y = center_x + 4, center_y - 1  # (23, 14)
        pixel_x = farm_x * GRID_SIZE
        pixel_y = farm_y * GRID_SIZE
        self.buildings.append({
            "type": "farm",
            "x": pixel_x,
            "y": pixel_y,
            "grid_x": farm_x,
            "grid_y": farm_y,
            "active": False
        })
        self.occupy_grid(farm_x, farm_y, "farm")
        self.resources -= BUILDINGS["farm"]["base_cost"]  # Deduct $75

        house_positions = [
            (center_x + 2, center_y - 1),  # (21, 14)
            (center_x + 3, center_y - 1),  # (22, 14)
            (center_x + 2, center_y),      # (21, 15)
            (center_x + 3, center_y)       # (22, 15)
        ]
        for grid_x, grid_y in house_positions:
            pixel_x = grid_x * GRID_SIZE
            pixel_y = grid_y * GRID_SIZE
            self.buildings.append({
                "type": "house",
                "x": pixel_x,
                "y": pixel_y,
                "grid_x": grid_x,
                "grid_y": grid_y,
                "active": True
            })
            self.occupy_grid(grid_x, grid_y, "house")
            self.resources -= BUILDINGS["house"]["base_cost"]  # Deduct $50 each

        self.assign_workers()

    def is_space_available(self, grid_x, grid_y, building_type):
        grid_w, grid_h = BUILDINGS[building_type]["grid_size"]
        if grid_x + grid_w > GRID_WIDTH or grid_y + grid_h > GRID_HEIGHT:
            return False
        for i in range(grid_w):
            for j in range(grid_h):
                if self.grid[grid_x + i][grid_y + j]:
                    return False
        return True

    def occupy_grid(self, grid_x, grid_y, building_type):
        grid_w, grid_h = BUILDINGS[building_type]["grid_size"]
        for i in range(grid_w):
            for j in range(grid_h):
                self.grid[grid_x + i][grid_y + j] = True

    def add_building_to_grid(self, grid_x, grid_y, building_type):
        if building_type not in self.unlocked_buildings:
            return
        if self.resources < BUILDINGS[building_type]["current_cost"]:
            return
        if not self.is_space_available(grid_x, grid_y, building_type):
            return
        
        pixel_x = grid_x * GRID_SIZE
        pixel_y = grid_y * GRID_SIZE
        self.buildings.append({
            "type": building_type,
            "x": pixel_x,
            "y": pixel_y,
            "grid_x": grid_x,
            "grid_y": grid_y,
            "active": False
        })
        self.occupy_grid(grid_x, grid_y, building_type)
        self.resources -= BUILDINGS[building_type]["current_cost"]
        
        if building_type == "railroad":
            railroad_count = sum(1 for b in self.buildings if b["type"] == "railroad")
            BUILDINGS["railroad"]["current_cost"] += railroad_count
        else:
            BUILDINGS[building_type]["current_cost"] += 1
        
        if BUILD_SOUND:
            BUILD_SOUND.play()

    def add_building(self, x, y):
        grid_x = x // GRID_SIZE
        grid_y = y // GRID_SIZE
        self.add_building_to_grid(grid_x, grid_y, self.current_building)

    def assign_workers(self):
        house_count = sum(1 for b in self.buildings if b["type"] == "house")
        total_workers = house_count * HOUSE_CAPACITY
        workers_available = total_workers

        for building in self.buildings:
            if building["type"] in ["factory", "farm", "mine"]:
                building["active"] = False

        for building in self.buildings:
            if building["type"] == "factory" and workers_available >= WORKERS_PER_FACTORY:
                workers_available -= WORKERS_PER_FACTORY
                building["active"] = True
            elif building["type"] == "farm" and workers_available >= WORKERS_PER_FARM:
                workers_available -= WORKERS_PER_FARM
                building["active"] = True
            elif building["type"] == "mine" and workers_available >= WORKERS_PER_MINE:
                workers_available -= WORKERS_PER_MINE
                building["active"] = True
        
        self.total_workers = total_workers
        self.available_workers = workers_available

    def update_pollution(self):
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - self.last_pollution_time) / 1000
        factory_count = sum(1 for b in self.buildings if b["type"] == "factory")
        self.pollution += factory_count * elapsed_time
        self.last_pollution_time = current_time

    def get_connected_railroads(self):
        railroad_tiles = [(b["grid_x"], b["grid_y"]) for b in self.buildings if b["type"] == "railroad"]
        if not railroad_tiles:
            return set()
        
        visited = set()
        to_visit = [railroad_tiles[0]]
        
        while to_visit:
            x, y = to_visit.pop()
            if (x, y) not in visited:
                visited.add((x, y))
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in railroad_tiles and (nx, ny) not in visited:
                        to_visit.append((nx, ny))
        
        return visited

    def is_adjacent_to_railroad(self, building):
        grid_w, grid_h = BUILDINGS[building["type"]]["grid_size"]
        building_x, building_y = building["grid_x"], building["grid_y"]
        railroad_tiles = self.get_connected_railroads()

        for i in range(grid_w):
            for j in range(grid_h):
                bx, by = building_x + i, building_y + j
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = bx + dx, by + dy
                    if (nx, ny) in railroad_tiles:
                        return True
        return False

    def produce_resources(self):
        current_time = pygame.time.get_ticks()
        produced = False
        railroad_count = len(self.get_connected_railroads())

        if current_time - self.last_factory_production >= 5000:
            active_factories = [b for b in self.buildings if b["type"] == "factory" and b["active"]]
            for factory in active_factories:
                base_yield = 10
                bonus = base_yield * 0.01 * railroad_count if self.is_adjacent_to_railroad(factory) else 0
                self.resources += FACTORY_PRODUCTION + bonus
            self.last_factory_production = current_time
            if active_factories:
                produced = True

        if current_time - self.last_farm_production >= 10000:
            active_farms = [b for b in self.buildings if b["type"] == "farm" and b["active"]]
            for farm in active_farms:
                base_yield = 20
                bonus = base_yield * 0.01 * railroad_count if self.is_adjacent_to_railroad(farm) else 0
                self.resources += FARM_PRODUCTION + bonus
            self.last_farm_production = current_time
            if active_farms:
                produced = True

        if current_time - self.last_mine_production >= 10000:
            active_mines = [b for b in self.buildings if b["type"] == "mine" and b["active"]]
            for mine in active_mines:
                base_yield = 20
                bonus = base_yield * 0.01 * railroad_count if self.is_adjacent_to_railroad(mine) else 0
                self.resources += MINE_PRODUCTION + bonus
            self.last_mine_production = current_time
            if active_mines:
                produced = True

        if produced and RESOURCE_SOUND:
            RESOURCE_SOUND.play()

    def get_tech_cost(self, tech_key):
        researched_count = len(self.researched_technologies)
        base_cost = TECHNOLOGIES[tech_key]["base_cost"]
        return base_cost * (2 ** researched_count)

    def research_technology(self, index):
        if index < len(tech_list):
            tech_key = tech_list[index]
            if tech_key not in self.researched_technologies:
                current_cost = self.get_tech_cost(tech_key)
                if self.resources >= current_cost:
                    self.resources -= current_cost
                    TECHNOLOGIES[tech_key]["effect"]()
                    self.researched_technologies.add(tech_key)
                    self.assign_workers()

    def draw_tech_menu(self, screen):
        menu_width, menu_height = 600, 400
        menu_x, menu_y = WIDTH // 2 - menu_width // 2, HEIGHT // 2 - menu_height // 2
        pygame.draw.rect(screen, GRAY, (menu_x, menu_y, menu_width, menu_height))

        title = self.tech_font.render("Technologies (Press T to close)", True, BLACK)
        screen.blit(title, (menu_x + 10, menu_y + 10))

        for i, tech_key in enumerate(tech_list):
            tech = TECHNOLOGIES[tech_key]
            if tech_key in self.researched_technologies:
                text = f"{i+1}. {tech_key.replace('_', ' ').title()} - {tech['description']}"
                tech_text = self.tech_font.render(text, True, RED)
            else:
                current_cost = self.get_tech_cost(tech_key)
                text = f"{i+1}. {tech_key.replace('_', ' ').title()} - Cost: ${current_cost} - {tech['description']}"
                tech_text = self.tech_font.render(text, True, BLACK)
            screen.blit(tech_text, (menu_x + 10, menu_y + 40 + i * 30))

    def update_smoke(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_smoke_time >= 200:  # Emit every 200ms
            for building in self.buildings:
                if building["type"] == "factory" and building["active"]:
                    x = building["x"] + BUILDINGS["factory"]["grid_size"][0] * GRID_SIZE - 5
                    y = building["y"] - 10
                    self.smoke_particles.append({
                        "x": x + random.uniform(-2, 2),
                        "y": y,
                        "alpha": 255,
                        "vx": random.uniform(-0.1, 0.1),
                        "vy": -0.5
                    })
            self.last_smoke_time = current_time

        # Update particles
        new_particles = []
        for particle in self.smoke_particles:
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["alpha"] -= 5
            if particle["alpha"] > 0:
                new_particles.append(particle)
        self.smoke_particles = new_particles

    def draw(self, screen):
        # Draw solid background
        screen.fill(GREEN)

        # Apply pollution tint
        if self.pollution > 0:
            tint = min(50, int(self.pollution // 10))
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((100, 100, 50, tint))
            screen.blit(overlay, (0, 0))

        for building in self.buildings:
            specs = BUILDINGS[building["type"]]
            x, y = building["x"], building["y"]
            grid_w, grid_h = specs["grid_size"]
            pixel_w = grid_w * GRID_SIZE
            pixel_h = grid_h * GRID_SIZE
            base_color = specs["color"]
            if not building.get("active", True) and building["type"] != "railroad":
                base_color = tuple(c // 2 for c in base_color)

            if building["type"] == "house":
                # Base structure with gradient
                for i in range(pixel_h // 2):
                    color = (
                        max(0, base_color[0] - i * 2),
                        max(0, base_color[1] - i * 2),
                        max(0, base_color[2] - i * 2)
                    )
                    pygame.draw.rect(screen, color, (x, y + pixel_h//2 + i, pixel_w, 1))
                # Pitched roof
                roof_points = [
                    (x, y + pixel_h//2),
                    (x + pixel_w//2, y),
                    (x + pixel_w, y + pixel_h//2)
                ]
                pygame.draw.polygon(screen, DARK_RED, roof_points)
                # Windows
                pygame.draw.rect(screen, BEIGE, (x + pixel_w//4, y + 3*pixel_h//4, pixel_w//4, pixel_h//8))
                pygame.draw.rect(screen, BEIGE, (x + pixel_w//2, y + 3*pixel_h//4, pixel_w//4, pixel_h//8))

            elif building["type"] == "factory":
                # Base structure with gradient
                for i in range(pixel_h):
                    color = (
                        max(0, base_color[0] - i // 2),
                        max(0, base_color[1] - i // 2),
                        max(0, base_color[2] - i // 2)
                    )
                    pygame.draw.rect(screen, color, (x, y + i, pixel_w, 1))
                # Windows
                for wx in range(x + pixel_w//4, x + pixel_w, pixel_w//3):
                    for wy in range(y + pixel_h//4, y + pixel_h, pixel_h//3):
                        pygame.draw.rect(screen, LIGHT_GRAY, (wx, wy, pixel_w//8, pixel_h//8))
                # Chimneys
                pygame.draw.rect(screen, DARK_GRAY, (x + pixel_w - 10, y - 15, 5, 15))
                pygame.draw.rect(screen, DARK_GRAY, (x + pixel_w - 20, y - 10, 5, 10))

            elif building["type"] == "farm":
                # Field base
                pygame.draw.rect(screen, YELLOW, (x, y, pixel_w, pixel_h))
                # Barn
                barn_w, barn_h = pixel_w // 2, pixel_h // 2
                pygame.draw.rect(screen, RED, (x, y, barn_w, barn_h))
                pygame.draw.polygon(screen, DARK_RED, [
                    (x, y + barn_h),
                    (x + barn_w//2, y + barn_h//2),
                    (x + barn_w, y + barn_h)
                ])
                # Static crops
                crop_color = GREEN if building["active"] else DARK_GREEN
                for cx in range(x + pixel_w//4, x + pixel_w, 5):
                    for cy in range(y + pixel_h//2, y + pixel_h, 5):
                        pygame.draw.line(screen, crop_color,
                                        (cx, cy),
                                        (cx, cy + 5), 1)

            elif building["type"] == "mine":
                # Ground base
                pygame.draw.rect(screen, base_color, (x, y, pixel_w, pixel_h))
                # Mine entrance
                entrance_h = pixel_h // 2
                pygame.draw.rect(screen, BLACK, (x + pixel_w//4, y + pixel_h//2, pixel_w//2, entrance_h))
                # Tracks
                pygame.draw.line(screen, DARK_GRAY, (x + pixel_w//2, y + pixel_h//2), (x + pixel_w//2, y + pixel_h), 3)
                for ty in range(y + pixel_h//2, y + pixel_h, 5):
                    pygame.draw.line(screen, DARK_GRAY, (x + pixel_w//2 - 5, ty), (x + pixel_w//2 + 5, ty), 1)
                # Ore pile
                pygame.draw.circle(screen, GRAY, (x + 3*pixel_w//4, y + pixel_h//4), 5)

            elif building["type"] == "railroad":
                # Check orientation
                grid_x, grid_y = building["grid_x"], building["grid_y"]
                is_vertical = False
                # Check for railroad neighbors above or below
                for b in self.buildings:
                    if b["type"] == "railroad" and b is not building:
                        if (b["grid_x"] == grid_x and 
                            (b["grid_y"] == grid_y - 1 or b["grid_y"] == grid_y + 1)):
                            is_vertical = True
                            break

                # Track bed
                pygame.draw.rect(screen, base_color, (x, y, pixel_w, pixel_h))
                if is_vertical:
                    # Vertical railroad: two vertical rails, horizontal ties
                    pygame.draw.line(screen, BLACK, 
                                    (x + pixel_w//4, y), 
                                    (x + pixel_w//4, y + pixel_h), 2)
                    pygame.draw.line(screen, BLACK, 
                                    (x + 3*pixel_w//4, y), 
                                    (x + 3*pixel_w//4, y + pixel_h), 2)
                    for ty in range(y, y + pixel_h, 5):
                        pygame.draw.line(screen, DARK_BROWN, 
                                        (x + pixel_w//4, ty), 
                                        (x + 3*pixel_w//4, ty), 1)
                else:
                    # Horizontal railroad: two horizontal rails, vertical ties
                    pygame.draw.line(screen, BLACK, 
                                    (x, y + pixel_h//4), 
                                    (x + pixel_w, y + pixel_h//4), 2)
                    pygame.draw.line(screen, BLACK, 
                                    (x, y + 3*pixel_h//4), 
                                    (x + pixel_w, y + 3*pixel_h//4), 2)
                    for tx in range(x, x + pixel_w, 5):
                        pygame.draw.line(screen, DARK_BROWN, 
                                        (tx, y + pixel_h//4), 
                                        (tx, y + 3*pixel_h//4), 1)

        # Draw smoke particles
        for particle in self.smoke_particles:
            smoke_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(smoke_surface, (100, 100, 100, particle["alpha"]), (3, 3), 3)
            screen.blit(smoke_surface, (int(particle["x"]), int(particle["y"])))

        # Draw UI
        resource_text = self.font.render(f"Resources: ${self.resources:.1f}", True, BLACK)
        pollution_text = self.font.render(f"Pollution: {int(self.pollution)}", True, BLACK)
        workers_text = self.font.render(f"Workers: {self.available_workers}/{self.total_workers}", True, BLACK)
        building_text = self.font.render(f"Building: {self.current_building}", True, BLACK)
        
        inst_line1 = self.font.render("1: House  2: Farm  3: Mine  4: Factory  5: Railroad  T: Tech", True, BLACK)
        inst_line2 = self.font.render(
            f"${BUILDINGS['house']['current_cost']},+{HOUSE_CAPACITY}W  "
            f"${BUILDINGS['farm']['current_cost']},{WORKERS_PER_FARM}W  "
            f"${BUILDINGS['mine']['current_cost']},{WORKERS_PER_MINE}W  "
            f"${BUILDINGS['factory']['current_cost']},{WORKERS_PER_FACTORY}W  "
            f"${BUILDINGS['railroad']['current_cost']}",
            True, BLACK
        )

        screen.blit(resource_text, (10, 10))
        screen.blit(pollution_text, (10, 50))
        screen.blit(workers_text, (10, 90))
        screen.blit(building_text, (10, 130))
        screen.blit(inst_line1, (10, HEIGHT - 80))
        screen.blit(inst_line2, (10, HEIGHT - 40))

        if self.tech_menu_open:
            self.draw_tech_menu(screen)

# Game instance
game = CityBuilder()

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not game.tech_menu_open:
            x, y = pygame.mouse.get_pos()
            game.add_building(x, y)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t:
                game.tech_menu_open = not game.tech_menu_open
            elif game.tech_menu_open:
                if event.key == pygame.K_1:
                    game.research_technology(0)
                elif event.key == pygame.K_2:
                    game.research_technology(1)
                elif event.key == pygame.K_3:
                    game.research_technology(2)
                elif event.key == pygame.K_4:
                    game.research_technology(3)
                elif event.key == pygame.K_5:
                    game.research_technology(4)
                elif event.key == pygame.K_6:
                    game.research_technology(5)
                elif event.key == pygame.K_7:
                    game.research_technology(6)
                elif event.key == pygame.K_8:
                    game.research_technology(7)
            else:
                if event.key == pygame.K_1:
                    game.current_building = "house"
                elif event.key == pygame.K_2:
                    game.current_building = "farm"
                elif event.key == pygame.K_3:
                    game.current_building = "mine"
                elif event.key == pygame.K_4:
                    game.current_building = "factory"
                elif event.key == pygame.K_5:
                    game.current_building = "railroad"

    game.assign_workers()
    game.update_pollution()
    game.produce_resources()
    game.update_smoke()  # Update smoke particles
    game.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
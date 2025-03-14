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

def tenement_housing():
    global HOUSE_CAPACITY
    HOUSE_CAPACITY = 7

def steam_pump():
    global WORKERS_PER_HOUSE
    WORKERS_PER_HOUSE = 3

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
    "tenement_housing": {
        "base_cost": 200,
        "effect": tenement_housing,
        "description": "Increases house worker capacity to 7"
    },
    "steam_pump": {
        "base_cost": 150,
        "effect": steam_pump,
        "description": "Improves housing efficiency (placeholder)"
    }
}

tech_list = [
    "bessemer_steel_process", "factory_efficiency",
    "mccormicks_reaper", "advanced_farming",
    "dynamite", "deep_mining",
    "tenement_housing", "steam_pump"
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
        """Find all railroad tiles in the network."""
        railroad_tiles = [(b["grid_x"], b["grid_y"]) for b in self.buildings if b["type"] == "railroad"]
        if not railroad_tiles:
            return set()
        
        # Use flood fill to find connected railroads
        visited = set()
        to_visit = [railroad_tiles[0]]
        
        while to_visit:
            x, y = to_visit.pop()
            if (x, y) not in visited:
                visited.add((x, y))
                # Check adjacent tiles (up, down, left, right)
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) in railroad_tiles and (nx, ny) not in visited:
                        to_visit.append((nx, ny))
        
        return visited

    def is_adjacent_to_railroad(self, building):
        """Check if a building is adjacent to any railroad tile."""
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
                base_yield = 10  # Base value before tech
                bonus = base_yield * 0.01 * railroad_count if self.is_adjacent_to_railroad(factory) else 0
                self.resources += FACTORY_PRODUCTION + bonus
            self.last_factory_production = current_time
            if active_factories:
                produced = True

        if current_time - self.last_farm_production >= 10000:
            active_farms = [b for b in self.buildings if b["type"] == "farm" and b["active"]]
            for farm in active_farms:
                base_yield = 20  # Base value before tech
                bonus = base_yield * 0.01 * railroad_count if self.is_adjacent_to_railroad(farm) else 0
                self.resources += FARM_PRODUCTION + bonus
            self.last_farm_production = current_time
            if active_farms:
                produced = True

        if current_time - self.last_mine_production >= 10000:
            active_mines = [b for b in self.buildings if b["type"] == "mine" and b["active"]]
            for mine in active_mines:
                base_yield = 20  # Base value before tech
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

    def draw(self, screen):
        screen.fill(GREEN)

        for building in self.buildings:
            specs = BUILDINGS[building["type"]]
            x, y = building["x"], building["y"]
            grid_w, grid_h = specs["grid_size"]
            pixel_w = grid_w * GRID_SIZE
            pixel_h = grid_h * GRID_SIZE
            color = specs["color"]
            if not building.get("active", True) and building["type"] != "railroad":
                color = tuple(c // 2 for c in color)

            if building["type"] == "house":
                pygame.draw.rect(screen, color, (x, y + pixel_h//2, pixel_w, pixel_h//2))
                points = [(x, y + pixel_h//2), (x + pixel_w//2, y), (x + pixel_w, y + pixel_h//2)]
                pygame.draw.polygon(screen, RED, points)
            elif building["type"] == "factory":
                pygame.draw.rect(screen, color, (x, y, pixel_w, pixel_h))
                chimney_x = x + pixel_w - 5
                chimney_y = y - 10
                pygame.draw.rect(screen, BLACK, (chimney_x, chimney_y, 5, 10))
                if building["active"]:
                    smoke_x = chimney_x + 2
                    smoke_y = chimney_y - 5
                    pygame.draw.circle(screen, GRAY, (smoke_x, smoke_y), 3)
            elif building["type"] == "farm":
                pygame.draw.rect(screen, color, (x, y, pixel_w, pixel_h))
                wheat_color = GREEN if building["active"] else (0, 100, 0)
                if building["active"]:
                    for i in range(1, 4):
                        pygame.draw.line(screen, wheat_color, 
                                       (x + pixel_w//4*i, y + 2), 
                                       (x + pixel_w//4*i, y + pixel_h - 2), 1)
                else:
                    for i in range(1, 4):
                        pygame.draw.line(screen, wheat_color, 
                                       (x + pixel_w//4*i, y + pixel_h//2), 
                                       (x + pixel_w//4*i, y + pixel_h - 2), 1)
            elif building["type"] == "mine":
                pygame.draw.rect(screen, color, (x, y, pixel_w, pixel_h))
                pygame.draw.line(screen, BLACK, (x, y), (x + pixel_w, y + pixel_h), 1)
                pygame.draw.line(screen, BLACK, (x + pixel_w, y), (x, y + pixel_h), 1)
            elif building["type"] == "railroad":
                pygame.draw.rect(screen, color, (x, y, pixel_w, pixel_h))
                pygame.draw.line(screen, BLACK, (x, y + pixel_h//2), (x + pixel_w, y + pixel_h//2), 2)

        resource_text = self.font.render(f"Resources: ${self.resources:.1f}", True, BLACK)  # Show decimals
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
    game.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
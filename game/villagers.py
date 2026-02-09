"""Villager entities with needs and behavior."""
import random
import math
from .enums import VillagerState
from .constants import (
    HUNGER_RATE, THIRST_RATE, FOOD_RESTORE, WATER_RESTORE,
    STARVATION_DAMAGE, DEHYDRATION_DAMAGE, HEALTH_REGEN,
    VILLAGER_SPEED, VILLAGER_SIZE, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE,
)

NAMES = [
    "Aldric", "Berta", "Conrad", "Daria", "Edric", "Frieda",
    "Gunther", "Hilda", "Igor", "Johanna", "Karl", "Liesa",
    "Magnus", "Nora", "Otto", "Petra", "Rolf", "Sigrid",
    "Theron", "Ursula", "Viktor", "Wanda", "Xander", "Yara",
    "Baldric", "Celeste", "Dietrich", "Elara", "Felix", "Greta",
]


class Villager:
    _next_id = 0

    def __init__(self, world_x, world_y):
        self.id = Villager._next_id
        Villager._next_id += 1
        self.name = random.choice(NAMES)
        self.world_x = world_x
        self.world_y = world_y
        self.hunger = 80.0
        self.thirst = 80.0
        self.health = 100.0
        self.workplace = None
        self.home = None
        self.state = VillagerState.IDLE
        self.target_x = world_x
        self.target_y = world_y
        self.alive = True
        self.eat_cd = 0.0
        self.drink_cd = 0.0
        self.color = (
            random.randint(180, 240),
            random.randint(140, 200),
            random.randint(100, 160),
        )

    def update(self, game_hours, time_mgr, resource_mgr):
        """Update needs, consume resources, and choose behavior."""
        if not self.alive:
            return

        # Deplete needs
        self.hunger = max(0, min(100, self.hunger - HUNGER_RATE * game_hours))
        self.thirst = max(0, min(100, self.thirst - THIRST_RATE * game_hours))
        self.eat_cd = max(0, self.eat_cd - game_hours)
        self.drink_cd = max(0, self.drink_cd - game_hours)

        # Damage from starvation / dehydration
        if self.hunger <= 0:
            self.health -= STARVATION_DAMAGE * game_hours
        if self.thirst <= 0:
            self.health -= DEHYDRATION_DAMAGE * game_hours
        if self.hunger > 50 and self.thirst > 50 and self.health < 100:
            self.health += HEALTH_REGEN * game_hours
        self.health = max(0, min(100, self.health))

        # Death
        if self.health <= 0:
            self.alive = False
            if self.workplace and self in self.workplace.workers:
                self.workplace.workers.remove(self)
            if self.home and self in self.home.residents:
                self.home.residents.remove(self)
            self.workplace = self.home = None
            return

        # Auto-consume food and water when hungry/thirsty
        if self.hunger < 30 and self.eat_cd <= 0:
            if resource_mgr.remove("FOOD", 1):
                self.hunger = min(100, self.hunger + FOOD_RESTORE)
                self.eat_cd = 2.0
        if self.thirst < 30 and self.drink_cd <= 0:
            if resource_mgr.remove("WATER", 1):
                self.thirst = min(100, self.thirst + WATER_RESTORE)
                self.drink_cd = 2.0

        # Behavior based on time of day
        if time_mgr.is_daytime:
            if self.workplace:
                self.state = VillagerState.WORKING
                self.target_x, self.target_y = self.workplace.center_world
            else:
                self.state = VillagerState.IDLE
                # Wander near home
                if random.random() < 0.02 * game_hours:
                    cx = (self.home.center_world[0] if self.home
                          else MAP_WIDTH * TILE_SIZE / 2)
                    cy = (self.home.center_world[1] if self.home
                          else MAP_HEIGHT * TILE_SIZE / 2)
                    self.target_x = cx + random.uniform(-64, 64)
                    self.target_y = cy + random.uniform(-64, 64)
        else:
            if self.home:
                self.state = VillagerState.SLEEPING
                self.target_x, self.target_y = self.home.center_world
            else:
                self.state = VillagerState.IDLE

    def update_movement(self, dt):
        """Move toward target position."""
        if not self.alive:
            return
        dx = self.target_x - self.world_x
        dy = self.target_y - self.world_y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 2:
            speed = VILLAGER_SPEED * dt
            if speed >= dist:
                self.world_x, self.world_y = self.target_x, self.target_y
            else:
                self.world_x += (dx / dist) * speed
                self.world_y += (dy / dist) * speed

    @property
    def needs_summary(self):
        return f"Hunger:{self.hunger:.0f} Thirst:{self.thirst:.0f} HP:{self.health:.0f}"

    @property
    def status_text(self):
        return {
            VillagerState.IDLE: "Idle",
            VillagerState.WORKING: "Working",
            VillagerState.SLEEPING: "Sleeping",
        }.get(self.state, "Unknown")

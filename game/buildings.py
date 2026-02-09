"""Building definitions and runtime instances with condition & maintenance."""
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
from .enums import BuildingCategory, TileType
from .constants import (
    TILE_SIZE,
    MAINTENANCE_COSTS, CONDITION_DECAY_PER_SEASON,
    INACTIVE_CONDITION_THRESHOLD, DEMOLISH_REFUND_RATIO,
    SEASON_PRODUCTION,
)


@dataclass
class BuildingData:
    name: str
    category: BuildingCategory
    size: Tuple[int, int]
    cost: Dict[str, int]
    required_tile: Optional[TileType]
    adjacent_tile: Optional[TileType]
    max_workers: int
    housing_capacity: int
    storage_bonus: int
    production_input: Dict[str, int]
    production_output: Dict[str, int]
    production_interval: float
    color: Tuple[int, int, int]
    description: str


BUILDINGS = {
    "hut": BuildingData(
        name="Hut", category=BuildingCategory.HOUSING, size=(2, 2),
        cost={"WOOD": 20, "STONE": 5}, required_tile=None, adjacent_tile=None,
        max_workers=0, housing_capacity=4, storage_bonus=0,
        production_input={}, production_output={}, production_interval=0,
        color=(139, 90, 43), description="Houses up to 4 villagers",
    ),
    "farm": BuildingData(
        name="Farm", category=BuildingCategory.PRODUCTION, size=(3, 3),
        cost={"WOOD": 25}, required_tile=TileType.FERTILE, adjacent_tile=None,
        max_workers=2, housing_capacity=0, storage_bonus=0,
        production_input={}, production_output={"WHEAT": 3},
        production_interval=1.0,
        color=(180, 150, 50), description="Grows wheat on fertile land",
    ),
    "woodcutter": BuildingData(
        name="Woodcutter", category=BuildingCategory.PRODUCTION, size=(2, 2),
        cost={"WOOD": 10}, required_tile=None, adjacent_tile=TileType.FOREST,
        max_workers=1, housing_capacity=0, storage_bonus=0,
        production_input={}, production_output={"WOOD": 2},
        production_interval=1.0,
        color=(100, 70, 30), description="Cuts wood near forests",
    ),
    "quarry": BuildingData(
        name="Quarry", category=BuildingCategory.PRODUCTION, size=(2, 2),
        cost={"WOOD": 15, "STONE": 5}, required_tile=TileType.STONE,
        adjacent_tile=None, max_workers=2, housing_capacity=0, storage_bonus=0,
        production_input={}, production_output={"STONE": 2},
        production_interval=1.5,
        color=(130, 130, 120), description="Mines stone from rock",
    ),
    "well": BuildingData(
        name="Well", category=BuildingCategory.PRODUCTION, size=(1, 1),
        cost={"WOOD": 10, "STONE": 10}, required_tile=None, adjacent_tile=None,
        max_workers=1, housing_capacity=0, storage_bonus=0,
        production_input={}, production_output={"WATER": 4},
        production_interval=1.0,
        color=(80, 140, 200), description="Draws fresh water",
    ),
    "stockpile": BuildingData(
        name="Stockpile", category=BuildingCategory.STORAGE, size=(2, 2),
        cost={"WOOD": 20, "STONE": 10}, required_tile=None, adjacent_tile=None,
        max_workers=0, housing_capacity=0, storage_bonus=100,
        production_input={}, production_output={}, production_interval=0,
        color=(120, 90, 60), description="Increases storage capacity",
    ),
    "granary": BuildingData(
        name="Granary", category=BuildingCategory.STORAGE, size=(2, 2),
        cost={"WOOD": 15, "STONE": 10}, required_tile=None, adjacent_tile=None,
        max_workers=0, housing_capacity=0, storage_bonus=60,
        production_input={}, production_output={}, production_interval=0,
        color=(180, 140, 60), description="Stores food and grain",
    ),
    "mill": BuildingData(
        name="Mill", category=BuildingCategory.PROCESSING, size=(2, 2),
        cost={"WOOD": 30, "STONE": 15}, required_tile=None, adjacent_tile=None,
        max_workers=1, housing_capacity=0, storage_bonus=0,
        production_input={"WHEAT": 3}, production_output={"FLOUR": 3},
        production_interval=1.5,
        color=(200, 180, 140), description="Grinds wheat into flour",
    ),
    "bakery": BuildingData(
        name="Bakery", category=BuildingCategory.PROCESSING, size=(2, 2),
        cost={"WOOD": 30, "STONE": 15}, required_tile=None, adjacent_tile=None,
        max_workers=1, housing_capacity=0, storage_bonus=0,
        production_input={"FLOUR": 2}, production_output={"FOOD": 4},
        production_interval=1.5,
        color=(210, 170, 110), description="Bakes bread from flour",
    ),
    "hunter": BuildingData(
        name="Hunter Lodge", category=BuildingCategory.PRODUCTION, size=(2, 2),
        cost={"WOOD": 20}, required_tile=None, adjacent_tile=TileType.FOREST,
        max_workers=1, housing_capacity=0, storage_bonus=0,
        production_input={}, production_output={"FOOD": 2},
        production_interval=1.0,
        color=(80, 110, 60), description="Hunts game near forests",
    ),
    "chapel": BuildingData(
        name="Chapel", category=BuildingCategory.SERVICE, size=(2, 2),
        cost={"WOOD": 20, "STONE": 25}, required_tile=None, adjacent_tile=None,
        max_workers=0, housing_capacity=0, storage_bonus=0,
        production_input={}, production_output={}, production_interval=0,
        color=(200, 200, 220), description="Boosts villager morale",
    ),
    "marketplace": BuildingData(
        name="Marketplace", category=BuildingCategory.SERVICE, size=(3, 3),
        cost={"WOOD": 30, "STONE": 20}, required_tile=None, adjacent_tile=None,
        max_workers=0, housing_capacity=0, storage_bonus=40,
        production_input={}, production_output={}, production_interval=0,
        color=(190, 160, 100), description="Increases trade & storage",
    ),
    "tavern": BuildingData(
        name="Tavern", category=BuildingCategory.SERVICE, size=(2, 2),
        cost={"WOOD": 25, "STONE": 15}, required_tile=None, adjacent_tile=None,
        max_workers=1, housing_capacity=0, storage_bonus=0,
        production_input={"FOOD": 2}, production_output={}, production_interval=3.0,
        color=(160, 100, 50), description="Boosts morale, consumes food",
    ),
    "trading_post": BuildingData(
        name="Trading Post", category=BuildingCategory.SERVICE, size=(2, 2),
        cost={"WOOD": 35, "STONE": 25}, required_tile=None, adjacent_tile=None,
        max_workers=1, housing_capacity=0, storage_bonus=30,
        production_input={}, production_output={}, production_interval=0,
        color=(150, 120, 80), description="Enables trade with caravans",
    ),
    "barracks": BuildingData(
        name="Barracks", category=BuildingCategory.MILITARY, size=(3, 2),
        cost={"WOOD": 30, "STONE": 30}, required_tile=None, adjacent_tile=None,
        max_workers=2, housing_capacity=2, storage_bonus=0,
        production_input={}, production_output={}, production_interval=0,
        color=(100, 80, 70), description="Defends against threats",
    ),
}


class BuildingInstance:
    """A placed building on the map."""
    _next_id = 0

    def __init__(self, building_id: str, tile_x: int, tile_y: int):
        self.id = BuildingInstance._next_id
        BuildingInstance._next_id += 1
        self.building_id = building_id
        self.data = BUILDINGS[building_id]
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.workers: list = []
        self.residents: list = []
        self.production_timer = 0.0
        self.active = True
        # Condition & maintenance
        self.condition = 1.0  # 0..1 — goes inactive below threshold
        self.tile_yields: dict = {}  # track resource taken from adjacent tiles

    @property
    def world_x(self):
        return self.tile_x * TILE_SIZE

    @property
    def world_y(self):
        return self.tile_y * TILE_SIZE

    @property
    def pixel_width(self):
        return self.data.size[0] * TILE_SIZE

    @property
    def pixel_height(self):
        return self.data.size[1] * TILE_SIZE

    @property
    def center_world(self):
        return (self.world_x + self.pixel_width / 2,
                self.world_y + self.pixel_height / 2)

    @property
    def is_functional(self):
        """Building works only if condition > threshold."""
        return self.active and self.condition > INACTIVE_CONDITION_THRESHOLD

    def get_tiles(self):
        """Return list of (x, y) tile positions this building occupies."""
        tiles = []
        for dy in range(self.data.size[1]):
            for dx in range(self.data.size[0]):
                tiles.append((self.tile_x + dx, self.tile_y + dy))
        return tiles

    def worker_ratio(self):
        if self.data.max_workers == 0:
            return 1.0
        return len(self.workers) / self.data.max_workers

    def efficiency(self, season_name: str = "Spring", event_prod_mod: float = 1.0,
                   avg_worker_morale: float = 60.0) -> float:
        """Combined efficiency multiplier for this building."""
        base = self.worker_ratio()
        # Season modifier
        seasonal = SEASON_PRODUCTION.get(season_name, {}).get(self.building_id, 1.0)
        # Condition modifier (linear)
        cond = self.condition
        # Morale modifier (0.8 at morale 0, 1.2 at morale 100)
        morale_mod = 0.8 + (avg_worker_morale / 100) * 0.4
        # Event modifier (e.g. drought, bountiful harvest)
        event_mod = event_prod_mod
        return base * seasonal * cond * morale_mod * event_mod

    # ── Maintenance ─────────────────────────────────────
    def apply_maintenance(self, resource_mgr) -> bool:
        """Called once per season. Deduct maintenance cost; decay if unpaid."""
        costs = MAINTENANCE_COSTS.get(self.building_id, {})
        can_pay = all(resource_mgr.has(r, a) for r, a in costs.items())
        if can_pay:
            for r, a in costs.items():
                resource_mgr.remove(r, a)
            # Small repair when maintained
            self.condition = min(1.0, self.condition + 0.05)
            return True
        else:
            self.condition -= CONDITION_DECAY_PER_SEASON
            self.condition = max(0.0, self.condition)
            return False

    def damage(self, amount):
        """Apply condition damage (fire, event, etc.)."""
        self.condition = max(0, self.condition - amount)

    def demolish_refund(self) -> dict:
        """Calculate materials returned on demolition."""
        return {r: max(1, int(a * DEMOLISH_REFUND_RATIO * self.condition))
                for r, a in self.data.cost.items()}

    # ── Production ──────────────────────────────────────
    def update_production(self, game_hours, resource_mgr,
                          season_name="Spring", event_prod_mod=1.0,
                          event_well_mod=1.0):
        """Tick production based on elapsed game hours with efficiency."""
        if not self.is_functional or self.data.production_interval <= 0:
            return None
        if self.data.max_workers > 0 and len(self.workers) == 0:
            return None

        # Average morale of assigned workers
        morale_vals = [w.morale for w in self.workers if hasattr(w, "morale")]
        avg_morale = sum(morale_vals) / len(morale_vals) if morale_vals else 60.0

        eff = self.efficiency(season_name, event_prod_mod, avg_morale)

        self.production_timer += game_hours * eff
        produced = None
        while self.production_timer >= self.data.production_interval:
            self.production_timer -= self.data.production_interval
            # Check if we have required inputs
            can_produce = all(
                resource_mgr.get(r) >= a
                for r, a in self.data.production_input.items()
            )
            if can_produce:
                for r, a in self.data.production_input.items():
                    resource_mgr.remove(r, a)
                for r, a in self.data.production_output.items():
                    amount = a
                    # Well modifier from drought
                    if self.building_id == "well":
                        amount = int(amount * event_well_mod)
                    resource_mgr.add(r, amount)
                    produced = produced or {}
                    produced[r] = produced.get(r, 0) + amount
        return produced

    # ── Serialisation ───────────────────────────────────
    def serialise(self) -> dict:
        return {
            "building_id": self.building_id,
            "tile_x": self.tile_x, "tile_y": self.tile_y,
            "condition": round(self.condition, 3),
            "tile_yields": self.tile_yields,
            "production_timer": self.production_timer,
        }

    @classmethod
    def deserialise(cls, data) -> "BuildingInstance":
        b = cls(data["building_id"], data["tile_x"], data["tile_y"])
        b.condition = data.get("condition", 1.0)
        b.tile_yields = data.get("tile_yields", {})
        b.production_timer = data.get("production_timer", 0)
        return b

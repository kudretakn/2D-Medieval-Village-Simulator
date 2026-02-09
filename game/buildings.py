"""Building definitions and runtime instances."""
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
from .enums import BuildingCategory, TileType
from .constants import TILE_SIZE


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

    def update_production(self, game_hours, resource_mgr):
        """Tick production based on elapsed game hours."""
        if not self.active or self.data.production_interval <= 0:
            return
        if self.data.max_workers > 0 and len(self.workers) == 0:
            return
        self.production_timer += game_hours * self.worker_ratio()
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
                    resource_mgr.add(r, a)

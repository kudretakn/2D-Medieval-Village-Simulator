"""Game enumerations."""
from enum import Enum, auto


class TileType(Enum):
    GRASS = "GRASS"
    WATER = "WATER"
    FOREST = "FOREST"
    STONE = "STONE"
    FERTILE = "FERTILE"
    SAND = "SAND"


class ResourceType(Enum):
    WOOD = "WOOD"
    STONE = "STONE"
    FOOD = "FOOD"
    WATER = "WATER"
    GOLD = "GOLD"
    WHEAT = "WHEAT"
    FLOUR = "FLOUR"


class BuildingCategory(Enum):
    PRODUCTION = auto()
    HOUSING = auto()
    STORAGE = auto()
    PROCESSING = auto()


class GameSpeed(Enum):
    PAUSED = 0
    NORMAL = 1
    FAST = 2
    FASTEST = 3


class Season(Enum):
    SPRING = "Spring"
    SUMMER = "Summer"
    AUTUMN = "Autumn"
    WINTER = "Winter"


class VillagerState(Enum):
    IDLE = auto()
    WORKING = auto()
    SLEEPING = auto()

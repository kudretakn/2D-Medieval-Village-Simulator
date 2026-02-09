"""Game constants and configuration."""

# ── Screen ───────────────────────────────────────────────
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
GAME_TITLE = "Medieval Village Simulator"

# ── Map ──────────────────────────────────────────────────
MAP_WIDTH = 50
MAP_HEIGHT = 50
TILE_SIZE = 32

# ── Camera ───────────────────────────────────────────────
CAMERA_PAN_SPEED = 400
ZOOM_MIN = 0.5
ZOOM_MAX = 3.0
ZOOM_STEP = 0.15
CAMERA_SMOOTHING = 10.0        # lerp speed for zoom
CAMERA_SHAKE_DECAY = 8.0       # how fast shake dies down
CAMERA_SHAKE_INTENSITY = 3.0   # max pixel offset
CAMERA_SHAKE_AMPLITUDE = 3.0   # alias for code clarity
CAMERA_SHAKE_FREQ = 25.0       # oscillations per second

# ── UI Layout ────────────────────────────────────────────
UI_TOP_HEIGHT = 70
UI_RIGHT_WIDTH = 220
UI_BOTTOM_HEIGHT = 60
MAP_VIEW_X = 0
MAP_VIEW_Y = UI_TOP_HEIGHT
MAP_VIEW_W = SCREEN_WIDTH - UI_RIGHT_WIDTH
MAP_VIEW_H = SCREEN_HEIGHT - UI_TOP_HEIGHT - UI_BOTTOM_HEIGHT

# ── Tile colours ─────────────────────────────────────────
TILE_COLORS = {
    "GRASS": (76, 153, 0),
    "WATER": (51, 119, 204),
    "FOREST": (34, 102, 34),
    "STONE": (148, 148, 140),
    "FERTILE": (102, 178, 51),
    "SAND": (210, 190, 140),
    "DEPLETED": (115, 105, 85),
}

# ── Medieval UI palette ──────────────────────────────────
UI_BG = (45, 30, 20)
UI_PANEL = (60, 42, 28)
UI_PANEL_LIGHT = (80, 58, 38)
UI_BORDER = (160, 120, 60)
UI_TEXT = (240, 220, 180)
UI_TEXT_DIM = (180, 160, 120)
UI_ACCENT = (200, 160, 50)
UI_BUTTON = (70, 50, 35)
UI_BUTTON_HOVER = (90, 65, 45)
UI_BUTTON_ACTIVE = (110, 80, 50)
UI_RED = (180, 50, 50)
UI_GREEN = (60, 160, 60)

# ── Resource display colours ─────────────────────────────
RESOURCE_COLORS = {
    "WOOD": (139, 90, 43),
    "STONE": (160, 160, 160),
    "FOOD": (200, 80, 80),
    "WATER": (80, 150, 220),
    "GOLD": (255, 215, 0),
    "WHEAT": (220, 190, 80),
    "FLOUR": (240, 230, 210),
    "BREAD": (210, 160, 90),
}

# ── Game balance ─────────────────────────────────────────
DAY_LENGTH_SECONDS = 240.0
HOURS_PER_DAY = 24
DAYS_PER_SEASON = 30

# ── Starting resources ───────────────────────────────────
STARTING_RESOURCES = {
    "WOOD": 100,
    "STONE": 40,
    "FOOD": 50,
    "WATER": 50,
    "GOLD": 0,
    "WHEAT": 0,
    "FLOUR": 0,
}

STARTING_VILLAGERS = 3
MAX_POPULATION_BASE = 0
POPULATION_PER_HUT = 4

# ── Villager needs ───────────────────────────────────────
HUNGER_RATE = 4.5
THIRST_RATE = 6.0
FOOD_RESTORE = 40.0
WATER_RESTORE = 50.0
STARVATION_DAMAGE = 8.0
DEHYDRATION_DAMAGE = 12.0
HEALTH_REGEN = 2.0

# ── Morale ───────────────────────────────────────────────
MORALE_BASE = 60.0
MORALE_HOMELESS_PENALTY = 15.0       # penalty to target morale
MORALE_HUNGRY_PENALTY = 12.0         # when hunger < 20
MORALE_THIRSTY_PENALTY = 10.0        # when thirst < 20
MORALE_SICK_PENALTY = 15.0           # when health < 40
MORALE_SOCIAL_BONUS = 3.0            # per nearby friend (max 3)
MORALE_TRAIT_DRIFT = 0.05            # smooth lerp per update
MORALE_FED_BONUS = 1.0               # when hunger > 70
MORALE_HOUSED_BONUS = 0.5            # per game-hour if housed
MORALE_FRIEND_DEATH_PENALTY = -20.0  # instant on friend death
MORALE_DECAY_TOWARD_BASE = 0.3       # per game-hour, regress toward base
MORALE_EMIGRATION_THRESHOLD = 15.0   # below this, villager warns
EMIGRATION_GRACE_DAYS = 3.0          # days of warning before leaving
EMIGRATION_LEAVE_HOURS = EMIGRATION_GRACE_DAYS * HOURS_PER_DAY

# ── Immigration ──────────────────────────────────────────
IMMIGRATION_CHECK_HOURS = 12
IMMIGRATION_MIN_FOOD = 15
IMMIGRATION_MIN_WATER = 15
IMMIGRATION_MIN_HOUSING = 1

# ── Win / Lose ───────────────────────────────────────────
WIN_POPULATION = 150

# ── Day / Night ──────────────────────────────────────────
DAWN_HOUR = 6
DAY_HOUR = 8
DUSK_HOUR = 18
NIGHT_HOUR = 20

# ── Villager ─────────────────────────────────────────────
VILLAGER_SPEED = 60.0
VILLAGER_SIZE = 12

# ── Seasonal production multipliers ──────────────────────
# Keys are building_id.  Missing keys default to 1.0.
SEASON_PRODUCTION = {
    "Spring": {"farm": 0.8, "hunter": 1.0, "woodcutter": 1.0, "quarry": 1.0},
    "Summer": {"farm": 1.2, "hunter": 1.0, "woodcutter": 1.0, "quarry": 1.0},
    "Autumn": {"farm": 1.4, "hunter": 0.8, "woodcutter": 1.1, "quarry": 1.0},
    "Winter": {"farm": 0.0, "hunter": 0.5, "woodcutter": 0.7, "quarry": 0.8},
}

# ── Seasonal need modifiers ──────────────────────────────
SEASON_HUNGER_MULT = {"Spring": 1.0, "Summer": 1.0, "Autumn": 1.0, "Winter": 1.2}
SEASON_THIRST_MULT = {"Spring": 1.0, "Summer": 1.3, "Autumn": 1.0, "Winter": 0.9}

# Winter heating: wood per villager per game-hour
WINTER_HEATING_WOOD_PER_HOUR = 0.02
WINTER_NO_HEAT_HEALTH_DAMAGE = 3.0   # per game-hour if no wood

# ── Building maintenance (resource per season) ───────────
MAINTENANCE_COSTS = {
    "hut": {"WOOD": 2},
    "farm": {"WOOD": 1},
    "woodcutter": {"WOOD": 1},
    "quarry": {"STONE": 1},
    "well": {"STONE": 1},
    "stockpile": {"WOOD": 1},
    "granary": {"WOOD": 1, "STONE": 1},
    "mill": {"WOOD": 2, "STONE": 1},
    "bakery": {"WOOD": 2},
    "hunter": {"WOOD": 1},
}

CONDITION_DECAY_PER_SEASON = 0.20     # out of 1.0 when maintenance missed
INACTIVE_CONDITION_THRESHOLD = 0.25   # building stops working below this
DEMOLISH_REFUND_RATIO = 0.4

# ── Tile depletion / regrowth ────────────────────────────
FOREST_YIELD_PER_TILE = 60.0      # total wood before tile depletes
STONE_YIELD_PER_TILE = 80.0       # total stone before tile depletes
FERTILITY_DEPLETION_PER_SEASON = 0.06
FERTILITY_FALLOW_RECOVERY = 0.15  # per season when no workers
FOREST_REGROWTH_CHANCE = 0.06     # per season, if adjacent to ≥2 forest tiles

# ── Food spoilage (fraction lost per season) ─────────────
SPOILAGE_RATES = {
    "FOOD": 0.05,
    "WHEAT": 0.03,
    "FLOUR": 0.02,
}
SPOILAGE_GRANARY_MULT = 0.3       # granary reduces spoilage to 30%

# ── Villager traits ──────────────────────────────────────
TRAITS = {
    "hardworking":  {"work_speed": 0.20, "morale_offset": 3.0, "opposite": "lazy"},
    "lazy":         {"work_speed": -0.25, "morale_offset": -2.0, "opposite": "hardworking"},
    "glutton":      {"hunger_mult": 0.40, "opposite": "frugal"},
    "frugal":       {"hunger_mult": -0.20, "opposite": "glutton"},
    "tough":        {"health_regen_bonus": 1.0, "opposite": "sickly"},
    "sickly":       {"health_regen_bonus": -0.8, "opposite": "tough"},
    "social":       {"morale_offset": 5.0, "opposite": "loner"},
    "loner":        {"morale_offset": -3.0, "speed_mult": 0.05, "opposite": "social"},
    "skilled":      {"skill_gain": 0.50, "opposite": "clumsy"},
    "clumsy":       {"skill_gain": -0.40, "opposite": "skilled"},
}

# ── Skill system ─────────────────────────────────────────
SKILL_HOURS_PER_LEVEL = 24.0   # game-hours of work per +1% efficiency
SKILL_MAX_BONUS = 0.20          # cap at +20%

# ── Village levels ───────────────────────────────────────
VILLAGE_LEVELS = [
    # (level, name, pop_req, building_req, unlocked building ids)
    (1, "Camp",    0,  0, ["hut", "farm", "woodcutter", "hunter", "well", "stockpile"]),
    (2, "Hamlet",  8,  3, ["quarry", "granary"]),
    (3, "Village", 18, 6, ["mill", "bakery", "chapel", "marketplace"]),
    (4, "Town",    35, 10, ["tavern", "trading_post", "barracks"]),
    (5, "City",    60, 15, ["church", "aqueduct"]),
]

# ── Random events ────────────────────────────────────────
EVENT_CHECK_INTERVAL_HOURS = 48.0  # check for new events every 2 days

# ── Trade ────────────────────────────────────────────────
MERCHANT_INTERVAL_SEASONS = 2    # merchant arrives every N seasons
MERCHANT_DURATION_DAYS = 3       # stays for N game-days

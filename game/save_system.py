"""Save / Load system — JSON serialisation of full game state."""
import json
import os

SAVE_DIR = os.path.join(os.path.expanduser("~"), ".medieval_village")
SAVE_FILE = os.path.join(SAVE_DIR, "savegame.json")


def ensure_save_dir():
    os.makedirs(SAVE_DIR, exist_ok=True)


def save_game(game) -> str:
    """Serialise the full game state to JSON file. Returns filepath."""
    ensure_save_dir()
    state = {
        "version": 2,
        "grid_seed": game.grid.seed,
        "time": {
            "hour": game.time_mgr.game_hour,
            "day": game.time_mgr.day,
            "season_index": game.time_mgr.season_index,
            "year": game.time_mgr.year,
            "total_hours": game.time_mgr.total_hours,
        },
        "resources": dict(game.resource_mgr.resources),
        "storage_capacity": game.resource_mgr.storage_capacity,
        "buildings": [
            {
                "id": b.building_id,
                "x": b.tile_x,
                "y": b.tile_y,
                "timer": b.production_timer,
                "condition": b.condition,
                "tile_yields": b.tile_yields,
            }
            for b in game.buildings
        ],
        "villagers": [
            {
                "name": v.name,
                "x": v.world_x,
                "y": v.world_y,
                "hunger": v.hunger,
                "thirst": v.thirst,
                "health": v.health,
                "morale": v.morale,
                "alive": v.alive,
                "traits": v.traits,
                "skills": v.skills,
                "history": v.history[-20:],  # keep last 20 entries
                "workplace_idx": _building_idx(game, v.workplace),
                "home_idx": _building_idx(game, v.home),
                "emigration_timer": v.emigration_timer,
            }
            for v in game.villagers
        ],
        "tile_meta": game.grid.serialise_metadata(),
        "progression": game.progression.serialise(),
        "events": game.event_system.serialise(),
        "immigration_timer": game.immigration_timer,
        "stats": game.stats,
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(state, f, indent=1)
    return SAVE_FILE


def load_game(game) -> bool:
    """Deserialise game state from JSON file. Returns True on success."""
    if not os.path.exists(SAVE_FILE):
        return False
    try:
        with open(SAVE_FILE, "r") as f:
            state = json.load(f)
    except (json.JSONDecodeError, IOError):
        return False

    if state.get("version", 0) < 2:
        return False  # incompatible save

    from .grid import Grid
    from .buildings import BuildingInstance, BUILDINGS
    from .villagers import Villager
    from .time_manager import TimeManager
    from .resources import ResourceManager

    # Grid with same seed
    game.grid = Grid(seed=state["grid_seed"])
    game.grid.deserialise_metadata(state.get("tile_meta", {}))

    # Time
    t = state["time"]
    game.time_mgr.game_hour = t["hour"]
    game.time_mgr.day = t["day"]
    game.time_mgr.season_index = t["season_index"]
    game.time_mgr.year = t["year"]
    game.time_mgr.total_hours = t["total_hours"]

    # Resources
    game.resource_mgr.resources = state["resources"]
    game.resource_mgr.storage_capacity = state.get("storage_capacity", 200)

    # Buildings
    game.buildings = []
    BuildingInstance._next_id = 0
    for bd in state["buildings"]:
        if bd["id"] not in BUILDINGS:
            continue
        b = BuildingInstance(bd["id"], bd["x"], bd["y"])
        b.production_timer = bd.get("timer", 0)
        b.condition = bd.get("condition", 1.0)
        b.tile_yields = bd.get("tile_yields", {})
        game.buildings.append(b)
        game._cache_building_sprite(b)

    # Villagers
    game.villagers = []
    Villager._next_id = 0
    for vd in state["villagers"]:
        v = Villager(vd["x"], vd["y"])
        v.name = vd["name"]
        v.hunger = vd["hunger"]
        v.thirst = vd["thirst"]
        v.health = vd["health"]
        v.morale = vd.get("morale", 60.0)
        v.alive = vd["alive"]
        v.traits = vd.get("traits", [])
        v.skills = vd.get("skills", {})
        v.history = vd.get("history", [])
        v.emigration_timer = vd.get("emigration_timer", 0.0)
        # Restore workplace/home references
        wi = vd.get("workplace_idx")
        if wi is not None and 0 <= wi < len(game.buildings):
            v.workplace = game.buildings[wi]
            game.buildings[wi].workers.append(v)
        hi = vd.get("home_idx")
        if hi is not None and 0 <= hi < len(game.buildings):
            v.home = game.buildings[hi]
            game.buildings[hi].residents.append(v)
        game.villagers.append(v)
        game._cache_villager_sprite(v)

    # Progression & events
    game.progression.deserialise(state.get("progression", {}))
    game.event_system.deserialise(state.get("events", {}))
    game.immigration_timer = state.get("immigration_timer", 0)
    game.stats = state.get("stats", _default_stats())

    # Rebuild tile surface
    game._build_tile_surface()

    return True


def has_save() -> bool:
    return os.path.exists(SAVE_FILE)


def delete_save():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)


def _building_idx(game, building):
    """Get the index of a building in game.buildings, or None."""
    if building is None:
        return None
    try:
        return game.buildings.index(building)
    except ValueError:
        return None


def _default_stats():
    return {
        "total_born": 0,
        "total_died": 0,
        "total_emigrated": 0,
        "buildings_built": 0,
        "buildings_demolished": 0,
    }

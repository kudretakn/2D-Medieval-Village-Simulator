"""Grid and map generation with value noise + tile metadata."""
import random
from .enums import TileType
from .constants import (
    MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, TILE_COLORS,
    FOREST_YIELD_PER_TILE, STONE_YIELD_PER_TILE,
    FERTILITY_DEPLETION_PER_SEASON, FERTILITY_FALLOW_RECOVERY,
    FOREST_REGROWTH_CHANCE,
)


class TileMeta:
    """Per-tile metadata for depletion / regrowth."""
    __slots__ = ("fertility", "remaining_yield", "regrowth_timer")

    def __init__(self, fertility=1.0, remaining_yield=0.0):
        self.fertility = fertility
        self.remaining_yield = remaining_yield
        self.regrowth_timer = 0.0


class Grid:
    def __init__(self, seed=None):
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        self.tiles = []
        self.meta = []   # parallel 2D array of TileMeta
        self.seed = seed
        self.generate(seed)

    def generate(self, seed=None):
        if seed is None:
            seed = random.randint(0, 999999)
        self.seed = seed
        random.seed(seed)

        scale = 7
        noise_w = self.width // scale + 3
        noise_h = self.height // scale + 3
        noise = [[random.random() for _ in range(noise_w)] for _ in range(noise_h)]
        moist = [[random.random() for _ in range(noise_w)] for _ in range(noise_h)]

        self.tiles = []
        self.meta = []
        for y in range(self.height):
            row = []
            mrow = []
            for x in range(self.width):
                h = self._sample(noise, x, y, scale)
                m = self._sample(moist, x, y, scale + 2)

                if h < 0.22:
                    tile = TileType.WATER
                elif h < 0.30:
                    tile = TileType.SAND
                elif h < 0.55:
                    tile = TileType.FERTILE if m > 0.6 else TileType.GRASS
                elif h < 0.75:
                    tile = TileType.FOREST if m > 0.4 else TileType.GRASS
                else:
                    tile = TileType.STONE
                row.append(tile)

                # Set metadata
                tm = TileMeta()
                if tile == TileType.FERTILE:
                    tm.fertility = 0.8 + m * 0.2
                elif tile == TileType.FOREST:
                    tm.remaining_yield = FOREST_YIELD_PER_TILE
                elif tile == TileType.STONE:
                    tm.remaining_yield = STONE_YIELD_PER_TILE
                mrow.append(tm)
            self.tiles.append(row)
            self.meta.append(mrow)

        # Ensure center starting area is buildable
        cx, cy = self.width // 2, self.height // 2
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                tx, ty = cx + dx, cy + dy
                if 0 <= tx < self.width and 0 <= ty < self.height:
                    if self.tiles[ty][tx] == TileType.WATER:
                        self.tiles[ty][tx] = TileType.GRASS

    def _sample(self, noise, x, y, scale):
        """Bilinear interpolation of noise grid."""
        nx, ny = x / scale, y / scale
        ix, iy = int(nx), int(ny)
        fx, fy = nx - ix, ny - iy
        fx = fx * fx * (3 - 2 * fx)
        fy = fy * fy * (3 - 2 * fy)
        v0 = noise[iy][ix] + (noise[iy][ix + 1] - noise[iy][ix]) * fx
        v1 = noise[iy + 1][ix] + (noise[iy + 1][ix + 1] - noise[iy + 1][ix]) * fx
        return v0 + (v1 - v0) * fy

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def get_meta(self, x, y) -> TileMeta | None:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.meta[y][x]
        return None

    def set_tile(self, x, y, new_type: TileType):
        """Change a tile type (for depletion, regrowth, etc.)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = new_type

    def is_buildable(self, x, y):
        tile = self.get_tile(x, y)
        return tile is not None and tile not in (TileType.WATER, TileType.DEPLETED)

    def get_tile_color(self, x, y):
        tile = self.get_tile(x, y)
        if tile:
            return TILE_COLORS.get(tile.value, (100, 100, 100))
        return (0, 0, 0)

    def deplete_resource(self, x, y, amount) -> float:
        """Remove resource yield from a tile. Returns amount actually taken."""
        m = self.get_meta(x, y)
        if m is None:
            return 0.0
        taken = min(amount, m.remaining_yield)
        m.remaining_yield -= taken
        if m.remaining_yield <= 0:
            tile = self.get_tile(x, y)
            if tile == TileType.FOREST:
                self.set_tile(x, y, TileType.GRASS)
            elif tile == TileType.STONE:
                self.set_tile(x, y, TileType.DEPLETED)
        return taken

    def deplete_fertility(self, x, y, amount=None):
        """Reduce fertility on a tile (for farming)."""
        if amount is None:
            amount = FERTILITY_DEPLETION_PER_SEASON
        m = self.get_meta(x, y)
        if m:
            m.fertility = max(0.0, m.fertility - amount)

    def recover_fertility(self, x, y, amount=None):
        """Restore fertility when field is fallow."""
        if amount is None:
            amount = FERTILITY_FALLOW_RECOVERY
        m = self.get_meta(x, y)
        if m:
            m.fertility = min(1.0, m.fertility + amount)

    def season_update(self, changed_tiles_callback=None):
        """Run once per season: regrowth, etc. Returns list of changed (x,y)."""
        changed = []
        for y in range(self.height):
            for x in range(self.width):
                tile = self.get_tile(x, y)
                if tile == TileType.GRASS:
                    # Forest regrowth check
                    adj_forest = 0
                    for dx, dy2 in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        if self.get_tile(x + dx, y + dy2) == TileType.FOREST:
                            adj_forest += 1
                    if adj_forest >= 2 and random.random() < FOREST_REGROWTH_CHANCE:
                        self.set_tile(x, y, TileType.FOREST)
                        m = self.get_meta(x, y)
                        if m:
                            m.remaining_yield = FOREST_YIELD_PER_TILE
                        changed.append((x, y))
        return changed

    def count_adjacent(self, x, y, tile_type) -> int:
        """Count how many of the 8 neighbours match tile_type."""
        count = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if self.get_tile(x + dx, y + dy) == tile_type:
                    count += 1
        return count

    def serialise_metadata(self) -> dict:
        """Serialise tile metadata for save system."""
        data = {}
        for y in range(self.height):
            for x in range(self.width):
                m = self.meta[y][x]
                tile = self.tiles[y][x]
                # Only save non-default metadata
                if (m.fertility < 0.99 or m.remaining_yield != self._default_yield(tile)
                        or tile != self._original_tile_at(x, y)):
                    key = f"{x},{y}"
                    data[key] = {
                        "tile": tile.value,
                        "fert": round(m.fertility, 3),
                        "yield": round(m.remaining_yield, 1),
                    }
        return data

    def deserialise_metadata(self, data: dict):
        """Restore tile metadata from save."""
        type_map = {t.value: t for t in TileType}
        for key, val in data.items():
            parts = key.split(",")
            if len(parts) != 2:
                continue
            x, y = int(parts[0]), int(parts[1])
            if 0 <= x < self.width and 0 <= y < self.height:
                ttype = type_map.get(val.get("tile"))
                if ttype:
                    self.tiles[y][x] = ttype
                m = self.meta[y][x]
                m.fertility = val.get("fert", 1.0)
                m.remaining_yield = val.get("yield", 0.0)

    def _default_yield(self, tile):
        if tile == TileType.FOREST:
            return FOREST_YIELD_PER_TILE
        if tile == TileType.STONE:
            return STONE_YIELD_PER_TILE
        return 0.0

    def _original_tile_at(self, x, y):
        """Approximate — we can't know original without re-generating."""
        return self.tiles[y][x]

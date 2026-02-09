"""Grid and map generation with value noise."""
import random
from .enums import TileType
from .constants import MAP_WIDTH, MAP_HEIGHT, TILE_SIZE, TILE_COLORS


class Grid:
    def __init__(self, seed=None):
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        self.tiles = []
        self.generate(seed)

    def generate(self, seed=None):
        if seed is None:
            seed = random.randint(0, 999999)
        random.seed(seed)

        scale = 7
        noise_w = self.width // scale + 3
        noise_h = self.height // scale + 3
        noise = [[random.random() for _ in range(noise_w)] for _ in range(noise_h)]
        moist = [[random.random() for _ in range(noise_w)] for _ in range(noise_h)]

        self.tiles = []
        for y in range(self.height):
            row = []
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
            self.tiles.append(row)

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
        # Smoothstep
        fx = fx * fx * (3 - 2 * fx)
        fy = fy * fy * (3 - 2 * fy)
        v0 = noise[iy][ix] + (noise[iy][ix + 1] - noise[iy][ix]) * fx
        v1 = noise[iy + 1][ix] + (noise[iy + 1][ix + 1] - noise[iy + 1][ix]) * fx
        return v0 + (v1 - v0) * fy

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def is_buildable(self, x, y):
        tile = self.get_tile(x, y)
        return tile is not None and tile != TileType.WATER

    def get_tile_color(self, x, y):
        tile = self.get_tile(x, y)
        if tile:
            return TILE_COLORS.get(tile.value, (100, 100, 100))
        return (0, 0, 0)

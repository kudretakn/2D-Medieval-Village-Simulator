"""Main game manager — orchestrates all systems and runs the game loop."""
import pygame
import math
import random
from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GAME_TITLE,
    MAP_WIDTH, MAP_HEIGHT, TILE_SIZE,
    MAP_VIEW_X, MAP_VIEW_Y, MAP_VIEW_W, MAP_VIEW_H,
    UI_TOP_HEIGHT, UI_RIGHT_WIDTH,
    UI_GREEN, UI_RED, UI_ACCENT,
    STARTING_VILLAGERS, MAX_POPULATION_BASE, WIN_POPULATION,
    IMMIGRATION_CHECK_HOURS, IMMIGRATION_MIN_FOOD,
    IMMIGRATION_MIN_WATER, IMMIGRATION_MIN_HOUSING,
    VILLAGER_SIZE, DAWN_HOUR, DAY_HOUR, DUSK_HOUR, NIGHT_HOUR,
)
from .enums import GameSpeed
from .camera import Camera
from .grid import Grid
from .buildings import BUILDINGS, BuildingInstance
from .resources import ResourceManager
from .villagers import Villager
from .time_manager import TimeManager
from .ui import UIManager


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(GAME_TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self._reset()

    # ── Reset / New Game ─────────────────────────────────────
    def _reset(self):
        self.camera = Camera()
        self.grid = Grid()
        self.time_mgr = TimeManager()
        self.resource_mgr = ResourceManager()
        self.ui = UIManager(self.screen)
        self.buildings = []
        self.villagers = []
        self.running = True
        self.game_over = False
        self.game_won = False
        self.selected = None
        self.placement_mode = None
        self.immigration_timer = 0.0
        BuildingInstance._next_id = 0
        Villager._next_id = 0

        # Spawn starting villagers near center
        cx, cy = MAP_WIDTH // 2, MAP_HEIGHT // 2
        for _ in range(STARTING_VILLAGERS):
            wx = (cx + random.uniform(-2, 2)) * TILE_SIZE
            wy = (cy + random.uniform(-2, 2)) * TILE_SIZE
            self.villagers.append(Villager(wx, wy))

        # Pre-render tile surface
        self._build_tile_surface()
        # Day/night overlay surface
        self.dn_surface = pygame.Surface((MAP_VIEW_W, MAP_VIEW_H), pygame.SRCALPHA)

    def _build_tile_surface(self):
        """Pre-render the entire tile map to a surface for fast drawing."""
        w, h = MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE
        self.tile_surface = pygame.Surface((w, h))
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                r, g, b = self.grid.get_tile_color(x, y)
                # Subtle per-tile variation
                v = ((x * 7 + y * 13) % 20) - 10
                c = (max(0, min(255, r + v)), max(0, min(255, g + v)),
                     max(0, min(255, b + v)))
                px, py = x * TILE_SIZE, y * TILE_SIZE
                pygame.draw.rect(self.tile_surface, c,
                                 (px, py, TILE_SIZE, TILE_SIZE))
                # Thin grid lines
                pygame.draw.rect(self.tile_surface,
                                 (max(0, r - 20), max(0, g - 20), max(0, b - 20)),
                                 (px, py, TILE_SIZE, TILE_SIZE), 1)

    # ── Main loop ────────────────────────────────────────────
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._render()
        pygame.quit()

    # ── Events ───────────────────────────────────────────────
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN:
                self._on_key(event)
                continue
            if self.ui.handle_event(event, self):
                continue
            self.camera.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._on_click(event)

    def _on_key(self, event):
        k = event.key
        if k == pygame.K_ESCAPE:
            if self.placement_mode:
                self.placement_mode = None
            elif self.game_over or self.game_won:
                self.running = False
            else:
                self.selected = None
        elif k == pygame.K_SPACE:
            self.time_mgr.toggle_pause()
        elif k == pygame.K_b:
            self.ui.build_panel_open = not self.ui.build_panel_open
        elif k == pygame.K_r:
            self._reset()
        elif k == pygame.K_1:
            self.time_mgr.set_speed(GameSpeed.NORMAL)
        elif k == pygame.K_2:
            self.time_mgr.set_speed(GameSpeed.FAST)
        elif k == pygame.K_3:
            self.time_mgr.set_speed(GameSpeed.FASTEST)

    def _on_click(self, event):
        mx, my = event.pos
        if not (MAP_VIEW_X <= mx < MAP_VIEW_X + MAP_VIEW_W and
                MAP_VIEW_Y <= my < MAP_VIEW_Y + MAP_VIEW_H):
            return
        if event.button == 1:
            if self.placement_mode:
                self._try_place(mx, my)
            else:
                self._try_select(mx, my)
        elif event.button == 3:
            self.placement_mode = None
            self.selected = None

    # ── Placement ────────────────────────────────────────────
    def start_placement(self, bid):
        self.placement_mode = bid
        self.selected = None

    def _try_place(self, mx, my):
        tx, ty = self.camera.screen_to_tile(mx, my)
        if self._can_place(self.placement_mode, tx, ty):
            bd = BUILDINGS[self.placement_mode]
            if self.resource_mgr.spend(bd.cost):
                b = BuildingInstance(self.placement_mode, tx, ty)
                self.buildings.append(b)
                self.resource_mgr.update_storage(self.buildings)
                self._auto_assign_workers(b)
                self._auto_assign_housing(b)
                self.ui.add_alert(f"Built {bd.name}")
            else:
                self.ui.add_alert("Not enough resources!")

    def _can_place(self, bid, tx, ty):
        bd = BUILDINGS[bid]
        w, h = bd.size
        # Check every tile the building occupies
        for dy in range(h):
            for dx in range(w):
                cx, cy = tx + dx, ty + dy
                if cx < 0 or cx >= MAP_WIDTH or cy < 0 or cy >= MAP_HEIGHT:
                    return False
                if not self.grid.is_buildable(cx, cy):
                    return False
                if bd.required_tile and self.grid.get_tile(cx, cy) != bd.required_tile:
                    return False
                # Collision with existing buildings
                for b in self.buildings:
                    if (cx, cy) in b.get_tiles():
                        return False
        # Adjacent tile requirement (e.g. woodcutter needs forest nearby)
        if bd.adjacent_tile:
            found = False
            for dy2 in range(-1, h + 1):
                for dx2 in range(-1, w + 1):
                    if 0 <= dx2 < w and 0 <= dy2 < h:
                        continue
                    if self.grid.get_tile(tx + dx2, ty + dy2) == bd.adjacent_tile:
                        found = True
                        break
                if found:
                    break
            if not found:
                return False
        return True

    # ── Selection info ───────────────────────────────────────
    def _try_select(self, mx, my):
        wx, wy = self.camera.screen_to_world(mx, my)
        # Try villagers first (smaller targets)
        for v in self.villagers:
            if v.alive and math.hypot(wx - v.world_x, wy - v.world_y) < VILLAGER_SIZE * 2:
                self.selected = v
                return
        # Try buildings
        for b in self.buildings:
            if (b.world_x <= wx < b.world_x + b.pixel_width and
                    b.world_y <= wy < b.world_y + b.pixel_height):
                self.selected = b
                return
        # Tile info
        tx, ty = self.camera.screen_to_tile(mx, my)
        tile = self.grid.get_tile(tx, ty)
        if tile:
            self.selected = ("tile", tx, ty, tile)

    def get_selection_info(self):
        s = self.selected
        if isinstance(s, BuildingInstance):
            parts = [s.data.name]
            if s.data.max_workers:
                parts.append(f"Workers: {len(s.workers)}/{s.data.max_workers}")
            if s.data.housing_capacity:
                parts.append(f"Residents: {len(s.residents)}/{s.data.housing_capacity}")
            return "  ".join(parts)
        if isinstance(s, Villager):
            return f"{s.name}  [{s.status_text}]  {s.needs_summary}"
        if isinstance(s, tuple) and s[0] == "tile":
            return f"Tile ({s[1]},{s[2]}) - {s[3].value}"
        return None

    def get_selection_detail(self):
        s = self.selected
        if isinstance(s, BuildingInstance):
            if s.data.production_output:
                out = ", ".join(f"{r}:{a}" for r, a in s.data.production_output.items())
                inp = (", ".join(f"{r}:{a}" for r, a in s.data.production_input.items())
                       if s.data.production_input else "None")
                return f"Produces: {out}  |  Requires: {inp}"
            if s.data.storage_bonus:
                return f"Storage bonus: +{s.data.storage_bonus}"
        if isinstance(s, Villager):
            wp = s.workplace.data.name if s.workplace else "None"
            hm = s.home.data.name if s.home else "Homeless"
            return f"Works at: {wp}  |  Home: {hm}"
        return None

    def get_max_population(self):
        return MAX_POPULATION_BASE + sum(b.data.housing_capacity for b in self.buildings)

    # ── Auto-assign workers and housing ──────────────────────
    def _auto_assign_workers(self, building):
        if building.data.max_workers <= 0:
            return
        for v in self.villagers:
            if v.alive and v.workplace is None:
                building.workers.append(v)
                v.workplace = building
                if len(building.workers) >= building.data.max_workers:
                    break

    def _auto_assign_housing(self, building):
        if building.data.housing_capacity <= 0:
            return
        for v in self.villagers:
            if v.alive and v.home is None:
                building.residents.append(v)
                v.home = building
                if len(building.residents) >= building.data.housing_capacity:
                    break

    # ── Immigration ──────────────────────────────────────────
    def _check_immigration(self, gh):
        self.immigration_timer += gh
        if self.immigration_timer < IMMIGRATION_CHECK_HOURS:
            return
        self.immigration_timer = 0
        alive = [v for v in self.villagers if v.alive]
        free = self.get_max_population() - len(alive)
        if (free >= IMMIGRATION_MIN_HOUSING and
                self.resource_mgr.get("FOOD") >= IMMIGRATION_MIN_FOOD and
                self.resource_mgr.get("WATER") >= IMMIGRATION_MIN_WATER):
            cx, cy = MAP_WIDTH // 2, MAP_HEIGHT // 2
            nv = Villager((cx + random.uniform(-3, 3)) * TILE_SIZE,
                          (cy + random.uniform(-3, 3)) * TILE_SIZE)
            self.villagers.append(nv)
            # Auto-assign home
            for b in self.buildings:
                if b.data.housing_capacity > 0 and len(b.residents) < b.data.housing_capacity:
                    b.residents.append(nv)
                    nv.home = b
                    break
            # Auto-assign work
            for b in self.buildings:
                if b.data.max_workers > 0 and len(b.workers) < b.data.max_workers:
                    b.workers.append(nv)
                    nv.workplace = b
                    break
            self.ui.add_alert(f"{nv.name} has joined your village!")

    # ── Update ───────────────────────────────────────────────
    def _update(self, dt):
        if self.game_over or self.game_won:
            return
        self.camera.update(dt)
        gh = self.time_mgr.update(dt)
        if gh > 0:
            for b in self.buildings:
                b.update_production(gh, self.resource_mgr)
            for v in self.villagers:
                v.update(gh, self.time_mgr, self.resource_mgr)
            self._check_immigration(gh)

            # Win/Lose check
            alive = [v for v in self.villagers if v.alive]
            if len(alive) >= WIN_POPULATION:
                self.game_won = True
                self.time_mgr.set_speed(GameSpeed.PAUSED)
            elif len(alive) == 0 and self.time_mgr.total_hours > 1:
                self.game_over = True
                self.time_mgr.set_speed(GameSpeed.PAUSED)

        # Movement runs at real-time (scaled by game speed)
        spd = self.time_mgr.speed_multiplier if self.time_mgr.speed != GameSpeed.PAUSED else 0
        for v in self.villagers:
            v.update_movement(dt * spd)
        self.ui.update(dt)

    # ── Render ───────────────────────────────────────────────
    def _render(self):
        self.screen.fill((0, 0, 0))
        mr = pygame.Rect(MAP_VIEW_X, MAP_VIEW_Y, MAP_VIEW_W, MAP_VIEW_H)
        self.screen.set_clip(mr)
        self._draw_tiles()
        self._draw_buildings()
        self._draw_villagers()
        if self.placement_mode:
            self._draw_ghost()
        self._draw_selection()
        self._draw_daynight()
        self.screen.set_clip(None)
        self.ui.render(self)
        pygame.display.flip()

    def _draw_tiles(self):
        z = self.camera.zoom
        sw = MAP_VIEW_W / z
        sh = MAP_VIEW_H / z
        sx = max(0, min(self.camera.x, MAP_WIDTH * TILE_SIZE - sw))
        sy = max(0, min(self.camera.y, MAP_HEIGHT * TILE_SIZE - sh))
        src = pygame.Rect(int(sx), int(sy), int(sw), int(sh))
        try:
            sub = self.tile_surface.subsurface(src)
            scaled = pygame.transform.scale(sub, (MAP_VIEW_W, MAP_VIEW_H))
            self.screen.blit(scaled, (MAP_VIEW_X, MAP_VIEW_Y))
        except ValueError:
            pass

    def _draw_buildings(self):
        z = self.camera.zoom
        font = self.ui.font_sm
        for b in self.buildings:
            sx, sy = self.camera.world_to_screen(b.world_x, b.world_y)
            sw, sh = b.pixel_width * z, b.pixel_height * z
            r = pygame.Rect(int(sx), int(sy), int(sw), int(sh))
            pygame.draw.rect(self.screen, b.data.color, r)
            pygame.draw.rect(self.screen, (0, 0, 0), r, 2)
            if z >= 0.8:
                lbl = font.render(b.data.name[:10], True, (255, 255, 255))
                self.screen.blit(lbl, lbl.get_rect(center=r.center))

    def _draw_villagers(self):
        z = self.camera.zoom
        for v in self.villagers:
            if not v.alive:
                continue
            sx, sy = self.camera.world_to_screen(v.world_x, v.world_y)
            sz = max(4, int(VILLAGER_SIZE * z))
            pygame.draw.circle(self.screen, v.color, (int(sx), int(sy)), sz)
            pygame.draw.circle(self.screen, (0, 0, 0), (int(sx), int(sy)), sz, 1)
            # Health bar
            if v.health < 100 and z >= 0.7:
                bw = sz * 3
                bx, by = int(sx - bw / 2), int(sy - sz - 6)
                pygame.draw.rect(self.screen, (60, 0, 0), (bx, by, bw, 3))
                hw = int(bw * v.health / 100)
                pygame.draw.rect(self.screen,
                                 UI_GREEN if v.health > 50 else UI_RED,
                                 (bx, by, hw, 3))

    def _draw_ghost(self):
        mx, my = pygame.mouse.get_pos()
        if not (MAP_VIEW_X <= mx < MAP_VIEW_X + MAP_VIEW_W and
                MAP_VIEW_Y <= my < MAP_VIEW_Y + MAP_VIEW_H):
            return
        tx, ty = self.camera.screen_to_tile(mx, my)
        bd = BUILDINGS[self.placement_mode]
        ok = self._can_place(self.placement_mode, tx, ty)
        sx, sy = self.camera.world_to_screen(tx * TILE_SIZE, ty * TILE_SIZE)
        z = self.camera.zoom
        sw = bd.size[0] * TILE_SIZE * z
        sh = bd.size[1] * TILE_SIZE * z
        ghost = pygame.Surface((int(sw), int(sh)), pygame.SRCALPHA)
        ghost.fill((60, 200, 60, 100) if ok else (200, 60, 60, 100))
        self.screen.blit(ghost, (int(sx), int(sy)))
        pygame.draw.rect(self.screen, UI_GREEN if ok else UI_RED,
                         (int(sx), int(sy), int(sw), int(sh)), 2)

    def _draw_selection(self):
        s = self.selected
        if isinstance(s, BuildingInstance):
            sx, sy = self.camera.world_to_screen(s.world_x, s.world_y)
            z = self.camera.zoom
            pygame.draw.rect(self.screen, UI_ACCENT,
                             (int(sx) - 2, int(sy) - 2,
                              int(s.pixel_width * z) + 4,
                              int(s.pixel_height * z) + 4), 3)
        elif isinstance(s, Villager) and s.alive:
            sx, sy = self.camera.world_to_screen(s.world_x, s.world_y)
            sz = max(6, int(VILLAGER_SIZE * self.camera.zoom * 1.5))
            pygame.draw.circle(self.screen, UI_ACCENT, (int(sx), int(sy)), sz, 2)

    def _draw_daynight(self):
        h = self.time_mgr.game_hour
        if DAWN_HOUR <= h < DAY_HOUR:
            t = (h - DAWN_HOUR) / (DAY_HOUR - DAWN_HOUR)
            color = (255, 180, 100, int(60 * (1 - t)))
        elif DAY_HOUR <= h < DUSK_HOUR:
            color = (0, 0, 0, 0)
        elif DUSK_HOUR <= h < NIGHT_HOUR:
            t = (h - DUSK_HOUR) / (NIGHT_HOUR - DUSK_HOUR)
            color = (40, 20, 80, int(80 * t))
        else:
            color = (10, 10, 50, 90)
        self.dn_surface.fill(color)
        self.screen.blit(self.dn_surface, (MAP_VIEW_X, MAP_VIEW_Y))

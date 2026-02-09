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
from .enums import GameSpeed, TileType
from .camera import Camera
from .grid import Grid
from .buildings import BUILDINGS, BuildingInstance
from .resources import ResourceManager
from .villagers import Villager
from .time_manager import TimeManager
from .ui import UIManager
from .sprites import generate_tile_variants, generate_building_sprite, generate_villager_sprite
from .particles import ParticleSystem
from .events import EventSystem
from .progression import ProgressionManager
from .save_system import save_game, load_game, has_save


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
        self.buildings: list[BuildingInstance] = []
        self.villagers: list[Villager] = []
        self.running = True
        self.game_over = False
        self.game_won = False
        self.selected = None
        self.placement_mode = None
        self.immigration_timer = 0.0
        self.particles = ParticleSystem()
        self.particle_timer = 0.0
        self.water_anim_timer = 0.0
        self.water_anim_frame = 0
        BuildingInstance._next_id = 0
        Villager._next_id = 0

        # New systems
        self.event_system = EventSystem()
        self.progression = ProgressionManager()
        self.stats = {"total_born": 0, "total_died": 0, "total_emigrated": 0,
                      "buildings_built": 0, "buildings_demolished": 0}
        self.floating_texts: list[dict] = []   # {x,y,text,color,timer,dy}

        # Ghost sprite caching
        self._ghost_cache_bid = None
        self._ghost_sprite = None

        # Generate visual sprites
        self.tile_variants = generate_tile_variants(8)
        self.building_sprites = {}
        self.villager_sprites = {}

        # Spawn starting villagers near center
        cx, cy = MAP_WIDTH // 2, MAP_HEIGHT // 2
        for _ in range(STARTING_VILLAGERS):
            wx = (cx + random.uniform(-2, 2)) * TILE_SIZE
            wy = (cy + random.uniform(-2, 2)) * TILE_SIZE
            v = Villager(wx, wy)
            self.villagers.append(v)
            self._cache_villager_sprite(v)
            self.stats["total_born"] += 1

        # Pre-render tile surface
        self._build_tile_surface()
        # Day/night overlay surface
        self.dn_surface = pygame.Surface((MAP_VIEW_W, MAP_VIEW_H), pygame.SRCALPHA)

    def _cache_villager_sprite(self, v):
        self.villager_sprites[v.id] = generate_villager_sprite(
            VILLAGER_SIZE * 2, v.color)

    def _cache_building_sprite(self, b):
        self.building_sprites[b.id] = generate_building_sprite(
            b.building_id, b.pixel_width, b.pixel_height)

    def _build_tile_surface(self):
        w, h = MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE
        self.tile_surface = pygame.Surface((w, h))
        self.tile_variant_map = []
        for y in range(MAP_HEIGHT):
            row = []
            for x in range(MAP_WIDTH):
                tile = self.grid.get_tile(x, y)
                if tile is None:
                    row.append(0)
                    continue
                name = tile.value
                variants = self.tile_variants.get(name, [])
                vi = (x * 7 + y * 13) % len(variants) if variants else 0
                row.append(vi)
                if variants:
                    self.tile_surface.blit(variants[vi],
                                          (x * TILE_SIZE, y * TILE_SIZE))
            self.tile_variant_map.append(row)
        self.water_tiles = []
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                tile = self.grid.get_tile(x, y)
                if tile and tile.value == "WATER":
                    self.water_tiles.append((x, y))

    def _refresh_tile(self, x, y):
        """Re-draw a single tile on the tile surface (after depletion/regrowth)."""
        tile = self.grid.get_tile(x, y)
        if tile is None:
            return
        name = tile.value
        variants = self.tile_variants.get(name, [])
        if not variants:
            # Use GRASS variant for DEPLETED
            variants = self.tile_variants.get("GRASS", [])
        if variants:
            vi = (x * 7 + y * 13) % len(variants)
            self.tile_surface.blit(variants[vi], (x * TILE_SIZE, y * TILE_SIZE))

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
        elif k == pygame.K_F5:
            save_game(self)
            self.ui.add_alert("Game saved!")
        elif k == pygame.K_F9:
            if has_save():
                load_game(self)
                self.ui.add_alert("Game loaded!")
            else:
                self.ui.add_alert("No save file found")
        elif k == pygame.K_DELETE or k == pygame.K_x:
            self._try_demolish()

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
        ok, reason = self._can_place(self.placement_mode, tx, ty)
        if ok:
            bd = BUILDINGS[self.placement_mode]
            if self.resource_mgr.spend(bd.cost):
                b = BuildingInstance(self.placement_mode, tx, ty)
                self.buildings.append(b)
                self._cache_building_sprite(b)
                self.resource_mgr.update_storage(self.buildings)
                self._auto_assign_workers(b)
                self._auto_assign_housing(b)
                self.stats["buildings_built"] += 1
                self.ui.add_alert(f"Built {bd.name}")
                # Check progression
                alive = [v for v in self.villagers if v.alive]
                if self.progression.check_level_up(len(alive), len(self.buildings)):
                    self.ui.add_alert(f"Village upgraded to {self.progression.level_name}!")
            else:
                self.ui.add_alert("Not enough resources!")
        else:
            self.ui.add_alert(reason or "Can't build here!")

    def _can_place(self, bid, tx, ty):
        bd = BUILDINGS[bid]
        w, h = bd.size
        # Check unlock
        if not self.progression.is_unlocked(bid):
            return False, f"{bd.name} not yet unlocked"
        for dy in range(h):
            for dx in range(w):
                cx, cy2 = tx + dx, ty + dy
                if cx < 0 or cx >= MAP_WIDTH or cy2 < 0 or cy2 >= MAP_HEIGHT:
                    return False, "Out of bounds"
                if not self.grid.is_buildable(cx, cy2):
                    return False, "Tile not buildable"
                if bd.required_tile and self.grid.get_tile(cx, cy2) != bd.required_tile:
                    return False, f"Requires {bd.required_tile.value} tile"
                for b in self.buildings:
                    if (cx, cy2) in b.get_tiles():
                        return False, "Occupied by building"
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
                return False, f"Must be adjacent to {bd.adjacent_tile.value}"
        return True, ""

    # ── Demolition ───────────────────────────────────────────
    def _try_demolish(self):
        s = self.selected
        if not isinstance(s, BuildingInstance):
            return
        refund = s.demolish_refund()
        for r, a in refund.items():
            self.resource_mgr.add(r, a)
        # Unassign workers & residents
        for w in s.workers:
            w.workplace = None
        for r in s.residents:
            r.home = None
        self.buildings.remove(s)
        self.resource_mgr.update_storage(self.buildings)
        self.stats["buildings_demolished"] += 1
        self.ui.add_alert(f"Demolished {s.data.name}")
        self.selected = None

    # ── Selection info ───────────────────────────────────────
    def _try_select(self, mx, my):
        wx, wy = self.camera.screen_to_world(mx, my)
        for v in self.villagers:
            if v.alive and math.hypot(wx - v.world_x, wy - v.world_y) < VILLAGER_SIZE * 2:
                self.selected = v
                return
        for b in self.buildings:
            if (b.world_x <= wx < b.world_x + b.pixel_width and
                    b.world_y <= wy < b.world_y + b.pixel_height):
                self.selected = b
                return
        tx, ty = self.camera.screen_to_tile(mx, my)
        tile = self.grid.get_tile(tx, ty)
        if tile:
            meta = self.grid.get_meta(tx, ty)
            self.selected = ("tile", tx, ty, tile, meta)

    def get_selection_info(self):
        s = self.selected
        if isinstance(s, BuildingInstance):
            parts = [s.data.name]
            parts.append(f"Condition: {s.condition:.0%}")
            if s.data.max_workers:
                parts.append(f"Workers: {len(s.workers)}/{s.data.max_workers}")
            if s.data.housing_capacity:
                parts.append(f"Residents: {len(s.residents)}/{s.data.housing_capacity}")
            if not s.is_functional:
                parts.append("[INACTIVE]")
            return "  ".join(parts)
        if isinstance(s, Villager):
            return (f"{s.name}  [{s.status_text}]  {s.needs_summary}  "
                    f"Morale:{s.morale:.0f}  Traits: {s.trait_names}")
        if isinstance(s, tuple) and s[0] == "tile":
            _, tx, ty, tile, meta = s
            info = f"Tile ({tx},{ty}) - {tile.value}"
            if meta:
                if tile == TileType.FERTILE:
                    info += f"  Fertility: {meta.fertility:.0%}"
                elif tile in (TileType.FOREST, TileType.STONE):
                    info += f"  Yield left: {meta.remaining_yield:.0f}"
            return info
        return None

    def get_selection_detail(self):
        s = self.selected
        if isinstance(s, BuildingInstance):
            if s.data.production_output:
                out = ", ".join(f"{r}:{a}" for r, a in s.data.production_output.items())
                inp = (", ".join(f"{r}:{a}" for r, a in s.data.production_input.items())
                       if s.data.production_input else "None")
                eff = s.efficiency(self.time_mgr.season_name,
                                   self.event_system.get_production_modifier(s.building_id),
                                   60.0)
                return f"Produces: {out}  |  Requires: {inp}  |  Eff: {eff:.0%}"
            if s.data.storage_bonus:
                return f"Storage bonus: +{s.data.storage_bonus}"
            return s.data.description
        if isinstance(s, Villager):
            wp = s.workplace.data.name if s.workplace else "None"
            hm = s.home.data.name if s.home else "Homeless"
            skills = ", ".join(f"{k}:Lv{s.skill_level(k)}" for k in s.skills if s.skill_level(k) > 0)
            skills = skills or "None"
            return f"Works at: {wp}  |  Home: {hm}  |  Skills: {skills}"
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
            self.stats["total_born"] += 1
            for b in self.buildings:
                if b.data.housing_capacity > 0 and len(b.residents) < b.data.housing_capacity:
                    b.residents.append(nv)
                    nv.home = b
                    break
            for b in self.buildings:
                if b.data.max_workers > 0 and len(b.workers) < b.data.max_workers:
                    b.workers.append(nv)
                    nv.workplace = b
                    break
            self.ui.add_alert(f"{nv.name} has joined your village!")
            self._cache_villager_sprite(nv)

    # ── Floating text ────────────────────────────────────────
    def _add_floating_text(self, wx, wy, text, color=(255, 255, 200)):
        self.floating_texts.append({
            "x": wx, "y": wy, "text": text,
            "color": color, "timer": 1.5, "dy": 0,
        })

    def _update_floating_texts(self, dt):
        for ft in self.floating_texts:
            ft["timer"] -= dt
            ft["dy"] -= 30 * dt  # float upward
        self.floating_texts = [ft for ft in self.floating_texts if ft["timer"] > 0]

    # ── Season change hooks ──────────────────────────────────
    def _on_season_change(self):
        """Called once when season transitions."""
        season = self.time_mgr.season_name
        self.ui.add_alert(f"Season changed to {season}")

        # Building maintenance
        for b in self.buildings:
            paid = b.apply_maintenance(self.resource_mgr)
            if not paid:
                self.ui.add_alert(f"{b.data.name} deteriorating — no maintenance!")

        # Food spoilage
        has_granary = any(b.building_id == "granary" for b in self.buildings)
        losses = self.resource_mgr.apply_spoilage(season, has_granary)
        if losses:
            loss_str = ", ".join(f"{r}: -{a:.0f}" for r, a in losses.items())
            self.ui.add_alert(f"Spoilage: {loss_str}")

        # Tile regrowth
        changed = self.grid.season_update()
        for cx, cy in changed:
            self._refresh_tile(cx, cy)

        # Farm fertility depletion
        for b in self.buildings:
            if b.building_id == "farm" and b.is_functional:
                for tx, ty in b.get_tiles():
                    self.grid.deplete_fertility(tx, ty)

        # Resource rate snapshot
        self.resource_mgr.flush_rates()

    def _on_new_day(self):
        """Called once per in-game day."""
        self.resource_mgr.tick_day()

        # Villager morale update (daily)
        alive = [v for v in self.villagers if v.alive]
        for v in alive:
            v.update_morale(self.buildings, alive)

        # Emigration check
        for v in alive:
            if v.check_emigration(True):
                self._emigrate(v)

    def _emigrate(self, v):
        """Remove a villager who chose to leave."""
        v.alive = False
        if v.workplace and v in v.workplace.workers:
            v.workplace.workers.remove(v)
        if v.home and v in v.home.residents:
            v.home.residents.remove(v)
        v.workplace = v.home = None
        self.stats["total_emigrated"] += 1
        self.ui.add_alert(f"{v.name} left the village (morale too low)")

    # ── Update ───────────────────────────────────────────────
    def _update(self, dt):
        if self.game_over or self.game_won:
            self.particles.update(dt)
            return
        self.camera.update(dt)
        gh = self.time_mgr.update(dt)

        # Season / day hooks
        if self.time_mgr.season_changed_flag:
            self._on_season_change()
        if self.time_mgr.new_day_flag:
            self._on_new_day()

        if gh > 0:
            season = self.time_mgr.season_name
            event_well = self.event_system.get_well_modifier()

            # Building production
            for b in self.buildings:
                event_prod = self.event_system.get_production_modifier(b.building_id)
                produced = b.update_production(
                    gh, self.resource_mgr, season, event_prod, event_well)
                if produced:
                    txt = " ".join(f"+{a}{r[0]}" for r, a in produced.items())
                    self._add_floating_text(
                        b.center_world[0], b.center_world[1] - 10, txt)

            # Villager updates
            for v in self.villagers:
                was_alive = v.alive
                v.update(gh, self.time_mgr, self.resource_mgr)
                if was_alive and not v.alive:
                    self.stats["total_died"] += 1
                    self.ui.add_alert(f"{v.name} has died!")

            self._check_immigration(gh)

            # Event system
            self.event_system.update(gh, self)

            # Win/Lose check
            alive = [v for v in self.villagers if v.alive]
            if len(alive) >= WIN_POPULATION:
                self.game_won = True
                self.time_mgr.set_speed(GameSpeed.PAUSED)
            elif len(alive) == 0 and self.time_mgr.total_hours > 1:
                self.game_over = True
                self.time_mgr.set_speed(GameSpeed.PAUSED)

        # Movement
        spd = self.time_mgr.speed_multiplier if self.time_mgr.speed != GameSpeed.PAUSED else 0
        for v in self.villagers:
            v.update_movement(dt * spd)

        # Particles
        self.particles.update(dt)
        self._update_floating_texts(dt)
        self.particle_timer += dt
        if self.particle_timer > 0.4:
            self.particle_timer = 0
            for b in self.buildings:
                if b.building_id in ("bakery", "mill") and b.is_functional and len(b.workers) > 0:
                    self.particles.emit_smoke(
                        b.world_x + b.pixel_width - 8, b.world_y + 2, count=1)
                if b.data.production_output and b.is_functional and len(b.workers) > 0:
                    if random.random() < 0.3:
                        self.particles.emit_sparkle(
                            b.center_world[0], b.center_world[1],
                            color=(255, 230, 120), count=2)
            if random.random() < 0.3 and self.water_tiles:
                wx, wy = random.choice(self.water_tiles)
                self.particles.emit_water_ripple(
                    wx * TILE_SIZE + TILE_SIZE // 2,
                    wy * TILE_SIZE + TILE_SIZE // 2)

        # Animated water
        self.water_anim_timer += dt
        if self.water_anim_timer > 0.8:
            self.water_anim_timer = 0
            self.water_anim_frame = (self.water_anim_frame + 1) % 8
            water_variants = self.tile_variants.get("WATER", [])
            if water_variants:
                for wx, wy in self.water_tiles:
                    vi = (self.water_anim_frame + wx + wy) % len(water_variants)
                    self.tile_surface.blit(water_variants[vi],
                                          (wx * TILE_SIZE, wy * TILE_SIZE))
        self.ui.update(dt)

    # ── Render ───────────────────────────────────────────────
    def _render(self):
        self.screen.fill((0, 0, 0))
        mr = pygame.Rect(MAP_VIEW_X, MAP_VIEW_Y, MAP_VIEW_W, MAP_VIEW_H)
        self.screen.set_clip(mr)
        self._draw_tiles()
        self._draw_building_shadows()
        self._draw_buildings()
        self._draw_villagers()
        self.particles.draw(self.screen, self.camera)
        self._draw_floating_texts()
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
            scaled = pygame.transform.smoothscale(sub, (MAP_VIEW_W, MAP_VIEW_H))
            self.screen.blit(scaled, (MAP_VIEW_X, MAP_VIEW_Y))
        except ValueError:
            pass

    def _draw_building_shadows(self):
        z = self.camera.zoom
        for b in self.buildings:
            sx, sy = self.camera.world_to_screen(b.world_x, b.world_y)
            sw, sh = b.pixel_width * z, b.pixel_height * z
            shadow = pygame.Surface((int(sw) + 6, 8), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 50),
                                (0, 0, int(sw) + 6, 8))
            self.screen.blit(shadow, (int(sx) - 3, int(sy) + int(sh) - 2))

    def _draw_buildings(self):
        z = self.camera.zoom
        font = self.ui.font_sm
        for b in self.buildings:
            if b.id not in self.building_sprites:
                self._cache_building_sprite(b)
            sprite = self.building_sprites[b.id]
            sx, sy = self.camera.world_to_screen(b.world_x, b.world_y)
            sw, sh = int(b.pixel_width * z), int(b.pixel_height * z)
            if sw < 4 or sh < 4:
                continue
            scaled = pygame.transform.smoothscale(sprite, (sw, sh))
            # Tint red if damaged
            if b.condition < 0.5:
                tint = pygame.Surface((sw, sh), pygame.SRCALPHA)
                tint.fill((255, 60, 60, int(80 * (1 - b.condition * 2))))
                scaled.blit(tint, (0, 0))
            self.screen.blit(scaled, (int(sx), int(sy)))
            if z >= 1.0:
                lbl = font.render(b.data.name[:10], True, (255, 255, 255))
                lbl_shadow = font.render(b.data.name[:10], True, (0, 0, 0))
                cx = int(sx) + sw // 2 - lbl.get_width() // 2
                cy2 = int(sy) - 14
                self.screen.blit(lbl_shadow, (cx + 1, cy2 + 1))
                self.screen.blit(lbl, (cx, cy2))
                # Condition bar
                if b.condition < 0.95:
                    bar_w = sw
                    bar_h = max(2, int(3 * z))
                    bx = int(sx)
                    by = int(sy) + sh + 1
                    self._draw_bar(bx, by, bar_w, bar_h, b.condition,
                                   UI_GREEN if b.condition > 0.5 else UI_RED)

    def _draw_villagers(self):
        z = self.camera.zoom
        for v in self.villagers:
            if not v.alive:
                continue
            sx, sy = self.camera.world_to_screen(v.world_x, v.world_y)
            sprite = self.villager_sprites.get(v.id)
            if sprite is None:
                self._cache_villager_sprite(v)
                sprite = self.villager_sprites[v.id]
            sz = max(8, int(VILLAGER_SIZE * 2 * z))
            scaled = pygame.transform.smoothscale(sprite, (sz, sz))
            self.screen.blit(scaled, (int(sx) - sz // 2, int(sy) - sz // 2))
            if z >= 0.7:
                bar_w = max(8, sz)
                bar_h = max(2, int(3 * z))
                bx = int(sx) - bar_w // 2
                if v.health < 100:
                    by = int(sy) - sz // 2 - bar_h - 2
                    self._draw_bar(bx, by, bar_w, bar_h,
                                   v.health / 100, UI_GREEN if v.health > 50 else UI_RED)
                if v.hunger < 60:
                    by = int(sy) - sz // 2 - (bar_h + 2) * 2
                    self._draw_bar(bx, by, bar_w, bar_h,
                                   v.hunger / 100, (220, 160, 40))

    def _draw_bar(self, x, y, w, h, ratio, color):
        bg = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 120))
        self.screen.blit(bg, (x - 1, y - 1))
        fill_w = max(1, int(w * ratio))
        pygame.draw.rect(self.screen, color, (x, y, fill_w, h))

    def _draw_floating_texts(self):
        font = self.ui.font_sm
        for ft in self.floating_texts:
            sx, sy = self.camera.world_to_screen(ft["x"], ft["y"] + ft["dy"])
            alpha = min(255, int(ft["timer"] / 1.5 * 255))
            color = ft["color"]
            surf = font.render(ft["text"], True, color)
            surf.set_alpha(alpha)
            self.screen.blit(surf, (int(sx) - surf.get_width() // 2, int(sy)))

    def _draw_ghost(self):
        mx, my = pygame.mouse.get_pos()
        if not (MAP_VIEW_X <= mx < MAP_VIEW_X + MAP_VIEW_W and
                MAP_VIEW_Y <= my < MAP_VIEW_Y + MAP_VIEW_H):
            return
        tx, ty = self.camera.screen_to_tile(mx, my)
        bd = BUILDINGS[self.placement_mode]
        ok, _ = self._can_place(self.placement_mode, tx, ty)
        sx, sy = self.camera.world_to_screen(tx * TILE_SIZE, ty * TILE_SIZE)
        z = self.camera.zoom
        sw = int(bd.size[0] * TILE_SIZE * z)
        sh = int(bd.size[1] * TILE_SIZE * z)
        # Cache ghost sprite
        if self._ghost_cache_bid != self.placement_mode:
            self._ghost_cache_bid = self.placement_mode
            self._ghost_sprite = generate_building_sprite(
                self.placement_mode, bd.size[0] * TILE_SIZE, bd.size[1] * TILE_SIZE)
        preview = pygame.transform.smoothscale(self._ghost_sprite, (sw, sh))
        tint = pygame.Surface((sw, sh), pygame.SRCALPHA)
        tint.fill((60, 220, 60, 80) if ok else (220, 60, 60, 80))
        preview.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        preview.set_alpha(160)
        self.screen.blit(preview, (int(sx), int(sy)))
        pygame.draw.rect(self.screen, UI_GREEN if ok else UI_RED,
                         (int(sx), int(sy), sw, sh), 2)

    def _draw_selection(self):
        s = self.selected
        if isinstance(s, BuildingInstance):
            sx, sy = self.camera.world_to_screen(s.world_x, s.world_y)
            z = self.camera.zoom
            w = int(s.pixel_width * z)
            h = int(s.pixel_height * z)
            t = pygame.time.get_ticks() % 1000 / 1000
            alpha = int(180 + 75 * math.sin(t * math.pi * 2))
            border = pygame.Surface((w + 6, h + 6), pygame.SRCALPHA)
            pygame.draw.rect(border, (*UI_ACCENT, alpha),
                             (0, 0, w + 6, h + 6), 3, border_radius=2)
            self.screen.blit(border, (int(sx) - 3, int(sy) - 3))
        elif isinstance(s, Villager) and s.alive:
            sx, sy = self.camera.world_to_screen(s.world_x, s.world_y)
            sz = max(8, int(VILLAGER_SIZE * self.camera.zoom * 2))
            t = pygame.time.get_ticks() % 1000 / 1000
            alpha = int(180 + 75 * math.sin(t * math.pi * 2))
            ring = pygame.Surface((sz * 2 + 4, sz * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ring, (*UI_ACCENT, alpha),
                               (sz + 2, sz + 2), sz, 2)
            self.screen.blit(ring, (int(sx) - sz - 2, int(sy) - sz - 2))

    def _draw_daynight(self):
        h = self.time_mgr.game_hour
        if DAWN_HOUR <= h < DAY_HOUR:
            t = (h - DAWN_HOUR) / (DAY_HOUR - DAWN_HOUR)
            color = (255, 190, 110, int(50 * (1 - t)))
        elif DAY_HOUR <= h < DUSK_HOUR:
            color = (0, 0, 0, 0)
        elif DUSK_HOUR <= h < NIGHT_HOUR:
            t = (h - DUSK_HOUR) / (NIGHT_HOUR - DUSK_HOUR)
            r = int(60 * t)
            g = int(20 * t)
            b2 = int(80 * t)
            color = (r, g, b2, int(70 * t))
        else:
            color = (8, 8, 45, 100)
        self.dn_surface.fill(color)
        self.screen.blit(self.dn_surface, (MAP_VIEW_X, MAP_VIEW_Y))

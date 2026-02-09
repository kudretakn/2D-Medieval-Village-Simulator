"""UI rendering system — top bar, build panel, bottom info, alerts."""
import pygame
import math
from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    UI_TOP_HEIGHT, UI_RIGHT_WIDTH, UI_BOTTOM_HEIGHT,
    MAP_VIEW_W,
    UI_BG, UI_PANEL, UI_PANEL_LIGHT, UI_BORDER, UI_TEXT, UI_TEXT_DIM, UI_ACCENT,
    UI_BUTTON, UI_BUTTON_HOVER, UI_BUTTON_ACTIVE,
    UI_RED, UI_GREEN, RESOURCE_COLORS,
)
from .enums import GameSpeed
from .buildings import BUILDINGS, BuildingInstance
from .villagers import Villager
from .sprites import generate_building_sprite


RESOURCE_ICONS = {
    "WOOD": "W", "STONE": "S", "FOOD": "F",
    "WATER": "~", "GOLD": "G", "WHEAT": "w", "FLOUR": "f", "BREAD": "B",
}


class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.font_lg = pygame.font.SysFont("arial", 20, bold=True)
        self.font_md = pygame.font.SysFont("arial", 16)
        self.font_sm = pygame.font.SysFont("arial", 13)
        self.font_icon = pygame.font.SysFont("arial", 11, bold=True)
        self.build_panel_open = True
        self.build_scroll = 0
        self.build_buttons = []
        self.alerts = []
        self.mini_building_cache = {}
        self._build_resource_icons()

    def _build_resource_icons(self):
        self.res_icons = {}
        for rn, col in RESOURCE_COLORS.items():
            s = pygame.Surface((18, 18), pygame.SRCALPHA)
            pygame.draw.circle(s, col, (9, 9), 8)
            pygame.draw.circle(s, (0, 0, 0, 100), (9, 9), 8, 1)
            letter = RESOURCE_ICONS.get(rn, "?")
            t = self.font_icon.render(letter, True, (255, 255, 255))
            s.blit(t, t.get_rect(center=(9, 9)))
            self.res_icons[rn] = s

    def add_alert(self, msg, dur=5.0):
        self.alerts.append([msg, dur])

    def update(self, dt):
        self.alerts = [[m, t - dt] for m, t in self.alerts if t > dt]

    def handle_event(self, event, game):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.build_panel_open and mx >= SCREEN_WIDTH - UI_RIGHT_WIDTH:
                for rect, bid in self.build_buttons:
                    if rect.collidepoint(mx, my):
                        game.start_placement(bid)
                        return True
            for i, spd in enumerate([GameSpeed.PAUSED, GameSpeed.NORMAL,
                                     GameSpeed.FAST, GameSpeed.FASTEST]):
                bx = 500 + i * 45
                if pygame.Rect(bx, 45, 40, 22).collidepoint(mx, my):
                    game.time_mgr.set_speed(spd)
                    return True
            toggle = pygame.Rect(SCREEN_WIDTH - UI_RIGHT_WIDTH, UI_TOP_HEIGHT,
                                 UI_RIGHT_WIDTH, 30)
            if toggle.collidepoint(mx, my):
                self.build_panel_open = not self.build_panel_open
                return True

        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if mx >= SCREEN_WIDTH - UI_RIGHT_WIDTH and my > UI_TOP_HEIGHT + 30:
                self.build_scroll -= event.y * 30
                self.build_scroll = max(0, self.build_scroll)
                return True
        return False

    def render(self, game):
        self._top_bar(game)
        self._build_panel(game)
        self._bottom_bar(game)
        self._render_alerts()
        self._render_events(game)
        self._game_over(game)

    # ── Top Bar ──────────────────────────────────────────────
    def _top_bar(self, game):
        for row in range(UI_TOP_HEIGHT):
            t = row / UI_TOP_HEIGHT
            c = tuple(int(UI_BG[i] + (UI_PANEL_LIGHT[i] - UI_BG[i]) * t * 0.3) for i in range(3))
            pygame.draw.line(self.screen, c, (0, row), (SCREEN_WIDTH, row))
        pygame.draw.line(self.screen, UI_BORDER,
                         (0, UI_TOP_HEIGHT - 1), (SCREEN_WIDTH, UI_TOP_HEIGHT - 1), 2)
        pygame.draw.line(self.screen, UI_ACCENT, (0, UI_TOP_HEIGHT - 1), (8, UI_TOP_HEIGHT - 1), 3)
        pygame.draw.line(self.screen, UI_ACCENT,
                         (SCREEN_WIDTH - 8, UI_TOP_HEIGHT - 1),
                         (SCREEN_WIDTH, UI_TOP_HEIGHT - 1), 3)

        # Resources with net rates
        x, y = 12, 6
        for rn in ["WOOD", "STONE", "FOOD", "WATER", "WHEAT", "FLOUR"]:
            amt = game.resource_mgr.get(rn)
            col = RESOURCE_COLORS.get(rn, UI_TEXT)
            icon = self.res_icons.get(rn)
            if icon:
                self.screen.blit(icon, (x, y))
            self.screen.blit(self.font_sm.render(rn.capitalize(), True, UI_TEXT_DIM), (x + 20, y))
            # Amount + net rate
            rate = game.resource_mgr.net_rate(rn)
            rate_str = ""
            rate_col = UI_TEXT_DIM
            if rate > 0.01:
                rate_str = f" +{rate:.1f}"
                rate_col = UI_GREEN
            elif rate < -0.01:
                rate_str = f" {rate:.1f}"
                rate_col = UI_RED
            self.screen.blit(self.font_md.render(str(int(amt)), True, col), (x + 20, y + 16))
            if rate_str:
                self.screen.blit(self.font_sm.render(rate_str, True, rate_col), (x + 50, y + 18))
            if rn != "FLOUR":
                pygame.draw.circle(self.screen, UI_BORDER, (x + 80, y + 16), 2)
            x += 85

        # Population, village level, date, time, speed
        y2 = 45
        alive = len([v for v in game.villagers if v.alive])
        mp = game.get_max_population()
        pc = UI_GREEN if alive < mp else UI_ACCENT
        pygame.draw.circle(self.screen, pc, (24, y2 + 8), 5)
        pygame.draw.circle(self.screen, pc, (24, y2 + 2), 3)
        self.screen.blit(self.font_md.render(f"{alive}/{mp}", True, pc), (35, y2))

        # Village level
        lvl_name = game.progression.level_name if hasattr(game, 'progression') else "Camp"
        self.screen.blit(self.font_sm.render(f"[{lvl_name}]", True, UI_ACCENT), (90, y2 + 2))

        self.screen.blit(self.font_md.render(game.time_mgr.date_string, True, UI_TEXT), (170, y2))
        self.screen.blit(self.font_md.render(game.time_mgr.time_string, True, UI_ACCENT), (400, y2))

        for i, (lb, spd) in enumerate([("||", GameSpeed.PAUSED), ("▶", GameSpeed.NORMAL),
                                        ("▶▶", GameSpeed.FAST), ("▶▶▶", GameSpeed.FASTEST)]):
            bx = 480 + i * 48
            active = game.time_mgr.speed == spd
            c = UI_ACCENT if active else UI_BUTTON
            pygame.draw.rect(self.screen, c, (bx, y2, 42, 22), border_radius=4)
            pygame.draw.rect(self.screen, UI_BORDER, (bx, y2, 42, 22), 1, border_radius=4)
            if active:
                glow = pygame.Surface((46, 26), pygame.SRCALPHA)
                pygame.draw.rect(glow, (*UI_ACCENT, 40), (0, 0, 46, 26), border_radius=5)
                self.screen.blit(glow, (bx - 2, y2 - 2))
            t = self.font_sm.render(lb, True, UI_BG if active else UI_TEXT)
            self.screen.blit(t, t.get_rect(center=(bx + 21, y2 + 11)))

    def _get_mini_building(self, bid):
        if bid not in self.mini_building_cache:
            bd = BUILDINGS[bid]
            pw = bd.size[0] * 16
            ph = bd.size[1] * 16
            sprite = generate_building_sprite(bid, pw, ph)
            self.mini_building_cache[bid] = pygame.transform.smoothscale(sprite, (28, 28))
        return self.mini_building_cache[bid]

    # ── Build Panel ──────────────────────────────────────────
    def _build_panel(self, game):
        px = SCREEN_WIDTH - UI_RIGHT_WIDTH
        py = UI_TOP_HEIGHT
        ph = SCREEN_HEIGHT - UI_TOP_HEIGHT
        for row in range(ph):
            t = row / ph
            c = tuple(int(UI_PANEL[i] + (UI_BG[i] - UI_PANEL[i]) * t * 0.4) for i in range(3))
            pygame.draw.line(self.screen, c, (px, py + row), (SCREEN_WIDTH, py + row))
        pygame.draw.line(self.screen, UI_BORDER, (px, py), (px, SCREEN_HEIGHT), 2)

        hdr = "⚒ BUILD  [B]" if self.build_panel_open else "⚒ BUILD ▶"
        pygame.draw.rect(self.screen, UI_PANEL_LIGHT, (px + 1, py, UI_RIGHT_WIDTH - 1, 28))
        pygame.draw.line(self.screen, UI_ACCENT, (px + 8, py + 28), (SCREEN_WIDTH - 8, py + 28), 1)
        self.screen.blit(self.font_md.render(hdr, True, UI_ACCENT), (px + 10, py + 5))

        if not self.build_panel_open:
            return

        self.build_buttons = []
        by = py + 35 - self.build_scroll
        bw, bh, mg = UI_RIGHT_WIDTH - 16, 64, 4
        clip = pygame.Rect(px, py + 30, UI_RIGHT_WIDTH, ph - 30)
        self.screen.set_clip(clip)
        mx, my = pygame.mouse.get_pos()

        for bid, bd in BUILDINGS.items():
            unlocked = game.progression.is_unlocked(bid) if hasattr(game, 'progression') else True
            if by + bh > py + 30 and by < SCREEN_HEIGHT:
                rect = pygame.Rect(px + 8, by, bw, bh)
                self.build_buttons.append((rect, bid))
                hov = rect.collidepoint(mx, my)
                aff = game.resource_mgr.can_afford(bd.cost) and unlocked
                is_active = game.placement_mode == bid
                bg = (UI_BUTTON_ACTIVE if is_active
                      else UI_BUTTON_HOVER if hov else UI_BUTTON)
                pygame.draw.rect(self.screen, bg, rect, border_radius=5)
                border_col = UI_ACCENT if is_active else (UI_GREEN if aff else UI_RED)
                if not unlocked:
                    border_col = (80, 80, 80)
                pygame.draw.rect(self.screen, border_col,
                                 rect, 2 if is_active else 1, border_radius=5)
                mini = self._get_mini_building(bid)
                if not unlocked:
                    # Grey out locked buildings
                    grey_mini = mini.copy()
                    grey_surf = pygame.Surface(grey_mini.get_size(), pygame.SRCALPHA)
                    grey_surf.fill((0, 0, 0, 130))
                    grey_mini.blit(grey_surf, (0, 0))
                    self.screen.blit(grey_mini, (px + 13, by + 4))
                else:
                    self.screen.blit(mini, (px + 13, by + 4))
                name_col = UI_TEXT if unlocked else (100, 100, 100)
                self.screen.blit(self.font_md.render(bd.name, True, name_col), (px + 44, by + 3))
                cx2 = px + 13
                for r, a in bd.cost.items():
                    icon = self.res_icons.get(r)
                    if icon:
                        small_icon = pygame.transform.smoothscale(icon, (12, 12))
                        self.screen.blit(small_icon, (cx2, by + 24))
                    cost_col = UI_TEXT_DIM if aff else UI_RED
                    if not unlocked:
                        cost_col = (80, 80, 80)
                    ct = self.font_sm.render(str(a), True, cost_col)
                    self.screen.blit(ct, (cx2 + 14, by + 24))
                    cx2 += 40
                desc = bd.description[:32] if unlocked else "🔒 Locked"
                self.screen.blit(self.font_sm.render(desc, True, UI_TEXT_DIM),
                                 (px + 13, by + 42))
            by += bh + mg
        self.screen.set_clip(None)

    # ── Bottom Bar ───────────────────────────────────────────
    def _bottom_bar(self, game):
        by = SCREEN_HEIGHT - UI_BOTTOM_HEIGHT
        bw = SCREEN_WIDTH - UI_RIGHT_WIDTH
        for row in range(UI_BOTTOM_HEIGHT):
            t = row / UI_BOTTOM_HEIGHT
            c = tuple(int(UI_PANEL_LIGHT[i] * (1 - t) + UI_BG[i] * t) for i in range(3))
            pygame.draw.line(self.screen, c, (0, by + row), (bw, by + row))
        pygame.draw.line(self.screen, UI_BORDER, (0, by), (bw, by), 2)

        if game.selected:
            info = game.get_selection_info()
            if info:
                self.screen.blit(self.font_md.render(info, True, UI_TEXT), (15, by + 8))
            detail = game.get_selection_detail()
            if detail:
                self.screen.blit(self.font_sm.render(detail, True, UI_TEXT_DIM), (15, by + 32))
            # Demolish hint for buildings
            if isinstance(game.selected, BuildingInstance):
                self.screen.blit(self.font_sm.render(
                    "[DEL/X] Demolish", True, UI_RED), (bw - 130, by + 8))
        else:
            self.screen.blit(self.font_sm.render(
                "Click: select | B: build | Space: pause | WASD: pan | Scroll: zoom",
                True, UI_TEXT_DIM), (15, by + 10))
            self.screen.blit(self.font_sm.render(
                "F5: save | F9: load | DEL: demolish | R: restart",
                True, UI_TEXT_DIM), (15, by + 28))

    # ── Active events banner ─────────────────────────────────
    def _render_events(self, game):
        if not hasattr(game, 'event_system'):
            return
        active = game.event_system.active_events
        if not active:
            return
        y = UI_TOP_HEIGHT + 5
        x = SCREEN_WIDTH - UI_RIGHT_WIDTH - 200
        for ev in active:
            bg = pygame.Surface((190, 20), pygame.SRCALPHA)
            bg.fill((60, 10, 10, 180))
            self.screen.blit(bg, (x, y))
            self.screen.blit(self.font_sm.render(
                f"⚠ {ev.event_type.value}", True, (255, 180, 80)), (x + 4, y + 2))
            y += 24

    # ── Alerts ───────────────────────────────────────────────
    def _render_alerts(self):
        y = UI_TOP_HEIGHT + 10
        for msg, timer in self.alerts[-5:]:
            a = min(1.0, timer)
            c = (255, int(220 * a), int(100 * a))
            txt = self.font_md.render(f"★ {msg}", True, c)
            tw = txt.get_width() + 24
            bg = pygame.Surface((tw, 28), pygame.SRCALPHA)
            bg.fill((30, 15, 5, int(210 * a)))
            pygame.draw.rect(bg, (*UI_ACCENT, int(150 * a)),
                             (0, 0, tw, 28), 1, border_radius=4)
            self.screen.blit(bg, (10, y))
            self.screen.blit(txt, (22, y + 4))
            y += 32

    # ── Game Over / Win ──────────────────────────────────────
    def _game_over(self, game):
        if not game.game_over and not game.game_won:
            return
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 170))
        self.screen.blit(ov, (0, 0))

        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        if game.game_won:
            msg, col = "♕ VICTORY! ♕", UI_ACCENT
            sub = f"Village thrived with {len([v for v in game.villagers if v.alive])} villagers!"
        else:
            msg, col = "☠ GAME OVER ☠", UI_RED
            sub = "All villagers have perished..."

        banner = pygame.Surface((500, 160), pygame.SRCALPHA)
        pygame.draw.rect(banner, (30, 20, 12, 220), (0, 0, 500, 160), border_radius=8)
        pygame.draw.rect(banner, col + (200,), (0, 0, 500, 160), 3, border_radius=8)
        self.screen.blit(banner, (cx - 250, cy - 80))

        t = pygame.font.SysFont("arial", 44, bold=True).render(msg, True, col)
        self.screen.blit(t, t.get_rect(center=(cx, cy - 40)))
        s = self.font_lg.render(sub, True, UI_TEXT)
        self.screen.blit(s, s.get_rect(center=(cx, cy + 5)))
        # Stats
        stats = game.stats
        stat_txt = (f"Born: {stats['total_born']}  Died: {stats['total_died']}  "
                    f"Emigrated: {stats['total_emigrated']}  "
                    f"Built: {stats['buildings_built']}")
        self.screen.blit(self.font_sm.render(stat_txt, True, UI_TEXT_DIM),
                         (cx - 200, cy + 30))
        r = self.font_md.render("Press R to restart  |  ESC to quit", True, UI_TEXT_DIM)
        self.screen.blit(r, r.get_rect(center=(cx, cy + 55)))

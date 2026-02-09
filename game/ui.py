"""UI rendering system — top bar, build panel, bottom info, alerts."""
import pygame
from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    UI_TOP_HEIGHT, UI_RIGHT_WIDTH, UI_BOTTOM_HEIGHT,
    MAP_VIEW_W,
    UI_BG, UI_PANEL, UI_BORDER, UI_TEXT, UI_TEXT_DIM, UI_ACCENT,
    UI_BUTTON, UI_BUTTON_HOVER, UI_BUTTON_ACTIVE,
    UI_RED, UI_GREEN, RESOURCE_COLORS,
)
from .enums import GameSpeed
from .buildings import BUILDINGS, BuildingInstance
from .villagers import Villager


class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.font_lg = pygame.font.SysFont("arial", 20, bold=True)
        self.font_md = pygame.font.SysFont("arial", 16)
        self.font_sm = pygame.font.SysFont("arial", 13)
        self.build_panel_open = True
        self.build_scroll = 0
        self.build_buttons = []
        self.alerts = []

    # ── Alerts ───────────────────────────────────────────────
    def add_alert(self, msg, dur=5.0):
        self.alerts.append([msg, dur])

    def update(self, dt):
        self.alerts = [[m, t - dt] for m, t in self.alerts if t > dt]

    # ── Event handling ───────────────────────────────────────
    def handle_event(self, event, game):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Build panel click
            if self.build_panel_open and mx >= SCREEN_WIDTH - UI_RIGHT_WIDTH:
                for rect, bid in self.build_buttons:
                    if rect.collidepoint(mx, my):
                        game.start_placement(bid)
                        return True
            # Speed buttons
            for i, spd in enumerate([GameSpeed.PAUSED, GameSpeed.NORMAL,
                                     GameSpeed.FAST, GameSpeed.FASTEST]):
                bx = 500 + i * 45
                if pygame.Rect(bx, 45, 40, 22).collidepoint(mx, my):
                    game.time_mgr.set_speed(spd)
                    return True
            # Build panel toggle header
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

    # ── Main render ──────────────────────────────────────────
    def render(self, game):
        self._top_bar(game)
        self._build_panel(game)
        self._bottom_bar(game)
        self._render_alerts()
        self._game_over(game)

    # ── Top Bar ──────────────────────────────────────────────
    def _top_bar(self, game):
        pygame.draw.rect(self.screen, UI_BG, (0, 0, SCREEN_WIDTH, UI_TOP_HEIGHT))
        pygame.draw.line(self.screen, UI_BORDER,
                         (0, UI_TOP_HEIGHT - 1), (SCREEN_WIDTH, UI_TOP_HEIGHT - 1), 2)
        # Resource display
        x, y = 15, 8
        for rn in ["WOOD", "STONE", "FOOD", "WATER", "GOLD", "WHEAT", "FLOUR"]:
            amt = game.resource_mgr.get(rn)
            col = RESOURCE_COLORS.get(rn, UI_TEXT)
            self.screen.blit(self.font_sm.render(rn.capitalize(), True, UI_TEXT_DIM), (x, y))
            self.screen.blit(self.font_md.render(str(int(amt)), True, col), (x, y + 16))
            x += 85

        # Population, date, time, speed buttons
        y2 = 45
        alive = len([v for v in game.villagers if v.alive])
        mp = game.get_max_population()
        pc = UI_GREEN if alive < mp else UI_ACCENT
        self.screen.blit(self.font_md.render(f"Pop: {alive}/{mp}", True, pc), (15, y2))
        self.screen.blit(self.font_md.render(game.time_mgr.date_string, True, UI_TEXT), (150, y2))
        self.screen.blit(self.font_md.render(game.time_mgr.time_string, True, UI_ACCENT), (420, y2))

        for i, (lb, spd) in enumerate([("||", GameSpeed.PAUSED), (">", GameSpeed.NORMAL),
                                        (">>", GameSpeed.FAST), (">>>", GameSpeed.FASTEST)]):
            bx = 500 + i * 45
            active = game.time_mgr.speed == spd
            c = UI_ACCENT if active else UI_BUTTON
            pygame.draw.rect(self.screen, c, (bx, y2, 40, 22), border_radius=3)
            pygame.draw.rect(self.screen, UI_BORDER, (bx, y2, 40, 22), 1, border_radius=3)
            t = self.font_sm.render(lb, True, UI_BG if active else UI_TEXT)
            self.screen.blit(t, t.get_rect(center=(bx + 20, y2 + 11)))

    # ── Build Panel ──────────────────────────────────────────
    def _build_panel(self, game):
        px = SCREEN_WIDTH - UI_RIGHT_WIDTH
        py = UI_TOP_HEIGHT
        ph = SCREEN_HEIGHT - UI_TOP_HEIGHT
        pygame.draw.rect(self.screen, UI_PANEL, (px, py, UI_RIGHT_WIDTH, ph))
        pygame.draw.line(self.screen, UI_BORDER, (px, py), (px, SCREEN_HEIGHT), 2)

        hdr = "BUILD  [B]" if self.build_panel_open else "BUILD >"
        self.screen.blit(self.font_md.render(hdr, True, UI_ACCENT), (px + 10, py + 6))

        if not self.build_panel_open:
            return

        self.build_buttons = []
        by = py + 35 - self.build_scroll
        bw, bh, mg = UI_RIGHT_WIDTH - 20, 60, 5
        clip = pygame.Rect(px, py + 30, UI_RIGHT_WIDTH, ph - 30)
        self.screen.set_clip(clip)
        mx, my = pygame.mouse.get_pos()

        for bid, bd in BUILDINGS.items():
            if by + bh > py + 30 and by < SCREEN_HEIGHT:
                rect = pygame.Rect(px + 10, by, bw, bh)
                self.build_buttons.append((rect, bid))
                hov = rect.collidepoint(mx, my)
                aff = game.resource_mgr.can_afford(bd.cost)
                bg = (UI_BUTTON_ACTIVE if game.placement_mode == bid
                      else UI_BUTTON_HOVER if hov else UI_BUTTON)
                pygame.draw.rect(self.screen, bg, rect, border_radius=4)
                pygame.draw.rect(self.screen, UI_GREEN if aff else UI_RED,
                                 rect, 1, border_radius=4)
                # Color swatch
                pygame.draw.rect(self.screen, bd.color, (px + 15, by + 5, 16, 16))
                # Name
                self.screen.blit(self.font_md.render(bd.name, True, UI_TEXT), (px + 36, by + 4))
                # Cost
                cost_s = "  ".join(f"{r[0]}:{a}" for r, a in bd.cost.items())
                self.screen.blit(self.font_sm.render(cost_s, True,
                                 UI_TEXT_DIM if aff else UI_RED), (px + 15, by + 24))
                # Description
                self.screen.blit(self.font_sm.render(bd.description[:30], True, UI_TEXT_DIM),
                                 (px + 15, by + 40))
            by += bh + mg
        self.screen.set_clip(None)

    # ── Bottom Bar ───────────────────────────────────────────
    def _bottom_bar(self, game):
        by = SCREEN_HEIGHT - UI_BOTTOM_HEIGHT
        bw = SCREEN_WIDTH - UI_RIGHT_WIDTH
        pygame.draw.rect(self.screen, UI_BG, (0, by, bw, UI_BOTTOM_HEIGHT))
        pygame.draw.line(self.screen, UI_BORDER, (0, by), (bw, by), 2)

        if game.selected:
            info = game.get_selection_info()
            if info:
                self.screen.blit(self.font_md.render(info, True, UI_TEXT), (15, by + 8))
            detail = game.get_selection_detail()
            if detail:
                self.screen.blit(self.font_sm.render(detail, True, UI_TEXT_DIM), (15, by + 30))
        else:
            self.screen.blit(self.font_sm.render(
                "Click: select | B: build | Space: pause | WASD: pan | Scroll: zoom | R: restart",
                True, UI_TEXT_DIM), (15, by + 20))

    # ── Alerts ───────────────────────────────────────────────
    def _render_alerts(self):
        y = UI_TOP_HEIGHT + 10
        for msg, timer in self.alerts[-5:]:
            a = min(1.0, timer)
            c = (255, int(220 * a), int(100 * a))
            txt = self.font_md.render(f"! {msg}", True, c)
            bg = pygame.Surface((txt.get_width() + 20, 26), pygame.SRCALPHA)
            bg.fill((40, 20, 10, int(200 * a)))
            self.screen.blit(bg, (10, y))
            self.screen.blit(txt, (20, y + 3))
            y += 30

    # ── Game Over / Win ──────────────────────────────────────
    def _game_over(self, game):
        if not game.game_over and not game.game_won:
            return
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 150))
        self.screen.blit(ov, (0, 0))

        if game.game_won:
            msg, col = "VICTORY!", UI_ACCENT
            sub = f"Village thrived with {len([v for v in game.villagers if v.alive])} villagers!"
        else:
            msg, col = "GAME OVER", UI_RED
            sub = "All villagers have perished..."

        t = pygame.font.SysFont("arial", 48, bold=True).render(msg, True, col)
        self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)))
        s = self.font_lg.render(sub, True, UI_TEXT)
        self.screen.blit(s, s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)))
        r = self.font_md.render("Press R to restart  |  ESC to quit", True, UI_TEXT_DIM)
        self.screen.blit(r, r.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)))

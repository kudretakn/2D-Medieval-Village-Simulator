"""Procedural sprite generation for tiles, buildings, and villagers.

All visuals are generated at startup as pygame Surfaces so rendering
is just blitting pre-made images — fast and good-looking.
"""
import pygame
import random
import math
from .constants import TILE_SIZE


# ═══════════════════════════════════════════════════════════════
#  TILE SPRITES  (32×32 each, multiple variants per type)
# ═══════════════════════════════════════════════════════════════

def _vary(base, amt=15):
    """Return a colour slightly varied from base."""
    return tuple(max(0, min(255, c + random.randint(-amt, amt))) for c in base)


def _draw_grass(surf, base=(66, 148, 20)):
    surf.fill(_vary(base, 8))
    # Grass blade tufts
    for _ in range(random.randint(6, 12)):
        x = random.randint(2, TILE_SIZE - 3)
        y = random.randint(4, TILE_SIZE - 2)
        h = random.randint(3, 7)
        col = _vary((40, 120 + random.randint(0, 40), 10), 10)
        lean = random.randint(-2, 2)
        pygame.draw.line(surf, col, (x, y), (x + lean, y - h), 1)
    # Small flowers occasionally
    if random.random() < 0.3:
        fx = random.randint(5, TILE_SIZE - 5)
        fy = random.randint(5, TILE_SIZE - 5)
        fc = random.choice([(255, 255, 100), (255, 180, 200), (200, 200, 255)])
        pygame.draw.circle(surf, fc, (fx, fy), 2)


def _draw_water(surf, variant=0):
    # Deep blue gradient with wave hints
    base_b = 140 + (variant % 3) * 15
    for row in range(TILE_SIZE):
        wave = int(math.sin(row * 0.4 + variant * 0.7) * 8)
        r = max(0, min(255, 30 + wave))
        g = max(0, min(255, 80 + wave + row // 4))
        b = max(0, min(255, base_b + wave + row // 3))
        pygame.draw.line(surf, (r, g, b), (0, row), (TILE_SIZE, row))
    # Specular highlights
    for _ in range(random.randint(2, 5)):
        hx = random.randint(3, TILE_SIZE - 4)
        hy = random.randint(3, TILE_SIZE - 4)
        hw = random.randint(3, 8)
        pygame.draw.line(surf, (180, 210, 255, 120),
                         (hx, hy), (hx + hw, hy), 1)


def _draw_forest(surf):
    # Forest floor
    surf.fill(_vary((28, 72, 24), 8))
    # Dark undergrowth
    for _ in range(5):
        ux = random.randint(0, TILE_SIZE)
        uy = random.randint(TILE_SIZE // 2, TILE_SIZE)
        pygame.draw.circle(surf, _vary((20, 55, 18), 8), (ux, uy),
                           random.randint(3, 6))
    # Tree trunk
    tx = TILE_SIZE // 2 + random.randint(-4, 4)
    tw = random.randint(3, 5)
    th = random.randint(10, 16)
    trunk_col = _vary((80, 55, 30), 10)
    pygame.draw.rect(surf, trunk_col, (tx - tw // 2, TILE_SIZE - th, tw, th))
    # Canopy layers — lush rounded tree top
    canopy_y = TILE_SIZE - th - 2
    for i in range(3):
        cr = random.randint(8, 13) - i * 2
        cy = canopy_y - i * 3
        col = _vary((25 + i * 15, 90 + i * 20, 15), 12)
        pygame.draw.circle(surf, col, (tx, cy), cr)
    # Highlight on canopy
    pygame.draw.circle(surf, _vary((60, 140, 40), 10),
                       (tx - 2, canopy_y - 7), 4)


def _draw_stone(surf):
    surf.fill(_vary((130, 125, 115), 6))
    # Large rocks
    for _ in range(random.randint(2, 4)):
        rx = random.randint(4, TILE_SIZE - 8)
        ry = random.randint(4, TILE_SIZE - 8)
        rw = random.randint(6, 14)
        rh = random.randint(5, 10)
        rc = _vary((155, 150, 140), 12)
        pygame.draw.ellipse(surf, rc, (rx, ry, rw, rh))
        # Highlight
        pygame.draw.arc(surf, _vary((180, 175, 165), 8),
                        (rx, ry, rw, rh), 0.3, 2.0, 1)
    # Cracks
    for _ in range(random.randint(1, 3)):
        cx = random.randint(3, TILE_SIZE - 3)
        cy = random.randint(3, TILE_SIZE - 3)
        points = [(cx, cy)]
        for _ in range(random.randint(2, 4)):
            cx += random.randint(-4, 4)
            cy += random.randint(-3, 5)
            points.append((cx, cy))
        if len(points) >= 2:
            pygame.draw.lines(surf, _vary((90, 85, 78), 10), False, points, 1)


def _draw_fertile(surf):
    surf.fill(_vary((80, 130, 40), 8))
    # Plowed furrow lines
    for row in range(3, TILE_SIZE - 2, 5):
        col = _vary((65, 110, 30), 6)
        pygame.draw.line(surf, col, (2, row), (TILE_SIZE - 2, row), 1)
    # Small wheat/crop hints
    for _ in range(random.randint(4, 8)):
        wx = random.randint(4, TILE_SIZE - 4)
        wy = random.randint(4, TILE_SIZE - 4)
        wh = random.randint(3, 6)
        col = _vary((160, 180, 50), 15)
        pygame.draw.line(surf, col, (wx, wy), (wx, wy - wh), 1)
        pygame.draw.circle(surf, _vary((190, 170, 60), 10), (wx, wy - wh), 1)


def _draw_sand(surf):
    surf.fill(_vary((210, 190, 140), 8))
    # Sandy dots / grain texture
    for _ in range(random.randint(15, 30)):
        dx = random.randint(0, TILE_SIZE - 1)
        dy = random.randint(0, TILE_SIZE - 1)
        col = _vary((200, 180, 130), 12)
        surf.set_at((dx, dy), col)
    # Small dune ripples
    for _ in range(random.randint(1, 3)):
        ry = random.randint(5, TILE_SIZE - 5)
        rx = random.randint(2, 8)
        rw = random.randint(8, 18)
        pygame.draw.arc(surf, _vary((195, 175, 125), 8),
                        (rx, ry, rw, 6), 0, math.pi, 1)


TILE_GENERATORS = {
    "GRASS": _draw_grass,
    "WATER": _draw_water,
    "FOREST": _draw_forest,
    "STONE": _draw_stone,
    "FERTILE": _draw_fertile,
    "SAND": _draw_sand,
}


def generate_tile_variants(variants_per_type=6):
    """Return dict mapping tile_type_name -> [list of Surface variants]."""
    tiles = {}
    for name, gen_fn in TILE_GENERATORS.items():
        variants = []
        for i in range(variants_per_type):
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            if name == "WATER":
                gen_fn(s, variant=i)
            else:
                gen_fn(s)
            variants.append(s)
        tiles[name] = variants
    return tiles


# ═══════════════════════════════════════════════════════════════
#  BUILDING SPRITES  (sized per building, pre-rendered)
# ═══════════════════════════════════════════════════════════════

def _draw_hut(surf, w, h):
    # Stone/wood foundation
    fw, fh = w, h // 3
    pygame.draw.rect(surf, (120, 90, 55), (0, h - fh, fw, fh))
    # Wooden walls
    wall_col = (150, 110, 65)
    wh = h - fh - h // 3
    wy = h - fh - wh
    pygame.draw.rect(surf, wall_col, (2, wy, w - 4, wh))
    # Horizontal planks
    for py in range(wy, wy + wh, 4):
        pygame.draw.line(surf, (130, 95, 55), (2, py), (w - 3, py), 1)
    # Thatched roof (triangle)
    roof_col = (160, 130, 50)
    points = [(w // 2, 2), (0, wy + 2), (w, wy + 2)]
    pygame.draw.polygon(surf, roof_col, points)
    pygame.draw.polygon(surf, (140, 110, 40), points, 2)
    # Roof thatch lines
    for i in range(3, w - 3, 3):
        ry = 2 + (wy * abs(i - w // 2)) // (w // 2)
        pygame.draw.line(surf, (145, 120, 45), (i, ry + 2), (i, wy), 1)
    # Door
    dw, dh_ = max(6, w // 6), max(10, h // 4)
    dx = w // 2 - dw // 2
    pygame.draw.rect(surf, (90, 60, 30), (dx, h - fh - dh_, dw, dh_))
    pygame.draw.rect(surf, (70, 45, 20), (dx, h - fh - dh_, dw, dh_), 1)
    # Window
    if w > 30:
        pygame.draw.rect(surf, (180, 200, 220), (w // 4 - 3, wy + 4, 6, 6))
        pygame.draw.rect(surf, (70, 45, 20), (w // 4 - 3, wy + 4, 6, 6), 1)
        pygame.draw.line(surf, (70, 45, 20), (w // 4, wy + 4), (w // 4, wy + 10), 1)


def _draw_farm(surf, w, h):
    # Plowed field
    for y in range(0, h, 3):
        col = _vary((100, 75, 45), 8) if (y // 3) % 2 == 0 else _vary((85, 130, 40), 8)
        pygame.draw.line(surf, col, (0, y), (w, y), 2)
    # Crop rows
    for cx in range(6, w - 4, 8):
        for cy in range(6, h - 4, 10):
            stem_h = random.randint(4, 8)
            pygame.draw.line(surf, (50, 130, 30), (cx, cy), (cx, cy - stem_h), 1)
            pygame.draw.circle(surf, _vary((200, 180, 60), 15), (cx, cy - stem_h), 2)
    # Small fences on edges
    for fx in range(0, w, 6):
        pygame.draw.rect(surf, (130, 90, 50), (fx, 0, 2, 4))
        pygame.draw.rect(surf, (130, 90, 50), (fx, h - 4, 2, 4))
    pygame.draw.line(surf, (130, 90, 50), (0, 2), (w, 2), 1)
    pygame.draw.line(surf, (130, 90, 50), (0, h - 2), (w, h - 2), 1)


def _draw_woodcutter(surf, w, h):
    # Log cabin style
    pygame.draw.rect(surf, (95, 65, 35), (0, h // 4, w, h * 3 // 4))
    # Horizontal logs
    for py in range(h // 4, h, 5):
        c = _vary((110, 75, 40), 8)
        pygame.draw.line(surf, c, (0, py), (w, py), 3)
        pygame.draw.line(surf, (80, 55, 28), (0, py + 3), (w, py + 3), 1)
    # Flat roof
    pygame.draw.rect(surf, (80, 55, 30), (0, h // 4 - 4, w, 6))
    pygame.draw.rect(surf, (60, 40, 22), (0, h // 4 - 4, w, 6), 1)
    # Axe icon
    ax, ay = w - 12, 6
    pygame.draw.line(surf, (140, 100, 50), (ax, ay), (ax, ay + 12), 2)
    pygame.draw.polygon(surf, (180, 180, 190),
                        [(ax - 4, ay), (ax + 1, ay), (ax + 1, ay + 5), (ax - 4, ay + 3)])
    # Wood pile
    for i in range(3):
        lx = 4 + i * 7
        ly = h - 8
        pygame.draw.ellipse(surf, _vary((130, 85, 40), 10), (lx, ly, 8, 6))
        pygame.draw.ellipse(surf, (90, 60, 30), (lx, ly, 8, 6), 1)


def _draw_quarry(surf, w, h):
    # Rocky pit
    pygame.draw.rect(surf, (110, 105, 95), (0, 0, w, h))
    # Layered rock faces
    for ly in range(0, h, 6):
        c = _vary((135, 130, 120), 12)
        pygame.draw.rect(surf, c, (2, ly, w - 4, 5))
        pygame.draw.line(surf, (90, 85, 78), (2, ly), (w - 3, ly), 1)
    # Boulders
    for _ in range(3):
        bx = random.randint(4, w - 12)
        by = random.randint(h // 2, h - 8)
        pygame.draw.ellipse(surf, _vary((155, 150, 140), 10), (bx, by, 10, 7))
        pygame.draw.ellipse(surf, (100, 95, 88), (bx, by, 10, 7), 1)
    # Pickaxe icon
    px_, py_ = w // 2, 8
    pygame.draw.line(surf, (120, 80, 40), (px_, py_), (px_, py_ + 10), 2)
    pygame.draw.line(surf, (170, 170, 180), (px_ - 4, py_), (px_ + 4, py_), 2)


def _draw_well(surf, w, h):
    # Stone circular base
    cx, cy = w // 2, h // 2 + 2
    pygame.draw.ellipse(surf, (140, 135, 125), (2, cy - 4, w - 4, h // 2))
    pygame.draw.ellipse(surf, (100, 95, 88), (2, cy - 4, w - 4, h // 2), 2)
    # Water inside
    pygame.draw.ellipse(surf, (60, 120, 190), (5, cy, w - 10, h // 3))
    # Wooden frame
    pygame.draw.line(surf, (110, 75, 40), (4, cy - 6), (4, 2), 2)
    pygame.draw.line(surf, (110, 75, 40), (w - 5, cy - 6), (w - 5, 2), 2)
    pygame.draw.line(surf, (110, 75, 40), (3, 3), (w - 4, 3), 2)
    # Bucket
    pygame.draw.rect(surf, (130, 90, 50), (cx - 3, 5, 6, 5))
    # Rope
    pygame.draw.line(surf, (160, 140, 100), (cx, 3), (cx, 5), 1)


def _draw_stockpile(surf, w, h):
    # Wooden platform
    pygame.draw.rect(surf, (130, 95, 55), (0, h - 6, w, 6))
    for px_ in range(0, w, 4):
        pygame.draw.line(surf, (110, 78, 42), (px_, h - 6), (px_, h), 1)
    # Stacked crates
    for row in range(3):
        for col in range(3):
            cx_ = 4 + col * (w // 3 - 2)
            cy_ = h - 10 - row * 12
            if cy_ < 4:
                break
            cw_, ch_ = w // 3 - 4, 10
            c = _vary((150, 110, 60), 12)
            pygame.draw.rect(surf, c, (cx_, cy_, cw_, ch_))
            pygame.draw.rect(surf, (100, 70, 35), (cx_, cy_, cw_, ch_), 1)
            pygame.draw.line(surf, (100, 70, 35),
                             (cx_ + cw_ // 2, cy_), (cx_ + cw_ // 2, cy_ + ch_), 1)


def _draw_granary(surf, w, h):
    # Stone base
    pygame.draw.rect(surf, (140, 130, 110), (2, h * 2 // 3, w - 4, h // 3))
    # Wooden upper
    pygame.draw.rect(surf, (170, 140, 80), (0, h // 4, w, h * 2 // 3 - h // 4 + 2))
    # Sloped roof
    points = [(w // 2, 2), (-2, h // 4 + 2), (w + 2, h // 4 + 2)]
    pygame.draw.polygon(surf, (140, 80, 35), points)
    pygame.draw.polygon(surf, (110, 60, 25), points, 2)
    # Grain texture
    for _ in range(10):
        gx = random.randint(6, w - 6)
        gy = random.randint(h // 3, h * 2 // 3)
        pygame.draw.circle(surf, _vary((200, 180, 80), 15), (gx, gy), 2)
    # Door
    dw_ = max(6, w // 5)
    pygame.draw.rect(surf, (100, 70, 35), (w // 2 - dw_ // 2, h - h // 3 - 8, dw_, 10))


def _draw_mill(surf, w, h):
    # Tower body
    tw_ = w * 2 // 3
    tx_ = (w - tw_) // 2
    pygame.draw.rect(surf, (190, 175, 150), (tx_, h // 3, tw_, h * 2 // 3))
    pygame.draw.rect(surf, (160, 145, 120), (tx_, h // 3, tw_, h * 2 // 3), 1)
    # Stone texture dots
    for _ in range(6):
        sx_ = random.randint(tx_ + 2, tx_ + tw_ - 3)
        sy_ = random.randint(h // 3 + 2, h - 3)
        pygame.draw.circle(surf, _vary((170, 155, 130), 10), (sx_, sy_), 2)
    # Conical roof
    pts = [(w // 2, 4), (tx_ - 2, h // 3 + 2), (tx_ + tw_ + 2, h // 3 + 2)]
    pygame.draw.polygon(surf, (160, 60, 40), pts)
    pygame.draw.polygon(surf, (130, 45, 30), pts, 1)
    # Windmill blades
    bcx, bcy = w // 2, h // 3 + 2
    blade_len = min(w, h) // 3
    for angle_offset in [0, 90, 180, 270]:
        a = math.radians(angle_offset + 20)
        ex = bcx + int(math.cos(a) * blade_len)
        ey = bcy + int(math.sin(a) * blade_len)
        pygame.draw.line(surf, (180, 160, 130), (bcx, bcy), (ex, ey), 2)
        # Blade shape
        pa = a + 0.25
        px1 = bcx + int(math.cos(pa) * blade_len * 0.7)
        py1 = bcy + int(math.sin(pa) * blade_len * 0.7)
        pygame.draw.polygon(surf, (200, 190, 170),
                            [(bcx, bcy), (ex, ey), (px1, py1)])
    pygame.draw.circle(surf, (120, 80, 50), (bcx, bcy), 3)


def _draw_bakery(surf, w, h):
    # Brick walls
    for by_ in range(h // 4, h, 4):
        offset = 4 if (by_ // 4) % 2 else 0
        for bx_ in range(offset, w, 8):
            c = _vary((185, 120, 80), 12)
            pygame.draw.rect(surf, c, (bx_, by_, 7, 3))
    pygame.draw.rect(surf, (140, 85, 55), (0, h // 4, w, h * 3 // 4), 1)
    # Sloped roof
    pts = [(w // 2, 2), (- 2, h // 4 + 2), (w + 2, h // 4 + 2)]
    pygame.draw.polygon(surf, (150, 70, 40), pts)
    # Chimney with smoke hint
    pygame.draw.rect(surf, (160, 100, 70), (w - 12, 0, 6, h // 4))
    pygame.draw.rect(surf, (130, 75, 50), (w - 12, 0, 6, h // 4), 1)
    # Door
    dw_ = max(6, w // 5)
    dx_ = w // 2 - dw_ // 2
    pygame.draw.rect(surf, (100, 65, 35), (dx_, h - 12, dw_, 12))
    pygame.draw.rect(surf, (80, 50, 25), (dx_, h - 12, dw_, 12), 1)
    # Bread sign
    pygame.draw.circle(surf, (210, 180, 100), (dx_ + dw_ // 2, h - 16), 4)


def _draw_hunter(surf, w, h):
    # Log cabin
    pygame.draw.rect(surf, (85, 60, 32), (0, h // 3, w, h * 2 // 3))
    for py_ in range(h // 3, h, 5):
        c = _vary((100, 70, 38), 8)
        pygame.draw.line(surf, c, (0, py_), (w, py_), 3)
        pygame.draw.line(surf, (70, 48, 25), (0, py_ + 3), (w, py_ + 3), 1)
    # Lean-to roof
    pts = [(0, h // 3), (w, h // 3), (w, h // 6), (0, h // 3 - 4)]
    pygame.draw.polygon(surf, (60, 90, 40), pts)
    pygame.draw.polygon(surf, (45, 70, 30), pts, 1)
    # Animal hide drying
    pygame.draw.line(surf, (110, 80, 45), (4, 4), (w - 4, 4), 2)
    pygame.draw.polygon(surf, (170, 140, 90),
                        [(8, 5), (w // 2, 5), (w // 2 - 2, h // 6), (10, h // 6)])
    # Bow icon
    bx_, by_ = w - 10, h // 6 + 4
    pygame.draw.arc(surf, (130, 90, 50), (bx_ - 4, by_, 4, 14), -1.2, 1.2, 2)
    pygame.draw.line(surf, (160, 140, 100), (bx_ - 4, by_ + 1), (bx_ - 4, by_ + 13), 1)


BUILDING_DRAWERS = {
    "hut": _draw_hut,
    "farm": _draw_farm,
    "woodcutter": _draw_woodcutter,
    "quarry": _draw_quarry,
    "well": _draw_well,
    "stockpile": _draw_stockpile,
    "granary": _draw_granary,
    "mill": _draw_mill,
    "bakery": _draw_bakery,
    "hunter": _draw_hunter,
}


def generate_building_sprite(building_id, pixel_w, pixel_h):
    """Generate a detailed building sprite surface."""
    surf = pygame.Surface((pixel_w, pixel_h), pygame.SRCALPHA)
    drawer = BUILDING_DRAWERS.get(building_id)
    if drawer:
        drawer(surf, pixel_w, pixel_h)
    else:
        pygame.draw.rect(surf, (150, 100, 60), (0, 0, pixel_w, pixel_h))
    return surf


# ═══════════════════════════════════════════════════════════════
#  VILLAGER SPRITES  (small humanoid figures)
# ═══════════════════════════════════════════════════════════════

def generate_villager_sprite(size, body_color, hair_color=None):
    """Generate a small medieval villager sprite.
    size: diameter of the bounding area  (typically 12–24 px)
    """
    s = max(12, size)
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    cx = s // 2
    head_r = max(2, s // 6)
    body_h = max(4, s // 3)
    leg_h = max(2, s // 5)

    head_y = head_r + 1
    body_y = head_y + head_r + 1
    leg_y = body_y + body_h

    # Shadow
    pygame.draw.ellipse(surf, (0, 0, 0, 40),
                        (cx - s // 4, s - 3, s // 2, 3))

    # Legs
    pygame.draw.line(surf, (90, 60, 40), (cx - 2, leg_y), (cx - 2, leg_y + leg_h), 2)
    pygame.draw.line(surf, (90, 60, 40), (cx + 2, leg_y), (cx + 2, leg_y + leg_h), 2)

    # Body (tunic)
    pygame.draw.rect(surf, body_color, (cx - 3, body_y, 7, body_h))
    pygame.draw.rect(surf, tuple(max(0, c - 30) for c in body_color),
                     (cx - 3, body_y, 7, body_h), 1)

    # Arms
    arm_col = tuple(max(0, c - 20) for c in body_color)
    pygame.draw.line(surf, arm_col, (cx - 3, body_y + 1), (cx - 5, body_y + body_h - 1), 2)
    pygame.draw.line(surf, arm_col, (cx + 3, body_y + 1), (cx + 5, body_y + body_h - 1), 2)

    # Head (skin)
    skin = (220, 185, 150)
    pygame.draw.circle(surf, skin, (cx, head_y), head_r)
    pygame.draw.circle(surf, (180, 150, 120), (cx, head_y), head_r, 1)

    # Hair
    if hair_color is None:
        hair_color = random.choice([(60, 40, 20), (140, 100, 50),
                                     (180, 140, 80), (40, 30, 20), (160, 60, 30)])
    pygame.draw.arc(surf, hair_color,
                    (cx - head_r, head_y - head_r, head_r * 2, head_r * 2),
                    0.2, math.pi - 0.2, 2)

    return surf

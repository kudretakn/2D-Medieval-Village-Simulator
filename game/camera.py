"""Camera system with pan, smooth zoom, and screen-shake."""
import math
import random
import pygame
from .constants import (
    MAP_VIEW_X, MAP_VIEW_Y, MAP_VIEW_W, MAP_VIEW_H,
    MAP_WIDTH, MAP_HEIGHT, TILE_SIZE,
    CAMERA_PAN_SPEED, ZOOM_MIN, ZOOM_MAX, ZOOM_STEP,
    CAMERA_SMOOTHING, CAMERA_SHAKE_AMPLITUDE, CAMERA_SHAKE_FREQ,
)


class Camera:
    def __init__(self):
        self.x = (MAP_WIDTH * TILE_SIZE) / 2 - MAP_VIEW_W / 2
        self.y = (MAP_HEIGHT * TILE_SIZE) / 2 - MAP_VIEW_H / 2
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.dragging = False
        self.drag_start = (0, 0)
        self.drag_cam_start = (0, 0)
        # Screen shake
        self.shake_timer = 0.0
        self.shake_duration = 0.0
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0

    def start_shake(self, duration=0.4):
        """Begin screen-shake effect (e.g., fire, wolves attack)."""
        self.shake_timer = 0.0
        self.shake_duration = duration

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if self._in_map_view(mx, my):
                old_zoom = self.zoom
                self.target_zoom += event.y * ZOOM_STEP
                self.target_zoom = max(ZOOM_MIN, min(ZOOM_MAX, self.target_zoom))
                # Immediate partial zoom for pivot calculation
                world_x = self.x + (mx - MAP_VIEW_X) / old_zoom
                world_y = self.y + (my - MAP_VIEW_Y) / old_zoom
                self.x = world_x - (mx - MAP_VIEW_X) / self.target_zoom
                self.y = world_y - (my - MAP_VIEW_Y) / self.target_zoom

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
            mx, my = event.pos
            if self._in_map_view(mx, my):
                self.dragging = True
                self.drag_start = (mx, my)
                self.drag_cam_start = (self.x, self.y)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mx, my = event.pos
            dx = (self.drag_start[0] - mx) / self.zoom
            dy = (self.drag_start[1] - my) / self.zoom
            self.x = self.drag_cam_start[0] + dx
            self.y = self.drag_cam_start[1] + dy

    def update(self, dt):
        # Keyboard pan
        keys = pygame.key.get_pressed()
        speed = CAMERA_PAN_SPEED / self.zoom * dt
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y -= speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y += speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += speed

        # Smooth zoom interpolation
        diff = self.target_zoom - self.zoom
        if abs(diff) > 0.001:
            self.zoom += diff * min(1.0, CAMERA_SMOOTHING * dt)
        else:
            self.zoom = self.target_zoom

        # Clamp position
        max_x = MAP_WIDTH * TILE_SIZE - MAP_VIEW_W / self.zoom
        max_y = MAP_HEIGHT * TILE_SIZE - MAP_VIEW_H / self.zoom
        self.x = max(0, min(max_x, self.x))
        self.y = max(0, min(max_y, self.y))

        # Screen shake
        if self.shake_duration > 0:
            self.shake_timer += dt
            if self.shake_timer >= self.shake_duration:
                self.shake_duration = 0.0
                self.shake_offset_x = 0.0
                self.shake_offset_y = 0.0
            else:
                progress = self.shake_timer / self.shake_duration
                intensity = (1.0 - progress) * CAMERA_SHAKE_AMPLITUDE
                t = self.shake_timer * CAMERA_SHAKE_FREQ
                self.shake_offset_x = math.sin(t * 7.3) * intensity
                self.shake_offset_y = math.cos(t * 5.1) * intensity

    def world_to_screen(self, wx, wy):
        sx = MAP_VIEW_X + (wx - self.x) * self.zoom + self.shake_offset_x
        sy = MAP_VIEW_Y + (wy - self.y) * self.zoom + self.shake_offset_y
        return sx, sy

    def screen_to_world(self, sx, sy):
        wx = self.x + (sx - MAP_VIEW_X - self.shake_offset_x) / self.zoom
        wy = self.y + (sy - MAP_VIEW_Y - self.shake_offset_y) / self.zoom
        return wx, wy

    def screen_to_tile(self, sx, sy):
        wx, wy = self.screen_to_world(sx, sy)
        return int(wx // TILE_SIZE), int(wy // TILE_SIZE)

    def _in_map_view(self, mx, my):
        return (MAP_VIEW_X <= mx < MAP_VIEW_X + MAP_VIEW_W and
                MAP_VIEW_Y <= my < MAP_VIEW_Y + MAP_VIEW_H)

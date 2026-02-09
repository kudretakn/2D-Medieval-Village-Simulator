"""Game time management."""
from .constants import (
    DAY_LENGTH_SECONDS, HOURS_PER_DAY, DAYS_PER_SEASON,
    DAWN_HOUR, DUSK_HOUR,
)
from .enums import GameSpeed, Season


class TimeManager:
    SEASON_ORDER = [Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER]

    def __init__(self):
        self.game_hour = 8.0
        self.day = 1
        self.season_index = 0
        self.year = 1
        self.speed = GameSpeed.NORMAL
        self.total_hours = 0.0

    @property
    def season(self):
        return self.SEASON_ORDER[self.season_index]

    @property
    def time_string(self):
        h = int(self.game_hour)
        m = int((self.game_hour % 1) * 60)
        return f"{h:02d}:{m:02d}"

    @property
    def date_string(self):
        return f"Day {self.day} - {self.season.value} Y{self.year}"

    @property
    def is_daytime(self):
        return DAWN_HOUR <= self.game_hour < DUSK_HOUR

    @property
    def speed_multiplier(self):
        return self.speed.value

    def update(self, dt):
        if self.speed == GameSpeed.PAUSED:
            return 0.0
        hours_per_sec = HOURS_PER_DAY / DAY_LENGTH_SECONDS
        hours_elapsed = dt * hours_per_sec * self.speed_multiplier
        self.game_hour += hours_elapsed
        self.total_hours += hours_elapsed
        while self.game_hour >= HOURS_PER_DAY:
            self.game_hour -= HOURS_PER_DAY
            self.day += 1
            if self.day > DAYS_PER_SEASON:
                self.day = 1
                self.season_index = (self.season_index + 1) % 4
                if self.season_index == 0:
                    self.year += 1
        return hours_elapsed

    def set_speed(self, speed: GameSpeed):
        self.speed = speed

    def toggle_pause(self):
        if self.speed == GameSpeed.PAUSED:
            self.speed = GameSpeed.NORMAL
        else:
            self.speed = GameSpeed.PAUSED

"""Villager entities with traits, morale, skills, and utility-based AI."""
import random
import math
from .enums import VillagerState
from .constants import (
    HUNGER_RATE, THIRST_RATE, FOOD_RESTORE, WATER_RESTORE,
    STARVATION_DAMAGE, DEHYDRATION_DAMAGE, HEALTH_REGEN,
    VILLAGER_SPEED, MAP_WIDTH, MAP_HEIGHT, TILE_SIZE,
    TRAITS, SKILL_HOURS_PER_LEVEL, SKILL_MAX_BONUS,
    MORALE_BASE, MORALE_HOMELESS_PENALTY, MORALE_HUNGRY_PENALTY,
    MORALE_THIRSTY_PENALTY, MORALE_SICK_PENALTY,
    MORALE_SOCIAL_BONUS, MORALE_TRAIT_DRIFT,
    MORALE_EMIGRATION_THRESHOLD, EMIGRATION_GRACE_DAYS,
    SEASON_HUNGER_MULT, SEASON_THIRST_MULT,
)

NAMES = [
    "Aldric", "Berta", "Conrad", "Daria", "Edric", "Frieda",
    "Gunther", "Hilda", "Igor", "Johanna", "Karl", "Liesa",
    "Magnus", "Nora", "Otto", "Petra", "Rolf", "Sigrid",
    "Theron", "Ursula", "Viktor", "Wanda", "Xander", "Yara",
    "Baldric", "Celeste", "Dietrich", "Elara", "Felix", "Greta",
]


class Villager:
    _next_id = 0

    def __init__(self, world_x, world_y, traits=None):
        self.id = Villager._next_id
        Villager._next_id += 1
        self.name = random.choice(NAMES)
        self.world_x = world_x
        self.world_y = world_y

        # Needs
        self.hunger = 80.0
        self.thirst = 80.0
        self.health = 100.0

        # Morale & traits
        self.morale = MORALE_BASE
        self.traits: list[str] = traits if traits else self._roll_traits()
        self.skills: dict[str, float] = {}   # building_id -> hours worked
        self.history: list[str] = []           # log significant events
        self.friends: set[int] = set()

        # Emigration
        self.emigration_timer = 0.0  # counts days of low morale

        # Assignments
        self.workplace = None
        self.home = None
        self.state = VillagerState.IDLE
        self.target_x = world_x
        self.target_y = world_y
        self.alive = True
        self.eat_cd = 0.0
        self.drink_cd = 0.0
        self.color = (
            random.randint(180, 240),
            random.randint(140, 200),
            random.randint(100, 160),
        )
        self._log(f"Born in the village")

    # ── Trait system ─────────────────────────────────────
    @staticmethod
    def _roll_traits() -> list[str]:
        """Pick 2 non-conflicting random traits."""
        pool = list(TRAITS.keys())
        chosen = []
        for _ in range(2):
            if not pool:
                break
            t = random.choice(pool)
            chosen.append(t)
            pool.remove(t)
            # Remove opposite trait
            opp = TRAITS[t].get("opposite")
            if opp and opp in pool:
                pool.remove(opp)
        return chosen

    def trait_modifier(self, key: str) -> float:
        """Sum a named modifier from all traits. E.g. 'hunger_mult'."""
        total = 0.0
        for t in self.traits:
            total += TRAITS.get(t, {}).get(key, 0.0)
        return total

    # ── Skills ───────────────────────────────────────────
    def skill_level(self, building_id: str) -> int:
        hours = self.skills.get(building_id, 0)
        return int(hours // SKILL_HOURS_PER_LEVEL)

    def skill_bonus(self, building_id: str) -> float:
        lvl = self.skill_level(building_id)
        return min(lvl * 0.05, SKILL_MAX_BONUS)

    def add_work_hours(self, building_id: str, hours: float):
        self.skills[building_id] = self.skills.get(building_id, 0) + hours

    # ── History ──────────────────────────────────────────
    def _log(self, msg: str):
        self.history.append(msg)
        if len(self.history) > 30:
            self.history.pop(0)

    # ── Morale ───────────────────────────────────────────
    def update_morale(self, buildings, villagers):
        """Recalculate morale toward a target based on conditions."""
        target = MORALE_BASE

        # Housing
        if self.home is None:
            target -= MORALE_HOMELESS_PENALTY
        # Hunger / thirst
        if self.hunger < 20:
            target -= MORALE_HUNGRY_PENALTY
        if self.thirst < 20:
            target -= MORALE_THIRSTY_PENALTY
        # Sickness
        if self.health < 40:
            target -= MORALE_SICK_PENALTY
        # Social — nearby friends
        friends_near = 0
        for v in villagers:
            if v.id == self.id or not v.alive:
                continue
            dist = math.hypot(v.world_x - self.world_x, v.world_y - self.world_y)
            if dist < 80:
                friends_near += 1
                self.friends.add(v.id)
        if friends_near > 0:
            target += min(friends_near, 3) * MORALE_SOCIAL_BONUS
        # Trait drift
        target += self.trait_modifier("morale_offset")

        # Smooth drift toward target
        self.morale += (target - self.morale) * MORALE_TRAIT_DRIFT
        self.morale = max(0, min(100, self.morale))

    # ── Main update ──────────────────────────────────────
    def update(self, game_hours, time_mgr, resource_mgr):
        """Update needs, consume resources, and choose behavior."""
        if not self.alive:
            return

        season = time_mgr.season_name
        # Deplete needs (modified by season + trait)
        h_mult = SEASON_HUNGER_MULT.get(season, 1.0) + self.trait_modifier("hunger_mult")
        t_mult = SEASON_THIRST_MULT.get(season, 1.0) + self.trait_modifier("thirst_mult")
        self.hunger = max(0, min(100, self.hunger - HUNGER_RATE * game_hours * max(0.5, h_mult)))
        self.thirst = max(0, min(100, self.thirst - THIRST_RATE * game_hours * max(0.5, t_mult)))
        self.eat_cd = max(0, self.eat_cd - game_hours)
        self.drink_cd = max(0, self.drink_cd - game_hours)

        # Damage from starvation / dehydration
        if self.hunger <= 0:
            self.health -= STARVATION_DAMAGE * game_hours
        if self.thirst <= 0:
            self.health -= DEHYDRATION_DAMAGE * game_hours
        if self.hunger > 50 and self.thirst > 50 and self.health < 100:
            regen = HEALTH_REGEN + self.trait_modifier("health_regen_bonus")
            self.health += regen * game_hours
        self.health = max(0, min(100, self.health))

        # Death
        if self.health <= 0:
            self._die()
            return

        # Auto-consume food and water using utility scoring
        self._consume_needs(resource_mgr)

        # Behavior based on time of day (utility scoring)
        self._choose_behaviour(time_mgr, game_hours)

    def _consume_needs(self, resource_mgr):
        """Consume food/water when needs are low."""
        if self.hunger < 30 and self.eat_cd <= 0:
            # Try bread first (better food), then raw food
            if resource_mgr.remove("BREAD", 1):
                restore = FOOD_RESTORE * 1.5
                self.hunger = min(100, self.hunger + restore)
                self.eat_cd = 2.0
            elif resource_mgr.remove("FOOD", 1):
                self.hunger = min(100, self.hunger + FOOD_RESTORE)
                self.eat_cd = 2.0
        if self.thirst < 30 and self.drink_cd <= 0:
            if resource_mgr.remove("WATER", 1):
                self.thirst = min(100, self.thirst + WATER_RESTORE)
                self.drink_cd = 2.0

    def _choose_behaviour(self, time_mgr, game_hours):
        """Simple utility-based behaviour selector."""
        if time_mgr.is_daytime:
            # Urgency scores
            eat_urgency = max(0, 40 - self.hunger) / 40
            drink_urgency = max(0, 40 - self.thirst) / 40
            work_urgency = 0.5 if self.workplace else 0.0

            if eat_urgency > 0.5 or drink_urgency > 0.5:
                # Go home to eat/drink
                if self.home:
                    self.state = VillagerState.IDLE
                    self.target_x, self.target_y = self.home.center_world
                else:
                    self.state = VillagerState.IDLE
            elif self.workplace:
                self.state = VillagerState.WORKING
                self.target_x, self.target_y = self.workplace.center_world
                # Accrue skill hours
                self.add_work_hours(self.workplace.building_id, game_hours)
            else:
                self.state = VillagerState.IDLE
                if random.random() < 0.02 * game_hours:
                    cx = (self.home.center_world[0] if self.home
                          else MAP_WIDTH * TILE_SIZE / 2)
                    cy = (self.home.center_world[1] if self.home
                          else MAP_HEIGHT * TILE_SIZE / 2)
                    self.target_x = cx + random.uniform(-64, 64)
                    self.target_y = cy + random.uniform(-64, 64)
        else:
            if self.home:
                self.state = VillagerState.SLEEPING
                self.target_x, self.target_y = self.home.center_world
            else:
                self.state = VillagerState.IDLE

    # ── Emigration ───────────────────────────────────────
    def check_emigration(self, new_day: bool) -> bool:
        """Returns True if villager decides to leave. Call daily."""
        if not new_day or not self.alive:
            return False
        if self.morale < MORALE_EMIGRATION_THRESHOLD:
            self.emigration_timer += 1
            if self.emigration_timer >= EMIGRATION_GRACE_DAYS:
                self._log("Left the village due to low morale")
                return True
        else:
            self.emigration_timer = max(0, self.emigration_timer - 0.5)
        return False

    # ── Injury / events ─────────────────────────────────
    def injure(self, amount, reason=""):
        """Apply damage from event (wolves, fire, plague)."""
        self.health = max(0, self.health - amount)
        if reason:
            self._log(reason)
        if self.health <= 0:
            self._die()

    # ── Death ────────────────────────────────────────────
    def _die(self):
        self.alive = False
        self._log("Died")
        if self.workplace and self in self.workplace.workers:
            self.workplace.workers.remove(self)
        if self.home and self in self.home.residents:
            self.home.residents.remove(self)
        self.workplace = self.home = None

    # ── Movement ─────────────────────────────────────────
    def update_movement(self, dt):
        """Move toward target position."""
        if not self.alive:
            return
        dx = self.target_x - self.world_x
        dy = self.target_y - self.world_y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 2:
            speed = VILLAGER_SPEED * dt
            # Trait speed modifier
            speed *= (1.0 + self.trait_modifier("speed_mult"))
            if speed >= dist:
                self.world_x, self.world_y = self.target_x, self.target_y
            else:
                self.world_x += (dx / dist) * speed
                self.world_y += (dy / dist) * speed

    # ── Display helpers ──────────────────────────────────
    @property
    def needs_summary(self):
        return f"Hunger:{self.hunger:.0f} Thirst:{self.thirst:.0f} HP:{self.health:.0f}"

    @property
    def morale_text(self):
        if self.morale >= 80:
            return "Happy"
        if self.morale >= 50:
            return "Content"
        if self.morale >= 25:
            return "Unhappy"
        return "Miserable"

    @property
    def status_text(self):
        return {
            VillagerState.IDLE: "Idle",
            VillagerState.WORKING: "Working",
            VillagerState.SLEEPING: "Sleeping",
            VillagerState.EATING: "Eating",
            VillagerState.DRINKING: "Drinking",
            VillagerState.FLEEING: "Fleeing",
            VillagerState.EMIGRATING: "Leaving",
        }.get(self.state, "Unknown")

    @property
    def trait_names(self):
        return ", ".join(self.traits) if self.traits else "None"

    # ── Serialisation ────────────────────────────────────
    def serialise(self) -> dict:
        return {
            "name": self.name,
            "x": self.world_x, "y": self.world_y,
            "hunger": self.hunger, "thirst": self.thirst,
            "health": self.health, "morale": self.morale,
            "traits": self.traits,
            "skills": self.skills,
            "history": self.history[-20:],
            "emigration_timer": self.emigration_timer,
        }

    @classmethod
    def deserialise(cls, data) -> "Villager":
        v = cls(data["x"], data["y"], traits=data.get("traits", []))
        v.name = data["name"]
        v.hunger = data["hunger"]
        v.thirst = data["thirst"]
        v.health = data["health"]
        v.morale = data.get("morale", MORALE_BASE)
        v.skills = data.get("skills", {})
        v.history = data.get("history", [])
        v.emigration_timer = data.get("emigration_timer", 0)
        return v

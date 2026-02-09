"""Random event system — droughts, fires, wolves, plagues, bonuses."""
import random
from .enums import EventType, Season
from .constants import EVENT_CHECK_INTERVAL_HOURS


# ── Event definitions ────────────────────────────────────
# Each has: type, base_chance (per check), seasons allowed,
# min_pop, duration_hours, description
EVENT_DEFS = [
    {
        "type": EventType.DROUGHT,
        "chance": 0.12,
        "seasons": [Season.SUMMER],
        "min_pop": 5,
        "duration": 30 * 24,   # ~1 season
        "message": "A drought has struck! Wells produce half water.",
        "end_message": "The drought has ended. Water returns to normal.",
    },
    {
        "type": EventType.FIRE,
        "chance": 0.08,
        "seasons": [Season.SUMMER, Season.AUTUMN],
        "min_pop": 4,
        "duration": 0,         # instant
        "message": "Fire! A building has been damaged!",
        "end_message": None,
    },
    {
        "type": EventType.WOLVES,
        "chance": 0.07,
        "seasons": [Season.WINTER, Season.AUTUMN],
        "min_pop": 5,
        "duration": 0,
        "message": "Wolves attacked the village!",
        "end_message": None,
    },
    {
        "type": EventType.BOUNTIFUL,
        "chance": 0.15,
        "seasons": [Season.AUTUMN],
        "min_pop": 3,
        "duration": 15 * 24,   # ~half season
        "message": "A bountiful harvest! Farm output +50% this period.",
        "end_message": "The bountiful harvest period has ended.",
    },
    {
        "type": EventType.PLAGUE,
        "chance": 0.06,
        "seasons": [Season.SPRING, Season.SUMMER],
        "min_pop": 12,
        "duration": 20 * 24,
        "message": "Plague! Villagers are falling ill!",
        "end_message": "The plague has passed.",
    },
    {
        "type": EventType.WANDERER,
        "chance": 0.10,
        "seasons": [Season.SPRING, Season.SUMMER, Season.AUTUMN],
        "min_pop": 3,
        "duration": 3 * 24,
        "message": "A wandering merchant has arrived!",
        "end_message": "The merchant has departed.",
    },
]


class ActiveEvent:
    """An event currently in progress."""
    __slots__ = ("event_type", "remaining_hours", "end_message", "data")

    def __init__(self, event_type, duration, end_message):
        self.event_type = event_type
        self.remaining_hours = duration
        self.end_message = end_message
        self.data = {}  # extra data (e.g. which building caught fire)


class EventSystem:
    def __init__(self):
        self.active_events: list[ActiveEvent] = []
        self.check_timer = 0.0
        self.event_log: list[tuple] = []  # (day, season, message)

    def get_active_types(self) -> set:
        """Return set of currently active EventTypes."""
        return {e.event_type for e in self.active_events}

    def is_active(self, etype: EventType) -> bool:
        return etype in self.get_active_types()

    def update(self, game_hours, game):
        """Tick event timers and check for new events."""
        # Tick active events
        ended = []
        for ev in self.active_events:
            if ev.remaining_hours > 0:
                ev.remaining_hours -= game_hours
                if ev.remaining_hours <= 0:
                    ended.append(ev)
        for ev in ended:
            self.active_events.remove(ev)
            if ev.end_message:
                game.ui.add_alert(ev.end_message, dur=6.0)
                self.event_log.append(
                    (game.time_mgr.day, game.time_mgr.season.value, ev.end_message))

        # Check for new events periodically
        self.check_timer += game_hours
        if self.check_timer < EVENT_CHECK_INTERVAL_HOURS:
            return
        self.check_timer = 0.0

        alive_count = sum(1 for v in game.villagers if v.alive)
        active_types = self.get_active_types()

        for edef in EVENT_DEFS:
            if edef["type"] in active_types:
                continue  # don't stack same event
            if game.time_mgr.season not in edef["seasons"]:
                continue
            if alive_count < edef["min_pop"]:
                continue
            if random.random() > edef["chance"]:
                continue
            # Fire event!
            self._trigger(edef, game)
            break  # max one new event per check

    def _trigger(self, edef, game):
        """Apply an event's immediate effects and create ActiveEvent if duration > 0."""
        etype = edef["type"]
        ev = ActiveEvent(etype, edef["duration"], edef.get("end_message"))

        if etype == EventType.FIRE:
            self._apply_fire(game, ev)
        elif etype == EventType.WOLVES:
            self._apply_wolves(game, ev)
        elif etype == EventType.WANDERER:
            self._apply_wanderer(game, ev)

        if edef["duration"] > 0:
            self.active_events.append(ev)

        game.ui.add_alert(edef["message"], dur=8.0)
        self.event_log.append(
            (game.time_mgr.day, game.time_mgr.season.value, edef["message"]))
        # Camera shake on dramatic events
        if etype in (EventType.FIRE, EventType.WOLVES, EventType.PLAGUE):
            game.camera.start_shake(0.5)

    # ── Instant event effects ────────────────────────────
    def _apply_fire(self, game, ev):
        """Damage a random building's condition."""
        if not game.buildings:
            return
        b = random.choice(game.buildings)
        b.condition = max(0.0, b.condition - 0.40)
        ev.data["target_building"] = b.id
        game.ui.add_alert(f"{b.data.name} caught fire! Condition: {b.condition:.0%}")

    def _apply_wolves(self, game, ev):
        """Injure a random villager."""
        alive = [v for v in game.villagers if v.alive]
        if not alive:
            return
        victim = random.choice(alive)
        damage = random.uniform(25, 50)
        victim.health = max(0, victim.health - damage)
        ev.data["victim"] = victim.id
        game.ui.add_alert(f"Wolves injured {victim.name}! (-{damage:.0f} HP)")
        if victim.health <= 0:
            victim.alive = False
            game.ui.add_alert(f"{victim.name} was killed by wolves!")

    def _apply_wanderer(self, game, ev):
        """Give the player a small resource bonus."""
        bonus_res = random.choice(["FOOD", "WOOD", "STONE"])
        amount = random.randint(15, 35)
        game.resource_mgr.add(bonus_res, amount)
        ev.data["gift"] = (bonus_res, amount)
        game.ui.add_alert(f"Merchant gifted {amount} {bonus_res.capitalize()}!")

    def get_production_modifier(self, building_id):
        """Return a multiplier based on active events."""
        mult = 1.0
        for ev in self.active_events:
            if ev.event_type == EventType.DROUGHT:
                if building_id == "well":
                    mult *= 0.5
            elif ev.event_type == EventType.BOUNTIFUL:
                if building_id == "farm":
                    mult *= 1.5
            elif ev.event_type == EventType.PLAGUE:
                mult *= 0.7  # general productivity hit
        return mult

    def get_well_modifier(self):
        """Return well output multiplier."""
        return 0.5 if self.is_active(EventType.DROUGHT) else 1.0

    def serialise(self):
        return {
            "active": [
                {"type": e.event_type.value, "remaining": e.remaining_hours,
                 "end_msg": e.end_message}
                for e in self.active_events
            ],
            "timer": self.check_timer,
        }

    def deserialise(self, data):
        self.check_timer = data.get("timer", 0)
        self.active_events = []
        type_map = {e.value: e for e in EventType}
        for ed in data.get("active", []):
            etype = type_map.get(ed["type"])
            if etype:
                self.active_events.append(
                    ActiveEvent(etype, ed["remaining"], ed.get("end_msg")))

"""Village progression / level system."""
from .constants import VILLAGE_LEVELS


class ProgressionManager:
    """Tracks village level, unlocks, and milestones."""

    def __init__(self):
        self.level = 1
        self.level_name = "Camp"
        self.unlocked_buildings: set[str] = set()
        self._apply_level(1)

    def _apply_level(self, lvl):
        for lv, name, _pop, _bld, unlocks in VILLAGE_LEVELS:
            if lv <= lvl:
                self.level = lv
                self.level_name = name
                self.unlocked_buildings.update(unlocks)

    def check_level_up(self, alive_count, building_count) -> str | None:
        """Check if village qualifies for next level.  Returns new name or None."""
        for lv, name, pop_req, bld_req, unlocks in VILLAGE_LEVELS:
            if lv <= self.level:
                continue
            if alive_count >= pop_req and building_count >= bld_req:
                self.level = lv
                self.level_name = name
                self.unlocked_buildings.update(unlocks)
                return name
        return None

    def is_unlocked(self, building_id: str) -> bool:
        return building_id in self.unlocked_buildings

    def next_level_info(self) -> str | None:
        """Return a description of what's needed for the next level."""
        for lv, name, pop_req, bld_req, _unlocks in VILLAGE_LEVELS:
            if lv == self.level + 1:
                return f"Next: {name} (Pop {pop_req}, {bld_req} buildings)"
        return "Max level reached!"

    def serialise(self):
        return {"level": self.level}

    def deserialise(self, data):
        self._apply_level(data.get("level", 1))

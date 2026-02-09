"""Resource management system with spoilage and rate tracking."""
from .constants import STARTING_RESOURCES, SPOILAGE_RATES


class ResourceManager:
    def __init__(self):
        self.resources = dict(STARTING_RESOURCES)
        self.storage_capacity = 200
        # Rate tracking (per-season production / consumption snapshot)
        self._produced = {}   # resource -> amount produced this season
        self._consumed = {}   # resource -> amount consumed this season
        self.rates = {}       # resource -> net per-day (updated each season)
        self._season_days = 0

    def get(self, name: str) -> float:
        return self.resources.get(name, 0)

    def add(self, name: str, amount: float):
        cur = self.resources.get(name, 0)
        self.resources[name] = min(cur + amount, self.storage_capacity)
        self._produced[name] = self._produced.get(name, 0) + amount

    def remove(self, name: str, amount: float) -> bool:
        cur = self.resources.get(name, 0)
        if cur >= amount:
            self.resources[name] = cur - amount
            self._consumed[name] = self._consumed.get(name, 0) + amount
            return True
        return False

    def has(self, name: str, amount: float) -> bool:
        return self.get(name) >= amount

    def can_afford(self, cost: dict) -> bool:
        return all(self.has(r, a) for r, a in cost.items())

    def spend(self, cost: dict) -> bool:
        if not self.can_afford(cost):
            return False
        for r, a in cost.items():
            self.remove(r, a)
        return True

    def update_storage(self, buildings):
        """Recalculate storage from all storage buildings."""
        base = 200
        for b in buildings:
            base += b.data.storage_bonus
        self.storage_capacity = base

    # ── Spoilage ────────────────────────────────────────────
    def apply_spoilage(self, season_name: str, has_granary: bool):
        """Deduct spoilage; called once per season. Returns dict of losses."""
        losses = {}
        for res, rate in SPOILAGE_RATES.items():
            cur = self.get(res)
            if cur <= 0:
                continue
            effective = rate
            # Granary halves food spoilage
            if has_granary and res in ("FOOD", "BREAD"):
                effective *= 0.5
            # Winter doubles food spoilage
            if season_name == "Winter":
                effective *= 1.5
            loss = round(cur * effective, 1)
            if loss > 0:
                self.resources[res] = max(0, cur - loss)
                losses[res] = loss
        return losses

    # ── Rate tracking ───────────────────────────────────────
    def tick_day(self):
        """Call once per in-game day to accumulate season day counter."""
        self._season_days += 1

    def flush_rates(self):
        """At season end, compute average daily net rate and reset."""
        if self._season_days > 0:
            all_keys = set(self._produced) | set(self._consumed) | set(self.resources)
            for k in all_keys:
                p = self._produced.get(k, 0) / self._season_days
                c = self._consumed.get(k, 0) / self._season_days
                self.rates[k] = round(p - c, 2)
        self._produced.clear()
        self._consumed.clear()
        self._season_days = 0

    def net_rate(self, name: str) -> float:
        return self.rates.get(name, 0.0)

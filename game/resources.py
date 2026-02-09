"""Resource management system."""
from .constants import STARTING_RESOURCES


class ResourceManager:
    def __init__(self):
        self.resources = dict(STARTING_RESOURCES)
        self.storage_capacity = 200

    def get(self, name: str) -> float:
        return self.resources.get(name, 0)

    def add(self, name: str, amount: float):
        cur = self.resources.get(name, 0)
        self.resources[name] = min(cur + amount, self.storage_capacity)

    def remove(self, name: str, amount: float) -> bool:
        cur = self.resources.get(name, 0)
        if cur >= amount:
            self.resources[name] = cur - amount
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

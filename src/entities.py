"""
Core game entities: Enemy, Tower, Projectile.
"""

from typing import Tuple, Optional, List
import math


class Enemy:
    """Represents an enemy unit moving along the path."""

    def __init__(self, enemy_id: int, enemy_type: str, config: dict, path: List[Tuple[int, int]]):
        self.id = enemy_id
        self.enemy_type = enemy_type
        self.name = config["name"]
        self.max_hp = config["hp"]
        self.hp = config["hp"]
        self.speed = config["speed"]  # cells per tick
        self.reward = config["reward"]
        
        self.path = path  # List of (x, y) coordinates
        self.path_index = 0  # Current target waypoint index
        self.progress = 0.0  # Progress towards current waypoint (0.0 to 1.0)
        self.total_progress = 0.0  # Total progress along entire path (for targeting priority)
        
        # Start at spawn point
        if path:
            self.x, self.y = float(path[0][0]), float(path[0][1])
        else:
            self.x, self.y = 0.0, 0.0

    @property
    def position(self) -> Tuple[float, float]:
        return (self.x, self.y)

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    @property
    def has_reached_end(self) -> bool:
        return self.path_index >= len(self.path) - 1 and self.progress >= 1.0

    def move(self) -> bool:
        """
        Move the enemy along the path by one tick.
        Returns True if the enemy reached the end of the path.
        """
        if self.has_reached_end:
            return True

        # Check if we're already at the last waypoint
        if self.path_index >= len(self.path) - 1:
            # We're at the last waypoint, just need to complete progress
            self.progress += self.speed
            self.total_progress += self.speed
            return self.has_reached_end

        # Calculate remaining progress needed to reach current waypoint
        remaining_in_cell = 1.0 - self.progress
        
        if self.speed >= remaining_in_cell:
            # Move to next waypoint
            self.progress = 0.0
            self.path_index += 1
            self.x, self.y = float(self.path[self.path_index][0]), float(self.path[self.path_index][1])
            
            # Continue moving if speed allows (for high-speed enemies)
            leftover_speed = self.speed - remaining_in_cell
            if self.path_index < len(self.path) - 1 and leftover_speed > 0:
                self.progress = leftover_speed
                self.total_progress += leftover_speed
                if self.path_index + 1 < len(self.path):
                    dx = self.path[self.path_index + 1][0] - self.path[self.path_index][0]
                    dy = self.path[self.path_index + 1][1] - self.path[self.path_index][1]
                    self.x = float(self.path[self.path_index][0]) + dx * self.progress
                    self.y = float(self.path[self.path_index][1]) + dy * self.progress
        else:
            # Move within current cell
            self.progress += self.speed
            self.total_progress += self.speed
            if self.path_index + 1 < len(self.path):
                dx = self.path[self.path_index + 1][0] - self.path[self.path_index][0]
                dy = self.path[self.path_index + 1][1] - self.path[self.path_index][1]
                self.x = float(self.path[self.path_index][0]) + dx * self.progress
                self.y = float(self.path[self.path_index][1]) + dy * self.progress

        return self.has_reached_end

    def take_damage(self, damage: int) -> bool:
        """
        Apply damage to the enemy.
        Returns True if the enemy died.
        """
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            return True
        return False

    def get_hp_percentage(self) -> float:
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0


class Tower:
    """Represents a defensive tower."""

    def __init__(self, tower_id: int, tower_type: str, config: dict, x: int, y: int):
        self.id = tower_id
        self.tower_type = tower_type
        self.name = config["name"]
        self.x = x
        self.y = y
        self.damage = config["damage"]
        self.range = config["range"]
        self.cooldown_max = config["cooldown"]
        self.cooldown = 0
        self.projectile_speed = config["projectile_speed"]

    @property
    def position(self) -> Tuple[int, int]:
        return (self.x, self.y)

    @property
    def is_ready(self) -> bool:
        return self.cooldown == 0

    def tick(self):
        """Decrease cooldown if active."""
        if self.cooldown > 0:
            self.cooldown -= 1

    def can_target(self, enemy: Enemy) -> bool:
        """Check if tower can target this enemy based on range."""
        distance = math.sqrt((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2)
        return distance <= self.range

    def find_target(self, enemies: List[Enemy]) -> Optional[Enemy]:
        """
        Find the first enemy in range (by path progress priority).
        Returns the enemy with the highest total_progress (furthest along path) within range.
        """
        valid_targets = [e for e in enemies if e.is_alive and self.can_target(e)]
        
        if not valid_targets:
            return None
        
        # Select enemy with highest total_progress (first to reach end, i.e., most dangerous)
        # Specification says "первая цель, которая попадает в область видимости" 
        # interpreted as the one furthest along the path among those in range
        return max(valid_targets, key=lambda e: e.total_progress)

    def fire(self, target: Enemy) -> Optional['Projectile']:
        """
        Fire a projectile at the target if ready.
        Returns a Projectile if fired, None otherwise.
        """
        if not self.is_ready or not target.is_alive:
            return None

        self.cooldown = self.cooldown_max
        
        # Calculate distance and flight time
        distance = math.sqrt((self.x - target.x) ** 2 + (self.y - target.y) ** 2)
        flight_time = math.ceil(distance / self.projectile_speed) if self.projectile_speed > 0 else 1
        
        return Projectile(
            target_id=target.id,
            damage=self.damage,
            flight_time=flight_time,
            source_tower_id=self.id
        )


class Projectile:
    """Represents a projectile in flight."""

    def __init__(self, target_id: int, damage: int, flight_time: int, source_tower_id: int):
        self.target_id = target_id
        self.damage = damage
        self.flight_time = flight_time  # Ticks until impact
        self.source_tower_id = source_tower_id
        self.time_elapsed = 0

    @property
    def has_impacted(self) -> bool:
        return self.time_elapsed >= self.flight_time

    def tick(self) -> bool:
        """
        Advance projectile by one tick.
        Returns True if projectile has impacted.
        """
        self.time_elapsed += 1
        return self.has_impacted

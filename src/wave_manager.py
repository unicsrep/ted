"""
Wave management module.
Handles enemy spawning and wave progression.
"""

from typing import List, Optional
from src.entities import Enemy


class WaveManager:
    """Manages enemy waves and spawning logic."""

    def __init__(self, waves_config: list, enemies_config: dict, path: list):
        self.waves = waves_config
        self.enemies_config = enemies_config
        self.path = path
        
        self.current_wave_index = 0
        self.enemies_spawned_in_wave = 0
        self.ticks_since_last_spawn = 0
        self.ticks_between_waves = 0
        self.is_waiting_between_waves = False
        self.all_waves_complete = False

    @property
    def current_wave(self) -> Optional[dict]:
        if self.current_wave_index < len(self.waves):
            return self.waves[self.current_wave_index]
        return None

    @property
    def is_wave_active(self) -> bool:
        return self.current_wave is not None and not self.is_waiting_between_waves

    @property
    def is_spawning_complete(self) -> bool:
        """Check if all enemies in current wave have been spawned."""
        if self.current_wave is None:
            return True
        return self.enemies_spawned_in_wave >= self.current_wave["count"]

    def start_next_wave(self):
        """Initialize the next wave."""
        if self.current_wave_index >= len(self.waves):
            self.all_waves_complete = True
            return
        
        self.enemies_spawned_in_wave = 0
        self.ticks_since_last_spawn = 0
        self.is_waiting_between_waves = False

    def update(self) -> Optional[Enemy]:
        """
        Process spawning logic for current tick.
        Returns a new Enemy if one should be spawned, None otherwise.
        """
        # Check if all waves are complete
        if self.all_waves_complete:
            return None

        # Handle waiting between waves
        if self.is_waiting_between_waves:
            self.ticks_between_waves -= 1
            if self.ticks_between_waves <= 0:
                self.start_next_wave()
            return None

        # No active wave
        if self.current_wave is None:
            self.start_next_wave()
            return None

        # Check if current wave spawning is complete
        if self.is_spawning_complete:
            self.is_waiting_between_waves = True
            self.ticks_between_waves = 3  # Default pause between waves
            return None

        # Handle spawn timing
        self.ticks_since_last_spawn += 1
        spawn_interval = self.current_wave.get("spawn_interval", 1)
        
        if self.ticks_since_last_spawn >= spawn_interval:
            self.ticks_since_last_spawn = 0
            
            # Create new enemy
            enemy_type = self.current_wave["enemy_type"]
            enemy_config = self.enemies_config.get(enemy_type)
            
            if enemy_config:
                enemy_id = self._generate_enemy_id()
                enemy = Enemy(
                    enemy_id=enemy_id,
                    enemy_type=enemy_type,
                    config=enemy_config,
                    path=self.path
                )
                self.enemies_spawned_in_wave += 1
                return enemy
        
        return None

    def _generate_enemy_id(self) -> int:
        """Generate a unique enemy ID."""
        return self.current_wave_index * 1000 + self.enemies_spawned_in_wave

    def get_wave_info(self) -> dict:
        """Get information about current wave status."""
        return {
            "current_wave": self.current_wave_index + 1 if self.current_wave else 0,
            "total_waves": len(self.waves),
            "enemies_spawned": self.enemies_spawned_in_wave,
            "enemies_total": self.current_wave["count"] if self.current_wave else 0,
            "all_complete": self.all_waves_complete
        }

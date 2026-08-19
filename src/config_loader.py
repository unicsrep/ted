"""
Configuration loader module.
Loads and validates JSON configuration files for the Tower Defense game.
"""

import json
import os
from typing import Dict, Any, List


class ConfigLoader:
    """Handles loading of all game configuration files."""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self._cache: Dict[str, Any] = {}

    def load_json(self, filename: str) -> Dict[str, Any]:
        """Load a JSON file from the config directory."""
        if filename in self._cache:
            return self._cache[filename]

        filepath = os.path.join(self.config_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Configuration file not found: {filepath}")

        with open(filepath, 'r') as f:
            data = json.load(f)

        self._cache[filename] = data
        return data

    def load_game_settings(self) -> Dict[str, Any]:
        """Load global game settings."""
        return self.load_json("game_settings.json")

    def load_enemies(self) -> Dict[str, Any]:
        """Load enemy type definitions."""
        return self.load_json("enemies.json")

    def load_towers(self) -> Dict[str, Any]:
        """Load tower type definitions."""
        return self.load_json("towers.json")

    def load_map(self, map_name: str) -> Dict[str, Any]:
        """Load a specific map configuration."""
        return self.load_json(f"maps/{map_name}.json")

    def load_all(self, map_name: str = "map_1") -> Dict[str, Any]:
        """Load all configuration files at once."""
        return {
            "game_settings": self.load_game_settings(),
            "enemies": self.load_enemies(),
            "towers": self.load_towers(),
            "map": self.load_map(map_name)
        }

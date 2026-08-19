"""
Unit tests for Tower Defense game entities.
Following TDD approach - tests define expected behavior.
"""

import pytest
from src.entities import Enemy, Tower, Projectile
from src.game_map import GameMap
from src.wave_manager import WaveManager
from src.game_engine import GameEngine
from src.config_loader import ConfigLoader


class TestEnemyMovement:
    """Tests for enemy movement logic."""

    def test_enemy_initial_position(self):
        """Enemy should start at spawn point."""
        path = [(0, 0), (1, 0), (2, 0)]
        config = {"name": "Test", "hp": 10, "speed": 0.5, "reward": 5}
        enemy = Enemy(0, "test", config, path)
        
        assert enemy.x == 0.0
        assert enemy.y == 0.0
        assert enemy.path_index == 0
        assert enemy.progress == 0.0

    def test_enemy_movement_single_step(self):
        """Enemy should move along path based on speed."""
        path = [(0, 0), (1, 0), (2, 0)]
        config = {"name": "Test", "hp": 10, "speed": 0.5, "reward": 5}
        enemy = Enemy(0, "test", config, path)
        
        # First move: progress 0.5 within first cell
        reached_end = enemy.move()
        assert not reached_end
        assert enemy.progress == 0.5
        assert enemy.path_index == 0
        assert enemy.x == 0.5
        assert enemy.y == 0.0

    def test_enemy_movement_cell_transition(self):
        """Enemy should transition to next cell after completing current."""
        path = [(0, 0), (1, 0), (2, 0)]
        config = {"name": "Test", "hp": 10, "speed": 0.5, "reward": 5}
        enemy = Enemy(0, "test", config, path)
        
        # Move twice to complete first cell
        enemy.move()  # progress = 0.5
        reached_end = enemy.move()  # progress = 1.0, move to next cell
        
        assert not reached_end
        assert enemy.path_index == 1
        assert enemy.progress == 0.0
        assert enemy.x == 1.0
        assert enemy.y == 0.0

    def test_enemy_reaches_end(self):
        """Enemy should report reaching end of path."""
        # Need at least 3 points to properly test reaching the end
        path = [(0, 0), (1, 0), (2, 0)]
        config = {"name": "Test", "hp": 10, "speed": 1.0, "reward": 5}
        enemy = Enemy(0, "test", config, path)
        
        # Move twice to reach the last waypoint (index 2)
        enemy.move()  # Now at (1, 0), index 1
        enemy.move()  # Now at (2, 0), index 2 (last waypoint)
        
        assert enemy.path_index == 2  # At last waypoint
        assert enemy.progress == 0.0  # Just arrived
        
        # One more move to complete the path
        enemy.move()  # This should set progress to 1.0
        assert enemy.has_reached_end


class TestEnemyHealth:
    """Tests for enemy health and damage."""

    def test_enemy_take_damage(self):
        """Enemy should lose HP when damaged."""
        path = [(0, 0)]
        config = {"name": "Test", "hp": 10, "speed": 0.5, "reward": 5}
        enemy = Enemy(0, "test", config, path)
        
        died = enemy.take_damage(3)
        assert not died
        assert enemy.hp == 7

    def test_enemy_death(self):
        """Enemy should die when HP reaches 0."""
        path = [(0, 0)]
        config = {"name": "Test", "hp": 10, "speed": 0.5, "reward": 5}
        enemy = Enemy(0, "test", config, path)
        
        died = enemy.take_damage(10)
        assert died
        assert enemy.hp == 0
        assert not enemy.is_alive

    def test_hp_percentage(self):
        """HP percentage should be calculated correctly."""
        path = [(0, 0)]
        config = {"name": "Test", "hp": 10, "speed": 0.5, "reward": 5}
        enemy = Enemy(0, "test", config, path)
        
        enemy.take_damage(3)
        assert enemy.get_hp_percentage() == 0.7


class TestTowerTargeting:
    """Tests for tower targeting logic."""

    def test_tower_no_targets_in_range(self):
        """Tower should return None when no enemies in range."""
        config = {"name": "Test", "damage": 5, "range": 3, "cooldown": 2, "projectile_speed": 10.0}
        tower = Tower(0, "test", config, 0, 0)
        
        target = tower.find_target([])
        assert target is None

    def test_tower_targets_first_enemy_by_progress(self):
        """Tower should target enemy furthest along path (highest priority)."""
        path = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0)]
        
        # Create two enemies - one at start, one further along
        config = {"name": "Test", "hp": 10, "speed": 0.5, "reward": 5}
        enemy1 = Enemy(0, "test", config, path)  # At (0,0), progress 0
        enemy2 = Enemy(1, "test", config, path)  # Will be moved forward
        
        # Move enemy2 further along path
        for _ in range(4):
            enemy2.move()
        
        # Place tower at position that can see both
        tower_config = {"name": "Test", "damage": 5, "range": 10, "cooldown": 2, "projectile_speed": 10.0}
        tower = Tower(0, "test", tower_config, 2, 0)
        
        target = tower.find_target([enemy1, enemy2])
        assert target == enemy2  # Should target the one further along

    def test_tower_cooldown_decreases(self):
        """Tower cooldown should decrease each tick."""
        config = {"name": "Test", "damage": 5, "range": 3, "cooldown": 2, "projectile_speed": 10.0}
        tower = Tower(0, "test", config, 0, 0)
        
        # Manually set cooldown
        tower.cooldown = 2
        assert not tower.is_ready
        
        tower.tick()
        assert tower.cooldown == 1
        
        tower.tick()
        assert tower.cooldown == 0
        assert tower.is_ready


class TestProjectile:
    """Tests for projectile flight mechanics."""

    def test_projectile_flight_time(self):
        """Projectile should track flight time correctly."""
        projectile = Projectile(target_id=1, damage=5, flight_time=3, source_tower_id=0)
        
        assert not projectile.has_impacted
        assert projectile.time_elapsed == 0
        
        projectile.tick()
        assert projectile.time_elapsed == 1
        assert not projectile.has_impacted
        
        projectile.tick()
        projectile.tick()
        assert projectile.has_impacted


class TestGameMap:
    """Tests for map functionality."""

    def test_map_loads_correctly(self):
        """Map should load and validate positions."""
        config = {
            "width": 5,
            "height": 5,
            "spawn_point": [0, 2],
            "end_point": [4, 2],
            "path": [(0, 2), (1, 2), (2, 2), (3, 2), (4, 2)],
            "grid": [
                ["B", "B", "B", "B", "B"],
                ["B", "B", "B", "B", "B"],
                ["S", "P", "P", "P", "E"],
                ["B", "B", "B", "B", "B"],
                ["B", "B", "B", "B", "B"]
            ]
        }
        game_map = GameMap(config)
        
        assert game_map.width == 5
        assert game_map.height == 5
        assert game_map.spawn_point == (0, 2)
        assert game_map.end_point == (4, 2)

    def test_map_validates_positions(self):
        """Map should correctly validate coordinates."""
        config = {
            "width": 5,
            "height": 5,
            "spawn_point": [0, 2],
            "end_point": [4, 2],
            "path": [(0, 2)],
            "grid": [["B" for _ in range(5)] for _ in range(5)]
        }
        game_map = GameMap(config)
        
        assert game_map.is_valid_position(0, 0)
        assert game_map.is_valid_position(4, 4)
        assert not game_map.is_valid_position(5, 0)
        assert not game_map.is_valid_position(-1, 0)

    def test_map_buildable_cells(self):
        """Map should identify buildable cells."""
        config = {
            "width": 3,
            "height": 1,
            "spawn_point": [0, 0],
            "end_point": [2, 0],
            "path": [(0, 0), (1, 0), (2, 0)],
            "grid": [["S", "B", "E"]]
        }
        game_map = GameMap(config)
        
        assert game_map.is_buildable(1, 0)  # Build cell
        assert not game_map.is_buildable(0, 0)  # Spawn point (path)


class TestWaveManager:
    """Tests for wave spawning logic."""

    def test_wave_spawns_enemies(self):
        """Wave manager should spawn enemies according to config."""
        waves_config = [
            {"enemy_type": "basic", "count": 2, "spawn_interval": 1}
        ]
        enemies_config = {
            "basic": {"name": "Basic", "hp": 10, "speed": 0.5, "reward": 5}
        }
        path = [(0, 0), (1, 0)]
        
        wave_mgr = WaveManager(waves_config, enemies_config, path)
        
        # First update should spawn first enemy
        enemy1 = wave_mgr.update()
        assert enemy1 is not None
        assert enemy1.enemy_type == "basic"
        
        # Second update should spawn second enemy (interval=1)
        enemy2 = wave_mgr.update()
        assert enemy2 is not None
        
        # Third update should return None (wave complete)
        enemy3 = wave_mgr.update()
        assert enemy3 is None


class TestGameEngine:
    """Tests for main game engine."""

    def test_engine_initializes(self):
        """Game engine should initialize with correct state."""
        config_loader = ConfigLoader("config")
        config = config_loader.load_all("map_1")
        
        game = GameEngine(config)
        
        assert game.gold == 100
        assert game.lives == 5
        assert game.tick_count == 0
        assert not game.is_game_over

    def test_build_tower_success(self):
        """Should successfully build a tower when conditions are met."""
        config_loader = ConfigLoader("config")
        config = config_loader.load_all("map_1")
        
        game = GameEngine(config)
        success, message = game.build_tower("basic_tower", 1, 1)
        
        assert success
        assert len(game.towers) == 1
        assert game.gold == 80  # 100 - 20

    def test_build_tower_insufficient_gold(self):
        """Should fail to build tower when not enough gold."""
        config_loader = ConfigLoader("config")
        config = config_loader.load_all("map_1")
        
        game = GameEngine(config)
        # Build a basic tower first to reduce gold (100 - 20 = 80)
        game.build_tower("basic_tower", 1, 1)
        # Now try to build sniper tower (costs 40) with only 80 gold - should succeed
        # Let's build another basic tower: 80 - 20 = 60
        game.build_tower("basic_tower", 2, 1)
        # And another: 60 - 20 = 40
        game.build_tower("basic_tower", 3, 1)
        # Now we have 40 gold, sniper costs 40 - should succeed
        # Build one more basic: 40 - 20 = 20
        game.build_tower("basic_tower", 4, 1)
        # Now we have 20 gold, sniper costs 40 - should fail
        success, message = game.build_tower("sniper_tower", 5, 1)
        
        assert not success
        assert len(game.towers) == 4

    def test_build_tower_invalid_location(self):
        """Should fail to build tower on invalid location."""
        config_loader = ConfigLoader("config")
        config = config_loader.load_all("map_1")
        
        game = GameEngine(config)
        # Try to build outside map
        success, message = game.build_tower("basic_tower", 100, 100)
        
        assert not success

    def test_game_tick_processes(self):
        """Game tick should advance without errors."""
        config_loader = ConfigLoader("config")
        config = config_loader.load_all("map_1")
        
        game = GameEngine(config)
        result = game.tick()
        
        assert result == True  # Game continues
        assert game.tick_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

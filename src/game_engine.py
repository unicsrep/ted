"""
Main game engine module.
Orchestrates all game systems and manages the game loop.
"""

from typing import List, Dict, Optional, Tuple
from src.entities import Enemy, Tower, Projectile
from src.game_map import GameMap
from src.wave_manager import WaveManager
from src.config_loader import ConfigLoader


class GameEngine:
    """Main game engine managing all game logic."""

    def __init__(self, config: dict):
        # Initialize game state
        self.gold = config["game_settings"]["initial_gold"]
        self.lives = config["game_settings"]["initial_lives"]
        self.score = 0
        self.tick_count = 0
        
        # Initialize map
        self.game_map = GameMap(config["map"])
        
        # Initialize wave manager
        self.wave_manager = WaveManager(
            waves_config=config["game_settings"]["waves"],
            enemies_config=config["enemies"],
            path=self.game_map.path
        )
        
        # Entity collections
        self.enemies: List[Enemy] = []
        self.towers: List[Tower] = []
        self.projectiles: List[Projectile] = []
        
        # Tower configurations
        self.tower_configs = config["towers"]
        
        # Game state
        self.is_game_over = False
        self.is_victory = False
        
        # Event log
        self.event_log: List[str] = []

    def log_event(self, message: str):
        """Add an event to the log."""
        self.event_log.append(f"[Tick {self.tick_count}] {message}")
        # Keep only last 50 events
        if len(self.event_log) > 50:
            self.event_log = self.event_log[-50:]

    def build_tower(self, tower_type: str, x: int, y: int) -> Tuple[bool, str]:
        """
        Attempt to build a tower at specified location.
        Returns (success, message).
        """
        # Validate coordinates
        if not self.game_map.is_valid_position(x, y):
            return False, f"Invalid coordinates: ({x}, {y}) is outside map bounds."
        
        # Check if buildable
        if not self.game_map.is_buildable(x, y):
            return False, f"Cannot build on cell ({x}, {y}): not a buildable area."
        
        # Check if cell is occupied by another tower
        if any(t.x == x and t.y == y for t in self.towers):
            return False, f"Cell ({x}, {y}) is already occupied by a tower."
        
        # Get tower config
        if tower_type not in self.tower_configs:
            return False, f"Unknown tower type: {tower_type}. Available: {list(self.tower_configs.keys())}"
        
        tower_config = self.tower_configs[tower_type]
        cost = tower_config["cost"]
        
        # Check gold
        if self.gold < cost:
            return False, f"Not enough gold. Need {cost}, have {self.gold}."
        
        # Build tower
        tower_id = len(self.towers)
        tower = Tower(tower_id, tower_type, tower_config, x, y)
        self.towers.append(tower)
        self.gold -= cost
        
        self.log_event(f"Built {tower.name} at ({x}, {y}) for {cost} gold.")
        return True, f"Successfully built {tower.name} at ({x}, {y})."

    def _process_spawning(self):
        """Process enemy spawning."""
        new_enemy = self.wave_manager.update()
        if new_enemy:
            self.enemies.append(new_enemy)
            self.log_event(f"Enemy {new_enemy.name} (ID:{new_enemy.id}) spawned.")

    def _process_movement(self):
        """Process enemy movement."""
        enemies_reached_end = []
        
        for enemy in self.enemies:
            if enemy.is_alive and not enemy.has_reached_end:
                if enemy.move():
                    enemies_reached_end.append(enemy)
        
        # Handle enemies that reached the end
        for enemy in enemies_reached_end:
            self.lives -= 1
            self.log_event(f"Enemy {enemy.name} (ID:{enemy.id}) reached the end! Lives: {self.lives}")
            if self.lives <= 0:
                self.is_game_over = True
                self.is_victory = False

    def _process_combat(self):
        """Process tower targeting and firing."""
        # Reset tower cooldowns
        for tower in self.towers:
            tower.tick()
        
        # Each tower attempts to fire
        for tower in self.towers:
            if tower.is_ready:
                target = tower.find_target(self.enemies)
                if target:
                    projectile = tower.fire(target)
                    if projectile:
                        self.projectiles.append(projectile)
                        self.log_event(f"Tower {tower.name} (ID:{tower.id}) fired at Enemy ID:{target.id}.")

    def _process_projectiles(self):
        """Process projectile flight and impacts."""
        projectiles_to_remove = []
        
        for projectile in self.projectiles:
            projectile.tick()
            
            if projectile.has_impacted:
                # Find target
                target = next((e for e in self.enemies 
                              if e.id == projectile.target_id and e.is_alive), None)
                
                if target:
                    died = target.take_damage(projectile.damage)
                    if died:
                        self.gold += target.reward
                        self.score += target.reward
                        self.log_event(f"Enemy {target.name} (ID:{target.id}) destroyed! +{target.reward} gold.")
                    else:
                        self.log_event(f"Enemy ID:{target.id} hit for {projectile.damage} damage. HP: {target.hp}/{target.max_hp}")
                else:
                    self.log_event(f"Projectile missed (target ID:{projectile.target_id} no longer valid).")
                
                projectiles_to_remove.append(projectile)
        
        # Remove impacted projectiles
        for p in projectiles_to_remove:
            self.projectiles.remove(p)

    def _cleanup_dead_enemies(self):
        """Remove dead enemies from the list."""
        self.enemies = [e for e in self.enemies if e.is_alive]

    def _check_victory_condition(self):
        """Check if player has won."""
        if self.wave_manager.all_waves_complete and len(self.enemies) == 0:
            self.is_game_over = True
            self.is_victory = True
            self.log_event("VICTORY! All waves completed.")

    def tick(self) -> bool:
        """
        Execute one game tick.
        Returns False if game is over, True otherwise.
        """
        if self.is_game_over:
            return False
        
        self.tick_count += 1
        
        # Process phases
        self._process_spawning()
        self._process_movement()
        self._process_combat()
        self._process_projectiles()
        self._cleanup_dead_enemies()
        self._check_victory_condition()
        
        # Check defeat
        if self.lives <= 0:
            self.is_game_over = True
            self.is_victory = False
            self.log_event("DEFEAT! Lives depleted.")
        
        return not self.is_game_over

    def get_status(self) -> dict:
        """Get current game status."""
        wave_info = self.wave_manager.get_wave_info()
        return {
            "gold": self.gold,
            "lives": self.lives,
            "score": self.score,
            "tick": self.tick_count,
            "wave": wave_info["current_wave"],
            "total_waves": wave_info["total_waves"],
            "enemies_on_map": len([e for e in self.enemies if e.is_alive]),
            "towers_count": len(self.towers),
            "projectiles_in_flight": len(self.projectiles),
            "is_game_over": self.is_game_over,
            "is_victory": self.is_victory
        }

    def render(self) -> str:
        """Render current game state to string."""
        status = self.get_status()
        
        output = []
        output.append("=" * 40)
        output.append(f"TICK: {status['tick']} | WAVE: {status['wave']}/{status['total_waves']}")
        output.append(f"GOLD: {status['gold']} | LIVES: {status['lives']} | SCORE: {status['score']}")
        output.append(f"ENEMIES: {status['enemies_on_map']} | TOWERS: {status['towers_count']}")
        output.append("=" * 40)
        
        # Render map with entities
        output.append(self.game_map.render({
            "enemies": self.enemies,
            "towers": self.towers,
            "projectiles": self.projectiles
        }))
        
        # Show recent events
        if self.event_log:
            output.append("-" * 40)
            output.append("RECENT EVENTS:")
            for event in self.event_log[-5:]:
                output.append(f"  {event}")
        
        # Game over message
        if self.is_game_over:
            output.append("=" * 40)
            if self.is_victory:
                output.append("*** VICTORY! ***")
            else:
                output.append("*** DEFEAT! ***")
            output.append(f"FINAL SCORE: {self.score}")
            output.append("=" * 40)
        
        return "\n".join(output)

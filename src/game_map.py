"""
Map management module.
Handles map loading, path validation, and cell type queries.
"""

from typing import List, Tuple, Optional


class GameMap:
    """Represents the game map with grid, path, and buildable areas."""

    def __init__(self, config: dict):
        self.width = config["width"]
        self.height = config["height"]
        self.spawn_point = tuple(config["spawn_point"])
        self.end_point = tuple(config["end_point"])
        self.path = [tuple(p) for p in config["path"]]
        self.grid = config["grid"]  # 2D list of cell types
        
        # Cell type constants
        self.CELL_PATH = "P"
        self.CELL_BUILD = "B"
        self.CELL_OBSTACLE = "O"
        self.CELL_SPAWN = "S"
        self.CELL_END = "E"

    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if coordinates are within map bounds."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_cell_type(self, x: int, y: int) -> Optional[str]:
        """Get the type of cell at given coordinates."""
        if not self.is_valid_position(x, y):
            return None
        return self.grid[y][x]

    def is_buildable(self, x: int, y: int) -> bool:
        """Check if a tower can be built at given coordinates."""
        cell_type = self.get_cell_type(x, y)
        return cell_type in [self.CELL_BUILD, self.CELL_PATH]

    def is_path_cell(self, x: int, y: int) -> bool:
        """Check if cell is part of the enemy path."""
        return (x, y) in self.path

    def get_cell_symbol(self, x: int, y: int) -> str:
        """Get the display symbol for a cell."""
        cell_type = self.get_cell_type(x, y)
        if cell_type == self.CELL_PATH:
            return "."
        elif cell_type == self.CELL_BUILD:
            return " "
        elif cell_type == self.CELL_OBSTACLE:
            return "#"
        elif cell_type == self.CELL_SPAWN:
            return "S"
        elif cell_type == self.CELL_END:
            return "E"
        return "?"

    def render(self, entities: dict = None) -> str:
        """
        Render the map to a string representation.
        entities: dict with keys 'enemies', 'towers', 'projectiles'
        """
        if entities is None:
            entities = {"enemies": [], "towers": [], "projectiles": []}
        
        lines = []
        
        # Top border
        lines.append("+" + "-" * self.width + "+")
        
        for y in range(self.height):
            row = "|"
            for x in range(self.width):
                cell_type = self.get_cell_type(x, y)
                char = self.get_cell_symbol(x, y)
                
                # Check for towers
                tower = next((t for t in entities["towers"] if t.x == x and t.y == y), None)
                if tower:
                    char = "T"
                
                # Check for enemies (round positions for display)
                enemy = next((e for e in entities["enemies"] 
                             if e.is_alive and round(e.x) == x and round(e.y) == y), None)
                if enemy:
                    hp_pct = int(enemy.get_hp_percentage() * 100)
                    char = f"E{hp_pct // 10}"[:2]  # E9, E8, etc.
                
                # Check for projectiles (simplified - show on tower position)
                # In a real implementation, we'd track projectile positions
                
                row += char
            row += "|"
            lines.append(row)
        
        # Bottom border
        lines.append("+" + "-" * self.width + "+")
        
        return "\n".join(lines)

"""
Console interface for Tower Defense game.
Handles user input and game display.
"""

import sys
from src.config_loader import ConfigLoader
from src.game_engine import GameEngine


class ConsoleInterface:
    """Console-based user interface for the game."""

    def __init__(self, game: GameEngine):
        self.game = game
        self.commands = {
            'help': self.show_help,
            'status': self.show_status,
            'build': self.cmd_build,
            'tick': self.cmd_tick,
            'next': self.cmd_tick,
            'run': self.cmd_run,
            'map': self.show_map,
            'quit': self.cmd_quit,
            'exit': self.cmd_quit
        }

    def show_help(self, args=None):
        """Display available commands."""
        help_text = """
Available Commands:
  help              - Show this help message
  status            - Show current game status
  map               - Display the game map
  build <type> <x> <y> - Build a tower at coordinates (x, y)
  tick / next       - Execute one game tick
  run [n]           - Run n ticks (default: auto-run until game over)
  quit / exit       - Exit the game

Tower Types (check config/towers.json for details):
  - basic_tower: Cheap, balanced
  - sniper_tower: Long range, high damage, slow
  - rapid_tower: Fast fire rate, low damage

Examples:
  build basic_tower 1 3
  build sniper_tower 5 2
  tick
  run 10
"""
        return help_text.strip()

    def show_status(self, args=None):
        """Show detailed game status."""
        status = self.game.get_status()
        lines = [
            f"Game Status:",
            f"  Tick: {status['tick']}",
            f"  Wave: {status['wave']}/{status['total_waves']}",
            f"  Gold: {status['gold']}",
            f"  Lives: {status['lives']}",
            f"  Score: {status['score']}",
            f"  Enemies on map: {status['enemies_on_map']}",
            f"  Towers: {status['towers_count']}",
            f"  Projectiles in flight: {status['projectiles_in_flight']}",
            f"  Game Over: {status['is_game_over']}",
            f"  Victory: {status['is_victory']}"
        ]
        return "\n".join(lines)

    def show_map(self, args=None):
        """Display the game map."""
        return self.game.render()

    def cmd_build(self, args):
        """Handle build command."""
        if not args or len(args) < 3:
            return "Usage: build <tower_type> <x> <y>\nExample: build basic_tower 1 3"
        
        tower_type = args[0]
        try:
            x = int(args[1])
            y = int(args[2])
        except ValueError:
            return "Error: Coordinates must be integers."
        
        success, message = self.game.build_tower(tower_type, x, y)
        return message

    def cmd_tick(self, args=None):
        """Execute one game tick."""
        if self.game.is_game_over:
            return "Game is over. Type 'quit' to exit."
        
        self.game.tick()
        return self.game.render()

    def cmd_run(self, args=None):
        """Run multiple ticks automatically."""
        if self.game.is_game_over:
            return "Game is over."
        
        # Parse number of ticks or run until game over
        max_ticks = 999999  # Default to "until game over"
        if args and len(args) > 0:
            try:
                max_ticks = int(args[0])
            except ValueError:
                return "Error: Invalid number of ticks."
        
        ticks_run = 0
        while not self.game.is_game_over and ticks_run < max_ticks:
            self.game.tick()
            ticks_run += 1
            
            # Print progress every 5 ticks
            if ticks_run % 5 == 0:
                print(f"  ... Tick {self.game.tick_count} ...")
        
        return self.game.render()

    def cmd_quit(self, args=None):
        """Exit the game."""
        print("Thanks for playing!")
        sys.exit(0)

    def parse_command(self, input_line):
        """Parse user input into command and arguments."""
        parts = input_line.strip().split()
        if not parts:
            return None, []
        return parts[0].lower(), parts[1:]

    def process_command(self, input_line):
        """Process a user command and return output."""
        cmd, args = self.parse_command(input_line)
        
        if not cmd:
            return ""
        
        handler = self.commands.get(cmd)
        if handler:
            try:
                return handler(args)
            except Exception as e:
                return f"Error executing command: {e}"
        else:
            return f"Unknown command: {cmd}. Type 'help' for available commands."

    def run(self):
        """Main game loop."""
        print("=" * 50)
        print("   TOWER DEFENSE - Console Edition")
        print("=" * 50)
        print(self.show_help())
        print("\nInitial Game State:")
        print(self.game.render())
        
        while True:
            try:
                user_input = input("\nCommand> ").strip()
                if not user_input:
                    continue
                
                output = self.process_command(user_input)
                if output:
                    print(output)
                    
            except KeyboardInterrupt:
                print("\nGame interrupted.")
                break
            except EOFError:
                print("\nGoodbye!")
                break


def main():
    """Entry point for the console game."""
    # Load configuration
    config_loader = ConfigLoader("config")
    config = config_loader.load_all("map_1")
    
    # Create game engine
    game = GameEngine(config)
    
    # Create and run interface
    interface = ConsoleInterface(game)
    interface.run()


if __name__ == "__main__":
    main()

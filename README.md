# Tower Defense - Console Edition (MVP)

A Specification Driven Development (SDD) implementation of a Tower Defense game in Python.

## Project Structure

```
/workspace
├── config/                 # Configuration files
│   ├── game_settings.json  # Global game settings
│   ├── enemies.json        # Enemy type definitions
│   ├── towers.json         # Tower type definitions
│   └── maps/
│       └── map_1.json      # Map configuration
├── src/                    # Source code
│   ├── __init__.py
│   ├── config_loader.py    # Configuration file loader
│   ├── entities.py         # Enemy, Tower, Projectile classes
│   ├── game_map.py         # Map management
│   ├── wave_manager.py     # Wave spawning logic
│   ├── game_engine.py      # Main game engine
│   └── console_interface.py # Console UI
├── tests/                  # Unit tests
│   └── test_game.py
└── README.md
```

## Features Implemented

- ✅ Grid-based map with path, buildable areas, and obstacles
- ✅ Multiple enemy types with different HP, speed, and rewards
- ✅ Multiple tower types with different damage, range, cooldown
- ✅ Priority targeting (first enemy by path progress)
- ✅ Projectiles with flight time and guaranteed hits
- ✅ Wave-based enemy spawning
- ✅ Economy system (gold, lives, score)
- ✅ Console interface with interactive commands
- ✅ JSON configuration files for easy balancing
- ✅ Comprehensive unit tests

## How to Run

### Run Tests
```bash
cd /workspace
python -m pytest tests/test_game.py -v
```

### Play the Game
```bash
cd /workspace
PYTHONPATH=/workspace:$PYTHONPATH python src/console_interface.py
```

### Demo Script
```bash
python /tmp/play_game.py
```

## Console Commands

| Command | Description |
|---------|-------------|
| `help` | Show available commands |
| `status` | Show current game status |
| `map` | Display the game map |
| `build <type> <x> <y>` | Build a tower at coordinates |
| `tick` / `next` | Execute one game tick |
| `run [n]` | Run n ticks (or until game over) |
| `quit` / `exit` | Exit the game |

## Configuration Files

### game_settings.json
- `initial_gold`: Starting gold
- `initial_lives`: Starting lives
- `wave_interval`: Ticks between waves
- `waves`: Array of wave configurations

### enemies.json
Enemy types with:
- `hp`: Health points
- `speed`: Cells per tick
- `reward`: Gold on death

### towers.json
Tower types with:
- `cost`: Gold required
- `damage`: Damage per shot
- `range`: Targeting radius
- `cooldown`: Ticks between shots
- `projectile_speed`: Cells per tick

### maps/map_1.json
- `width`, `height`: Map dimensions
- `spawn_point`, `end_point`: Path endpoints
- `path`: Waypoint coordinates
- `grid`: Cell types (P=path, B=buildable, S=spawn, E=end)

## Architecture

The game follows a clean architecture pattern:
- **Entities**: Core game objects (Enemy, Tower, Projectile)
- **Managers**: Specialized logic (WaveManager)
- **Engine**: Orchestrates all systems (GameEngine)
- **Interface**: User interaction (ConsoleInterface)
- **Config**: Data-driven configuration (ConfigLoader)

## Next Steps (Post-MVP)

1. Add more tower types and enemy types
2. Implement special abilities (slow, splash damage)
3. Add multiple maps with different paths
4. Create graphical interface (Pygame, Unity)
5. Add save/load functionality
6. Implement leaderboards
7. Add sound effects and music

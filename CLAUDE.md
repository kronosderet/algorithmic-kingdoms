# Resonance

## Overview
Zero-asset Pygame RTS with algorithmic art (polar roses, L-systems, golden spirals, Mandelbrot menus).
Current version: v10_epsilon3. Working on v10 Economy Overhaul.

## Tech Stack
- Python 3.13, Pygame 2.6.1, NumPy
- PyInstaller for builds
- No external assets — all visuals generated algorithmically

## Common Commands
```bash
# Run the game
python main.py

# Check imports
python -c "from game import Game; print('OK')"

# Type check (pre-build gate — must pass with 0 errors)
pyright

# Build executable
python -m PyInstaller v10_epsilon3.spec --noconfirm
```

## Project Structure
- `main.py` — Entry point
- `constants.py` — All game constants, unit stats, building defs
- `unit.py` — Unit logic, physics, movement, state machine
- `building.py` — Building logic and rendering
- `building_shapes.py` — Algorithmic building shape helpers
- `entity_base.py` — Base entity class
- `projectiles.py` — Arrow/projectile system
- `game.py` — Main game loop, input handling, game logic
- `gui.py` — In-game HUD, selection panels, resource display
- `menu.py` — Main menu with Mandelbrot fractal background
- `camera.py` — Camera pan/zoom
- `pathfinding.py` — A* pathfinding
- `enemy_ai.py` — Wave spawning, enemy targeting, counter-pick AI
- `squads.py` — Squad formation system (Rose, Spiral, Sierpinski, Koch)
- `event_logger.py` — Game event logging
- `resources.py` — Resource manager
- `game_map.py` — Procedural map generation
- `utils.py` — Shared utilities
- `visuals/` — Visual PoC scripts
- `GDD_Current_v10.md` — Full spec of implemented systems
- `GDD_Roadmap.md` — Version pipeline and future design (v10-v12)

## Code Conventions
- All game constants in `constants.py` (UPPER_SNAKE_CASE)
- Unit classes in `unit.py` (Worker, Soldier, Archer)
- Building class in `building.py`
- Pygame coordinate system (top-left origin)
- Colors as RGB tuples
- No external asset files — everything is drawn with pygame.draw or algorithmic generation

## Important Notes
- The game uses a tile-based map with pixel-level unit positioning
- Enemy waves scale with difficulty and wave number
- Git remote: github.com/kronosderet/algorithmic-kingdoms (repo name predates rename to Resonance)

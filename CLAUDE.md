# Project Fractals — Algorithmic Kingdoms

## Overview
Zero-asset Pygame RTS with algorithmic art (polar roses, L-systems, golden spirals, Mandelbrot menus).
Current version: v10_2. Working on v10 Economy Overhaul.

## Tech Stack
- Python 3.10, Pygame 2.6.1, NumPy
- PyInstaller for builds
- No external assets — all visuals generated algorithmically

## Common Commands
```bash
# Must set PATH first in every bash session:
export PATH="/c/Users/krtek/AppData/Local/Programs/Python/Python310:/c/Users/krtek/AppData/Local/Programs/Python/Python310/Scripts:$PATH"

# Run the game
python main.py

# Check imports
python -c "from game import Game; print('OK')"

# Build executable
python -m PyInstaller v10_2.spec --noconfirm
```

## Project Structure
- `main.py` — Entry point
- `constants.py` — All game constants, unit stats, building defs
- `entities.py` — Units (Worker, Soldier, Archer) and Buildings (largest file ~106k)
- `game.py` — Main game loop, input handling, game logic
- `gui.py` — In-game HUD, selection panels, resource display
- `menu.py` — Main menu with algorithmic art background
- `camera.py` — Camera pan/zoom
- `pathfinding.py` — A* pathfinding
- `enemy_ai.py` — Wave spawning, enemy targeting, counter-pick AI
- `squads.py` — Squad formation system
- `event_logger.py` — Game event logging
- `resources.py` — Resource manager
- `game_map.py` — Procedural map generation
- `utils.py` — Shared utilities
- `visuals/` — Visual generation scripts
- `GDD_Current_v9.md` — Full spec of implemented systems
- `GDD_Roadmap.md` — Version pipeline and future design (v10-v12)

## Code Conventions
- All game constants in `constants.py` (UPPER_SNAKE_CASE)
- Entity classes in `entities.py` (Unit subclasses: Worker, Soldier, Archer; Building)
- Pygame coordinate system (top-left origin)
- Colors as RGB tuples
- No external asset files — everything is drawn with pygame.draw or algorithmic generation

## Important Notes
- Python is NOT on bash PATH by default — always export PATH first
- The game uses a tile-based map with pixel-level unit positioning
- Enemy waves scale with difficulty and wave number
- Git remote: github.com/kronosderet/algorithmic-kingdoms

# Medieval Village Simulator

A 2D medieval village builder strategy game built with **Python** and **Pygame**.

## Requirements
- Python 3.10+
- Pygame 2.5+

## Installation & Run

```bash
pip install pygame
python main.py
```

## Controls
| Key | Action |
|---|---|
| **WASD / Arrows** | Pan camera |
| **Scroll wheel** | Zoom in/out |
| **Middle mouse drag** | Pan camera |
| **Left click** | Select / Place building |
| **Right click** | Cancel placement / Deselect |
| **B** | Toggle build panel |
| **Space** | Pause / Resume |
| **1 / 2 / 3** | Normal / Fast / Fastest speed |
| **R** | Restart game |
| **ESC** | Cancel / Quit |

## How to Play
1. Start by building a **Hut** to house your 3 starting villagers
2. Build a **Woodcutter** near forests and a **Well** for water
3. Build a **Farm** on fertile land (green tiles) for wheat
4. Build a **Mill** and **Bakery** to turn wheat into bread (food)
5. Expand housing to attract more villagers via immigration
6. Keep your villagers fed and hydrated — they will die without food/water!
7. **Win** by reaching a population of 30

## Buildings
| Building | Cost | Function |
|---|---|---|
| Hut | 20W 5S | Houses 4 villagers |
| Farm | 25W | Produces wheat (fertile land) |
| Woodcutter | 10W | Produces wood (near forest) |
| Quarry | 15W 5S | Produces stone (on stone) |
| Well | 10W 10S | Produces water |
| Stockpile | 20W 10S | +100 storage |
| Granary | 15W 10S | +60 storage |
| Mill | 30W 15S | Wheat → Flour |
| Bakery | 30W 15S | Flour → Food |
| Hunter Lodge | 20W | Produces food (near forest) |

## Project Structure
```
main.py                 # Entry point
requirements.txt        # Dependencies
game/
  __init__.py
  constants.py          # All tuneable values
  enums.py              # Game enumerations
  camera.py             # Pan & zoom camera
  grid.py               # Procedural map generation
  time_manager.py       # Day/night cycle, seasons
  buildings.py          # Building definitions & instances
  resources.py          # Resource management
  villagers.py          # Villager AI & needs
  ui.py                 # HUD, panels, alerts
  game_manager.py       # Main game loop & orchestrator
```

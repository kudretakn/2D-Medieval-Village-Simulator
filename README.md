# 2D Medieval Village Simulator

A 2D strategy/city-builder/management game with a medieval theme, built in Unity.

## Overview

Build and manage a medieval village from scratch. Place buildings, assign workers, produce resources, and keep your villagers alive. Start with 3 settlers and grow your village to a thriving community of 30+.

## Core Gameplay

- **Build**: Place buildings on a tile-based map (farms, huts, wells, mills, bakeries, etc.)
- **Assign**: Send villagers to work in production buildings
- **Produce**: Create resources through production chains (Wheat → Flour → Bread)
- **Survive**: Keep villagers fed and hydrated — unmet needs lead to death
- **Grow**: Attract immigrants when food and housing are plentiful

## Current State: MVP

The MVP includes:
- 50×50 procedurally generated tile map (grass, water, forest, stone, fertile land)
- 9 building types (Woodcutter, Farm, Hut, Stockpile, Well, Granary, Mill, Bakery, Hunter's Lodge)
- Population system with hunger/thirst needs and starvation/dehydration death
- Day/night visual cycle
- Production chain system
- Auto-generated UI (no prefabs needed)
- Win condition: reach population 30

## Architecture

```
GameManager (orchestrator)
├── GridManager          — tile map, placement validation
├── CameraController     — pan/zoom (mouse + touch)
├── BuildingManager      — place/demolish buildings
├── ResourceManager      — village-wide resource stockpiles
├── PopulationManager    — villager spawning, needs, immigration
├── TimeManager          — day/night, speed control
├── BuildingPlacer       — ghost preview, placement input
├── SelectionManager     — click to inspect buildings/villagers
├── UIManager            — HUD, panels, alerts
└── DayNightCycle        — visual overlay
```

## How to Open

1. Install **Unity 2022.3 LTS** or newer
2. Open Unity Hub → "Add" → select this folder
3. Open the project. Unity will import packages and generate the Library folder.
4. Create an empty scene with a Camera and an empty GameObject named "Bootstrap"
5. Attach the `SceneBootstrap` component to the Bootstrap object
6. Press Play!

## Controls

- **WASD / Arrow Keys**: Pan camera
- **Mouse Scroll**: Zoom
- **Right-click drag**: Pan camera
- **Left-click**: Select / Place building
- **Escape**: Cancel placement / Close panels

## Project Structure

```
Assets/
├── Scripts/
│   ├── Core/           — SceneBootstrap
│   ├── Data/           — Enums, Constants, ScriptableObjects, BuildingDataFactory
│   ├── Managers/       — All system managers
│   ├── UI/             — UIManager, UISetup
│   ├── Utils/          — SpriteFactory
│   └── Villager/       — Villager entity
├── Scenes/             — (create MainScene in Unity)
├── Prefabs/            — (placeholder for future prefabs)
├── ScriptableObjects/  — (placeholder for SO assets)
└── Sprites/            — (placeholder for art assets)
```

## Development Roadmap

- [x] Phase 0: Project setup, architecture, core systems
- [ ] Phase 1: Playable prototype with core loop
- [ ] Phase 2: Survival loop (seasons, firewood, alerts)
- [ ] Phase 3: Production depth (chains, efficiency, upgrades)
- [ ] Phase 4: Society (happiness, stress, village levels)
- [ ] Phase 5: Economy & trade
- [ ] Phase 6: World & exploration
- [ ] Phase 7: Tech tree & events
- [ ] Phase 8: Polish & ship

## License

Private project.

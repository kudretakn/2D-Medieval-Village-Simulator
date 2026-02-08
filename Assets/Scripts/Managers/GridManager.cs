using UnityEngine;
using System.Collections.Generic;

namespace MedievalVillage
{
    /// <summary>
    /// Manages the tile-based grid map.
    /// Handles tile data, placement validation, and terrain generation.
    /// </summary>
    public class GridManager : MonoBehaviour
    {
        public static GridManager Instance { get; private set; }

        [Header("Map Settings")]
        [SerializeField] private int mapWidth = GameConstants.MAP_WIDTH;
        [SerializeField] private int mapHeight = GameConstants.MAP_HEIGHT;

        [Header("Tile Prefabs")]
        [SerializeField] private GameObject tilePrefab;
        [SerializeField] private Sprite grassSprite;
        [SerializeField] private Sprite waterSprite;
        [SerializeField] private Sprite forestSprite;
        [SerializeField] private Sprite stoneSprite;
        [SerializeField] private Sprite fertileSprite;

        // Grid data
        private TileType[,] tileGrid;
        private bool[,] occupiedGrid; // true if a building is placed on this tile
        private GameObject[,] tileObjects;

        public int MapWidth => mapWidth;
        public int MapHeight => mapHeight;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        /// <summary>
        /// Initialize the map grid. Call from GameManager on start.
        /// </summary>
        public void InitializeMap()
        {
            tileGrid = new TileType[mapWidth, mapHeight];
            occupiedGrid = new bool[mapWidth, mapHeight];
            tileObjects = new GameObject[mapWidth, mapHeight];

            GenerateMap();
            RenderMap();
        }

        /// <summary>
        /// Generate the tile map with a simple procedural layout.
        /// MVP: central clearing with surrounding forests and a river.
        /// </summary>
        private void GenerateMap()
        {
            // Fill with grass
            for (int x = 0; x < mapWidth; x++)
            {
                for (int y = 0; y < mapHeight; y++)
                {
                    tileGrid[x, y] = TileType.Grass;
                }
            }

            // River running vertically near center-left
            int riverX = mapWidth / 3;
            for (int y = 0; y < mapHeight; y++)
            {
                int offsetX = Mathf.RoundToInt(Mathf.PerlinNoise(0, y * 0.1f) * 2f);
                int rx = Mathf.Clamp(riverX + offsetX, 1, mapWidth - 2);
                tileGrid[rx, y] = TileType.Water;
                tileGrid[rx + 1, y] = TileType.Water;
            }

            // Forests around edges and scattered patches
            for (int x = 0; x < mapWidth; x++)
            {
                for (int y = 0; y < mapHeight; y++)
                {
                    if (tileGrid[x, y] != TileType.Grass) continue;

                    float distFromCenter = Vector2.Distance(
                        new Vector2(x, y),
                        new Vector2(mapWidth / 2f, mapHeight / 2f)
                    );

                    // Forest ring around edges
                    if (distFromCenter > mapWidth * 0.35f)
                    {
                        float noise = Mathf.PerlinNoise(x * 0.15f, y * 0.15f);
                        if (noise > 0.35f)
                            tileGrid[x, y] = TileType.Forest;
                    }

                    // Scattered forest patches
                    float patchNoise = Mathf.PerlinNoise(x * 0.2f + 100f, y * 0.2f + 100f);
                    if (patchNoise > 0.7f && distFromCenter > 8f)
                        tileGrid[x, y] = TileType.Forest;
                }
            }

            // Stone deposits in rocky hills area (upper right)
            for (int x = mapWidth * 2 / 3; x < mapWidth - 3; x++)
            {
                for (int y = mapHeight * 2 / 3; y < mapHeight - 3; y++)
                {
                    float noise = Mathf.PerlinNoise(x * 0.3f + 50f, y * 0.3f + 50f);
                    if (noise > 0.6f && tileGrid[x, y] == TileType.Grass)
                        tileGrid[x, y] = TileType.Stone;
                }
            }

            // Fertile land near river
            for (int x = 0; x < mapWidth; x++)
            {
                for (int y = 0; y < mapHeight; y++)
                {
                    if (tileGrid[x, y] != TileType.Grass) continue;

                    // Check proximity to water
                    bool nearWater = false;
                    for (int dx = -3; dx <= 3 && !nearWater; dx++)
                    {
                        for (int dy = -3; dy <= 3 && !nearWater; dy++)
                        {
                            int nx = x + dx, ny = y + dy;
                            if (nx >= 0 && nx < mapWidth && ny >= 0 && ny < mapHeight)
                            {
                                if (tileGrid[nx, ny] == TileType.Water)
                                    nearWater = true;
                            }
                        }
                    }

                    if (nearWater)
                    {
                        float noise = Mathf.PerlinNoise(x * 0.1f + 200f, y * 0.1f + 200f);
                        if (noise > 0.4f)
                            tileGrid[x, y] = TileType.FertileLand;
                    }
                }
            }

            // Clear starting area (center of map)
            int cx = mapWidth / 2;
            int cy = mapHeight / 2;
            for (int x = cx - 4; x <= cx + 4; x++)
            {
                for (int y = cy - 4; y <= cy + 4; y++)
                {
                    if (x >= 0 && x < mapWidth && y >= 0 && y < mapHeight)
                    {
                        if (tileGrid[x, y] != TileType.Water)
                            tileGrid[x, y] = TileType.Grass;
                    }
                }
            }
        }

        /// <summary>
        /// Instantiate tile GameObjects to visualize the map.
        /// </summary>
        private void RenderMap()
        {
            Transform mapParent = new GameObject("Map").transform;
            mapParent.SetParent(transform);

            for (int x = 0; x < mapWidth; x++)
            {
                for (int y = 0; y < mapHeight; y++)
                {
                    Vector3 pos = GridToWorld(x, y);
                    GameObject tile;

                    if (tilePrefab != null)
                    {
                        tile = Instantiate(tilePrefab, pos, Quaternion.identity, mapParent);
                    }
                    else
                    {
                        tile = new GameObject($"Tile_{x}_{y}");
                        tile.transform.position = pos;
                        tile.transform.SetParent(mapParent);
                        var sr = tile.AddComponent<SpriteRenderer>();
                        sr.sortingLayerName = "Terrain";
                        sr.sortingOrder = 0;
                    }

                    // Set sprite based on tile type
                    var renderer = tile.GetComponent<SpriteRenderer>();
                    if (renderer != null)
                    {
                        renderer.sprite = GetSpriteForTile(tileGrid[x, y]);
                        if (renderer.sprite == null)
                        {
                            // Fallback: color-coded squares
                            renderer.color = GetColorForTile(tileGrid[x, y]);
                        }
                    }

                    tileObjects[x, y] = tile;
                }
            }
        }

        private Sprite GetSpriteForTile(TileType type)
        {
            return type switch
            {
                TileType.Grass => grassSprite,
                TileType.Water => waterSprite,
                TileType.Forest => forestSprite,
                TileType.Stone => stoneSprite,
                TileType.FertileLand => fertileSprite,
                _ => grassSprite
            };
        }

        private Color GetColorForTile(TileType type)
        {
            return type switch
            {
                TileType.Grass => new Color(0.4f, 0.7f, 0.3f),
                TileType.Water => new Color(0.2f, 0.4f, 0.8f),
                TileType.Forest => new Color(0.15f, 0.45f, 0.15f),
                TileType.Stone => new Color(0.6f, 0.6f, 0.6f),
                TileType.FertileLand => new Color(0.55f, 0.45f, 0.2f),
                TileType.Sand => new Color(0.85f, 0.8f, 0.6f),
                TileType.IronDeposit => new Color(0.5f, 0.35f, 0.25f),
                _ => Color.magenta
            };
        }

        // === PUBLIC API ===

        /// <summary>
        /// Convert grid coordinates to world position.
        /// </summary>
        public Vector3 GridToWorld(int x, int y)
        {
            return new Vector3(
                x * GameConstants.TILE_SIZE,
                y * GameConstants.TILE_SIZE,
                0f
            );
        }

        /// <summary>
        /// Convert world position to grid coordinates.
        /// </summary>
        public Vector2Int WorldToGrid(Vector3 worldPos)
        {
            return new Vector2Int(
                Mathf.FloorToInt(worldPos.x / GameConstants.TILE_SIZE + 0.5f),
                Mathf.FloorToInt(worldPos.y / GameConstants.TILE_SIZE + 0.5f)
            );
        }

        /// <summary>
        /// Check if grid coordinates are within map bounds.
        /// </summary>
        public bool IsInBounds(int x, int y)
        {
            return x >= 0 && x < mapWidth && y >= 0 && y < mapHeight;
        }

        /// <summary>
        /// Check if a building can be placed at the given grid position.
        /// </summary>
        public bool CanPlaceBuilding(int x, int y, Vector2Int buildingSize, BuildingData buildingData)
        {
            for (int dx = 0; dx < buildingSize.x; dx++)
            {
                for (int dy = 0; dy < buildingSize.y; dy++)
                {
                    int tx = x + dx;
                    int ty = y + dy;

                    if (!IsInBounds(tx, ty)) return false;
                    if (occupiedGrid[tx, ty]) return false;
                    if (tileGrid[tx, ty] == TileType.Water) return false;
                }
            }

            // Check placement requirements
            if (buildingData != null)
            {
                if (buildingData.requiresAdjacentForest && !HasAdjacentTileType(x, y, buildingSize, TileType.Forest))
                    return false;
                if (buildingData.requiresAdjacentWater && !HasAdjacentTileType(x, y, buildingSize, TileType.Water))
                    return false;
                if (buildingData.requiresFertileLand && !IsTileArea(x, y, buildingSize, TileType.FertileLand))
                    return false;
                if (buildingData.requiresStoneDeposit && !HasAdjacentTileType(x, y, buildingSize, TileType.Stone))
                    return false;
            }

            return true;
        }

        /// <summary>
        /// Mark tiles as occupied when a building is placed.
        /// </summary>
        public void OccupyTiles(int x, int y, Vector2Int size)
        {
            for (int dx = 0; dx < size.x; dx++)
            {
                for (int dy = 0; dy < size.y; dy++)
                {
                    occupiedGrid[x + dx, y + dy] = true;
                }
            }
        }

        /// <summary>
        /// Free tiles when a building is demolished.
        /// </summary>
        public void FreeTiles(int x, int y, Vector2Int size)
        {
            for (int dx = 0; dx < size.x; dx++)
            {
                for (int dy = 0; dy < size.y; dy++)
                {
                    occupiedGrid[x + dx, y + dy] = false;
                }
            }
        }

        public TileType GetTileType(int x, int y)
        {
            if (!IsInBounds(x, y)) return TileType.Water; // treat out-of-bounds as impassable
            return tileGrid[x, y];
        }

        public bool IsOccupied(int x, int y)
        {
            if (!IsInBounds(x, y)) return true;
            return occupiedGrid[x, y];
        }

        public Vector3 GetMapCenter()
        {
            return GridToWorld(mapWidth / 2, mapHeight / 2);
        }

        // === HELPERS ===

        private bool HasAdjacentTileType(int x, int y, Vector2Int size, TileType type)
        {
            for (int dx = -1; dx <= size.x; dx++)
            {
                for (int dy = -1; dy <= size.y; dy++)
                {
                    // Skip interior tiles
                    if (dx >= 0 && dx < size.x && dy >= 0 && dy < size.y) continue;

                    int tx = x + dx, ty = y + dy;
                    if (IsInBounds(tx, ty) && tileGrid[tx, ty] == type)
                        return true;
                }
            }
            return false;
        }

        private bool IsTileArea(int x, int y, Vector2Int size, TileType type)
        {
            for (int dx = 0; dx < size.x; dx++)
            {
                for (int dy = 0; dy < size.y; dy++)
                {
                    int tx = x + dx, ty = y + dy;
                    if (!IsInBounds(tx, ty) || tileGrid[tx, ty] != type)
                        return false;
                }
            }
            return true;
        }
    }
}

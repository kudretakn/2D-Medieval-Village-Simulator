using UnityEngine;
using System.Collections.Generic;
using System;

namespace MedievalVillage
{
    /// <summary>
    /// Manages all placed buildings in the village.
    /// Handles placement, demolition, and building queries.
    /// </summary>
    public class BuildingManager : MonoBehaviour
    {
        public static BuildingManager Instance { get; private set; }

        /// <summary>Fires when a building is placed. (BuildingInstance)</summary>
        public event Action<BuildingInstance> OnBuildingPlaced;
        /// <summary>Fires when a building is demolished.</summary>
        public event Action<BuildingInstance> OnBuildingDemolished;

        [Header("Building Database")]
        [SerializeField] private BuildingData[] allBuildingTypes;

        [Header("Prefab")]
        [SerializeField] private GameObject buildingPrefab;

        private List<BuildingInstance> placedBuildings = new List<BuildingInstance>();

        public IReadOnlyList<BuildingInstance> PlacedBuildings => placedBuildings;
        public BuildingData[] AllBuildingTypes => allBuildingTypes;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        /// <summary>
        /// Attempt to place a building at the given grid position.
        /// Returns the BuildingInstance if successful, null otherwise.
        /// </summary>
        public BuildingInstance PlaceBuilding(BuildingData data, int gridX, int gridY)
        {
            // Validate placement
            if (!GridManager.Instance.CanPlaceBuilding(gridX, gridY, data.size, data))
            {
                Debug.Log($"Cannot place {data.buildingName} at ({gridX}, {gridY}): invalid location");
                return null;
            }

            // Check cost
            if (!data.CanAfford(ResourceManager.Instance))
            {
                Debug.Log($"Cannot afford {data.buildingName}");
                return null;
            }

            // Deduct cost
            data.DeductCosts(ResourceManager.Instance);

            // Mark tiles as occupied
            GridManager.Instance.OccupyTiles(gridX, gridY, data.size);

            // Create building GameObject
            Vector3 worldPos = GridManager.Instance.GridToWorld(gridX, gridY);
            // Center on footprint
            worldPos.x += (data.size.x - 1) * GameConstants.TILE_SIZE * 0.5f;
            worldPos.y += (data.size.y - 1) * GameConstants.TILE_SIZE * 0.5f;

            GameObject buildingGO;
            if (buildingPrefab != null)
            {
                buildingGO = Instantiate(buildingPrefab, worldPos, Quaternion.identity, transform);
            }
            else
            {
                buildingGO = new GameObject(data.buildingName);
                buildingGO.transform.position = worldPos;
                buildingGO.transform.SetParent(transform);
                var sr = buildingGO.AddComponent<SpriteRenderer>();
                sr.sortingLayerName = "Buildings";
                sr.sortingOrder = 1;
            }

            buildingGO.name = data.buildingName;

            // Set up sprite
            var renderer = buildingGO.GetComponent<SpriteRenderer>();
            if (renderer != null)
            {
                if (data.worldSprite != null)
                {
                    renderer.sprite = data.worldSprite;
                }
                else
                {
                    // Fallback: colored square based on category
                    renderer.color = GetCategoryColor(data.category);
                }
            }

            // Add collider for click detection
            var collider = buildingGO.AddComponent<BoxCollider2D>();
            collider.size = new Vector2(data.size.x * GameConstants.TILE_SIZE * 0.9f,
                                         data.size.y * GameConstants.TILE_SIZE * 0.9f);

            // Create BuildingInstance component
            var instance = buildingGO.AddComponent<BuildingInstance>();
            instance.Initialize(data, gridX, gridY);

            placedBuildings.Add(instance);

            // Register storage capacity
            if (data.generalStorageCapacity > 0)
                ResourceManager.Instance.AddGeneralStorage(data.generalStorageCapacity);
            if (data.foodStorageCapacity > 0)
                ResourceManager.Instance.AddFoodStorage(data.foodStorageCapacity);

            OnBuildingPlaced?.Invoke(instance);
            Debug.Log($"Placed {data.buildingName} at ({gridX}, {gridY})");

            return instance;
        }

        /// <summary>
        /// Demolish a building, freeing tiles and removing it.
        /// </summary>
        public void DemolishBuilding(BuildingInstance instance)
        {
            if (instance == null) return;

            // Free tiles
            GridManager.Instance.FreeTiles(instance.GridX, instance.GridY, instance.Data.size);

            // Remove storage capacity
            if (instance.Data.generalStorageCapacity > 0)
                ResourceManager.Instance.RemoveGeneralStorage(instance.Data.generalStorageCapacity);
            if (instance.Data.foodStorageCapacity > 0)
                ResourceManager.Instance.RemoveFoodStorage(instance.Data.foodStorageCapacity);

            // Unassign workers
            if (PopulationManager.Instance != null)
            {
                PopulationManager.Instance.UnassignWorkersFromBuilding(instance);
            }

            placedBuildings.Remove(instance);
            OnBuildingDemolished?.Invoke(instance);

            Destroy(instance.gameObject);
        }

        // === QUERIES ===

        public int GetBuildingCount()
        {
            return placedBuildings.Count;
        }

        public int GetBuildingCountOfType(BuildingData type)
        {
            int count = 0;
            foreach (var b in placedBuildings)
            {
                if (b.Data == type) count++;
            }
            return count;
        }

        public int GetTotalHousingCapacity()
        {
            int total = 0;
            foreach (var b in placedBuildings)
            {
                total += b.Data.housingCapacity;
            }
            return total;
        }

        public int GetTotalWaterProduction()
        {
            int total = 0;
            foreach (var b in placedBuildings)
            {
                total += b.Data.waterProductionPerDay;
            }
            return total;
        }

        /// <summary>
        /// Find nearby building of specific type for villager navigation.
        /// </summary>
        public BuildingInstance FindNearestBuilding(Vector3 fromPos, BuildingCategory category)
        {
            BuildingInstance nearest = null;
            float minDist = float.MaxValue;

            foreach (var b in placedBuildings)
            {
                if (b.Data.category != category) continue;
                float dist = Vector3.Distance(fromPos, b.transform.position);
                if (dist < minDist)
                {
                    minDist = dist;
                    nearest = b;
                }
            }

            return nearest;
        }

        public List<BuildingInstance> GetBuildingsWithAvailableWorkerSlots()
        {
            var result = new List<BuildingInstance>();
            foreach (var b in placedBuildings)
            {
                if (b.Data.maxWorkers > 0 && b.AssignedWorkerCount < b.Data.maxWorkers)
                    result.Add(b);
            }
            return result;
        }

        public List<BuildingInstance> GetHousingWithVacancy()
        {
            var result = new List<BuildingInstance>();
            foreach (var b in placedBuildings)
            {
                if (b.Data.housingCapacity > 0 && b.ResidentCount < b.Data.housingCapacity)
                    result.Add(b);
            }
            return result;
        }

        /// <summary>
        /// Get available building types for current village tier.
        /// </summary>
        public List<BuildingData> GetAvailableBuildingTypes(VillageTier currentTier)
        {
            var result = new List<BuildingData>();
            if (allBuildingTypes == null) return result;

            foreach (var data in allBuildingTypes)
            {
                if ((int)data.unlockTier <= (int)currentTier)
                    result.Add(data);
            }
            return result;
        }

        private Color GetCategoryColor(BuildingCategory category)
        {
            return category switch
            {
                BuildingCategory.Resources => new Color(0.6f, 0.4f, 0.2f),  // Brown
                BuildingCategory.Food => new Color(0.9f, 0.8f, 0.2f),       // Yellow
                BuildingCategory.Housing => new Color(0.8f, 0.5f, 0.3f),    // Orange
                BuildingCategory.Storage => new Color(0.5f, 0.5f, 0.7f),    // Blue-gray
                BuildingCategory.Services => new Color(0.7f, 0.3f, 0.7f),   // Purple
                BuildingCategory.Production => new Color(0.3f, 0.6f, 0.9f), // Blue
                BuildingCategory.Defense => new Color(0.7f, 0.2f, 0.2f),    // Red
                _ => Color.white
            };
        }
    }
}

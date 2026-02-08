using UnityEngine;
using System.Collections.Generic;
using System;

namespace MedievalVillage
{
    /// <summary>
    /// Manages village-wide resource stockpiles.
    /// Tracks all resource types, storage capacity, and provides add/remove/query API.
    /// </summary>
    public class ResourceManager : MonoBehaviour
    {
        public static ResourceManager Instance { get; private set; }

        /// <summary>Fires when any resource amount changes. (type, newAmount)</summary>
        public event Action<ResourceType, int> OnResourceChanged;

        // Current resource stocks
        private Dictionary<ResourceType, int> stocks = new Dictionary<ResourceType, int>();

        // Storage capacity per resource category
        private int totalGeneralStorage = 0;
        private int totalFoodStorage = 0;

        // Track which resources are food
        private HashSet<ResourceType> foodResources = new HashSet<ResourceType>
        {
            ResourceType.Wheat, ResourceType.Flour, ResourceType.Bread,
            ResourceType.RawMeat, ResourceType.DriedMeat, ResourceType.RawFish,
            ResourceType.SaltedFish, ResourceType.WildBerries, ResourceType.Barley,
            ResourceType.Ale
        };

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            InitializeStocks();
        }

        private void InitializeStocks()
        {
            foreach (ResourceType type in Enum.GetValues(typeof(ResourceType)))
            {
                stocks[type] = 0;
            }

            // Starting resources (per MVP: enough to build initial buildings)
            stocks[ResourceType.Wood] = 50;
            stocks[ResourceType.Stone] = 20;
            stocks[ResourceType.Wheat] = 20;
            stocks[ResourceType.Water] = 30;
        }

        // === PUBLIC API ===

        public int GetResourceAmount(ResourceType type)
        {
            return stocks.TryGetValue(type, out int amount) ? amount : 0;
        }

        public bool HasResource(ResourceType type, int amount)
        {
            return GetResourceAmount(type) >= amount;
        }

        /// <summary>
        /// Add resources to the stockpile. Returns amount actually added
        /// (may be less if storage is full).
        /// </summary>
        public int AddResource(ResourceType type, int amount)
        {
            if (amount <= 0) return 0;

            int currentTotal = GetTotalResourcesStored(IsFood(type));
            int capacity = IsFood(type) ? totalFoodStorage + totalGeneralStorage : totalGeneralStorage;

            // If no storage buildings yet, allow a base amount (starting camp)
            if (capacity == 0) capacity = GameConstants.STOCKPILE_CAPACITY;

            int space = Mathf.Max(0, capacity - currentTotal);
            int toAdd = Mathf.Min(amount, space);

            if (toAdd > 0)
            {
                stocks[type] += toAdd;
                OnResourceChanged?.Invoke(type, stocks[type]);
            }

            return toAdd;
        }

        /// <summary>
        /// Remove resources from the stockpile. Returns true if successful.
        /// </summary>
        public bool RemoveResource(ResourceType type, int amount)
        {
            if (amount <= 0) return true;
            if (stocks[type] < amount) return false;

            stocks[type] -= amount;
            OnResourceChanged?.Invoke(type, stocks[type]);
            return true;
        }

        /// <summary>
        /// Try to consume resources (e.g., for villager needs). Returns amount actually consumed.
        /// </summary>
        public int ConsumeResource(ResourceType type, int desiredAmount)
        {
            int available = GetResourceAmount(type);
            int consumed = Mathf.Min(available, desiredAmount);
            if (consumed > 0)
            {
                stocks[type] -= consumed;
                OnResourceChanged?.Invoke(type, stocks[type]);
            }
            return consumed;
        }

        // === STORAGE CAPACITY ===

        public void AddGeneralStorage(int capacity)
        {
            totalGeneralStorage += capacity;
        }

        public void RemoveGeneralStorage(int capacity)
        {
            totalGeneralStorage = Mathf.Max(0, totalGeneralStorage - capacity);
        }

        public void AddFoodStorage(int capacity)
        {
            totalFoodStorage += capacity;
        }

        public void RemoveFoodStorage(int capacity)
        {
            totalFoodStorage = Mathf.Max(0, totalFoodStorage - capacity);
        }

        public int GetTotalStorageCapacity()
        {
            int cap = totalGeneralStorage + totalFoodStorage;
            return cap > 0 ? cap : GameConstants.STOCKPILE_CAPACITY; // base capacity
        }

        // === QUERIES ===

        /// <summary>
        /// Get total food resource count (for HUD display).
        /// </summary>
        public int GetTotalFood()
        {
            int total = 0;
            foreach (var type in foodResources)
            {
                total += GetResourceAmount(type);
            }
            return total;
        }

        /// <summary>
        /// Get total count of all stored resources of the given food category.
        /// </summary>
        private int GetTotalResourcesStored(bool foodOnly)
        {
            int total = 0;
            foreach (var kvp in stocks)
            {
                if (foodOnly && !IsFood(kvp.Key)) continue;
                total += kvp.Value;
            }
            return total;
        }

        /// <summary>
        /// Returns the number of days food will last based on current population.
        /// </summary>
        public float GetFoodDaysRemaining(int populationCount)
        {
            if (populationCount <= 0) return float.MaxValue;
            float dailyConsumption = populationCount * (GameConstants.FOOD_PER_ADULT_12H * 2f);
            int totalFood = GetTotalFood();
            return totalFood / Mathf.Max(0.01f, dailyConsumption);
        }

        public bool IsFood(ResourceType type)
        {
            return foodResources.Contains(type);
        }

        /// <summary>
        /// Consume 1 unit of any available food. Returns true if fed successfully.
        /// Priority: Bread > Wheat > RawMeat > WildBerries > other food.
        /// </summary>
        public bool ConsumeAnyFood(int amount = 1)
        {
            ResourceType[] priority = {
                ResourceType.Bread,
                ResourceType.DriedMeat,
                ResourceType.SaltedFish,
                ResourceType.Wheat,
                ResourceType.RawMeat,
                ResourceType.RawFish,
                ResourceType.WildBerries,
                ResourceType.Flour,
                ResourceType.Barley,
                ResourceType.Ale
            };

            int remaining = amount;
            foreach (var type in priority)
            {
                if (remaining <= 0) break;
                int consumed = ConsumeResource(type, remaining);
                remaining -= consumed;
            }

            return remaining <= 0;
        }
    }
}

using UnityEngine;

namespace MedievalVillage
{
    /// <summary>
    /// Data definition for a building type.
    /// Create instances via Assets > Create > MedievalVillage > BuildingData.
    /// </summary>
    [CreateAssetMenu(fileName = "NewBuilding", menuName = "MedievalVillage/BuildingData")]
    public class BuildingData : ScriptableObject
    {
        [Header("Identity")]
        public string buildingName;
        [TextArea] public string description;
        public BuildingCategory category;
        public VillageTier unlockTier = VillageTier.Camp;

        [Header("Visuals")]
        public Sprite icon;
        public Sprite worldSprite;
        public Vector2Int size = Vector2Int.one; // Grid footprint (e.g., 2x2)
        public Color ghostValidColor = new Color(0f, 1f, 0f, 0.5f);
        public Color ghostInvalidColor = new Color(1f, 0f, 0f, 0.5f);

        [Header("Construction Cost")]
        public ResourceCost[] constructionCosts;

        [Header("Workers")]
        public int minWorkers = 0;
        public int maxWorkers = 0;

        [Header("Production")]
        public ResourceAmount[] inputResources;
        public ResourceAmount[] outputResources;
        /// <summary>Game hours between production cycles.</summary>
        public float productionIntervalHours = 12f;

        [Header("Housing")]
        public int housingCapacity = 0;
        public int comfortValue = 0;

        [Header("Storage")]
        public int generalStorageCapacity = 0;
        public int foodStorageCapacity = 0;

        [Header("Water")]
        /// <summary>Water units produced per game-day (for wells).</summary>
        public int waterProductionPerDay = 0;

        [Header("Placement Requirements")]
        public bool requiresAdjacentForest = false;
        public bool requiresAdjacentWater = false;
        public bool requiresFertileLand = false;
        public bool requiresStoneDeposit = false;

        /// <summary>
        /// Check if the player can afford to build this.
        /// </summary>
        public bool CanAfford(ResourceManager resourceManager)
        {
            foreach (var cost in constructionCosts)
            {
                if (resourceManager.GetResourceAmount(cost.resourceType) < cost.amount)
                    return false;
            }
            return true;
        }

        /// <summary>
        /// Deduct construction costs from resource manager.
        /// </summary>
        public void DeductCosts(ResourceManager resourceManager)
        {
            foreach (var cost in constructionCosts)
            {
                resourceManager.RemoveResource(cost.resourceType, cost.amount);
            }
        }
    }

    /// <summary>
    /// Resource cost entry for construction.
    /// </summary>
    [System.Serializable]
    public struct ResourceCost
    {
        public ResourceType resourceType;
        public int amount;
    }

    /// <summary>
    /// Resource amount entry for production input/output.
    /// </summary>
    [System.Serializable]
    public struct ResourceAmount
    {
        public ResourceType resourceType;
        public int amount;
    }
}

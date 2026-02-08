using UnityEngine;

namespace MedievalVillage
{
    /// <summary>
    /// Creates BuildingData ScriptableObjects at runtime for MVP.
    /// Use this when no pre-made ScriptableObject assets exist in the project.
    /// Attach to Bootstrap GameObject.
    /// </summary>
    public class BuildingDataFactory : MonoBehaviour
    {
        public static BuildingData[] CreateMVPBuildings()
        {
            return new BuildingData[]
            {
                CreateWoodcutter(),
                CreateFarm(),
                CreateHut(),
                CreateStockpile(),
                CreateWell(),
                CreateGranary(),
                CreateMill(),
                CreateBakery(),
                CreateHunterLodge()
            };
        }

        private static BuildingData CreateWoodcutter()
        {
            var data = ScriptableObject.CreateInstance<BuildingData>();
            data.buildingName = "Woodcutter's Hut";
            data.description = "Produces wood and firewood from nearby trees.";
            data.category = BuildingCategory.Resources;
            data.unlockTier = VillageTier.Camp;
            data.size = Vector2Int.one;
            data.constructionCosts = new ResourceCost[]
            {
                new ResourceCost { resourceType = ResourceType.Wood, amount = 10 }
            };
            data.minWorkers = 1;
            data.maxWorkers = 2;
            data.inputResources = new ResourceAmount[0];
            data.outputResources = new ResourceAmount[]
            {
                new ResourceAmount { resourceType = ResourceType.Wood, amount = 3 },
                new ResourceAmount { resourceType = ResourceType.Firewood, amount = 1 }
            };
            data.productionIntervalHours = 8f;
            data.requiresAdjacentForest = true;
            return data;
        }

        private static BuildingData CreateFarm()
        {
            var data = ScriptableObject.CreateInstance<BuildingData>();
            data.buildingName = "Farm";
            data.description = "Grows wheat on fertile land.";
            data.category = BuildingCategory.Food;
            data.unlockTier = VillageTier.Camp;
            data.size = new Vector2Int(2, 2);
            data.constructionCosts = new ResourceCost[]
            {
                new ResourceCost { resourceType = ResourceType.Wood, amount = 15 }
            };
            data.minWorkers = 2;
            data.maxWorkers = 4;
            data.inputResources = new ResourceAmount[0];
            data.outputResources = new ResourceAmount[]
            {
                new ResourceAmount { resourceType = ResourceType.Wheat, amount = 5 }
            };
            data.productionIntervalHours = 12f;
            data.requiresFertileLand = true;
            return data;
        }

        private static BuildingData CreateHut()
        {
            var data = ScriptableObject.CreateInstance<BuildingData>();
            data.buildingName = "Wooden Hut";
            data.description = "Provides shelter for up to 4 villagers.";
            data.category = BuildingCategory.Housing;
            data.unlockTier = VillageTier.Camp;
            data.size = Vector2Int.one;
            data.constructionCosts = new ResourceCost[]
            {
                new ResourceCost { resourceType = ResourceType.Wood, amount = 20 }
            };
            data.housingCapacity = 4;
            data.comfortValue = 30;
            return data;
        }

        private static BuildingData CreateStockpile()
        {
            var data = ScriptableObject.CreateInstance<BuildingData>();
            data.buildingName = "Stockpile";
            data.description = "Stores up to 200 units of resources.";
            data.category = BuildingCategory.Storage;
            data.unlockTier = VillageTier.Camp;
            data.size = new Vector2Int(2, 2);
            data.constructionCosts = new ResourceCost[]
            {
                new ResourceCost { resourceType = ResourceType.Wood, amount = 5 }
            };
            data.generalStorageCapacity = GameConstants.STOCKPILE_CAPACITY;
            return data;
        }

        private static BuildingData CreateWell()
        {
            var data = ScriptableObject.CreateInstance<BuildingData>();
            data.buildingName = "Well";
            data.description = "Provides fresh water for your villagers.";
            data.category = BuildingCategory.Resources;
            data.unlockTier = VillageTier.Camp;
            data.size = Vector2Int.one;
            data.constructionCosts = new ResourceCost[]
            {
                new ResourceCost { resourceType = ResourceType.Wood, amount = 15 },
                new ResourceCost { resourceType = ResourceType.Stone, amount = 10 }
            };
            data.waterProductionPerDay = 50;
            return data;
        }

        private static BuildingData CreateGranary()
        {
            var data = ScriptableObject.CreateInstance<BuildingData>();
            data.buildingName = "Granary";
            data.description = "Stores up to 500 units of food with reduced spoilage.";
            data.category = BuildingCategory.Storage;
            data.unlockTier = VillageTier.Hamlet;
            data.size = new Vector2Int(2, 2);
            data.constructionCosts = new ResourceCost[]
            {
                new ResourceCost { resourceType = ResourceType.Wood, amount = 25 },
                new ResourceCost { resourceType = ResourceType.Stone, amount = 10 }
            };
            data.foodStorageCapacity = GameConstants.GRANARY_CAPACITY;
            return data;
        }

        private static BuildingData CreateMill()
        {
            var data = ScriptableObject.CreateInstance<BuildingData>();
            data.buildingName = "Mill";
            data.description = "Grinds wheat into flour.";
            data.category = BuildingCategory.Production;
            data.unlockTier = VillageTier.Camp; // Unlocked from start for MVP
            data.size = new Vector2Int(2, 2);
            data.constructionCosts = new ResourceCost[]
            {
                new ResourceCost { resourceType = ResourceType.Wood, amount = 20 },
                new ResourceCost { resourceType = ResourceType.Stone, amount = 15 }
            };
            data.minWorkers = 1;
            data.maxWorkers = 2;
            data.inputResources = new ResourceAmount[]
            {
                new ResourceAmount { resourceType = ResourceType.Wheat, amount = 3 }
            };
            data.outputResources = new ResourceAmount[]
            {
                new ResourceAmount { resourceType = ResourceType.Flour, amount = 3 }
            };
            data.productionIntervalHours = 8f;
            return data;
        }

        private static BuildingData CreateBakery()
        {
            var data = ScriptableObject.CreateInstance<BuildingData>();
            data.buildingName = "Bakery";
            data.description = "Bakes bread from flour. Bread is the most efficient food source.";
            data.category = BuildingCategory.Production;
            data.unlockTier = VillageTier.Camp; // Unlocked from start for MVP
            data.size = new Vector2Int(2, 2);
            data.constructionCosts = new ResourceCost[]
            {
                new ResourceCost { resourceType = ResourceType.Wood, amount = 20 },
                new ResourceCost { resourceType = ResourceType.Stone, amount = 10 }
            };
            data.minWorkers = 1;
            data.maxWorkers = 2;
            data.inputResources = new ResourceAmount[]
            {
                new ResourceAmount { resourceType = ResourceType.Flour, amount = 2 },
                new ResourceAmount { resourceType = ResourceType.Firewood, amount = 1 }
            };
            data.outputResources = new ResourceAmount[]
            {
                new ResourceAmount { resourceType = ResourceType.Bread, amount = 4 }
            };
            data.productionIntervalHours = 6f;
            return data;
        }

        private static BuildingData CreateHunterLodge()
        {
            var data = ScriptableObject.CreateInstance<BuildingData>();
            data.buildingName = "Hunter's Lodge";
            data.description = "Hunts animals in nearby forests for meat.";
            data.category = BuildingCategory.Food;
            data.unlockTier = VillageTier.Camp;
            data.size = Vector2Int.one;
            data.constructionCosts = new ResourceCost[]
            {
                new ResourceCost { resourceType = ResourceType.Wood, amount = 15 }
            };
            data.minWorkers = 1;
            data.maxWorkers = 2;
            data.inputResources = new ResourceAmount[0];
            data.outputResources = new ResourceAmount[]
            {
                new ResourceAmount { resourceType = ResourceType.RawMeat, amount = 2 }
            };
            data.productionIntervalHours = 10f;
            data.requiresAdjacentForest = true;
            return data;
        }
    }
}

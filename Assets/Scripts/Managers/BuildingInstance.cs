using UnityEngine;
using System.Collections.Generic;

namespace MedievalVillage
{
    /// <summary>
    /// Runtime instance of a placed building.
    /// Tracks workers, residents, production state.
    /// </summary>
    public class BuildingInstance : MonoBehaviour
    {
        public BuildingData Data { get; private set; }
        public int GridX { get; private set; }
        public int GridY { get; private set; }

        // Workers assigned to this building
        private List<Villager> assignedWorkers = new List<Villager>();
        // Residents living in this building (housing only)
        private List<Villager> residents = new List<Villager>();

        // Production state
        private float productionTimer;
        private bool isProducing;

        public int AssignedWorkerCount => assignedWorkers.Count;
        public int ResidentCount => residents.Count;
        public IReadOnlyList<Villager> AssignedWorkers => assignedWorkers;
        public IReadOnlyList<Villager> Residents => residents;

        public void Initialize(BuildingData data, int gridX, int gridY)
        {
            Data = data;
            GridX = gridX;
            GridY = gridY;
            productionTimer = 0f;
            isProducing = data.outputResources != null && data.outputResources.Length > 0;
        }

        /// <summary>
        /// Called by TimeManager every game hour to process production.
        /// </summary>
        public void ProcessProductionTick()
        {
            if (!isProducing) return;
            if (Data.maxWorkers > 0 && assignedWorkers.Count == 0) return;

            productionTimer += 1f; // +1 game hour

            if (productionTimer >= Data.productionIntervalHours)
            {
                productionTimer = 0f;
                TryProduce();
            }
        }

        private void TryProduce()
        {
            // Check if inputs are available
            if (Data.inputResources != null)
            {
                foreach (var input in Data.inputResources)
                {
                    if (!ResourceManager.Instance.HasResource(input.resourceType, input.amount))
                        return; // Not enough input
                }

                // Consume inputs
                foreach (var input in Data.inputResources)
                {
                    ResourceManager.Instance.RemoveResource(input.resourceType, input.amount);
                }
            }

            // Calculate efficiency
            float efficiency = GetEfficiency();

            // Produce outputs
            if (Data.outputResources != null)
            {
                foreach (var output in Data.outputResources)
                {
                    int amount = Mathf.Max(1, Mathf.RoundToInt(output.amount * efficiency));
                    ResourceManager.Instance.AddResource(output.resourceType, amount);
                }
            }

            // Water production (wells)
            if (Data.waterProductionPerDay > 0)
            {
                int waterPerTick = Mathf.Max(1, Data.waterProductionPerDay / GameConstants.HOURS_PER_DAY);
                ResourceManager.Instance.AddResource(ResourceType.Water, waterPerTick);
            }
        }

        /// <summary>
        /// Calculate production efficiency based on worker count and villager stats.
        /// </summary>
        public float GetEfficiency()
        {
            if (Data.maxWorkers == 0) return 1f; // No workers needed (storage, well, etc.)

            // Worker ratio efficiency
            float workerRatio = (float)assignedWorkers.Count / Data.maxWorkers;

            // Average worker health/need penalty
            float avgPenalty = 1f;
            if (assignedWorkers.Count > 0)
            {
                float totalPenalty = 0f;
                foreach (var worker in assignedWorkers)
                {
                    totalPenalty += worker.GetWorkEfficiency();
                }
                avgPenalty = totalPenalty / assignedWorkers.Count;
            }

            return workerRatio * avgPenalty;
        }

        // === WORKER MANAGEMENT ===

        public bool CanAssignWorker()
        {
            return Data.maxWorkers > 0 && assignedWorkers.Count < Data.maxWorkers;
        }

        public bool AssignWorker(Villager villager)
        {
            if (!CanAssignWorker()) return false;
            if (assignedWorkers.Contains(villager)) return false;

            assignedWorkers.Add(villager);
            villager.AssignToWorkplace(this);
            return true;
        }

        public void RemoveWorker(Villager villager)
        {
            assignedWorkers.Remove(villager);
        }

        // === RESIDENT MANAGEMENT ===

        public bool CanAddResident()
        {
            return Data.housingCapacity > 0 && residents.Count < Data.housingCapacity;
        }

        public bool AddResident(Villager villager)
        {
            if (!CanAddResident()) return false;
            if (residents.Contains(villager)) return false;

            residents.Add(villager);
            villager.AssignToHome(this);
            return true;
        }

        public void RemoveResident(Villager villager)
        {
            residents.Remove(villager);
        }
    }
}

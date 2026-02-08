using UnityEngine;
using System.Collections.Generic;
using System;

namespace MedievalVillage
{
    /// <summary>
    /// Manages all villagers: spawning, needs ticking, immigration, death tracking.
    /// </summary>
    public class PopulationManager : MonoBehaviour
    {
        public static PopulationManager Instance { get; private set; }

        /// <summary>Fires when population count changes.</summary>
        public event Action<int> OnPopulationChanged;
        /// <summary>Fires when a villager dies. (villager, cause)</summary>
        public event Action<Villager, string> OnVillagerDeath;
        /// <summary>Fires when a new villager arrives.</summary>
        public event Action<Villager> OnVillagerArrived;

        [Header("Villager Prefab")]
        [SerializeField] private GameObject villagerPrefab;

        [Header("Name Pool")]
        [SerializeField] private string[] maleNames = {
            "Aldric", "Bran", "Cedric", "Dunstan", "Edmund", "Falk",
            "Gareth", "Harald", "Ivar", "Jarvis", "Kenric", "Lothar",
            "Magnus", "Norbert", "Oswin", "Percival", "Ranulf", "Sigurd",
            "Theron", "Ulric", "Walden", "Yorick"
        };
        [SerializeField] private string[] femaleNames = {
            "Aelith", "Brigid", "Celia", "Dagna", "Elara", "Freya",
            "Greta", "Hilda", "Isolde", "Jocelyn", "Katla", "Lena",
            "Maren", "Nessa", "Olwen", "Petra", "Ragna", "Sigrid",
            "Thora", "Una", "Vivian", "Willa"
        };

        private List<Villager> allVillagers = new List<Villager>();
        private List<Villager> deadVillagers = new List<Villager>();
        private float immigrationTimer = 0f;
        private int mealTickCounter = 0;

        public int PopulationCount => allVillagers.Count;
        public IReadOnlyList<Villager> AllVillagers => allVillagers;
        public int DeathCount => deadVillagers.Count;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        /// <summary>
        /// Subscribe to time events.
        /// </summary>
        public void Initialize()
        {
            if (TimeManager.Instance != null)
            {
                TimeManager.Instance.OnGameHourTick += OnHourTick;
            }
        }

        private void OnDestroy()
        {
            if (TimeManager.Instance != null)
            {
                TimeManager.Instance.OnGameHourTick -= OnHourTick;
            }
        }

        /// <summary>
        /// Spawn initial settlers at the center of the map.
        /// </summary>
        public void SpawnInitialVillagers()
        {
            Vector3 center = GridManager.Instance.GetMapCenter();

            for (int i = 0; i < GameConstants.STARTING_VILLAGERS; i++)
            {
                Vector3 offset = new Vector3(
                    UnityEngine.Random.Range(-2f, 2f),
                    UnityEngine.Random.Range(-2f, 2f),
                    0
                );
                SpawnVillager(center + offset);
            }
        }

        /// <summary>
        /// Spawn a single villager at the given world position.
        /// </summary>
        public Villager SpawnVillager(Vector3 position, string name = null, int age = -1)
        {
            GameObject go;
            if (villagerPrefab != null)
            {
                go = Instantiate(villagerPrefab, position, Quaternion.identity, transform);
            }
            else
            {
                go = new GameObject("Villager");
                go.transform.position = position;
                go.transform.SetParent(transform);

                var sr = go.AddComponent<SpriteRenderer>();
                sr.sortingLayerName = "Villagers";
                sr.sortingOrder = 2;
                sr.color = new Color(0.9f, 0.75f, 0.6f);

                // Add collider for click detection
                var col = go.AddComponent<CircleCollider2D>();
                col.radius = 0.3f;
            }

            var villager = go.AddComponent<Villager>();

            if (string.IsNullOrEmpty(name))
            {
                name = GenerateRandomName();
            }

            villager.Initialize(name, age);
            go.name = $"Villager_{name}";

            allVillagers.Add(villager);
            OnVillagerArrived?.Invoke(villager);
            OnPopulationChanged?.Invoke(PopulationCount);

            // Auto-assign to housing if available
            TryAutoAssignHome(villager);

            Debug.Log($"Villager {name} has arrived! Population: {PopulationCount}");

            return villager;
        }

        /// <summary>
        /// Process all villager needs each game hour.
        /// </summary>
        private void OnHourTick()
        {
            // Process in batches to avoid CPU spikes (per GDD 2.3)
            for (int i = allVillagers.Count - 1; i >= 0; i--)
            {
                if (i >= allVillagers.Count) continue; // Safety check during removal

                var villager = allVillagers[i];
                if (!villager.IsAlive) continue;

                villager.ProcessHourTick();
            }

            // Meal ticks every 12 hours
            mealTickCounter++;
            if (mealTickCounter >= 12)
            {
                mealTickCounter = 0;
                foreach (var villager in allVillagers)
                {
                    if (villager.IsAlive)
                        villager.ProcessMealTick();
                }
            }

            // Immigration check
            immigrationTimer++;
            if (immigrationTimer >= GameConstants.IMMIGRATION_CHECK_INTERVAL_HOURS)
            {
                immigrationTimer = 0;
                TryImmigration();
            }

            // Water production from wells (auto)
            ProcessWaterProduction();

            // Production ticks for all buildings
            ProcessBuildingProduction();
        }

        private void ProcessWaterProduction()
        {
            // Wells and water buildings auto-produce water
            if (BuildingManager.Instance == null) return;

            foreach (var building in BuildingManager.Instance.PlacedBuildings)
            {
                if (building.Data.waterProductionPerDay > 0)
                {
                    int waterPerHour = Mathf.Max(1, building.Data.waterProductionPerDay / GameConstants.HOURS_PER_DAY);
                    ResourceManager.Instance.AddResource(ResourceType.Water, waterPerHour);
                }
            }
        }

        private void ProcessBuildingProduction()
        {
            if (BuildingManager.Instance == null) return;

            foreach (var building in BuildingManager.Instance.PlacedBuildings)
            {
                building.ProcessProductionTick();
            }
        }

        /// <summary>
        /// MVP simplified immigration: chance-based when food and housing exist.
        /// </summary>
        private void TryImmigration()
        {
            // Check conditions
            int housingCapacity = BuildingManager.Instance != null
                ? BuildingManager.Instance.GetTotalHousingCapacity()
                : 0;
            bool hasHousingVacancy = housingCapacity > PopulationCount;

            float foodRatio = PopulationCount > 0
                ? ResourceManager.Instance.GetFoodDaysRemaining(PopulationCount) / 5f
                : 1f;

            if (!hasHousingVacancy) return;
            if (foodRatio < GameConstants.IMMIGRATION_MIN_FOOD_RATIO) return;

            // Roll for immigration
            float chance = GameConstants.IMMIGRATION_BASE_CHANCE * Mathf.Min(1f, foodRatio);
            if (UnityEngine.Random.value < chance)
            {
                // 1-2 immigrants arrive
                int count = UnityEngine.Random.Range(1, 3);
                Vector3 spawnPos = GridManager.Instance.GetMapCenter() +
                    new Vector3(UnityEngine.Random.Range(-5f, 5f), UnityEngine.Random.Range(-5f, 5f), 0);

                for (int i = 0; i < count; i++)
                {
                    SpawnVillager(spawnPos + new Vector3(i * 0.5f, 0, 0));
                }

                UIManager.Instance?.ShowAlert($"{count} new settler(s) have arrived!");
            }
        }

        /// <summary>
        /// Called by Villager when they die.
        /// </summary>
        public void OnVillagerDied(Villager villager, string cause)
        {
            allVillagers.Remove(villager);
            deadVillagers.Add(villager);
            OnVillagerDeath?.Invoke(villager, cause);
            OnPopulationChanged?.Invoke(PopulationCount);

            UIManager.Instance?.ShowAlert($"{villager.VillagerName} has died of {cause}!");

            // Cleanup the GameObject after delay
            Destroy(villager.gameObject, 2f);

            // Check for game over
            if (PopulationCount <= 0)
            {
                GameManager.Instance?.OnGameOver();
            }
        }

        /// <summary>
        /// Unassign all workers from a building being demolished.
        /// </summary>
        public void UnassignWorkersFromBuilding(BuildingInstance building)
        {
            foreach (var villager in allVillagers)
            {
                if (villager.Workplace == building)
                    villager.UnassignFromWorkplace();
                if (villager.Home == building)
                    villager.UnassignFromHome();
            }
        }

        /// <summary>
        /// Try to auto-assign a villager to available housing.
        /// </summary>
        public void TryAutoAssignHome(Villager villager)
        {
            if (villager.HasHome) return;
            if (BuildingManager.Instance == null) return;

            var housing = BuildingManager.Instance.GetHousingWithVacancy();
            if (housing.Count > 0)
            {
                housing[0].AddResident(villager);
            }
        }

        /// <summary>
        /// Get a list of unemployed villagers available for work assignment.
        /// </summary>
        public List<Villager> GetUnemployedVillagers()
        {
            var result = new List<Villager>();
            foreach (var v in allVillagers)
            {
                if (v.IsAlive && !v.HasJob)
                    result.Add(v);
            }
            return result;
        }

        private string GenerateRandomName()
        {
            bool isMale = UnityEngine.Random.value > 0.5f;
            string[] pool = isMale ? maleNames : femaleNames;
            return pool[UnityEngine.Random.Range(0, pool.Length)];
        }
    }
}

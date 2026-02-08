using UnityEngine;

namespace MedievalVillage
{
    /// <summary>
    /// Individual villager entity.
    /// Tracks needs (hunger, thirst, health), state, home, workplace.
    /// </summary>
    public class Villager : MonoBehaviour
    {
        [Header("Identity")]
        [SerializeField] private string villagerName;
        [SerializeField] private int age = 20;

        [Header("Needs")]
        [SerializeField] private float hunger = 80f;
        [SerializeField] private float thirst = 80f;
        [SerializeField] private float health = 100f;

        [Header("State")]
        [SerializeField] private VillagerState currentState = VillagerState.Idle;

        // References
        private BuildingInstance workplace;
        private BuildingInstance home;

        // Death timers (hours at zero)
        private float hoursAtZeroHunger = 0f;
        private float hoursAtZeroThirst = 0f;

        // Movement
        private Vector3 targetPosition;
        private bool isMoving;

        // === PUBLIC PROPERTIES ===
        public string VillagerName => villagerName;
        public int Age => age;
        public float Hunger => hunger;
        public float Thirst => thirst;
        public float Health => health;
        public VillagerState State => currentState;
        public BuildingInstance Workplace => workplace;
        public BuildingInstance Home => home;
        public bool IsAlive => currentState != VillagerState.Dead;
        public bool HasHome => home != null;
        public bool HasJob => workplace != null;

        /// <summary>
        /// Initialize a new villager with a name and starting stats.
        /// </summary>
        public void Initialize(string name, int startAge = -1)
        {
            villagerName = name;
            age = startAge >= 0 ? startAge : Random.Range(18, 40);
            hunger = Random.Range(60f, 90f);
            thirst = Random.Range(60f, 90f);
            health = 100f;
            currentState = VillagerState.Idle;

            // Visual setup
            var sr = GetComponent<SpriteRenderer>();
            if (sr != null)
            {
                sr.sortingLayerName = "Villagers";
                sr.sortingOrder = 2;
                sr.color = new Color(0.9f, 0.75f, 0.6f); // Skin tone fallback
            }
        }

        /// <summary>
        /// Called by PopulationManager every game hour tick.
        /// </summary>
        public void ProcessHourTick()
        {
            if (!IsAlive) return;

            // Decay needs
            hunger = Mathf.Max(0, hunger - GameConstants.HUNGER_DECAY_PER_HOUR);
            thirst = Mathf.Max(0, thirst - GameConstants.THIRST_DECAY_PER_HOUR);

            // Try to eat/drink if critically low
            if (hunger < GameConstants.HUNGER_CRITICAL)
            {
                TryEat();
            }
            if (thirst < GameConstants.THIRST_CRITICAL)
            {
                TryDrink();
            }

            // Track death timers
            if (hunger <= 0)
            {
                hoursAtZeroHunger++;
                if (hoursAtZeroHunger >= GameConstants.STARVATION_HOURS)
                {
                    Die("starvation");
                    return;
                }
            }
            else
            {
                hoursAtZeroHunger = 0;
            }

            if (thirst <= 0)
            {
                hoursAtZeroThirst++;
                if (hoursAtZeroThirst >= GameConstants.DEHYDRATION_HOURS)
                {
                    Die("dehydration");
                    return;
                }
            }
            else
            {
                hoursAtZeroThirst = 0;
            }

            // Health drain from unmet needs
            if (hunger <= 0) health = Mathf.Max(0, health - 1f);
            if (thirst <= 0) health = Mathf.Max(0, health - 1.5f);

            // Unsheltered health drain
            if (!HasHome)
            {
                health = Mathf.Max(0, health - GameConstants.UNSHELTERED_HEALTH_DRAIN_PER_HOUR);
            }

            // Health death
            if (health <= GameConstants.HEALTH_CRITICAL && health <= 0)
            {
                Die("poor health");
                return;
            }

            // Slow health recovery when needs met
            if (hunger > 50 && thirst > 50 && HasHome)
            {
                health = Mathf.Min(GameConstants.MAX_NEED_VALUE, health + 0.2f);
            }

            // Update state based on time of day
            UpdateState();
        }

        /// <summary>
        /// Regular consumption cycle (every 12 game hours).
        /// </summary>
        public void ProcessMealTick()
        {
            if (!IsAlive) return;
            TryEat();
            TryDrink();
        }

        private void TryEat()
        {
            if (ResourceManager.Instance.ConsumeAnyFood(1))
            {
                hunger = Mathf.Min(GameConstants.MAX_NEED_VALUE, hunger + 30f);
            }
        }

        private void TryDrink()
        {
            if (ResourceManager.Instance.RemoveResource(ResourceType.Water, 1))
            {
                thirst = Mathf.Min(GameConstants.MAX_NEED_VALUE, thirst + 40f);
            }
        }

        private void UpdateState()
        {
            if (!IsAlive) return;

            var time = TimeManager.Instance;
            if (time == null) return;

            // Night time: sleep
            if (time.IsNight())
            {
                currentState = VillagerState.Sleeping;
                return;
            }

            // Working hours: work if assigned
            int hour = time.CurrentHour;
            if (hour >= 7 && hour < 17 && HasJob)
            {
                currentState = VillagerState.Working;
                return;
            }

            // Meal times
            if ((hour >= 6 && hour < 7) || (hour >= 12 && hour < 13) || (hour >= 17 && hour < 18))
            {
                currentState = hunger < 40 ? VillagerState.Eating : VillagerState.Idle;
                return;
            }

            currentState = VillagerState.Idle;
        }

        /// <summary>
        /// Work efficiency modifier based on needs.
        /// </summary>
        public float GetWorkEfficiency()
        {
            float efficiency = 1f;

            if (hunger < GameConstants.HUNGER_CRITICAL)
                efficiency *= GameConstants.LOW_NEED_WORK_PENALTY;
            if (thirst < GameConstants.THIRST_CRITICAL)
                efficiency *= GameConstants.LOW_NEED_WORK_PENALTY;
            if (health < GameConstants.HEALTH_LOW)
                efficiency *= GameConstants.LOW_HEALTH_WORK_PENALTY;

            return efficiency;
        }

        // === ASSIGNMENT ===

        public void AssignToWorkplace(BuildingInstance building)
        {
            workplace = building;
        }

        public void AssignToHome(BuildingInstance building)
        {
            home = building;
        }

        public void UnassignFromWorkplace()
        {
            if (workplace != null)
            {
                workplace.RemoveWorker(this);
                workplace = null;
            }
            currentState = VillagerState.Idle;
        }

        public void UnassignFromHome()
        {
            if (home != null)
            {
                home.RemoveResident(this);
                home = null;
            }
        }

        // === DEATH ===

        private void Die(string cause)
        {
            currentState = VillagerState.Dead;
            Debug.Log($"Villager {villagerName} died of {cause}");

            // Unassign from buildings
            UnassignFromWorkplace();
            UnassignFromHome();

            // Notify population manager
            if (PopulationManager.Instance != null)
            {
                PopulationManager.Instance.OnVillagerDied(this, cause);
            }
        }

        // === MOVEMENT (simple direct movement for MVP) ===

        private void Update()
        {
            if (!IsAlive) return;

            if (isMoving && targetPosition != transform.position)
            {
                transform.position = Vector3.MoveTowards(
                    transform.position,
                    targetPosition,
                    GameConstants.VILLAGER_MOVE_SPEED * Time.deltaTime
                );

                if (Vector3.Distance(transform.position, targetPosition) < 0.05f)
                {
                    transform.position = targetPosition;
                    isMoving = false;
                }
            }
        }

        public void MoveTo(Vector3 position)
        {
            targetPosition = position;
            isMoving = true;
            currentState = VillagerState.Walking;
        }

        /// <summary>
        /// Get a summary string for UI display.
        /// </summary>
        public string GetStatusSummary()
        {
            return $"{villagerName} (Age {age})\n" +
                   $"Hunger: {hunger:F0} | Thirst: {thirst:F0} | Health: {health:F0}\n" +
                   $"State: {currentState}\n" +
                   $"Home: {(HasHome ? home.Data.buildingName : "None")}\n" +
                   $"Job: {(HasJob ? workplace.Data.buildingName : "Unemployed")}";
        }
    }
}

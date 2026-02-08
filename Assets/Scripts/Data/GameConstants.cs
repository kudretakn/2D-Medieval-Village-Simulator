namespace MedievalVillage
{
    /// <summary>
    /// Centralized game configuration constants.
    /// Tunable values per the GDD balancing notes.
    /// </summary>
    public static class GameConstants
    {
        // === MAP ===
        public const int MAP_WIDTH = 50;
        public const int MAP_HEIGHT = 50;
        public const float TILE_SIZE = 1f; // Unity units per tile

        // === TIME ===
        /// <summary>Real seconds per game hour at 1x speed.</summary>
        public const float SECONDS_PER_GAME_HOUR = 25f; // 10 min real = 1 game day (24h)
        public const int HOURS_PER_DAY = 24;
        public const int DAYS_PER_SEASON = 30;
        public const int SEASONS_PER_YEAR = 4;

        // === POPULATION ===
        public const int STARTING_VILLAGERS = 3;
        public const int MVP_WIN_POPULATION = 30;
        public const float VILLAGER_MOVE_SPEED = 3f; // tiles per second

        // === NEEDS (per game hour) ===
        public const float HUNGER_DECAY_PER_HOUR = 1f;
        public const float THIRST_DECAY_PER_HOUR = 2f;
        public const float MAX_NEED_VALUE = 100f;

        // === NEED THRESHOLDS ===
        public const float HUNGER_CRITICAL = 20f;
        public const float THIRST_CRITICAL = 20f;
        public const float HEALTH_LOW = 30f;
        public const float HEALTH_CRITICAL = 10f;

        // === DEATH TIMERS (in game hours at 0) ===
        public const float STARVATION_HOURS = 12f;
        public const float DEHYDRATION_HOURS = 6f;

        // === CONSUMPTION (per 12 game hours) ===
        public const float FOOD_PER_ADULT_12H = 1f;
        public const float WATER_PER_VILLAGER_8H = 1f;

        // === EFFICIENCY ===
        public const float LOW_NEED_WORK_PENALTY = 0.5f; // 50% speed when need < 20
        public const float LOW_HEALTH_WORK_PENALTY = 0.75f;

        // === STORAGE ===
        public const int STOCKPILE_CAPACITY = 200;
        public const int GRANARY_CAPACITY = 500;

        // === IMMIGRATION (MVP simplified) ===
        /// <summary>Seconds between immigration checks.</summary>
        public const float IMMIGRATION_CHECK_INTERVAL_HOURS = 72f; // Every 3 days
        /// <summary>Base chance of immigration per check (0-1).</summary>
        public const float IMMIGRATION_BASE_CHANCE = 0.3f;
        /// <summary>Min food ratio for immigration to occur.</summary>
        public const float IMMIGRATION_MIN_FOOD_RATIO = 0.3f;

        // === HEALTH ===
        public const float UNSHELTERED_HEALTH_DRAIN_PER_HOUR = 0.5f;

        // === CAMERA ===
        public const float CAMERA_MIN_ZOOM = 3f;
        public const float CAMERA_MAX_ZOOM = 15f;
        public const float CAMERA_PAN_SPEED = 10f;
        public const float CAMERA_ZOOM_SPEED = 2f;
    }
}

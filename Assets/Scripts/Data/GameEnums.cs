namespace MedievalVillage
{
    /// <summary>
    /// Building categories for UI organization.
    /// </summary>
    public enum BuildingCategory
    {
        Resources,
        Food,
        Housing,
        Storage,
        Services,
        Production,
        Defense
    }

    /// <summary>
    /// Village progression tiers. Buildings unlock at specific tiers.
    /// </summary>
    public enum VillageTier
    {
        Camp = 1,       // Game start
        Hamlet = 2,     // Pop 10, 3 buildings
        Village = 3,    // Pop 25, 6 buildings
        Town = 4,       // Pop 50, Marketplace
        LargeTown = 5,  // Pop 80, Trading Post
        Borough = 6,    // Pop 120, Church
        SmallCity = 7,  // Pop 180, 500 gold
        City = 8        // Pop 250, all tech
    }

    /// <summary>
    /// Tile types for the map grid.
    /// </summary>
    public enum TileType
    {
        Grass,
        Water,
        Forest,
        Stone,
        Sand,
        Road,
        FertileLand,
        IronDeposit,
        ClayDeposit
    }

    /// <summary>
    /// Villager behavioral states.
    /// </summary>
    public enum VillagerState
    {
        Idle,
        Working,
        Eating,
        Drinking,
        Sleeping,
        Walking,
        Breakdown,
        Dead
    }

    /// <summary>
    /// Game speed settings.
    /// </summary>
    public enum GameSpeed
    {
        Paused = 0,
        Normal = 1,
        Fast = 2,
        VeryFast = 3
    }

    /// <summary>
    /// Seasons of the year.
    /// </summary>
    public enum Season
    {
        Spring,
        Summer,
        Autumn,
        Winter
    }

    /// <summary>
    /// Time of day phases for day/night cycle.
    /// </summary>
    public enum DayPhase
    {
        Dawn,       // 5-7
        Morning,    // 7-12
        Afternoon,  // 12-17
        Dusk,       // 17-19
        Night       // 19-5
    }
}

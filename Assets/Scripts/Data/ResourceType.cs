namespace MedievalVillage
{
    /// <summary>
    /// All resource types in the game.
    /// MVP uses: Wood, Stone, Wheat, Flour, Bread, Water
    /// </summary>
    public enum ResourceType
    {
        // Raw Materials
        Wood,
        Stone,
        IronOre,
        Clay,
        Thatch,
        RawWool,
        Wheat,
        Barley,
        Hops,
        RawMeat,
        RawFish,
        Herbs,
        WildBerries,

        // Processed Materials
        Planks,
        CutStone,
        IronIngots,
        Bricks,
        Flour,
        Bread,
        Ale,
        Textiles,
        DriedMeat,
        SaltedFish,
        Tools,
        Weapons,
        Medicine,
        Firewood,

        // Special
        Salt,
        Glass,
        GoldCoins,

        // Basic Needs (tracked separately but in same enum for storage)
        Water
    }
}

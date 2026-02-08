using UnityEngine;

namespace MedievalVillage
{
    /// <summary>
    /// Data definition for a resource type.
    /// Create instances via Assets > Create > MedievalVillage > ResourceData.
    /// </summary>
    [CreateAssetMenu(fileName = "NewResource", menuName = "MedievalVillage/ResourceData")]
    public class ResourceData : ScriptableObject
    {
        public string resourceName;
        public ResourceType resourceType;
        public Sprite icon;
        [TextArea] public string description;

        [Header("Storage")]
        /// <summary>If true, this resource can be stored in a Granary (food storage).</summary>
        public bool isFood = false;
        /// <summary>Spoilage rate per season (0 = no spoilage). 0.05 = 5% per season.</summary>
        public float spoilageRatePerSeason = 0f;

        [Header("Processing")]
        /// <summary>If true, this is a processed/refined resource (lower spoilage).</summary>
        public bool isProcessed = false;
    }
}

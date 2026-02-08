using UnityEngine;

namespace MedievalVillage
{
    /// <summary>
    /// Scene bootstrap: creates all required manager GameObjects at runtime.
    /// Attach this to a single empty GameObject named "Bootstrap" in the scene.
    /// This ensures the game works even with a completely empty scene.
    /// </summary>
    public class SceneBootstrap : MonoBehaviour
    {
        [Header("Building Data (assign in inspector or auto-create)")]
        [SerializeField] private BuildingData[] buildingDatabase;

        private void Awake()
        {
            CreateManagers();
        }

        private void CreateManagers()
        {
            // Auto-create building data if not assigned via inspector
            if (buildingDatabase == null || buildingDatabase.Length == 0)
            {
                buildingDatabase = BuildingDataFactory.CreateMVPBuildings();
            }

            // GameManager
            if (GameManager.Instance == null)
            {
                var go = new GameObject("GameManager");
                go.AddComponent<GameManager>();
            }

            // TimeManager
            if (TimeManager.Instance == null)
            {
                var go = new GameObject("TimeManager");
                go.AddComponent<TimeManager>();
            }

            // ResourceManager
            if (ResourceManager.Instance == null)
            {
                var go = new GameObject("ResourceManager");
                go.AddComponent<ResourceManager>();
            }

            // GridManager
            if (GridManager.Instance == null)
            {
                var go = new GameObject("GridManager");
                go.AddComponent<GridManager>();
            }

            // BuildingManager
            if (BuildingManager.Instance == null)
            {
                var go = new GameObject("BuildingManager");
                var bm = go.AddComponent<BuildingManager>();

                // If we have building data from inspector or runtime-created, assign it
                if (buildingDatabase != null && buildingDatabase.Length > 0)
                {
                    SetPrivateField(bm, "allBuildingTypes", buildingDatabase);
                }
            }

            // PopulationManager
            if (PopulationManager.Instance == null)
            {
                var go = new GameObject("PopulationManager");
                go.AddComponent<PopulationManager>();
            }

            // CameraController (attach to main camera)
            var mainCam = Camera.main;
            if (mainCam != null && CameraController.Instance == null)
            {
                mainCam.gameObject.AddComponent<CameraController>();
                mainCam.orthographic = true;
                mainCam.orthographicSize = 10f;
                mainCam.backgroundColor = new Color(0.2f, 0.3f, 0.15f); // Dark green
            }

            // BuildingPlacer
            if (BuildingPlacer.Instance == null)
            {
                var go = new GameObject("BuildingPlacer");
                go.AddComponent<BuildingPlacer>();
            }

            // SelectionManager
            if (SelectionManager.Instance == null)
            {
                var go = new GameObject("SelectionManager");
                go.AddComponent<SelectionManager>();
            }

            // DayNightCycle
            if (FindObjectOfType<DayNightCycle>() == null)
            {
                var go = new GameObject("DayNightCycle");
                go.AddComponent<DayNightCycle>();
            }

            // UISetup (auto-creates Canvas and all UI)
            if (FindObjectOfType<UISetup>() == null)
            {
                var go = new GameObject("UISetup");
                go.AddComponent<UISetup>();
            }
        }

        private void SetPrivateField(object target, string fieldName, object value)
        {
            var field = target.GetType().GetField(fieldName,
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            field?.SetValue(target, value);
        }
    }
}

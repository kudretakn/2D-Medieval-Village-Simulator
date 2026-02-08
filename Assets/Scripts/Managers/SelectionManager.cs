using UnityEngine;
using UnityEngine.EventSystems;

namespace MedievalVillage
{
    /// <summary>
    /// Handles non-building input: selecting buildings/villagers, context menus.
    /// </summary>
    public class SelectionManager : MonoBehaviour
    {
        public static SelectionManager Instance { get; private set; }

        private BuildingInstance selectedBuilding;
        private Villager selectedVillager;

        public BuildingInstance SelectedBuilding => selectedBuilding;
        public Villager SelectedVillager => selectedVillager;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Update()
        {
            // Don't process selection when in building placement mode
            if (BuildingPlacer.Instance != null && BuildingPlacer.Instance.IsPlacing)
                return;

            if (Input.GetMouseButtonDown(0))
            {
                // Don't select if over UI
                if (EventSystem.current != null && EventSystem.current.IsPointerOverGameObject())
                    return;

                TrySelect();
            }
        }

        private void TrySelect()
        {
            Vector3 worldPos = CameraController.Instance.GetPointerWorldPosition();
            Vector2 pos2D = new Vector2(worldPos.x, worldPos.y);

            // Raycast for clickable objects
            RaycastHit2D hit = Physics2D.Raycast(pos2D, Vector2.zero);

            if (hit.collider != null)
            {
                // Check for building
                var building = hit.collider.GetComponent<BuildingInstance>();
                if (building != null)
                {
                    SelectBuilding(building);
                    return;
                }

                // Check for villager
                var villager = hit.collider.GetComponent<Villager>();
                if (villager != null)
                {
                    SelectVillager(villager);
                    return;
                }
            }

            // Clicked empty space: deselect
            Deselect();
        }

        public void SelectBuilding(BuildingInstance building)
        {
            Deselect();
            selectedBuilding = building;
            UIManager.Instance?.ShowBuildingInfo(building);
        }

        public void SelectVillager(Villager villager)
        {
            Deselect();
            selectedVillager = villager;
            UIManager.Instance?.ShowVillagerInfo(villager);
        }

        public void Deselect()
        {
            selectedBuilding = null;
            selectedVillager = null;
            UIManager.Instance?.HideInfoPanels();
        }

        /// <summary>
        /// Assign a villager to the currently selected building.
        /// </summary>
        public void AssignSelectedVillagerToBuilding(BuildingInstance building)
        {
            // Find an unemployed villager and assign
            var unemployed = PopulationManager.Instance.GetUnemployedVillagers();
            if (unemployed.Count > 0 && building.CanAssignWorker())
            {
                building.AssignWorker(unemployed[0]);
                UIManager.Instance?.ShowAlert($"{unemployed[0].VillagerName} assigned to {building.Data.buildingName}");
                UIManager.Instance?.ShowBuildingInfo(building);
            }
            else if (unemployed.Count == 0)
            {
                UIManager.Instance?.ShowAlert("No unemployed villagers available!");
            }
            else
            {
                UIManager.Instance?.ShowAlert("Building is fully staffed!");
            }
        }
    }
}

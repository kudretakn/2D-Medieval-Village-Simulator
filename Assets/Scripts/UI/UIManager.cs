using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections;
using System.Collections.Generic;

namespace MedievalVillage
{
    /// <summary>
    /// Manages all UI elements: HUD, build panel, info panels, alerts.
    /// Attach to a Canvas GameObject.
    /// </summary>
    public class UIManager : MonoBehaviour
    {
        public static UIManager Instance { get; private set; }

        [Header("HUD - Top Bar")]
        [SerializeField] private TextMeshProUGUI populationText;
        [SerializeField] private TextMeshProUGUI foodText;
        [SerializeField] private TextMeshProUGUI waterText;
        [SerializeField] private TextMeshProUGUI woodText;
        [SerializeField] private TextMeshProUGUI stoneText;
        [SerializeField] private TextMeshProUGUI timeText;

        [Header("HUD - Bottom Bar")]
        [SerializeField] private Button buildButton;
        [SerializeField] private Button speedButton;
        [SerializeField] private TextMeshProUGUI speedText;

        [Header("Build Panel")]
        [SerializeField] private GameObject buildPanel;
        [SerializeField] private Transform buildButtonContainer;
        [SerializeField] private GameObject buildItemButtonPrefab;

        [Header("Info Panels")]
        [SerializeField] private GameObject buildingInfoPanel;
        [SerializeField] private TextMeshProUGUI buildingInfoText;
        [SerializeField] private Button assignWorkerButton;
        [SerializeField] private Button demolishButton;

        [SerializeField] private GameObject villagerInfoPanel;
        [SerializeField] private TextMeshProUGUI villagerInfoText;

        [Header("Alerts")]
        [SerializeField] private GameObject alertPrefab;
        [SerializeField] private Transform alertContainer;

        [Header("Game Over")]
        [SerializeField] private GameObject gameOverPanel;
        [SerializeField] private TextMeshProUGUI gameOverText;

        [Header("Win Screen")]
        [SerializeField] private GameObject winPanel;

        private bool buildPanelOpen = false;
        private Queue<string> alertQueue = new Queue<string>();
        private bool isShowingAlert = false;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Start()
        {
            // Setup button listeners
            if (buildButton != null) buildButton.onClick.AddListener(ToggleBuildPanel);
            if (speedButton != null) speedButton.onClick.AddListener(OnSpeedButtonClicked);
            if (assignWorkerButton != null) assignWorkerButton.onClick.AddListener(OnAssignWorkerClicked);
            if (demolishButton != null) demolishButton.onClick.AddListener(OnDemolishClicked);

            // Hide panels initially
            if (buildPanel != null) buildPanel.SetActive(false);
            if (buildingInfoPanel != null) buildingInfoPanel.SetActive(false);
            if (villagerInfoPanel != null) villagerInfoPanel.SetActive(false);
            if (gameOverPanel != null) gameOverPanel.SetActive(false);
            if (winPanel != null) winPanel.SetActive(false);
        }

        private void Update()
        {
            UpdateHUD();

            // Escape closes panels
            if (Input.GetKeyDown(KeyCode.Escape))
            {
                if (buildPanelOpen) ToggleBuildPanel();
                HideInfoPanels();
            }
        }

        // === HUD UPDATE ===

        private void UpdateHUD()
        {
            if (PopulationManager.Instance != null && populationText != null)
            {
                int pop = PopulationManager.Instance.PopulationCount;
                populationText.text = $"Pop: {pop}";
            }

            if (ResourceManager.Instance != null)
            {
                if (foodText != null)
                {
                    int food = ResourceManager.Instance.GetTotalFood();
                    float days = ResourceManager.Instance.GetFoodDaysRemaining(
                        PopulationManager.Instance?.PopulationCount ?? 0
                    );
                    string daysStr = days > 99 ? "99+" : $"{days:F0}";
                    foodText.text = $"Food: {food} ({daysStr}d)";

                    // Color coding
                    foodText.color = days < 3 ? Color.red : (days < 7 ? Color.yellow : Color.white);
                }

                if (waterText != null)
                {
                    int water = ResourceManager.Instance.GetResourceAmount(ResourceType.Water);
                    waterText.text = $"Water: {water}";
                    waterText.color = water < 10 ? Color.red : Color.white;
                }

                if (woodText != null)
                    woodText.text = $"Wood: {ResourceManager.Instance.GetResourceAmount(ResourceType.Wood)}";

                if (stoneText != null)
                    stoneText.text = $"Stone: {ResourceManager.Instance.GetResourceAmount(ResourceType.Stone)}";
            }

            if (TimeManager.Instance != null && timeText != null)
            {
                timeText.text = TimeManager.Instance.GetTimeString();
            }

            if (speedText != null && TimeManager.Instance != null)
            {
                speedText.text = TimeManager.Instance.CurrentSpeed switch
                {
                    GameSpeed.Paused => "II",
                    GameSpeed.Normal => ">",
                    GameSpeed.Fast => ">>",
                    GameSpeed.VeryFast => ">>>",
                    _ => ">"
                };
            }
        }

        // === BUILD PANEL ===

        public void ToggleBuildPanel()
        {
            buildPanelOpen = !buildPanelOpen;
            if (buildPanel != null)
            {
                buildPanel.SetActive(buildPanelOpen);
                if (buildPanelOpen) PopulateBuildPanel();
            }
        }

        private void PopulateBuildPanel()
        {
            if (buildButtonContainer == null || BuildingManager.Instance == null) return;

            // Clear existing buttons
            foreach (Transform child in buildButtonContainer)
            {
                Destroy(child.gameObject);
            }

            var available = BuildingManager.Instance.GetAvailableBuildingTypes(VillageTier.Camp); // TODO: use actual village tier

            foreach (var buildingData in available)
            {
                CreateBuildButton(buildingData);
            }
        }

        private void CreateBuildButton(BuildingData data)
        {
            if (buildItemButtonPrefab != null)
            {
                var go = Instantiate(buildItemButtonPrefab, buildButtonContainer);
                var text = go.GetComponentInChildren<TextMeshProUGUI>();
                if (text != null)
                {
                    string costStr = "";
                    foreach (var cost in data.constructionCosts)
                    {
                        costStr += $"{cost.resourceType}: {cost.amount} ";
                    }
                    text.text = $"{data.buildingName}\n<size=10>{costStr}</size>";
                }

                var button = go.GetComponent<Button>();
                if (button != null)
                {
                    var captured = data; // Capture for lambda
                    button.onClick.AddListener(() => OnBuildItemSelected(captured));
                }
            }
            else
            {
                // Fallback: create a simple button
                var go = new GameObject(data.buildingName);
                go.transform.SetParent(buildButtonContainer);

                var rectTransform = go.AddComponent<RectTransform>();
                rectTransform.sizeDelta = new Vector2(200, 50);

                var button = go.AddComponent<Button>();
                var image = go.AddComponent<Image>();
                image.color = new Color(0.3f, 0.25f, 0.2f);

                var textGO = new GameObject("Text");
                textGO.transform.SetParent(go.transform);
                var textRect = textGO.AddComponent<RectTransform>();
                textRect.anchorMin = Vector2.zero;
                textRect.anchorMax = Vector2.one;
                textRect.offsetMin = Vector2.zero;
                textRect.offsetMax = Vector2.zero;

                var tmp = textGO.AddComponent<TextMeshProUGUI>();
                tmp.text = data.buildingName;
                tmp.fontSize = 14;
                tmp.alignment = TextAlignmentOptions.Center;
                tmp.color = Color.white;

                bool canAfford = data.CanAfford(ResourceManager.Instance);
                if (!canAfford) image.color = new Color(0.5f, 0.3f, 0.3f);

                var captured = data;
                button.onClick.AddListener(() => OnBuildItemSelected(captured));
            }
        }

        private void OnBuildItemSelected(BuildingData data)
        {
            if (buildPanelOpen) ToggleBuildPanel();
            BuildingPlacer.Instance?.StartPlacing(data);
        }

        // === INFO PANELS ===

        public void ShowBuildingInfo(BuildingInstance building)
        {
            HideInfoPanels();

            if (buildingInfoPanel != null)
            {
                buildingInfoPanel.SetActive(true);

                if (buildingInfoText != null)
                {
                    string info = $"<b>{building.Data.buildingName}</b>\n\n";

                    if (building.Data.maxWorkers > 0)
                        info += $"Workers: {building.AssignedWorkerCount}/{building.Data.maxWorkers}\n";

                    if (building.Data.housingCapacity > 0)
                        info += $"Residents: {building.ResidentCount}/{building.Data.housingCapacity}\n";

                    if (building.Data.outputResources != null && building.Data.outputResources.Length > 0)
                    {
                        info += "Produces: ";
                        foreach (var output in building.Data.outputResources)
                        {
                            info += $"{output.resourceType} x{output.amount} ";
                        }
                        info += $"\nEfficiency: {building.GetEfficiency() * 100:F0}%\n";
                    }

                    if (building.Data.generalStorageCapacity > 0)
                        info += $"Storage: {building.Data.generalStorageCapacity} units\n";

                    if (building.Data.waterProductionPerDay > 0)
                        info += $"Water: {building.Data.waterProductionPerDay}/day\n";

                    buildingInfoText.text = info;
                }

                if (assignWorkerButton != null)
                    assignWorkerButton.gameObject.SetActive(building.Data.maxWorkers > 0 && building.CanAssignWorker());
            }
        }

        public void ShowVillagerInfo(Villager villager)
        {
            HideInfoPanels();

            if (villagerInfoPanel != null)
            {
                villagerInfoPanel.SetActive(true);

                if (villagerInfoText != null)
                {
                    villagerInfoText.text = villager.GetStatusSummary();
                }
            }
        }

        public void HideInfoPanels()
        {
            if (buildingInfoPanel != null) buildingInfoPanel.SetActive(false);
            if (villagerInfoPanel != null) villagerInfoPanel.SetActive(false);
        }

        // === BUTTON CALLBACKS ===

        private void OnSpeedButtonClicked()
        {
            TimeManager.Instance?.CycleSpeed();
        }

        private void OnAssignWorkerClicked()
        {
            var selected = SelectionManager.Instance?.SelectedBuilding;
            if (selected != null)
            {
                SelectionManager.Instance.AssignSelectedVillagerToBuilding(selected);
            }
        }

        private void OnDemolishClicked()
        {
            var selected = SelectionManager.Instance?.SelectedBuilding;
            if (selected != null)
            {
                BuildingManager.Instance?.DemolishBuilding(selected);
                HideInfoPanels();
            }
        }

        // === ALERTS ===

        public void ShowAlert(string message)
        {
            Debug.Log($"[Alert] {message}");
            alertQueue.Enqueue(message);
            if (!isShowingAlert)
            {
                StartCoroutine(ProcessAlertQueue());
            }
        }

        private IEnumerator ProcessAlertQueue()
        {
            isShowingAlert = true;

            while (alertQueue.Count > 0)
            {
                string msg = alertQueue.Dequeue();

                if (alertContainer != null && alertPrefab != null)
                {
                    var alertGO = Instantiate(alertPrefab, alertContainer);
                    var text = alertGO.GetComponentInChildren<TextMeshProUGUI>();
                    if (text != null) text.text = msg;
                    Destroy(alertGO, 4f);
                }

                yield return new WaitForSeconds(1f);
            }

            isShowingAlert = false;
        }

        // === GAME STATE SCREENS ===

        public void ShowGameOver()
        {
            if (gameOverPanel != null)
            {
                gameOverPanel.SetActive(true);
                if (gameOverText != null)
                {
                    int totalHours = TimeManager.Instance?.TotalHoursElapsed ?? 0;
                    gameOverText.text = $"Your village has fallen.\n\n" +
                                       $"Survived for {totalHours / 24} days.\n" +
                                       $"Total deaths: {PopulationManager.Instance?.DeathCount ?? 0}";
                }
            }
        }

        public void ShowWinScreen()
        {
            if (winPanel != null)
            {
                winPanel.SetActive(true);
            }
        }
    }
}

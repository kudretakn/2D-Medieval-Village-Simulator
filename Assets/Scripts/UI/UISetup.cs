using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace MedievalVillage
{
    /// <summary>
    /// Creates the full UI Canvas programmatically at runtime.
    /// Attach to the GameManager or a dedicated UI setup object.
    /// This handles the case where no pre-made UI prefabs exist.
    /// </summary>
    public class UISetup : MonoBehaviour
    {
        [Header("If these are null, UI will be auto-generated")]
        [SerializeField] private Canvas existingCanvas;

        private Canvas canvas;
        private UIManager uiManager;

        private void Awake()
        {
            if (existingCanvas != null) return;

            CreateCanvas();
            CreateHUD();
            CreateBuildPanel();
            CreateInfoPanels();
            CreateAlertSystem();
            CreateGameOverPanel();
            CreateWinPanel();
        }

        private void CreateCanvas()
        {
            var canvasGO = new GameObject("UICanvas");
            canvas = canvasGO.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 100;

            var scaler = canvasGO.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920, 1080);
            scaler.matchWidthOrHeight = 0.5f;

            canvasGO.AddComponent<GraphicRaycaster>();

            // Add UIManager
            uiManager = canvasGO.AddComponent<UIManager>();

            // EventSystem
            if (FindObjectOfType<UnityEngine.EventSystems.EventSystem>() == null)
            {
                var esGO = new GameObject("EventSystem");
                esGO.AddComponent<UnityEngine.EventSystems.EventSystem>();
                esGO.AddComponent<UnityEngine.EventSystems.StandaloneInputModule>();
            }
        }

        private void CreateHUD()
        {
            // === TOP BAR ===
            var topBar = CreatePanel("TopBar", canvas.transform, new Vector2(0, 1), new Vector2(1, 1),
                new Vector2(0, -40), new Vector2(0, 0), new Color(0.1f, 0.1f, 0.1f, 0.8f));
            var topBarRect = topBar.GetComponent<RectTransform>();
            topBarRect.sizeDelta = new Vector2(0, 40);

            var topLayout = topBar.AddComponent<HorizontalLayoutGroup>();
            topLayout.padding = new RectOffset(10, 10, 5, 5);
            topLayout.spacing = 20;
            topLayout.childAlignment = TextAnchor.MiddleLeft;
            topLayout.childForceExpandWidth = false;

            // HUD texts
            var popText = CreateText("PopText", topBar.transform, "Pop: 3", 16);
            var foodText = CreateText("FoodText", topBar.transform, "Food: 20 (10d)", 16);
            var waterText = CreateText("WaterText", topBar.transform, "Water: 30", 16);
            var woodText = CreateText("WoodText", topBar.transform, "Wood: 50", 16);
            var stoneText = CreateText("StoneText", topBar.transform, "Stone: 20", 16);

            var spacer = new GameObject("Spacer");
            spacer.transform.SetParent(topBar.transform);
            var spacerRect = spacer.AddComponent<RectTransform>();
            var spacerLayout = spacer.AddComponent<LayoutElement>();
            spacerLayout.flexibleWidth = 1;

            var timeText = CreateText("TimeText", topBar.transform, "Day 1, Spring, Year 1 - 06:00", 14);

            // Wire to UIManager via reflection or serialized fields
            SetPrivateField(uiManager, "populationText", popText);
            SetPrivateField(uiManager, "foodText", foodText);
            SetPrivateField(uiManager, "waterText", waterText);
            SetPrivateField(uiManager, "woodText", woodText);
            SetPrivateField(uiManager, "stoneText", stoneText);
            SetPrivateField(uiManager, "timeText", timeText);

            // === BOTTOM BAR ===
            var bottomBar = CreatePanel("BottomBar", canvas.transform, new Vector2(0, 0), new Vector2(1, 0),
                new Vector2(0, 0), new Vector2(0, 60), new Color(0.1f, 0.1f, 0.1f, 0.8f));

            var bottomLayout = bottomBar.AddComponent<HorizontalLayoutGroup>();
            bottomLayout.padding = new RectOffset(10, 10, 5, 5);
            bottomLayout.spacing = 10;
            bottomLayout.childAlignment = TextAnchor.MiddleCenter;
            bottomLayout.childForceExpandWidth = true;

            var buildBtn = CreateButton("BuildBtn", bottomBar.transform, "Build", new Color(0.3f, 0.5f, 0.3f));
            var speedBtn = CreateButton("SpeedBtn", bottomBar.transform, ">", new Color(0.3f, 0.3f, 0.5f));

            SetPrivateField(uiManager, "buildButton", buildBtn.GetComponent<Button>());
            SetPrivateField(uiManager, "speedButton", speedBtn.GetComponent<Button>());
            SetPrivateField(uiManager, "speedText", speedBtn.GetComponentInChildren<TextMeshProUGUI>());
        }

        private void CreateBuildPanel()
        {
            var panel = CreatePanel("BuildPanel", canvas.transform, new Vector2(0.1f, 0.15f), new Vector2(0.9f, 0.85f),
                Vector2.zero, Vector2.zero, new Color(0.15f, 0.12f, 0.1f, 0.95f));

            // Title
            var titleGO = new GameObject("Title");
            titleGO.transform.SetParent(panel.transform);
            var titleRect = titleGO.AddComponent<RectTransform>();
            titleRect.anchorMin = new Vector2(0, 0.9f);
            titleRect.anchorMax = new Vector2(1, 1);
            titleRect.offsetMin = Vector2.zero;
            titleRect.offsetMax = Vector2.zero;
            var titleText = titleGO.AddComponent<TextMeshProUGUI>();
            titleText.text = "BUILD";
            titleText.fontSize = 24;
            titleText.alignment = TextAlignmentOptions.Center;
            titleText.color = new Color(0.9f, 0.8f, 0.6f);

            // Scroll content area
            var scrollGO = new GameObject("ScrollContent");
            scrollGO.transform.SetParent(panel.transform);
            var scrollRect = scrollGO.AddComponent<RectTransform>();
            scrollRect.anchorMin = new Vector2(0.05f, 0.05f);
            scrollRect.anchorMax = new Vector2(0.95f, 0.88f);
            scrollRect.offsetMin = Vector2.zero;
            scrollRect.offsetMax = Vector2.zero;

            var gridLayout = scrollGO.AddComponent<GridLayoutGroup>();
            gridLayout.cellSize = new Vector2(200, 60);
            gridLayout.spacing = new Vector2(10, 10);
            gridLayout.constraint = GridLayoutGroup.Constraint.FixedColumnCount;
            gridLayout.constraintCount = 3;

            SetPrivateField(uiManager, "buildPanel", panel);
            SetPrivateField(uiManager, "buildButtonContainer", scrollGO.transform);
        }

        private void CreateInfoPanels()
        {
            // Building Info Panel
            var buildingPanel = CreatePanel("BuildingInfoPanel", canvas.transform,
                new Vector2(0.65f, 0.15f), new Vector2(0.98f, 0.85f),
                Vector2.zero, Vector2.zero, new Color(0.15f, 0.12f, 0.1f, 0.95f));

            var buildingText = CreateText("BuildingInfoText", buildingPanel.transform, "", 14);
            var biTextRect = buildingText.GetComponent<RectTransform>();
            biTextRect.anchorMin = new Vector2(0.05f, 0.25f);
            biTextRect.anchorMax = new Vector2(0.95f, 0.95f);
            biTextRect.offsetMin = Vector2.zero;
            biTextRect.offsetMax = Vector2.zero;

            // Buttons area
            var assignBtn = CreateButton("AssignWorkerBtn", buildingPanel.transform, "Assign Worker",
                new Color(0.3f, 0.5f, 0.3f));
            var assignRect = assignBtn.GetComponent<RectTransform>();
            assignRect.anchorMin = new Vector2(0.05f, 0.1f);
            assignRect.anchorMax = new Vector2(0.45f, 0.2f);
            assignRect.offsetMin = Vector2.zero;
            assignRect.offsetMax = Vector2.zero;

            var demolishBtn = CreateButton("DemolishBtn", buildingPanel.transform, "Demolish",
                new Color(0.6f, 0.2f, 0.2f));
            var demolishRect = demolishBtn.GetComponent<RectTransform>();
            demolishRect.anchorMin = new Vector2(0.55f, 0.1f);
            demolishRect.anchorMax = new Vector2(0.95f, 0.2f);
            demolishRect.offsetMin = Vector2.zero;
            demolishRect.offsetMax = Vector2.zero;

            SetPrivateField(uiManager, "buildingInfoPanel", buildingPanel);
            SetPrivateField(uiManager, "buildingInfoText", buildingText);
            SetPrivateField(uiManager, "assignWorkerButton", assignBtn.GetComponent<Button>());
            SetPrivateField(uiManager, "demolishButton", demolishBtn.GetComponent<Button>());

            // Villager Info Panel
            var villagerPanel = CreatePanel("VillagerInfoPanel", canvas.transform,
                new Vector2(0.65f, 0.15f), new Vector2(0.98f, 0.85f),
                Vector2.zero, Vector2.zero, new Color(0.15f, 0.12f, 0.1f, 0.95f));

            var villagerText = CreateText("VillagerInfoText", villagerPanel.transform, "", 14);
            var viTextRect = villagerText.GetComponent<RectTransform>();
            viTextRect.anchorMin = new Vector2(0.05f, 0.05f);
            viTextRect.anchorMax = new Vector2(0.95f, 0.95f);
            viTextRect.offsetMin = Vector2.zero;
            viTextRect.offsetMax = Vector2.zero;

            SetPrivateField(uiManager, "villagerInfoPanel", villagerPanel);
            SetPrivateField(uiManager, "villagerInfoText", villagerText);
        }

        private void CreateAlertSystem()
        {
            var container = new GameObject("AlertContainer");
            container.transform.SetParent(canvas.transform);
            var rect = container.AddComponent<RectTransform>();
            rect.anchorMin = new Vector2(0, 0.1f);
            rect.anchorMax = new Vector2(0.4f, 0.9f);
            rect.offsetMin = new Vector2(10, 0);
            rect.offsetMax = new Vector2(0, 0);

            var layout = container.AddComponent<VerticalLayoutGroup>();
            layout.spacing = 5;
            layout.childAlignment = TextAnchor.LowerLeft;
            layout.childForceExpandWidth = true;
            layout.childForceExpandHeight = false;

            // Alert prefab template
            var alertTemplate = CreatePanel("AlertTemplate", container.transform,
                Vector2.zero, Vector2.zero, Vector2.zero, Vector2.zero,
                new Color(0.8f, 0.6f, 0.2f, 0.9f));
            var alertRect = alertTemplate.GetComponent<RectTransform>();
            alertRect.sizeDelta = new Vector2(300, 35);
            var alertLayoutElem = alertTemplate.AddComponent<LayoutElement>();
            alertLayoutElem.preferredHeight = 35;

            var alertText = CreateText("AlertText", alertTemplate.transform, "Alert!", 13);
            alertText.color = Color.white;

            alertTemplate.SetActive(false); // Template, not visible

            SetPrivateField(uiManager, "alertContainer", container.transform);
            SetPrivateField(uiManager, "alertPrefab", alertTemplate);
        }

        private void CreateGameOverPanel()
        {
            var panel = CreatePanel("GameOverPanel", canvas.transform,
                new Vector2(0.2f, 0.2f), new Vector2(0.8f, 0.8f),
                Vector2.zero, Vector2.zero, new Color(0.1f, 0.05f, 0.05f, 0.95f));

            var titleGO = CreateText("Title", panel.transform, "GAME OVER", 36);
            var titleRect = titleGO.GetComponent<RectTransform>();
            titleRect.anchorMin = new Vector2(0, 0.7f);
            titleRect.anchorMax = new Vector2(1, 0.95f);
            titleRect.offsetMin = Vector2.zero;
            titleRect.offsetMax = Vector2.zero;
            titleGO.color = Color.red;
            titleGO.alignment = TextAlignmentOptions.Center;

            var infoText = CreateText("InfoText", panel.transform, "", 18);
            var infoRect = infoText.GetComponent<RectTransform>();
            infoRect.anchorMin = new Vector2(0.1f, 0.3f);
            infoRect.anchorMax = new Vector2(0.9f, 0.65f);
            infoRect.offsetMin = Vector2.zero;
            infoRect.offsetMax = Vector2.zero;
            infoText.alignment = TextAlignmentOptions.Center;

            var restartBtn = CreateButton("RestartBtn", panel.transform, "Restart", new Color(0.3f, 0.5f, 0.3f));
            var restartRect = restartBtn.GetComponent<RectTransform>();
            restartRect.anchorMin = new Vector2(0.3f, 0.1f);
            restartRect.anchorMax = new Vector2(0.7f, 0.25f);
            restartRect.offsetMin = Vector2.zero;
            restartRect.offsetMax = Vector2.zero;
            restartBtn.GetComponent<Button>().onClick.AddListener(() => GameManager.Instance?.RestartGame());

            SetPrivateField(uiManager, "gameOverPanel", panel);
            SetPrivateField(uiManager, "gameOverText", infoText);
        }

        private void CreateWinPanel()
        {
            var panel = CreatePanel("WinPanel", canvas.transform,
                new Vector2(0.2f, 0.2f), new Vector2(0.8f, 0.8f),
                Vector2.zero, Vector2.zero, new Color(0.05f, 0.1f, 0.05f, 0.95f));

            var titleGO = CreateText("Title", panel.transform, "VICTORY!", 36);
            var titleRect = titleGO.GetComponent<RectTransform>();
            titleRect.anchorMin = new Vector2(0, 0.6f);
            titleRect.anchorMax = new Vector2(1, 0.9f);
            titleRect.offsetMin = Vector2.zero;
            titleRect.offsetMax = Vector2.zero;
            titleGO.color = new Color(1f, 0.85f, 0.3f);
            titleGO.alignment = TextAlignmentOptions.Center;

            var subtitleText = CreateText("Subtitle", panel.transform,
                $"Population reached {GameConstants.MVP_WIN_POPULATION}!\nYour village thrives!", 20);
            var subRect = subtitleText.GetComponent<RectTransform>();
            subRect.anchorMin = new Vector2(0.1f, 0.35f);
            subRect.anchorMax = new Vector2(0.9f, 0.55f);
            subRect.offsetMin = Vector2.zero;
            subRect.offsetMax = Vector2.zero;
            subtitleText.alignment = TextAlignmentOptions.Center;

            var continueBtn = CreateButton("ContinueBtn", panel.transform, "Continue Playing",
                new Color(0.3f, 0.5f, 0.3f));
            var contRect = continueBtn.GetComponent<RectTransform>();
            contRect.anchorMin = new Vector2(0.2f, 0.1f);
            contRect.anchorMax = new Vector2(0.8f, 0.25f);
            contRect.offsetMin = Vector2.zero;
            contRect.offsetMax = Vector2.zero;
            continueBtn.GetComponent<Button>().onClick.AddListener(() =>
            {
                panel.SetActive(false);
                TimeManager.Instance?.SetSpeed(GameSpeed.Normal);
            });

            SetPrivateField(uiManager, "winPanel", panel);
        }

        // === UTILITY METHODS ===

        private GameObject CreatePanel(string name, Transform parent, Vector2 anchorMin, Vector2 anchorMax,
            Vector2 offsetMin, Vector2 offsetMax, Color color)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var rect = go.AddComponent<RectTransform>();
            rect.anchorMin = anchorMin;
            rect.anchorMax = anchorMax;
            rect.offsetMin = offsetMin;
            rect.offsetMax = offsetMax;
            var img = go.AddComponent<Image>();
            img.color = color;
            return go;
        }

        private TextMeshProUGUI CreateText(string name, Transform parent, string content, int fontSize)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var rect = go.AddComponent<RectTransform>();
            rect.sizeDelta = new Vector2(200, 30);
            var tmp = go.AddComponent<TextMeshProUGUI>();
            tmp.text = content;
            tmp.fontSize = fontSize;
            tmp.color = Color.white;
            tmp.alignment = TextAlignmentOptions.Left;
            return tmp;
        }

        private GameObject CreateButton(string name, Transform parent, string label, Color bgColor)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var rect = go.AddComponent<RectTransform>();
            rect.sizeDelta = new Vector2(150, 45);

            var img = go.AddComponent<Image>();
            img.color = bgColor;

            var btn = go.AddComponent<Button>();
            var colors = btn.colors;
            colors.normalColor = bgColor;
            colors.highlightedColor = bgColor * 1.2f;
            colors.pressedColor = bgColor * 0.8f;
            btn.colors = colors;

            var textGO = new GameObject("Text");
            textGO.transform.SetParent(go.transform, false);
            var textRect = textGO.AddComponent<RectTransform>();
            textRect.anchorMin = Vector2.zero;
            textRect.anchorMax = Vector2.one;
            textRect.offsetMin = new Vector2(5, 2);
            textRect.offsetMax = new Vector2(-5, -2);

            var tmp = textGO.AddComponent<TextMeshProUGUI>();
            tmp.text = label;
            tmp.fontSize = 16;
            tmp.alignment = TextAlignmentOptions.Center;
            tmp.color = Color.white;

            return go;
        }

        /// <summary>
        /// Use reflection to set serialized fields on UIManager.
        /// </summary>
        private void SetPrivateField(object target, string fieldName, object value)
        {
            var field = target.GetType().GetField(fieldName,
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            if (field != null)
            {
                field.SetValue(target, value);
            }
            else
            {
                Debug.LogWarning($"UISetup: Could not find field '{fieldName}' on {target.GetType().Name}");
            }
        }
    }
}

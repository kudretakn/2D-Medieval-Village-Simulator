using UnityEngine;
using UnityEngine.EventSystems;

namespace MedievalVillage
{
    /// <summary>
    /// Handles building placement mode.
    /// Ghost preview follows pointer, confirms on click/tap, cancels on right-click/escape.
    /// </summary>
    public class BuildingPlacer : MonoBehaviour
    {
        public static BuildingPlacer Instance { get; private set; }

        [Header("Settings")]
        [SerializeField] private Color validColor = new Color(0f, 1f, 0f, 0.4f);
        [SerializeField] private Color invalidColor = new Color(1f, 0f, 0f, 0.4f);

        private BuildingData currentBuilding;
        private GameObject ghostObject;
        private SpriteRenderer ghostRenderer;
        private bool isPlacingMode;
        private Vector2Int currentGridPos;
        private bool isValidPlacement;

        public bool IsPlacing => isPlacingMode;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Update()
        {
            if (!isPlacingMode) return;

            UpdateGhostPosition();
            HandleInput();
        }

        /// <summary>
        /// Enter building placement mode with the given building type.
        /// </summary>
        public void StartPlacing(BuildingData building)
        {
            if (building == null) return;

            // Cancel existing placement
            if (isPlacingMode) CancelPlacement();

            currentBuilding = building;
            isPlacingMode = true;

            // Create ghost preview
            ghostObject = new GameObject("BuildingGhost");
            ghostRenderer = ghostObject.AddComponent<SpriteRenderer>();
            ghostRenderer.sortingLayerName = "UI_World";
            ghostRenderer.sortingOrder = 10;

            if (building.worldSprite != null)
            {
                ghostRenderer.sprite = building.worldSprite;
            }
            else
            {
                // Fallback colored square
                ghostRenderer.color = validColor;
            }

            // Scale ghost to building size
            ghostObject.transform.localScale = new Vector3(
                building.size.x * GameConstants.TILE_SIZE,
                building.size.y * GameConstants.TILE_SIZE,
                1f
            );
        }

        /// <summary>
        /// Cancel placement mode.
        /// </summary>
        public void CancelPlacement()
        {
            isPlacingMode = false;
            currentBuilding = null;

            if (ghostObject != null)
            {
                Destroy(ghostObject);
                ghostObject = null;
            }
        }

        private void UpdateGhostPosition()
        {
            if (ghostObject == null || CameraController.Instance == null) return;

            Vector3 worldPos = CameraController.Instance.GetPointerWorldPosition();
            Vector2Int gridPos = GridManager.Instance.WorldToGrid(worldPos);
            currentGridPos = gridPos;

            // Snap ghost to grid
            Vector3 snappedPos = GridManager.Instance.GridToWorld(gridPos.x, gridPos.y);
            snappedPos.x += (currentBuilding.size.x - 1) * GameConstants.TILE_SIZE * 0.5f;
            snappedPos.y += (currentBuilding.size.y - 1) * GameConstants.TILE_SIZE * 0.5f;
            ghostObject.transform.position = snappedPos;

            // Check validity
            isValidPlacement = GridManager.Instance.CanPlaceBuilding(
                gridPos.x, gridPos.y, currentBuilding.size, currentBuilding
            ) && currentBuilding.CanAfford(ResourceManager.Instance);

            ghostRenderer.color = isValidPlacement ? validColor : invalidColor;
        }

        private void HandleInput()
        {
            // Cancel with Escape or right click
            if (Input.GetKeyDown(KeyCode.Escape) || Input.GetMouseButtonDown(1))
            {
                CancelPlacement();
                return;
            }

            // Don't place if over UI
            if (EventSystem.current != null && EventSystem.current.IsPointerOverGameObject())
                return;

            // Place with left click or touch
            if (Input.GetMouseButtonDown(0))
            {
                if (isValidPlacement)
                {
                    var instance = BuildingManager.Instance.PlaceBuilding(
                        currentBuilding,
                        currentGridPos.x,
                        currentGridPos.y
                    );

                    if (instance != null)
                    {
                        UIManager.Instance?.ShowAlert($"{currentBuilding.buildingName} placed!");

                        // Stay in placement mode if holding shift (desktop convenience)
                        if (!Input.GetKey(KeyCode.LeftShift))
                        {
                            CancelPlacement();
                        }
                    }
                }
                else
                {
                    UIManager.Instance?.ShowAlert("Cannot place here!");
                }
            }
        }
    }
}

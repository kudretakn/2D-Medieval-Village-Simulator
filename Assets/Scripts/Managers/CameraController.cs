using UnityEngine;

namespace MedievalVillage
{
    /// <summary>
    /// Handles camera pan and zoom.
    /// Supports both mouse (desktop) and touch (mobile) input.
    /// </summary>
    public class CameraController : MonoBehaviour
    {
        public static CameraController Instance { get; private set; }

        [Header("Pan Settings")]
        [SerializeField] private float panSpeed = GameConstants.CAMERA_PAN_SPEED;
        [SerializeField] private float panBorderThickness = 10f;
        [SerializeField] private bool enableEdgePan = false; // desktop only

        [Header("Zoom Settings")]
        [SerializeField] private float zoomSpeed = GameConstants.CAMERA_ZOOM_SPEED;
        [SerializeField] private float minZoom = GameConstants.CAMERA_MIN_ZOOM;
        [SerializeField] private float maxZoom = GameConstants.CAMERA_MAX_ZOOM;

        [Header("Bounds")]
        [SerializeField] private float boundsPadding = 2f;

        private Camera cam;
        private Vector3 lastMousePosition;
        private bool isDragging;

        // Touch support
        private float lastPinchDistance;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
            cam = GetComponent<Camera>();
            if (cam == null) cam = Camera.main;
        }

        /// <summary>
        /// Center camera on the map at start.
        /// </summary>
        public void CenterOnMap()
        {
            if (GridManager.Instance != null)
            {
                Vector3 center = GridManager.Instance.GetMapCenter();
                transform.position = new Vector3(center.x, center.y, transform.position.z);
            }
        }

        private void Update()
        {
            HandleKeyboardPan();
            HandleMousePan();
            HandleMouseZoom();
            HandleTouchInput();
            ClampPosition();
        }

        private void HandleKeyboardPan()
        {
            Vector3 move = Vector3.zero;

            if (Input.GetKey(KeyCode.W) || Input.GetKey(KeyCode.UpArrow))
                move.y += 1;
            if (Input.GetKey(KeyCode.S) || Input.GetKey(KeyCode.DownArrow))
                move.y -= 1;
            if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow))
                move.x -= 1;
            if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow))
                move.x += 1;

            if (move != Vector3.zero)
            {
                transform.position += move.normalized * panSpeed * Time.deltaTime;
            }
        }

        private void HandleMousePan()
        {
            // Middle mouse button or right mouse drag to pan
            if (Input.GetMouseButtonDown(2) || Input.GetMouseButtonDown(1))
            {
                isDragging = true;
                lastMousePosition = Input.mousePosition;
            }

            if (Input.GetMouseButtonUp(2) || Input.GetMouseButtonUp(1))
            {
                isDragging = false;
            }

            if (isDragging)
            {
                Vector3 delta = Input.mousePosition - lastMousePosition;
                float scaleFactor = cam.orthographicSize / (Screen.height * 0.5f);
                Vector3 move = new Vector3(-delta.x * scaleFactor, -delta.y * scaleFactor, 0);
                transform.position += move;
                lastMousePosition = Input.mousePosition;
            }

            // Edge pan (desktop)
            if (enableEdgePan && !isDragging)
            {
                Vector3 move = Vector3.zero;
                if (Input.mousePosition.y >= Screen.height - panBorderThickness)
                    move.y += 1;
                if (Input.mousePosition.y <= panBorderThickness)
                    move.y -= 1;
                if (Input.mousePosition.x >= Screen.width - panBorderThickness)
                    move.x += 1;
                if (Input.mousePosition.x <= panBorderThickness)
                    move.x -= 1;

                if (move != Vector3.zero)
                    transform.position += move.normalized * panSpeed * Time.deltaTime;
            }
        }

        private void HandleMouseZoom()
        {
            float scroll = Input.GetAxis("Mouse ScrollWheel");
            if (Mathf.Abs(scroll) > 0.01f)
            {
                cam.orthographicSize -= scroll * zoomSpeed * cam.orthographicSize;
                cam.orthographicSize = Mathf.Clamp(cam.orthographicSize, minZoom, maxZoom);
            }
        }

        private void HandleTouchInput()
        {
            if (Input.touchCount == 1)
            {
                Touch touch = Input.GetTouch(0);
                if (touch.phase == TouchPhase.Moved)
                {
                    float scaleFactor = cam.orthographicSize / (Screen.height * 0.5f);
                    Vector3 move = new Vector3(
                        -touch.deltaPosition.x * scaleFactor,
                        -touch.deltaPosition.y * scaleFactor,
                        0
                    );
                    transform.position += move;
                }
            }
            else if (Input.touchCount == 2)
            {
                // Pinch to zoom
                Touch touch0 = Input.GetTouch(0);
                Touch touch1 = Input.GetTouch(1);

                float currentDistance = Vector2.Distance(touch0.position, touch1.position);

                if (touch1.phase == TouchPhase.Began)
                {
                    lastPinchDistance = currentDistance;
                    return;
                }

                if (lastPinchDistance > 0)
                {
                    float delta = lastPinchDistance - currentDistance;
                    cam.orthographicSize += delta * 0.01f * zoomSpeed;
                    cam.orthographicSize = Mathf.Clamp(cam.orthographicSize, minZoom, maxZoom);
                }

                lastPinchDistance = currentDistance;
            }
            else
            {
                lastPinchDistance = 0;
            }
        }

        private void ClampPosition()
        {
            if (GridManager.Instance == null) return;

            float halfHeight = cam.orthographicSize;
            float halfWidth = halfHeight * cam.aspect;

            float minX = -boundsPadding + halfWidth;
            float maxX = GridManager.Instance.MapWidth * GameConstants.TILE_SIZE + boundsPadding - halfWidth;
            float minY = -boundsPadding + halfHeight;
            float maxY = GridManager.Instance.MapHeight * GameConstants.TILE_SIZE + boundsPadding - halfHeight;

            Vector3 pos = transform.position;
            pos.x = Mathf.Clamp(pos.x, minX, maxX);
            pos.y = Mathf.Clamp(pos.y, minY, maxY);
            transform.position = pos;
        }

        /// <summary>
        /// Get the world position under the mouse/touch pointer.
        /// </summary>
        public Vector3 GetPointerWorldPosition()
        {
            Vector3 mousePos = Input.mousePosition;
            mousePos.z = -cam.transform.position.z;
            return cam.ScreenToWorldPoint(mousePos);
        }

        /// <summary>
        /// Smoothly move camera to target position.
        /// </summary>
        public void FocusOn(Vector3 worldPos)
        {
            transform.position = new Vector3(worldPos.x, worldPos.y, transform.position.z);
        }
    }
}

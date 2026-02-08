using UnityEngine;

namespace MedievalVillage
{
    /// <summary>
    /// Top-level game orchestrator. Initializes all systems in correct order.
    /// Handles game state (playing, paused, game over, win).
    /// </summary>
    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }

        public enum GameState { Loading, Playing, Paused, GameOver, Win }

        [Header("Current State")]
        [SerializeField] private GameState currentState = GameState.Loading;

        public GameState CurrentState => currentState;

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Start()
        {
            InitializeGame();
        }

        /// <summary>
        /// Initialize all systems in dependency order.
        /// </summary>
        private void InitializeGame()
        {
            Debug.Log("=== Medieval Village Simulator - Initializing ===");

            // 1. Grid/Map first (other systems need it)
            if (GridManager.Instance != null)
            {
                GridManager.Instance.InitializeMap();
                Debug.Log("Grid initialized");
            }
            else
            {
                Debug.LogError("GridManager not found! Ensure it exists in the scene.");
                return;
            }

            // 2. Camera: center on map
            if (CameraController.Instance != null)
            {
                CameraController.Instance.CenterOnMap();
                Debug.Log("Camera centered");
            }

            // 3. Population system: initialize and spawn settlers
            if (PopulationManager.Instance != null)
            {
                PopulationManager.Instance.Initialize();
                PopulationManager.Instance.SpawnInitialVillagers();
                PopulationManager.Instance.OnPopulationChanged += CheckWinCondition;
                Debug.Log("Population initialized");
            }

            currentState = GameState.Playing;
            Debug.Log("=== Game Started! ===");
        }

        private void CheckWinCondition(int population)
        {
            if (population >= GameConstants.MVP_WIN_POPULATION && currentState == GameState.Playing)
            {
                OnWin();
            }
        }

        public void OnGameOver()
        {
            if (currentState == GameState.GameOver) return;

            currentState = GameState.GameOver;
            TimeManager.Instance?.SetSpeed(GameSpeed.Paused);
            UIManager.Instance?.ShowGameOver();
            Debug.Log("=== GAME OVER ===");
        }

        public void OnWin()
        {
            if (currentState == GameState.Win) return;

            currentState = GameState.Win;
            TimeManager.Instance?.SetSpeed(GameSpeed.Paused);
            UIManager.Instance?.ShowWinScreen();
            Debug.Log($"=== VICTORY! Population reached {GameConstants.MVP_WIN_POPULATION}! ===");
        }

        /// <summary>
        /// Restart the game (reload scene).
        /// </summary>
        public void RestartGame()
        {
            UnityEngine.SceneManagement.SceneManager.LoadScene(
                UnityEngine.SceneManagement.SceneManager.GetActiveScene().name
            );
        }

        /// <summary>
        /// Quit the game.
        /// </summary>
        public void QuitGame()
        {
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit();
#endif
        }
    }
}

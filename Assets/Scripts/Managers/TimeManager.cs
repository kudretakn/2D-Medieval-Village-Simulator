using UnityEngine;
using System;

namespace MedievalVillage
{
    /// <summary>
    /// Manages game time: hours, days, seasons, years.
    /// Provides events for other systems to subscribe to.
    /// Speed control: Pause, 1x, 2x, 3x.
    /// </summary>
    public class TimeManager : MonoBehaviour
    {
        public static TimeManager Instance { get; private set; }

        // === EVENTS ===
        /// <summary>Fires every game hour.</summary>
        public event Action OnGameHourTick;
        /// <summary>Fires at the start of each new day.</summary>
        public event Action OnNewDay;
        /// <summary>Fires at the start of each new season.</summary>
        public event Action<Season> OnNewSeason;
        /// <summary>Fires at the start of each new year.</summary>
        public event Action<int> OnNewYear;
        /// <summary>Fires when day phase changes (dawn, day, dusk, night).</summary>
        public event Action<DayPhase> OnDayPhaseChanged;

        // === STATE ===
        [Header("Current Time")]
        [SerializeField] private int currentHour = 6;
        [SerializeField] private int currentDay = 1;
        [SerializeField] private Season currentSeason = Season.Spring;
        [SerializeField] private int currentYear = 1;

        [Header("Speed")]
        [SerializeField] private GameSpeed gameSpeed = GameSpeed.Normal;

        private float hourTimer;
        private DayPhase currentPhase;

        // === PUBLIC PROPERTIES ===
        public int CurrentHour => currentHour;
        public int CurrentDay => currentDay;
        public Season CurrentSeason => currentSeason;
        public int CurrentYear => currentYear;
        public GameSpeed CurrentSpeed => gameSpeed;
        public DayPhase CurrentDayPhase => currentPhase;
        public bool IsPaused => gameSpeed == GameSpeed.Paused;

        /// <summary>Total game hours elapsed since game start.</summary>
        public int TotalHoursElapsed { get; private set; }

        private void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this;
        }

        private void Start()
        {
            currentPhase = GetDayPhase(currentHour);
        }

        private void Update()
        {
            if (gameSpeed == GameSpeed.Paused) return;

            float speedMultiplier = (int)gameSpeed;
            hourTimer += Time.deltaTime * speedMultiplier;

            float secondsPerHour = GameConstants.SECONDS_PER_GAME_HOUR;

            while (hourTimer >= secondsPerHour)
            {
                hourTimer -= secondsPerHour;
                AdvanceHour();
            }
        }

        private void AdvanceHour()
        {
            currentHour++;
            TotalHoursElapsed++;

            // Check day phase change
            DayPhase newPhase = GetDayPhase(currentHour);
            if (newPhase != currentPhase)
            {
                currentPhase = newPhase;
                OnDayPhaseChanged?.Invoke(currentPhase);
            }

            if (currentHour >= GameConstants.HOURS_PER_DAY)
            {
                currentHour = 0;
                AdvanceDay();
            }

            OnGameHourTick?.Invoke();
        }

        private void AdvanceDay()
        {
            currentDay++;
            OnNewDay?.Invoke();

            if (currentDay > GameConstants.DAYS_PER_SEASON)
            {
                currentDay = 1;
                AdvanceSeason();
            }
        }

        private void AdvanceSeason()
        {
            currentSeason = (Season)(((int)currentSeason + 1) % GameConstants.SEASONS_PER_YEAR);
            OnNewSeason?.Invoke(currentSeason);

            if (currentSeason == Season.Spring)
            {
                currentYear++;
                OnNewYear?.Invoke(currentYear);
            }
        }

        private DayPhase GetDayPhase(int hour)
        {
            if (hour >= 5 && hour < 7) return DayPhase.Dawn;
            if (hour >= 7 && hour < 12) return DayPhase.Morning;
            if (hour >= 12 && hour < 17) return DayPhase.Afternoon;
            if (hour >= 17 && hour < 19) return DayPhase.Dusk;
            return DayPhase.Night;
        }

        // === PUBLIC API ===

        public void SetSpeed(GameSpeed speed)
        {
            gameSpeed = speed;
        }

        public void TogglePause()
        {
            if (gameSpeed == GameSpeed.Paused)
                gameSpeed = GameSpeed.Normal;
            else
                gameSpeed = GameSpeed.Paused;
        }

        public void CycleSpeed()
        {
            gameSpeed = gameSpeed switch
            {
                GameSpeed.Paused => GameSpeed.Normal,
                GameSpeed.Normal => GameSpeed.Fast,
                GameSpeed.Fast => GameSpeed.VeryFast,
                GameSpeed.VeryFast => GameSpeed.Paused,
                _ => GameSpeed.Normal
            };
        }

        /// <summary>
        /// Get normalized time of day (0 = midnight, 0.5 = noon, 1 = midnight).
        /// Useful for day/night visual cycle.
        /// </summary>
        public float GetNormalizedTimeOfDay()
        {
            return (currentHour + hourTimer / GameConstants.SECONDS_PER_GAME_HOUR) / 24f;
        }

        /// <summary>
        /// Returns a formatted time string like "Day 5, Spring, Year 1 - 14:00"
        /// </summary>
        public string GetTimeString()
        {
            return $"Day {currentDay}, {currentSeason}, Year {currentYear} - {currentHour:D2}:00";
        }

        public bool IsNight()
        {
            return currentPhase == DayPhase.Night;
        }

        public bool IsWinter()
        {
            return currentSeason == Season.Winter;
        }
    }
}

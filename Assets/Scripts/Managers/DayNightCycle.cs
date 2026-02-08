using UnityEngine;

namespace MedievalVillage
{
    /// <summary>
    /// Simple day/night visual cycle using a screen overlay.
    /// Adjusts overlay color based on time of day.
    /// </summary>
    public class DayNightCycle : MonoBehaviour
    {
        [Header("Settings")]
        [SerializeField] private SpriteRenderer overlayRenderer;
        [SerializeField] private Color dawnColor = new Color(1f, 0.8f, 0.5f, 0.15f);
        [SerializeField] private Color dayColor = new Color(1f, 1f, 1f, 0f); // Transparent during day
        [SerializeField] private Color duskColor = new Color(1f, 0.5f, 0.3f, 0.2f);
        [SerializeField] private Color nightColor = new Color(0.1f, 0.1f, 0.3f, 0.4f);

        [Header("Global Light (optional)")]
        [SerializeField] private UnityEngine.Rendering.Universal.Light2D globalLight;
        [SerializeField] private float dayIntensity = 1f;
        [SerializeField] private float nightIntensity = 0.3f;

        private void Start()
        {
            // Create overlay if not assigned
            if (overlayRenderer == null)
            {
                var overlayGO = new GameObject("DayNightOverlay");
                overlayGO.transform.SetParent(Camera.main.transform);
                overlayGO.transform.localPosition = new Vector3(0, 0, 1);
                overlayRenderer = overlayGO.AddComponent<SpriteRenderer>();
                overlayRenderer.sortingLayerName = "UI_World";
                overlayRenderer.sortingOrder = 100;
                // Create a large white square sprite
                overlayRenderer.color = dayColor;

                // Scale to cover camera view
                overlayGO.transform.localScale = new Vector3(100, 100, 1);
            }
        }

        private void Update()
        {
            if (TimeManager.Instance == null) return;

            float t = TimeManager.Instance.GetNormalizedTimeOfDay();
            Color targetColor = EvaluateColor(t);

            if (overlayRenderer != null)
            {
                overlayRenderer.color = Color.Lerp(overlayRenderer.color, targetColor, Time.deltaTime * 2f);
            }

            // Update 2D global light if present
            if (globalLight != null)
            {
                float targetIntensity = Mathf.Lerp(nightIntensity, dayIntensity, GetLightCurve(t));
                globalLight.intensity = Mathf.Lerp(globalLight.intensity, targetIntensity, Time.deltaTime * 2f);
            }
        }

        private Color EvaluateColor(float normalizedTime)
        {
            // 0.0 = midnight, 0.25 = 6am, 0.5 = noon, 0.75 = 6pm
            if (normalizedTime < 0.2f) return nightColor;          // 0:00 - 4:48
            if (normalizedTime < 0.3f) return dawnColor;           // 4:48 - 7:12
            if (normalizedTime < 0.7f) return dayColor;            // 7:12 - 16:48
            if (normalizedTime < 0.8f) return duskColor;           // 16:48 - 19:12
            return nightColor;                                      // 19:12 - 24:00
        }

        private float GetLightCurve(float normalizedTime)
        {
            // Returns 0 at night, 1 during day, smooth transitions
            if (normalizedTime < 0.2f) return 0f;
            if (normalizedTime < 0.3f) return (normalizedTime - 0.2f) / 0.1f;
            if (normalizedTime < 0.7f) return 1f;
            if (normalizedTime < 0.8f) return 1f - (normalizedTime - 0.7f) / 0.1f;
            return 0f;
        }
    }
}

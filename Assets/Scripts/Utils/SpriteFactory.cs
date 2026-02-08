using UnityEngine;

namespace MedievalVillage
{
    /// <summary>
    /// Generates simple colored square sprites at runtime for prototyping.
    /// No external assets needed - everything is procedurally generated.
    /// </summary>
    public static class SpriteFactory
    {
        private static Texture2D whiteTexture;

        /// <summary>
        /// Create a colored square sprite.
        /// </summary>
        public static Sprite CreateSquareSprite(Color color, int pixelSize = 32)
        {
            var texture = new Texture2D(pixelSize, pixelSize);
            texture.filterMode = FilterMode.Point;

            Color[] pixels = new Color[pixelSize * pixelSize];
            for (int i = 0; i < pixels.Length; i++)
                pixels[i] = color;
            texture.SetPixels(pixels);
            texture.Apply();

            return Sprite.Create(texture,
                new Rect(0, 0, pixelSize, pixelSize),
                new Vector2(0.5f, 0.5f),
                pixelSize);
        }

        /// <summary>
        /// Create a simple building sprite with an outline.
        /// </summary>
        public static Sprite CreateBuildingSprite(Color fillColor, Color outlineColor, int pixelSize = 32)
        {
            var texture = new Texture2D(pixelSize, pixelSize);
            texture.filterMode = FilterMode.Point;

            for (int x = 0; x < pixelSize; x++)
            {
                for (int y = 0; y < pixelSize; y++)
                {
                    bool isBorder = x <= 1 || x >= pixelSize - 2 || y <= 1 || y >= pixelSize - 2;
                    texture.SetPixel(x, y, isBorder ? outlineColor : fillColor);
                }
            }
            texture.Apply();

            return Sprite.Create(texture,
                new Rect(0, 0, pixelSize, pixelSize),
                new Vector2(0.5f, 0.5f),
                pixelSize);
        }

        /// <summary>
        /// Create a simple villager sprite (circle-ish).
        /// </summary>
        public static Sprite CreateVillagerSprite(Color bodyColor, int pixelSize = 16)
        {
            var texture = new Texture2D(pixelSize, pixelSize);
            texture.filterMode = FilterMode.Point;

            float center = pixelSize / 2f;
            float radius = pixelSize / 2f - 1;

            for (int x = 0; x < pixelSize; x++)
            {
                for (int y = 0; y < pixelSize; y++)
                {
                    float dist = Vector2.Distance(new Vector2(x, y), new Vector2(center, center));
                    if (dist <= radius)
                        texture.SetPixel(x, y, bodyColor);
                    else
                        texture.SetPixel(x, y, Color.clear);
                }
            }
            texture.Apply();

            return Sprite.Create(texture,
                new Rect(0, 0, pixelSize, pixelSize),
                new Vector2(0.5f, 0.5f),
                pixelSize);
        }

        /// <summary>
        /// Get a plain white 1x1 texture (for UI overlays etc.)
        /// </summary>
        public static Texture2D GetWhiteTexture()
        {
            if (whiteTexture == null)
            {
                whiteTexture = new Texture2D(1, 1);
                whiteTexture.SetPixel(0, 0, Color.white);
                whiteTexture.Apply();
            }
            return whiteTexture;
        }
    }
}

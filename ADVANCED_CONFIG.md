# Configuración avanzada - Ejemplos

Este archivo contiene ejemplos de configuraciones personalizadas y trucos para casos especiales.

## 1. Crear un perfil personalizado para tu mapa

### Opción A: Usar la interfaz (Recomendado)

1. Ejecuta el script
2. Ajusta todos los parámetros con los sliders
3. Pulsa **g** para guardar como "custom"
4. El perfil se guarda en `perfiles_colisiones_rpg.json`

### Opción B: Editar JSON directamente

Después de ejecutar una vez (para que se cree `perfiles_colisiones_rpg.json`), edita:

```json
{
  "bosque": { ... },
  "ciudad": { ... },
  "costa": { ... },
  "custom": {
    "modo": 2,
    "blur": 5,
    "canny_low": 30,
    "canny_high": 100,
    "kernel": 7,
    "h_min": 0,
    "h_max": 179,
    "s_min": 0,
    "s_max": 255,
    "v_min": 0,
    "v_max": 255,
    "min_w": 20,
    "min_h": 20,
    "max_w_pct": 90,
    "max_h_pct": 90,
    "base_pct": 40,
    "margen_x_pct": 5,
    "hybrid_hsv_ranges": [
      {
        "type": "agua",
        "h_min": 80,
        "h_max": 130,
        "s_min": 40,
        "s_max": 255,
        "v_min": 20,
        "v_max": 255
      },
      {
        "type": "tejado",
        "h_min": 0,
        "h_max": 25,
        "s_min": 50,
        "s_max": 255,
        "v_min": 40,
        "v_max": 255
      },
      {
        "type": "vegetacion",
        "h_min": 35,
        "h_max": 90,
        "s_min": 35,
        "s_max": 255,
        "v_min": 20,
        "v_max": 255
      }
    ]
  }
}
```

## 2. Casos de uso frecuentes

### Caso: Detectar solo agua (río/lago)

```bash
# En el script:
# 1. Pulsa 2 o 4 (cargar un perfil)
# 2. Pulsa O para desactivar solidos
# 3. Pulsa T para desactivar tejado
# 4. Pulsa V para desactivar vegetacion
# 5. Pulsa s para guardar (solo agua)
```

### Caso: Mapas con mucho dithering (ruido visual)

```
Aumentar:
- Blur: 7-9
- Kernel: 7-9
- Canny Low: 50-70

Reducir:
- Canny High: 100-130 (menos sensible a transiciones suaves)
```

### Caso: Mapas con colores saturados

```
Editar HYBRID_HSV_RANGES en el código:
- Reducir S_min a 0 (permita colores desaturados)
- Expandir rangos H (ej: agua 70-140 en lugar de 80-130)
```

### Caso: Pixel art muy pequeño (32x32 tiles)

```
- Min W/H: 12-16 (objetos mínimos)
- Blur: 3 (preservar detalles)
- Kernel: 3-5 (conexiones suaves)
- Base%: 35-40 (colisión en parte más baja)
```

### Caso: Pixel art muy grande (128x128 tiles)

```
- Min W/H: 40-60
- Blur: 5-7
- Kernel: 7-9
- Base%: 35-45
```

## 3. Valores de referencia por tipo de arte

### Stardew Valley / Grounded (pixel art chico, colores planos)
```
Modo: 2 (híbrido)
Blur: 3
Canny Low: 25
Canny High: 95
Kernel: 5
Min W/H: 16
Base%: 40
Margen X%: 5
```

### Zelda Link's Awakening (colores simples, formas geométricas)
```
Modo: 2
Blur: 5
Canny Low: 35
Canny High: 120
Kernel: 7
Min W/H: 24
Base%: 35
Margen X%: 4
```

### Terraria (mucho detalle, texturas)
```
Modo: 2
Blur: 7
Canny Low: 40
Canny High: 130
Kernel: 9
Min W/H: 20
Base%: 45
Margen X%: 5
```

### Top-Down RPG (Ocarina of Time style)
```
Modo: 2
Blur: 5
Canny Low: 30
Canny High: 100
Kernel: 7
Min W/H: 24
Base%: 40
Margen X%: 5
```

## 4. Personalizar rangos HSV por tipo

### Editar en el código (líneas 14-42):

```python
HYBRID_HSV_RANGES = [
    {
        "type": "agua",
        "h_min": 80,      # ← Cambiar si el agua es más azul (90) o más verde (60)
        "h_max": 130,
        "s_min": 40,      # ← Si el agua es pálida, reducir a 0-20
        "s_max": 255,
        "v_min": 20,      # ← Agua oscura: 50-80; agua clara: 0-30
        "v_max": 255,
    },
    # ... más tipos
]
```

### Referencia HSV (Hue de 0-179 en OpenCV):

| Color | H (rango) | Ejemplo |
|-------|-----------|---------|
| Rojo | 0, 175-179 | Tejados, flores |
| Naranja | 10-20 | Madera, fuego |
| Amarillo | 20-35 | Oro, flores |
| Verde | 35-90 | Vegetación, hierba |
| Cyan | 90-110 | Agua clara |
| Azul | 110-130 | Agua oscura |
| Magenta | 130-179 | Raramente usado |

## 5. Exportar datos y usar en motor

### JSON generado

```json
{
  "colisiones": [
    { "x": 150, "y": 200, "width": 48, "height": 16, "type": "solido" },
    { "x": 300, "y": 150, "width": 32, "height": 24, "type": "agua" }
  ],
  "por_tipo": {
    "solido": [ ... ],
    "agua": [ ... ],
    "tejado": [ ... ],
    "vegetacion": [ ... ]
  }
}
```

### Usar en Python (ejemplo muy básico):

```python
import json

with open("datos_colisiones_rpg_hibrido.json") as f:
    data = json.load(f)

# Acceder a todas las colisiones
for col in data["colisiones"]:
    x, y, w, h = col["x"], col["y"], col["width"], col["height"]
    tipo = col["type"]
    print(f"Obstáculo {tipo} en ({x}, {y}) - {w}x{h}")

# O acceder por tipo
agua_colisiones = data["por_tipo"].get("agua", [])
print(f"Total obstáculos de agua: {len(agua_colisiones)}")
```

### Usar en C#/.NET (motor Godot/monogame/etc):

```csharp
using System.Collections.Generic;
using Newtonsoft.Json;

public class CollisionData
{
    public List<Collision> colisiones { get; set; }
    public Dictionary<string, List<Collision>> por_tipo { get; set; }
}

public class Collision
{
    public int x { get; set; }
    public int y { get; set; }
    public int width { get; set; }
    public int height { get; set; }
    public string type { get; set; }
}

// Cargar
string json = File.ReadAllText("datos_colisiones_rpg_hibrido.json");
var data = JsonConvert.DeserializeObject<CollisionData>(json);

// Usar
foreach (var col in data.colisiones)
{
    if (col.type == "solido")
        CreateWall(col.x, col.y, col.width, col.height);
}
```

## 6. Tip: Combinar múltiples capas

Si tu mapa tiene múltiples capas (agua debajo, suelo, objetos, cielo), exporta cada capa por separado:

1. Carga capa de agua
2. Modo HSV, ajusta rangos para agua
3. Pulsa s → `datos_colisiones_rpg_agua.json`
4. Carga capa de objetos
5. Modo Bordes, ajusta Canny
6. Pulsa g → guarda perfil como "objetos"
7. Pulsa s → `datos_colisiones_rpg_bordes.json`

Luego fusiona los JSONs en el motor.

## 7. Debugging avanzado

### Ver solo la máscara binaria

En el panel derecho de la ventana, ves la máscara blanca/negra. Usa eso para:

- **Blanco**: Detectado como obstáculo
- **Negro**: Fondo seguro

Si hay ruido blanco pequeño → aumenta Canny Low.
Si faltan obstáculos → reduce Canny Low.

### Verificar overlaps

Usa toggles (A/T/V/O) para ver si hay:
- Agua detectada donde no debería (ajusta H_min/H_max de agua)
- Sólidos sin detectar (ajusta Canny)
- Tipos superpuestos (edita rangos para que no se solapen)

---

**¡Listo para personalizaciones!** 🎨

Cualquier duda, experimenta con los sliders en tiempo real y guarda perfiles distintos para comparar.

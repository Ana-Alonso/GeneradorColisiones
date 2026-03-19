# Extractor de Colisiones RPG Top-Down 🎮

Script interactivo de Python con OpenCV para extraer cajas de colisión de mapas 2D pixel art con depuración visual en tiempo real.

## Características principales

✅ **3 modos de detección:**
- Modo 0: Detección por bordes (Canny + morfología)
- Modo 1: Segmentación HSV (selección manual de color)
- Modo 2: Híbrido automático (Bordes + HSV por tipos: agua/tejado/vegetacion)

✅ **Controles interactivos:** Sliders en vivo para ajustar Blur, Canny, Kernel, HSV y filtros de tamaño.

✅ **Perfiles guardables:** Bosque, Ciudad, Costa y Custom en formato JSON.

✅ **Edición de tipos HSV:** Ajusta rangos de agua/tejado/vegetacion sin editar código.

✅ **Toggles de visibilidad:** Muestra/oculta tipos individuales para depuración rápida.

✅ **Exportación etiquetada:** JSON con colisiones agrupadas por tipo + imagen preview.

---

## Instalación

### Requisitos previos
- Python 3.7+
- OpenCV: `pip install opencv-python`
- NumPy: `pip install numpy`

### Configuración
1. Coloca tu imagen de mapa en la misma carpeta que el script, llamada `fondo1.png` (o edita la línea final del script).
2. Ejecuta desde terminal:
```bash
python generar_colisiones.py
```

---

## Controles

### Atajos principales

| Tecla | Función |
|-------|---------|
| **s** | Guardar JSON + imagen preview |
| **q** / **ESC** | Salir |
| **g** | Guardar perfil actual como `custom` |
| **1/2/3/4** | Cargar perfil bosque/ciudad/costa/custom |

### Edición de tipos HSV (modo híbrido)

| Tecla | Función |
|-------|---------|
| **a** | Seleccionar tipo agua |
| **t** | Seleccionar tipo tejado |
| **v** | Seleccionar tipo vegetacion |
| **u** | Aplicar sliders H2/S2/V2 al tipo seleccionado |

### Toggles de visibilidad

| Tecla | Función |
|-------|---------|
| **A** (mayúscula) | Toggle agua on/off |
| **T** (mayúscula) | Toggle tejado on/off |
| **V** (mayúscula) | Toggle vegetacion on/off |
| **O** (mayúscula) | Toggle solidos on/off |

### Sliders en la ventana

- **Modo** (0-2): Selecciona modo de detección
- **Blur (impar)**: Tamaño de desenfoque (1-31)
- **Canny Low/High**: Umbrales de detección de bordes (0-255)
- **Kernel (impar)**: Tamaño de kernel morfológico (1-31)
- **H/S/V min/max**: Rangos HSV para modo 1
- **H2/S2/V2 min/max**: Rangos HSV para tipo activo en modo híbrido
- **Min W/H**: Tamaño mínimo de caja (píxeles)
- **Max W%/H%**: Tamaño máximo de caja (% de imagen)
- **Base%**: Altura de colisión respecto al objeto (% de altura del objeto)
- **Margen X%**: Margen lateral para ajustar ancho (%)

---

## Flujo de trabajo típico

### Paso 1: Cargar y calibrar
1. Ejecuta el script con tu imagen.
2. Carga un perfil inicial (tecla 1/2/3) según el tipo de mapa.
3. Ajusta Blur, Canny y Kernel hasta que veas bien los obstáculos en la máscara binaria (panel derecho).

### Paso 2: Depurar con toggles
1. Pulsa **A/T/V/O** para activar/desactivar tipos individuales.
2. Verifica que solo ves las colisiones que querés.
3. Si un tipo falla, sigue al paso 3.

### Paso 3: Afinar rangos HSV (modo híbrido)
1. Pulsa **a** (agua), **t** (tejado) o **v** (vegetacion) para seleccionar tipo.
2. Ajusta sliders H2/S2/V2 en la ventana para refinar la detección.
3. Pulsa **u** para aplicar cambios.

### Paso 4: Guardar perfil
1. Una vez satisfecho, pulsa **g** para guardar como `custom`.
2. El perfil se guarda en `perfiles_colisiones_rpg.json`.

### Paso 5: Exportar
1. Pulsa **s** para guardar:
   - `mapa_con_colisiones_rpg_hibrido.jpg` (preview con cajas)
   - `datos_colisiones_rpg_hibrido.json` (colisiones etiquetadas)

---

## Estructura del JSON exportado

```json
{
  "colisiones": [
    {
      "x": 100,
      "y": 150,
      "width": 50,
      "height": 20,
      "type": "solido"
    },
    {
      "x": 200,
      "y": 80,
      "width": 60,
      "height": 25,
      "type": "agua"
    }
  ],
  "por_tipo": {
    "solido": [...],
    "agua": [...],
    "tejado": [...],
    "vegetacion": [...]
  }
}
```

---

## Perfiles disponibles

### Bosque
- Optimizado para mapas con vegetación densa y sombras.
- Kernel pequeño (5) para detalles finos.

### Ciudad
- Enfocado en estructuras rectangulares (edificios).
- Kernel más grande (7) para agrupar detalles.

### Costa
- Especializado en agua y playas.
- Rangos HSV preajustados para agua azul.

### Custom
- Se guarda con tu configuración actual.
- Pulsa **g** en cualquier momento para actualizar.

---

## Rangos HSV por defecto para modo híbrido

| Tipo | H_min | H_max | S_min | S_max | V_min | V_max |
|------|-------|-------|-------|-------|-------|-------|
| Agua | 80 | 130 | 40 | 255 | 20 | 255 |
| Tejado | 0 | 25 | 50 | 255 | 40 | 255 |
| Vegetacion | 35 | 90 | 35 | 255 | 20 | 255 |

**Modificar en código:** Edita la sección `HYBRID_HSV_RANGES` al inicio del script.

---

## Recomendaciones para pixel art

### Blur
- Pixel art fino: 3-5
- Pixel art grueso: 5-7
- Demasiado alto: pierde detalles

### Canny Low/High
- Conservador: 20-50 / 70-120
- Agresivo: 10-30 / 60-100
- Diferencia mínima recomendada: 50 unidades

### Kernel
- Impar requerido: 1, 3, 5, 7, 9...
- Valores bajos mantienen precisión
- Valores altos unifican objetos cercanos

### Filtros de tamaño
- **Min W/H:** Evita flores, torches, etc. Empieza en 18-24.
- **Max %:** 85-95 para evitar capturar la capa de fondo completa.

---

## Troubleshooting

### "No se detectan obstáculos"
1. Sube Canny Low (reduce a 20-35).
2. Aumenta Blur un poco (5-7).
3. Verifica que el tipo está activado (toggle en ON).

### "Demasiado ruido en la máscara"
1. Baja Canny Low (aumenta a 50+).
2. Sube Kernel (7-9).
3. Reduce Blur si está muy alto.

### "Colisiones fragmentadas en varios rectángulos"
1. Aumenta Kernel para unir fragmentos.
2. Reduce Canny High (diferencia mayor con Low).

### "Custom no se guarda"
1. Verifica que la carpeta de `fondo1.png` tiene permisos de escritura.
2. Revisa la terminal para mensajes de error.
3. El archivo se guarda como `perfiles_colisiones_rpg.json`.

---

## Ejemplo de uso rápido

```bash
# 1. Ejecutar
python generar_colisiones.py

# 2. En la ventana de OpenCV:
# - Pulsa 2 para cargar perfil "ciudad"
# - Mueve slider Blur hasta ver bien obstáculos
# - Pulsa A/T/V/O para probar toggles
# - Pulsa s para guardar
# - Pulsa q para salir
```

**Resultado:** Archivos `mapa_con_colisiones_rpg_hibrido.jpg` y `datos_colisiones_rpg_hibrido.json` en la misma carpeta.

---

## Colores en la preview

| Color | Significado |
|-------|-----------|
| Azul claro | Contorno visual del objeto |
| Rojo | Caja de colisión (solido) |
| Amarillo | Caja de colisión (agua) |
| Cyan | Caja de colisión (tejado) |
| Verde | Caja de colisión (vegetacion) |
| Blanco (derecha) | Máscara binaria de detección |

---

## Notas técnicas

- **IoU Threshold:** 0.55 para deduplicación de cajas en modo híbrido.
- **Contornos:** RETR_EXTERNAL + CHAIN_APPROX_SIMPLE.
- **Base de colisión:** Por defecto 40% inferior (editable con slider Base%).
- **Margen X:** Por defecto 5% (editable con slider Margen X%).

---

## Licencia y créditos

Script desarrollado con especialización en visión artificial para RPG top-down en pixel art.

Basado en librerías:
- OpenCV (cv2)
- NumPy
- JSON (estándar Python)

---

**¿Preguntas o mejoras?** El script está diseñado para ser modificable. 
Edita `HYBRID_HSV_RANGES`, `DEFAULT_PROFILES` o funciones de detección según tus necesidades. 🚀

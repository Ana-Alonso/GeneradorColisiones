# Configuracion avanzada

Esta guia documenta ajustes finos del script actual (`generar_colisiones.py`) y estrategias para distintos mapas.

## 1. Donde se guardan los perfiles

El archivo `perfiles_colisiones_rpg.json` se guarda en la carpeta de la imagen que abriste.

Campos por perfil:

- `modo`, `blur`, `canny_low`, `canny_high`, `kernel`
- `h_min/h_max`, `s_min/s_max`, `v_min/v_max`
- `min_w`, `min_h`, `max_w_pct`, `max_h_pct`
- `base_pct`, `margen_x_pct`
- `hybrid_hsv_ranges` (lista por tipo)

## 2. Rango HSV por tipo en modo hibrido

Tipos incluidos por defecto:

- `agua`
- `tejado`
- `vegetacion`

Cada tipo usa:

```json
{
  "type": "agua",
  "h_min": 80,
  "h_max": 130,
  "s_min": 40,
  "s_max": 255,
  "v_min": 20,
  "v_max": 255
}
```

Para ajustar en caliente:

1. Pulsa `a`, `t` o `v`.
2. Mueve sliders `H2/S2/V2`.
3. Pulsa `u`.

## 3. Calibracion por escenario

### Mapa con mucho ruido de textura

- `Blur`: 5-9
- `Kernel`: 7-9
- `Canny Low`: 45-80
- `Min W/H`: subir para filtrar objetos pequenos

### Mapa muy limpio y pixel art fino

- `Blur`: 3-5
- `Kernel`: 3-5
- `Canny Low`: 20-40
- `Min W/H`: 12-20

### Falta deteccion en base de obstaculos

- Sube `Base %` (ej. 45-55) para hacer colision mas alta.
- Reduce `Margen X %` (ej. 2-4) para ensanchar la base.

### Exceso de colisiones gigantes

- Baja `Max W %` y `Max H %`.
- En mapas grandes suele funcionar 80-92.

## 4. Edicion manual precisa

Funciones soportadas:

- Dibujar y mover con mouse.
- Redimensionar con handle inferior derecho.
- Seleccion por teclado con `n/p`.
- Edicion numerica con trackbars `Manual X/Y/W/H`.
- Borrado de seleccionado con `x`.
- `z` deshace ultimo.
- `c` limpia todo.

## 5. Merge de manuales

`m` fusiona solo rectangulos del mismo tipo y solo para tipos habilitados.

Toggles de merge:

- `k`: `solido`
- `l`: `agua`
- `b`: `tejado`
- `r`: `vegetacion`

Presets:

- `5`: solo `solido`
- `6`: solo `agua`
- `7`: todos

Notas:

- Criterio de fusion: interseccion > 0 o IoU >= 0.2.
- Al guardar (`s` o boton) tambien se ejecuta merge de manuales.

## 6. Exportacion

Al guardar se solicitan 2 archivos:

1. Imagen resultado (`.png`, `.jpg`, `.jpeg`, `.webp`)
2. JSON resultado (`.json`)

Estructura de salida:

```json
{
  "colisiones": [
    { "x": 10, "y": 20, "width": 30, "height": 12, "type": "solido" }
  ],
  "por_tipo": {
    "solido": [],
    "agua": [],
    "tejado": [],
    "vegetacion": []
  }
}
```

## 7. Parametros internos relevantes

- Deduplicacion en modo hibrido: IoU `0.55`.
- Contornos: `RETR_EXTERNAL` + `CHAIN_APPROX_SIMPLE`.
- `Canny High` se fuerza a ser mayor que `Canny Low`.
- `Blur` y `Kernel` se fuerzan a impar.

## 8. Sugerencias para motores de juego

- Usa `por_tipo` para capas de colision diferenciadas.
- Trata `agua` como zona de movimiento restringido o efecto.
- Trata `tejado` como capa de ocultacion/altura si aplica.
- Mantiene `solido` para bloqueo duro.

## 9. Estrategia recomendada de calibracion

1. Ajusta primero bordes (`Blur`, `Canny`, `Kernel`) hasta estabilizar `solido`.
2. Ajusta luego los tipos HSV (`a/t/v` + `H2/S2/V2` + `u`).
3. Corrige excepciones con manuales (mouse + `Manual X/Y/W/H`).
4. Aplica merge segun tipo (`m` y toggles `k/l/b/r`).
5. Exporta y valida en motor antes de guardar `custom`.

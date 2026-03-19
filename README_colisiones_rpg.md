# Extractor de Colisiones RPG Top-Down

Script interactivo en Python + OpenCV para generar colisiones de mapas 2D con depuracion visual en tiempo real (preview + mascara).

## Resumen funcional

- 3 modos de deteccion:
  - Modo 0: bordes (Canny + cierre morfologico).
  - Modo 1: HSV (segmentacion por rango de color).
  - Modo 2: hibrido (solidos por bordes + tipos HSV por rango).
- Tipos de colision soportados:
  - `solido`, `agua`, `tejado`, `vegetacion`.
- Editor manual integrado:
  - Dibujar, mover, redimensionar, borrar y editar por trackbars.
- Fusion de rectangulos manuales por tipo (con toggles por tipo).
- Perfiles persistentes en `perfiles_colisiones_rpg.json`.
- Guardado con selector de rutas (imagen + JSON).

## Requisitos

- Python 3.8+
- opencv-python
- numpy

Instalacion:

```bash
pip install opencv-python numpy
```

## Ejecucion

```bash
python generar_colisiones.py
```

Al ejecutar, el script abre un selector de archivo para elegir la imagen.

Formatos de entrada permitidos:

- `.jpg`, `.jpeg`, `.png`, `.webp`, `.web`

## Flujo recomendado

1. Carga una imagen.
2. Pulsa `1`, `2` o `3` para cargar perfil base (`bosque`, `ciudad`, `costa`).
3. Ajusta sliders hasta limpiar la mascara del panel derecho.
4. Si hace falta, agrega/retoca colisiones manuales con mouse.
5. Pulsa `s` o boton `GUARDAR` para exportar.
6. Si quieres guardar la calibracion, pulsa `g` para actualizar perfil `custom`.

## Controles de teclado

### General

- `q` o `ESC`: salir.
- `s`: abrir dialogos para guardar imagen + JSON.
- `g`: guardar configuracion actual como perfil `custom`.
- `1/2/3/4`: cargar `bosque/ciudad/costa/custom`.

### Tipos HSV (modo hibrido)

- `a`: tipo activo `agua`.
- `t`: tipo activo `tejado`.
- `v`: tipo activo `vegetacion`.
- `u`: aplicar sliders `H2/S2/V2` al tipo activo.

### Tipo manual

- `o`: tipo manual `solido`.
- `a/t/v`: tambien cambian tipo manual a `agua/tejado/vegetacion`.

### Visibilidad por tipo

- `A`: mostrar/ocultar `agua`.
- `T`: mostrar/ocultar `tejado`.
- `V`: mostrar/ocultar `vegetacion`.
- `O`: mostrar/ocultar `solido`.

### Rectangulos manuales

- Click izquierdo + arrastrar: crear rectangulo.
- Click izquierdo sobre rectangulo: seleccionar y mover.
- Arrastrar esquina inferior derecha: redimensionar.
- Click derecho sobre rectangulo: borrar.
- `n/p`: siguiente/anterior rectangulo manual.
- `x`: borrar rectangulo seleccionado.
- `z`: deshacer ultimo rectangulo creado.
- `c`: limpiar todos los rectangulos manuales.

### Fusion de manuales

- `m`: fusionar manuales solapados del mismo tipo.
- `k/l/b/r`: activar/desactivar merge para `solido/agua/tejado/vegetacion`.
- `5`: preset merge solo `solido`.
- `6`: preset merge solo `agua`.
- `7`: preset merge todos los tipos.

## Trackbars disponibles

- `Modo (0 Bordes, 1 HSV, 2 Hibrido)`.
- `Blur (impar)`, `Canny Low`, `Canny High`, `Kernel (impar)`.
- `H min/max`, `S min/max`, `V min/max` (modo HSV global).
- `H2 min/max`, `S2 min/max`, `V2 min/max` (tipo HSV activo en hibrido).
- `Min W`, `Min H`, `Max W %`, `Max H %`.
- `Base %`, `Margen X %`.
- `Manual X`, `Manual Y`, `Manual W`, `Manual H` (rectangulo seleccionado).

## Archivos de salida

Al guardar, el script pide rutas para:

- Imagen con preview y cajas dibujadas (`.png`, `.jpg`, `.jpeg`, `.webp`).
- JSON con colisiones.

Estructura JSON:

```json
{
  "colisiones": [
    { "x": 100, "y": 150, "width": 50, "height": 20, "type": "solido" },
    { "x": 200, "y": 80, "width": 60, "height": 25, "type": "agua" }
  ],
  "por_tipo": {
    "solido": [],
    "agua": [],
    "tejado": [],
    "vegetacion": []
  }
}
```

## Perfiles

Perfiles por defecto:

- `bosque`
- `ciudad`
- `costa`

Perfil editable:

- `custom` (se guarda con `g`).

Archivo de perfiles:

- `perfiles_colisiones_rpg.json` en la misma carpeta de la imagen abierta.

## Notas de deteccion

- `Base %` controla cuanto ocupa la colision en la base del objeto.
- `Margen X %` recorta lateralmente la caja de colision.
- El modo hibrido deduplica colisiones automaticas con IoU 0.55.
- Los manuales se fusionan por interseccion o IoU (0.2) cuando ejecutas `m` o al guardar.

## Troubleshooting rapido

- No detecta casi nada:
  - Baja `Canny Low` (20-35) y/o `Min W/H`.
  - Revisa visibilidad por tipo (A/T/V/O).
- Hay mucho ruido:
  - Sube `Canny Low` y `Kernel`.
  - Ajusta `Blur` en rango 3-7.
- Agua/tejado/vegetacion salen mal:
  - Selecciona tipo (`a/t/v`) y ajusta sliders `H2/S2/V2`.
  - Pulsa `u` para aplicar.
- El rectangulo seleccionado se mueve raro:
  - Ajusta numericamente con `Manual X/Y/W/H`.

## Recomendacion de uso

- Usa `1/2/3` para empezar desde un perfil base antes de calibrar.
- Guarda en `custom` con `g` cuando encuentres una configuracion estable.
- Exporta varias veces durante el ajuste para validar el JSON en tu motor.

## Dependencias

- OpenCV (`cv2`)
- NumPy
- Tkinter (dialogos de abrir/guardar)
- JSON/os/copy (stdlib)

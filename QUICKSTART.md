# Quick Start (1 minuto)

## 1. Instalar dependencias

```bash
pip install opencv-python numpy
```

## 2. Ejecutar

```bash
python generar_colisiones.py
```

Se abrira un selector para elegir la imagen.

## 3. Calibrar rapido

1. Pulsa `2` para empezar con perfil `ciudad` (suele ser estable).
2. Ajusta `Blur`, `Canny Low/High`, `Kernel`.
3. Verifica mascara en panel derecho.
4. Si usas hibrido, edita tipos con `a/t/v` y sliders `H2/S2/V2`.
5. Pulsa `u` para aplicar esos rangos al tipo activo.

## 4. Corregir manualmente (si hace falta)

- Dibuja con click izquierdo + arrastre.
- Mueve con click izquierdo sobre rectangulo.
- Redimensiona desde esquina inferior derecha.
- Borra con click derecho o con `x` si esta seleccionado.

## 5. Exportar

- Pulsa `s` o click en boton `GUARDAR`.
- Elige ruta para imagen y para JSON.

## 6. Guardar perfil

- Pulsa `g` para guardar la configuracion actual como `custom`.
- Pulsa `4` para cargar `custom` en futuras sesiones.

## Checklist final

- La mascara del panel derecho representa bien lo que quieres bloquear.
- Revisaste visibilidad por tipo con `A/T/V/O`.
- Ajustaste o corregiste manuales si hacia falta.
- Exportaste imagen y JSON con `s`.

---

## Atajos esenciales

- `1/2/3/4`: cargar `bosque/ciudad/costa/custom`.
- `A/T/V/O`: mostrar u ocultar tipos.
- `m`: fusionar manuales segun tipos habilitados.
- `k/l/b/r`: toggles merge `solido/agua/tejado/vegetacion`.
- `5/6/7`: presets de merge.
- `q` o `ESC`: salir.

---

## Archivos utiles

- README completo: `README_colisiones_rpg.md`
- Ajustes avanzados: `ADVANCED_CONFIG.md`
- Atajos en formato rapido: `CHEATSHEET.txt`

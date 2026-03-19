# Quick Start (30 segundos) ⚡

## Instalación
```bash
pip install opencv-python numpy
```

## Uso básico

1. **Coloca tu imagen** en la carpeta del script como `fondo1.png`

2. **Ejecuta:**
```bash
python generar_colisiones.py
```

3. **En la ventana:**
   - Pulsa **1** → carga perfil "bosque"
   - Mueve sliders hasta que veas bien en la máscara (panel derecho)
   - Pulsa **A/T/V/O** para ver/ocultar tipos
   - Pulsa **s** → copia colisiones a JSON
   - Pulsa **q** → listo!

4. **Archivos generados:**
   - `mapa_con_colisiones_rpg_hibrido.jpg` ← preview
   - `datos_colisiones_rpg_hibrido.json` ← usa esto en tu motor

---

## Atajos clave

| Tecla | Qué hace |
|-------|----------|
| **1/2/3/4** | Cargar perfil (bosque/ciudad/costa/custom) |
| **g** | Guardar configuración actual |
| **s** | Exportar JSON + preview |
| **a/t/v** | Cambiar tipo HSV a editar (agua/tejado/vegetacion) |
| **A/T/V/O** | Toggle mostrar/ocultar tipos |
| **q** | Salir |

---

## Si la detección falla

**Muchos obstáculos no aparecen:**
- Sube Blur a 5-7
- Baja Canny Low a 20-35

**Mucho ruido:**
- Baja Blur a 3
- Sube Canny Low a 50+

**Objetos fragmentados:**
- Sube Kernel a 7-9

---

**Documentación completa:** Ver `README_colisiones_rpg.md`

**Configuraciones avanzadas:** Ver `ADVANCED_CONFIG.md`

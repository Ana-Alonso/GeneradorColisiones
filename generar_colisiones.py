import json
import os
from copy import deepcopy
import tkinter as tk
from tkinter import filedialog

import cv2
import numpy as np


WINDOW_NAME = "Colisiones RPG - Debug"
PROFILE_FILE = "perfiles_colisiones_rpg.json"
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".web"}
ALLOWED_SAVE_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Presets iniciales para modo híbrido. Ajusta estos rangos a tu paleta real.
HYBRID_HSV_RANGES = [
    {
        "type": "agua",
        "h_min": 80,
        "h_max": 130,
        "s_min": 40,
        "s_max": 255,
        "v_min": 20,
        "v_max": 255,
    },
    {
        "type": "tejado",
        "h_min": 0,
        "h_max": 25,
        "s_min": 50,
        "s_max": 255,
        "v_min": 40,
        "v_max": 255,
    },
    {
        "type": "vegetacion",
        "h_min": 35,
        "h_max": 90,
        "s_min": 35,
        "s_max": 255,
        "v_min": 20,
        "v_max": 255,
    },
]

DEFAULT_PROFILES = {
    "bosque": {
        "modo": 2,
        "blur": 3,
        "canny_low": 25,
        "canny_high": 95,
        "kernel": 5,
        "h_min": 0,
        "h_max": 179,
        "s_min": 0,
        "s_max": 255,
        "v_min": 0,
        "v_max": 255,
        "min_w": 18,
        "min_h": 18,
        "max_w_pct": 90,
        "max_h_pct": 90,
        "base_pct": 40,
        "margen_x_pct": 5,
        "hybrid_hsv_ranges": HYBRID_HSV_RANGES,
    },
    "ciudad": {
        "modo": 2,
        "blur": 5,
        "canny_low": 35,
        "canny_high": 120,
        "kernel": 7,
        "h_min": 0,
        "h_max": 179,
        "s_min": 0,
        "s_max": 255,
        "v_min": 0,
        "v_max": 255,
        "min_w": 24,
        "min_h": 24,
        "max_w_pct": 92,
        "max_h_pct": 92,
        "base_pct": 35,
        "margen_x_pct": 4,
        "hybrid_hsv_ranges": HYBRID_HSV_RANGES,
    },
    "costa": {
        "modo": 2,
        "blur": 3,
        "canny_low": 20,
        "canny_high": 80,
        "kernel": 5,
        "h_min": 80,
        "h_max": 130,
        "s_min": 40,
        "s_max": 255,
        "v_min": 20,
        "v_max": 255,
        "min_w": 20,
        "min_h": 20,
        "max_w_pct": 95,
        "max_h_pct": 95,
        "base_pct": 40,
        "margen_x_pct": 5,
        "hybrid_hsv_ranges": HYBRID_HSV_RANGES,
    },
}


def noop(_value):
    pass


def clamp(value, low, high):
    return max(low, min(high, int(value)))


def sanitize_profile(profile):
    p = deepcopy(profile)
    p["modo"] = clamp(p.get("modo", 2), 0, 2)
    p["blur"] = clamp(p.get("blur", 5), 1, 31)
    p["canny_low"] = clamp(p.get("canny_low", 35), 0, 255)
    p["canny_high"] = clamp(p.get("canny_high", 110), 1, 255)
    if p["canny_high"] <= p["canny_low"]:
        p["canny_high"] = min(255, p["canny_low"] + 1)
    p["kernel"] = clamp(p.get("kernel", 5), 1, 31)

    p["h_min"] = clamp(p.get("h_min", 0), 0, 179)
    p["h_max"] = clamp(p.get("h_max", 179), 0, 179)
    p["s_min"] = clamp(p.get("s_min", 0), 0, 255)
    p["s_max"] = clamp(p.get("s_max", 255), 0, 255)
    p["v_min"] = clamp(p.get("v_min", 0), 0, 255)
    p["v_max"] = clamp(p.get("v_max", 255), 0, 255)

    p["min_w"] = clamp(p.get("min_w", 24), 0, 500)
    p["min_h"] = clamp(p.get("min_h", 24), 0, 500)
    p["max_w_pct"] = clamp(p.get("max_w_pct", 90), 1, 100)
    p["max_h_pct"] = clamp(p.get("max_h_pct", 90), 1, 100)
    p["base_pct"] = clamp(p.get("base_pct", 40), 0, 100)
    p["margen_x_pct"] = clamp(p.get("margen_x_pct", 5), 0, 40)

    ranges = p.get("hybrid_hsv_ranges", HYBRID_HSV_RANGES)
    if not isinstance(ranges, list) or not ranges:
        ranges = deepcopy(HYBRID_HSV_RANGES)
    p["hybrid_hsv_ranges"] = []
    for r in ranges:
        p["hybrid_hsv_ranges"].append(
            {
                "type": str(r.get("type", "hsv")),
                "h_min": clamp(r.get("h_min", 0), 0, 179),
                "h_max": clamp(r.get("h_max", 179), 0, 179),
                "s_min": clamp(r.get("s_min", 0), 0, 255),
                "s_max": clamp(r.get("s_max", 255), 0, 255),
                "v_min": clamp(r.get("v_min", 0), 0, 255),
                "v_max": clamp(r.get("v_max", 255), 0, 255),
            }
        )

    return p


def find_hybrid_range(ranges, tipo):
    for r in ranges:
        if r.get("type") == tipo:
            return r
    return None


def ensure_hybrid_type(ranges, tipo):
    found = find_hybrid_range(ranges, tipo)
    if found is not None:
        return found

    default = find_hybrid_range(HYBRID_HSV_RANGES, tipo)
    if default is None:
        default = {
            "type": tipo,
            "h_min": 0,
            "h_max": 179,
            "s_min": 0,
            "s_max": 255,
            "v_min": 0,
            "v_max": 255,
        }
    else:
        default = deepcopy(default)

    ranges.append(default)
    return default


def set_hybrid_trackbars(tipo_range):
    cv2.setTrackbarPos("H2 min (tipo)", WINDOW_NAME, clamp(tipo_range["h_min"], 0, 179))
    cv2.setTrackbarPos("H2 max (tipo)", WINDOW_NAME, clamp(tipo_range["h_max"], 0, 179))
    cv2.setTrackbarPos("S2 min (tipo)", WINDOW_NAME, clamp(tipo_range["s_min"], 0, 255))
    cv2.setTrackbarPos("S2 max (tipo)", WINDOW_NAME, clamp(tipo_range["s_max"], 0, 255))
    cv2.setTrackbarPos("V2 min (tipo)", WINDOW_NAME, clamp(tipo_range["v_min"], 0, 255))
    cv2.setTrackbarPos("V2 max (tipo)", WINDOW_NAME, clamp(tipo_range["v_max"], 0, 255))


def read_hybrid_trackbars(tipo):
    return {
        "type": tipo,
        "h_min": cv2.getTrackbarPos("H2 min (tipo)", WINDOW_NAME),
        "h_max": cv2.getTrackbarPos("H2 max (tipo)", WINDOW_NAME),
        "s_min": cv2.getTrackbarPos("S2 min (tipo)", WINDOW_NAME),
        "s_max": cv2.getTrackbarPos("S2 max (tipo)", WINDOW_NAME),
        "v_min": cv2.getTrackbarPos("V2 min (tipo)", WINDOW_NAME),
        "v_max": cv2.getTrackbarPos("V2 max (tipo)", WINDOW_NAME),
    }


def cargar_perfiles(ruta_perfiles):
    perfiles = {k: sanitize_profile(v) for k, v in DEFAULT_PROFILES.items()}
    if not os.path.exists(ruta_perfiles):
        return perfiles

    try:
        with open(ruta_perfiles, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            for name, profile in data.items():
                if isinstance(profile, dict):
                    perfiles[name] = sanitize_profile(profile)
    except (OSError, json.JSONDecodeError):
        print("Aviso: no se pudieron leer perfiles guardados, se usarán defaults.")

    return perfiles


def guardar_perfiles(ruta_perfiles, perfiles):
    data = {name: sanitize_profile(profile) for name, profile in perfiles.items()}
    with open(ruta_perfiles, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def aplicar_perfil_trackbars(profile):
    p = sanitize_profile(profile)
    cv2.setTrackbarPos("Modo (0 Bordes, 1 HSV, 2 Hibrido)", WINDOW_NAME, p["modo"])
    cv2.setTrackbarPos("Blur (impar)", WINDOW_NAME, p["blur"])
    cv2.setTrackbarPos("Canny Low", WINDOW_NAME, p["canny_low"])
    cv2.setTrackbarPos("Canny High", WINDOW_NAME, p["canny_high"])
    cv2.setTrackbarPos("Kernel (impar)", WINDOW_NAME, p["kernel"])

    cv2.setTrackbarPos("H min", WINDOW_NAME, p["h_min"])
    cv2.setTrackbarPos("H max", WINDOW_NAME, p["h_max"])
    cv2.setTrackbarPos("S min", WINDOW_NAME, p["s_min"])
    cv2.setTrackbarPos("S max", WINDOW_NAME, p["s_max"])
    cv2.setTrackbarPos("V min", WINDOW_NAME, p["v_min"])
    cv2.setTrackbarPos("V max", WINDOW_NAME, p["v_max"])

    cv2.setTrackbarPos("Min W", WINDOW_NAME, p["min_w"])
    cv2.setTrackbarPos("Min H", WINDOW_NAME, p["min_h"])
    cv2.setTrackbarPos("Max W %", WINDOW_NAME, p["max_w_pct"])
    cv2.setTrackbarPos("Max H %", WINDOW_NAME, p["max_h_pct"])
    cv2.setTrackbarPos("Base %", WINDOW_NAME, p["base_pct"])
    cv2.setTrackbarPos("Margen X %", WINDOW_NAME, p["margen_x_pct"])


def perfil_desde_parametros(p, hybrid_hsv_ranges):
    return {
        "modo": p["modo"],
        "blur": p["blur"],
        "canny_low": p["canny_low"],
        "canny_high": p["canny_high"],
        "kernel": p["kernel"],
        "h_min": p["h_min"],
        "h_max": p["h_max"],
        "s_min": p["s_min"],
        "s_max": p["s_max"],
        "v_min": p["v_min"],
        "v_max": p["v_max"],
        "min_w": p["min_w"],
        "min_h": p["min_h"],
        "max_w_pct": p["max_w_pct"],
        "max_h_pct": p["max_h_pct"],
        "base_pct": int(round(p["base_ratio"] * 100)),
        "margen_x_pct": int(round(p["x_margin_ratio"] * 100)),
        "hybrid_hsv_ranges": deepcopy(hybrid_hsv_ranges),
    }


def odd_from_slider(value):
    """Convierte valor de trackbar en impar >= 1."""
    value = max(1, int(value))
    if value % 2 == 0:
        value += 1
    return value


def build_mask_edges(img, blur_size, canny_low, canny_high, kernel_size):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (blur_size, blur_size), 0)
    edges = cv2.Canny(blurred, canny_low, canny_high)

    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    return edges, closed


def build_mask_hsv(img, h_min, h_max, s_min, s_max, v_min, v_max, kernel_size):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower = np.array([h_min, s_min, v_min], dtype=np.uint8)
    upper = np.array([h_max, s_max, v_max], dtype=np.uint8)

    if h_min <= h_max:
        mask = cv2.inRange(hsv, lower, upper)
    else:
        # Permite wrap de H para seleccionar rojos y otros rangos que cruzan 179->0.
        lower_1 = np.array([0, s_min, v_min], dtype=np.uint8)
        upper_1 = np.array([h_max, s_max, v_max], dtype=np.uint8)
        lower_2 = np.array([h_min, s_min, v_min], dtype=np.uint8)
        upper_2 = np.array([179, s_max, v_max], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_1, upper_1) | cv2.inRange(hsv, lower_2, upper_2)

    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    cleaned = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)
    return mask, cleaned


def rect_iou(a, b):
    ax1, ay1 = a["x"], a["y"]
    ax2, ay2 = ax1 + a["width"], ay1 + a["height"]
    bx1, by1 = b["x"], b["y"]
    bx2, by2 = bx1 + b["width"], by1 + b["height"]

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h
    if inter_area == 0:
        return 0.0

    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    union = area_a + area_b - inter_area
    if union <= 0:
        return 0.0
    return inter_area / union


def deduplicar_colisiones(colisiones, iou_threshold=0.55):
    if not colisiones:
        return []

    ordenadas = sorted(colisiones, key=lambda c: c["width"] * c["height"], reverse=True)
    resultado = []

    for c in ordenadas:
        if all(rect_iou(c, kept) < iou_threshold for kept in resultado):
            resultado.append(c)

    return sorted(resultado, key=lambda c: (c["y"], c["x"]))


def extraer_cajas(
    mask,
    img_shape,
    min_w,
    min_h,
    max_w_pct,
    max_h_pct,
    base_ratio,
    x_margin_ratio,
    obstacle_type="solido",
):
    alto_img, ancho_img = img_shape[:2]

    max_w = int(ancho_img * (max_w_pct / 100.0))
    max_h = int(alto_img * (max_h_pct / 100.0))

    contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cajas_visuales = []
    colisiones = []

    for c in contornos:
        x, y, w, h = cv2.boundingRect(c)

        if w < min_w or h < min_h:
            continue
        if w > max_w or h > max_h:
            continue

        h_colision = max(1, int(h * base_ratio))
        y_colision = y + (h - h_colision)

        margen_x = int(w * x_margin_ratio)
        x_colision = x + margen_x
        w_colision = max(1, w - (margen_x * 2))

        cajas_visuales.append((x, y, w, h))
        colisiones.append(
            {
                "x": int(x_colision),
                "y": int(y_colision),
                "width": int(w_colision),
                "height": int(h_colision),
                "type": obstacle_type,
            }
        )

    return cajas_visuales, colisiones


def dibujar_resultado(img, cajas_visuales, colisiones):
    out = img.copy()
    for x, y, w, h in cajas_visuales:
        cv2.rectangle(out, (x, y), (x + w, y + h), (255, 0, 0), 1)

    color_por_tipo = {
        "solido": (0, 0, 255),
        "agua": (255, 255, 0),
        "tejado": (0, 165, 255),
        "vegetacion": (0, 255, 0),
    }

    for col in colisiones:
        x, y, w, h = col["x"], col["y"], col["width"], col["height"]
        tipo = col.get("type", "solido")
        color = color_por_tipo.get(tipo, (0, 0, 255))
        cv2.rectangle(out, (x, y), (x + w, y + h), color, 2)

    return out


def guardar_salida(output_img, colisiones, prefijo="rpg", imagen_salida=None, json_salida=None):
    if not imagen_salida:
        imagen_salida = f"mapa_con_colisiones_{prefijo}.jpg"
    if not json_salida:
        json_salida = f"datos_colisiones_{prefijo}.json"

    cv2.imwrite(imagen_salida, output_img)
    por_tipo = {}
    for col in colisiones:
        tipo = col.get("type", "solido")
        por_tipo.setdefault(tipo, []).append(col)

    with open(json_salida, "w", encoding="utf-8") as f:
        json.dump(
            {
                "colisiones": colisiones,
                "por_tipo": por_tipo,
            },
            f,
            indent=4,
            ensure_ascii=False,
        )

    print(f"Guardado: {imagen_salida}")
    print(f"Guardado: {json_salida}")
    print(f"Total colisiones: {len(colisiones)}")


def seleccionar_rutas_guardado(ruta_imagen, prefijo="rpg"):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    base_dir = os.path.dirname(os.path.abspath(ruta_imagen))
    base_name = os.path.splitext(os.path.basename(ruta_imagen))[0]

    imagen_salida = filedialog.asksaveasfilename(
        title="Guardar mapa con colisiones",
        initialdir=base_dir,
        initialfile=f"{base_name}_colisiones_{prefijo}.png",
        defaultextension=".png",
        filetypes=[
            ("Imagen PNG", "*.png"),
            ("Imagen JPG", "*.jpg;*.jpeg"),
            ("Imagen WEBP", "*.webp"),
        ],
    )

    if not imagen_salida:
        root.destroy()
        print("Guardado cancelado: no se selecciono ruta para la imagen.")
        return None, None

    ext = os.path.splitext(imagen_salida)[1].lower()
    if ext not in ALLOWED_SAVE_IMAGE_EXTENSIONS:
        root.destroy()
        print("Formato de salida de imagen no valido. Usa: jpg, jpeg, png o webp.")
        return None, None

    json_salida = filedialog.asksaveasfilename(
        title="Guardar datos de colisiones JSON",
        initialdir=os.path.dirname(imagen_salida),
        initialfile=f"{base_name}_colisiones_{prefijo}.json",
        defaultextension=".json",
        filetypes=[("Archivo JSON", "*.json")],
    )

    root.destroy()

    if not json_salida:
        print("Guardado cancelado: no se selecciono ruta para el JSON.")
        return None, None

    return imagen_salida, json_salida


def crear_trackbars():
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    # Modo: 0 = Canny + morph, 1 = HSV + morph, 2 = híbrido automático
    cv2.createTrackbar("Modo (0 Bordes, 1 HSV, 2 Hibrido)", WINDOW_NAME, 0, 2, noop)

    # Bordes
    cv2.createTrackbar("Blur (impar)", WINDOW_NAME, 5, 31, noop)
    cv2.createTrackbar("Canny Low", WINDOW_NAME, 35, 255, noop)
    cv2.createTrackbar("Canny High", WINDOW_NAME, 110, 255, noop)
    cv2.createTrackbar("Kernel (impar)", WINDOW_NAME, 5, 31, noop)

    # HSV
    cv2.createTrackbar("H min", WINDOW_NAME, 0, 179, noop)
    cv2.createTrackbar("H max", WINDOW_NAME, 179, 179, noop)
    cv2.createTrackbar("S min", WINDOW_NAME, 0, 255, noop)
    cv2.createTrackbar("S max", WINDOW_NAME, 255, 255, noop)
    cv2.createTrackbar("V min", WINDOW_NAME, 0, 255, noop)
    cv2.createTrackbar("V max", WINDOW_NAME, 255, 255, noop)

    # HSV por tipo para modo híbrido (edición en caliente)
    cv2.createTrackbar("H2 min (tipo)", WINDOW_NAME, 0, 179, noop)
    cv2.createTrackbar("H2 max (tipo)", WINDOW_NAME, 179, 179, noop)
    cv2.createTrackbar("S2 min (tipo)", WINDOW_NAME, 0, 255, noop)
    cv2.createTrackbar("S2 max (tipo)", WINDOW_NAME, 255, 255, noop)
    cv2.createTrackbar("V2 min (tipo)", WINDOW_NAME, 0, 255, noop)
    cv2.createTrackbar("V2 max (tipo)", WINDOW_NAME, 255, 255, noop)

    # Filtros de cajas
    cv2.createTrackbar("Min W", WINDOW_NAME, 24, 500, noop)
    cv2.createTrackbar("Min H", WINDOW_NAME, 24, 500, noop)
    cv2.createTrackbar("Max W %", WINDOW_NAME, 90, 100, noop)
    cv2.createTrackbar("Max H %", WINDOW_NAME, 90, 100, noop)
    cv2.createTrackbar("Base %", WINDOW_NAME, 40, 100, noop)
    cv2.createTrackbar("Margen X %", WINDOW_NAME, 5, 40, noop)


def leer_parametros():
    modo = cv2.getTrackbarPos("Modo (0 Bordes, 1 HSV, 2 Hibrido)", WINDOW_NAME)

    blur = odd_from_slider(cv2.getTrackbarPos("Blur (impar)", WINDOW_NAME))
    canny_low = cv2.getTrackbarPos("Canny Low", WINDOW_NAME)
    canny_high = cv2.getTrackbarPos("Canny High", WINDOW_NAME)
    if canny_high <= canny_low:
        canny_high = min(255, canny_low + 1)

    kernel = odd_from_slider(cv2.getTrackbarPos("Kernel (impar)", WINDOW_NAME))

    h_min = cv2.getTrackbarPos("H min", WINDOW_NAME)
    h_max = cv2.getTrackbarPos("H max", WINDOW_NAME)
    s_min = cv2.getTrackbarPos("S min", WINDOW_NAME)
    s_max = cv2.getTrackbarPos("S max", WINDOW_NAME)
    v_min = cv2.getTrackbarPos("V min", WINDOW_NAME)
    v_max = cv2.getTrackbarPos("V max", WINDOW_NAME)

    min_w = cv2.getTrackbarPos("Min W", WINDOW_NAME)
    min_h = cv2.getTrackbarPos("Min H", WINDOW_NAME)
    max_w_pct = max(1, cv2.getTrackbarPos("Max W %", WINDOW_NAME))
    max_h_pct = max(1, cv2.getTrackbarPos("Max H %", WINDOW_NAME))
    base_ratio = cv2.getTrackbarPos("Base %", WINDOW_NAME) / 100.0
    x_margin_ratio = cv2.getTrackbarPos("Margen X %", WINDOW_NAME) / 100.0

    return {
        "modo": modo,
        "blur": blur,
        "canny_low": canny_low,
        "canny_high": canny_high,
        "kernel": kernel,
        "h_min": h_min,
        "h_max": h_max,
        "s_min": s_min,
        "s_max": s_max,
        "v_min": v_min,
        "v_max": v_max,
        "min_w": min_w,
        "min_h": min_h,
        "max_w_pct": max_w_pct,
        "max_h_pct": max_h_pct,
        "base_ratio": base_ratio,
        "x_margin_ratio": x_margin_ratio,
    }


def extraer_colisiones_rpg_interactivo(ruta_imagen):
    img = cv2.imread(ruta_imagen)
    if img is None:
        print(f"Error: No se pudo cargar la imagen '{ruta_imagen}'")
        return

    crear_trackbars()

    base_dir = os.path.dirname(os.path.abspath(ruta_imagen))
    ruta_perfiles = os.path.join(base_dir, PROFILE_FILE)
    perfiles = cargar_perfiles(ruta_perfiles)
    profile_keys = ["bosque", "ciudad", "costa", "custom"]
    perfil_activo = "bosque"
    hybrid_hsv_ranges = deepcopy(HYBRID_HSV_RANGES)
    tipos_hibridos = ["agua", "tejado", "vegetacion"]
    tipo_hibrido_activo = "agua"

    img_h, img_w = img.shape[:2]
    button_rect = (max(10, img_w - 190), 10, max(160, img_w - 20), 48)

    ui_state = {
        "drawing": False,
        "start": (0, 0),
        "current": (0, 0),
        "manual_type": "solido",
        "manual_rects": [],
        "save_requested": False,
    }

    color_por_tipo = {
        "solido": (0, 0, 255),
        "agua": (255, 255, 0),
        "tejado": (0, 165, 255),
        "vegetacion": (0, 255, 0),
    }

    def clamp_point(x, y):
        return max(0, min(img_w - 1, x)), max(0, min(img_h - 1, y))

    def on_mouse(event, x, y, _flags, _param):
        if x >= img_w or y >= img_h:
            return

        bx1, by1, bx2, by2 = button_rect

        if event == cv2.EVENT_LBUTTONDOWN:
            if bx1 <= x <= bx2 and by1 <= y <= by2:
                ui_state["save_requested"] = True
                return

            ui_state["drawing"] = True
            ui_state["start"] = clamp_point(x, y)
            ui_state["current"] = clamp_point(x, y)

        elif event == cv2.EVENT_MOUSEMOVE and ui_state["drawing"]:
            ui_state["current"] = clamp_point(x, y)

        elif event == cv2.EVENT_LBUTTONUP and ui_state["drawing"]:
            ui_state["current"] = clamp_point(x, y)
            x1 = min(ui_state["start"][0], ui_state["current"][0])
            y1 = min(ui_state["start"][1], ui_state["current"][1])
            x2 = max(ui_state["start"][0], ui_state["current"][0])
            y2 = max(ui_state["start"][1], ui_state["current"][1])

            w = x2 - x1
            h = y2 - y1

            if w >= 5 and h >= 5:
                ui_state["manual_rects"].append(
                    {
                        "x": int(x1),
                        "y": int(y1),
                        "width": int(w),
                        "height": int(h),
                        "type": ui_state["manual_type"],
                        "source": "manual",
                    }
                )

            ui_state["drawing"] = False

    cv2.setMouseCallback(WINDOW_NAME, on_mouse)
    
    # Toggles de visibilidad por tipo
    tipos_visibles = {
        "solido": True,
        "agua": True,
        "tejado": True,
        "vegetacion": True,
    }

    if perfil_activo in perfiles:
        aplicar_perfil_trackbars(perfiles[perfil_activo])
        hybrid_hsv_ranges = deepcopy(perfiles[perfil_activo].get("hybrid_hsv_ranges", HYBRID_HSV_RANGES))

    set_hybrid_trackbars(ensure_hybrid_type(hybrid_hsv_ranges, tipo_hibrido_activo))

    print("Controles:")
    print("- Ajusta sliders en tiempo real")
    print("- Clic izquierdo y arrastrar en imagen para crear rectangulo manual")
    print("- Tipos manuales: a=agua, t=tejado, v=vegetacion, o=solido")
    print("- Boton GUARDAR (en la imagen) o tecla 's' para elegir donde guardar")
    print("- Tecla 'g' para guardar perfil actual como 'custom'")
    print("- Teclas 1/2/3/4 para cargar perfil bosque/ciudad/costa/custom")
    print("- Tecla 'a' selecciona tipo agua, 't' tipo tejado, 'v' tipo vegetacion")
    print("- Tecla 'u' aplica sliders H2/S2/V2 al tipo seleccionado")
    print("- Mayúsculas A/T/V/O togglean visibilidad agua/tejado/vegetacion/solidos")
    print("- Tecla 'z' deshace ultimo rectangulo manual, 'c' limpia todos")
    print("- Tecla 'q' o ESC para salir")
    print("  Modo 2 híbrido = HSV (agua/tejado) + bordes (sólidos)")

    ultima_preview = None
    ultimas_colisiones = []
    ultimo_modo = "bordes"

    while True:
        p = leer_parametros()

        # Sincroniza en vivo los sliders H2/S2/V2 con el tipo activo del modo híbrido.
        rango_actualizado = read_hybrid_trackbars(tipo_hibrido_activo)
        slot = ensure_hybrid_type(hybrid_hsv_ranges, tipo_hibrido_activo)
        slot.update(rango_actualizado)

        if p["modo"] == 0:
            _, mask = build_mask_edges(
                img,
                p["blur"],
                p["canny_low"],
                p["canny_high"],
                p["kernel"],
            )
            ultimo_modo = "bordes"

            cajas_visuales, colisiones = extraer_cajas(
                mask,
                img.shape,
                p["min_w"],
                p["min_h"],
                p["max_w_pct"],
                p["max_h_pct"],
                p["base_ratio"],
                p["x_margin_ratio"],
                obstacle_type="solido",
            )
        elif p["modo"] == 1:
            _, mask = build_mask_hsv(
                img,
                p["h_min"],
                p["h_max"],
                p["s_min"],
                p["s_max"],
                p["v_min"],
                p["v_max"],
                p["kernel"],
            )
            ultimo_modo = "hsv"

            cajas_visuales, colisiones = extraer_cajas(
                mask,
                img.shape,
                p["min_w"],
                p["min_h"],
                p["max_w_pct"],
                p["max_h_pct"],
                p["base_ratio"],
                p["x_margin_ratio"],
                obstacle_type="hsv_objeto",
            )
        else:
            ultimo_modo = "hibrido"

            _, mask_edges = build_mask_edges(
                img,
                p["blur"],
                p["canny_low"],
                p["canny_high"],
                p["kernel"],
            )

            cajas_visuales, colisiones = extraer_cajas(
                mask_edges,
                img.shape,
                p["min_w"],
                p["min_h"],
                p["max_w_pct"],
                p["max_h_pct"],
                p["base_ratio"],
                p["x_margin_ratio"],
                obstacle_type="solido",
            )

            mask_hsv_total = np.zeros(mask_edges.shape, dtype=np.uint8)

            for rango in hybrid_hsv_ranges:
                _, mask_tipo = build_mask_hsv(
                    img,
                    rango["h_min"],
                    rango["h_max"],
                    rango["s_min"],
                    rango["s_max"],
                    rango["v_min"],
                    rango["v_max"],
                    p["kernel"],
                )
                mask_hsv_total = cv2.bitwise_or(mask_hsv_total, mask_tipo)

                cajas_tipo, cols_tipo = extraer_cajas(
                    mask_tipo,
                    img.shape,
                    p["min_w"],
                    p["min_h"],
                    p["max_w_pct"],
                    p["max_h_pct"],
                    p["base_ratio"],
                    p["x_margin_ratio"],
                    obstacle_type=rango["type"],
                )
                cajas_visuales.extend(cajas_tipo)
                colisiones.extend(cols_tipo)

            colisiones = deduplicar_colisiones(colisiones, iou_threshold=0.55)
            mask = cv2.bitwise_or(mask_edges, mask_hsv_total)

        manual_rects = list(ui_state["manual_rects"])
        manual_cajas = [(m["x"], m["y"], m["width"], m["height"]) for m in manual_rects]

        colisiones_total = list(colisiones) + manual_rects
        cajas_visuales_total = list(cajas_visuales) + manual_cajas

        # Filtrar colisiones por visibilidad de tipos
        colisiones_visibles = [c for c in colisiones_total if tipos_visibles.get(c.get("type", "solido"), True)]
        cajas_visuales_visibles = [
            cajas_visuales_total[i]
            for i, c in enumerate(colisiones_total)
            if tipos_visibles.get(c.get("type", "solido"), True)
        ]
        
        preview = dibujar_resultado(img, cajas_visuales_visibles, colisiones_visibles)

        # Dibuja rectangulo temporal mientras se arrastra con el mouse.
        if ui_state["drawing"]:
            x1 = min(ui_state["start"][0], ui_state["current"][0])
            y1 = min(ui_state["start"][1], ui_state["current"][1])
            x2 = max(ui_state["start"][0], ui_state["current"][0])
            y2 = max(ui_state["start"][1], ui_state["current"][1])
            color_tmp = color_por_tipo.get(ui_state["manual_type"], (255, 255, 255))
            cv2.rectangle(preview, (x1, y1), (x2, y2), color_tmp, 2)
            cv2.putText(
                preview,
                f"Manual: {ui_state['manual_type']}",
                (x1, max(15, y1 - 6)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color_tmp,
                1,
                cv2.LINE_AA,
            )

        # Boton de guardado clicable.
        bx1, by1, bx2, by2 = button_rect
        cv2.rectangle(preview, (bx1, by1), (bx2, by2), (40, 120, 40), -1)
        cv2.rectangle(preview, (bx1, by1), (bx2, by2), (230, 230, 230), 1)
        cv2.putText(
            preview,
            "GUARDAR",
            (bx1 + 24, by1 + 26),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        vista = np.hstack((preview, mask_bgr))
        cv2.putText(
            vista,
            f"Modo: {ultimo_modo} | Perfil: {perfil_activo} | Colisiones: {len(colisiones_visibles)} | Manuales: {len(manual_rects)}",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            vista,
            f"Tipo HSV activo: {tipo_hibrido_activo} | Tipo manual: {ui_state['manual_type']} (a/t/v/o)",
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )
        
        estado_visibles = " | ".join([f"{t}:{('ON' if tipos_visibles[t] else 'OFF')}" for t in ["solido", "agua", "tejado", "vegetacion"]])
        cv2.putText(
            vista,
            f"Visibilidad: {estado_visibles} (A/T/V/O toggle)",
            (10, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1,
            cv2.LINE_AA,
        )
        cv2.imshow(WINDOW_NAME, vista)

        ultima_preview = preview
        ultimas_colisiones = colisiones_total

        key = cv2.waitKey(30) & 0xFF
        if key == ord("s") or ui_state["save_requested"]:
            prefijo = f"rpg_{ultimo_modo}"
            img_path, json_path = seleccionar_rutas_guardado(ruta_imagen, prefijo=prefijo)
            if img_path and json_path:
                guardar_salida(
                    ultima_preview,
                    ultimas_colisiones,
                    prefijo=prefijo,
                    imagen_salida=img_path,
                    json_salida=json_path,
                )
            ui_state["save_requested"] = False
        elif key == ord("A"):
            tipos_visibles["agua"] = not tipos_visibles["agua"]
            print(f"Agua: {'ON' if tipos_visibles['agua'] else 'OFF'}")
        elif key == ord("T"):
            tipos_visibles["tejado"] = not tipos_visibles["tejado"]
            print(f"Tejado: {'ON' if tipos_visibles['tejado'] else 'OFF'}")
        elif key == ord("V"):
            tipos_visibles["vegetacion"] = not tipos_visibles["vegetacion"]
            print(f"Vegetacion: {'ON' if tipos_visibles['vegetacion'] else 'OFF'}")
        elif key == ord("O"):
            tipos_visibles["solido"] = not tipos_visibles["solido"]
            print(f"Solido: {'ON' if tipos_visibles['solido'] else 'OFF'}")
        elif key == ord("g"):
            perfil_custom = perfil_desde_parametros(p, hybrid_hsv_ranges)
            perfiles["custom"] = sanitize_profile(perfil_custom)
            guardar_perfiles(ruta_perfiles, perfiles)
            perfil_activo = "custom"
            print(f"Perfil guardado en: {ruta_perfiles} (custom)")
        elif key == ord("a"):
            tipo_hibrido_activo = "agua"
            ui_state["manual_type"] = "agua"
            set_hybrid_trackbars(ensure_hybrid_type(hybrid_hsv_ranges, tipo_hibrido_activo))
            print("Tipo híbrido activo: agua")
        elif key == ord("t"):
            tipo_hibrido_activo = "tejado"
            ui_state["manual_type"] = "tejado"
            set_hybrid_trackbars(ensure_hybrid_type(hybrid_hsv_ranges, tipo_hibrido_activo))
            print("Tipo híbrido activo: tejado")
        elif key == ord("v"):
            tipo_hibrido_activo = "vegetacion"
            ui_state["manual_type"] = "vegetacion"
            set_hybrid_trackbars(ensure_hybrid_type(hybrid_hsv_ranges, tipo_hibrido_activo))
            print("Tipo híbrido activo: vegetacion")
        elif key == ord("o"):
            ui_state["manual_type"] = "solido"
            print("Tipo manual activo: solido")
        elif key == ord("u"):
            slot = ensure_hybrid_type(hybrid_hsv_ranges, tipo_hibrido_activo)
            slot.update(read_hybrid_trackbars(tipo_hibrido_activo))
            print(f"Rango actualizado para tipo: {tipo_hibrido_activo}")
        elif key == ord("z"):
            if ui_state["manual_rects"]:
                ui_state["manual_rects"].pop()
                print("Se deshizo el ultimo rectangulo manual.")
        elif key == ord("c"):
            ui_state["manual_rects"].clear()
            print("Se limpiaron todos los rectangulos manuales.")
        elif key in (ord("1"), ord("2"), ord("3"), ord("4")):
            idx = int(chr(key)) - 1
            if 0 <= idx < len(profile_keys):
                target = profile_keys[idx]
                if target in perfiles:
                    aplicar_perfil_trackbars(perfiles[target])
                    hybrid_hsv_ranges = deepcopy(perfiles[target].get("hybrid_hsv_ranges", HYBRID_HSV_RANGES))
                    if tipo_hibrido_activo not in tipos_hibridos:
                        tipo_hibrido_activo = "agua"
                    set_hybrid_trackbars(ensure_hybrid_type(hybrid_hsv_ranges, tipo_hibrido_activo))
                    perfil_activo = target
                    print(f"Perfil cargado: {target}")
                else:
                    print(f"Perfil no encontrado: {target}")
        elif key == ord("q") or key == 27:
            break

    cv2.destroyAllWindows()


def seleccionar_imagen():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    ruta_imagen = filedialog.askopenfilename(
        title="Selecciona una imagen para procesar",
        filetypes=[
            ("Imagenes", "*.jpg *.jpeg *.png *.webp *.web"),
            ("Todos los archivos", "*.*"),
        ],
    )

    root.destroy()

    if not ruta_imagen:
        print("No se seleccionó ninguna imagen.")
        return None

    ext = os.path.splitext(ruta_imagen)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        print(
            "Formato no permitido. Usa una imagen con extension: "
            "jpg, jpeg, png, webp o web."
        )
        return None

    return ruta_imagen


if __name__ == "__main__":
    ruta_imagen = seleccionar_imagen()
    if ruta_imagen:
        extraer_colisiones_rpg_interactivo(ruta_imagen)
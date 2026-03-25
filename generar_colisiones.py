import copy
import json
import os
import tkinter as tk
from dataclasses import dataclass
from tkinter import filedialog
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np


WINDOW_MAIN = "Extractor Universal - Mapa"
WINDOW_MASK = "Extractor Universal - Mascara"
WINDOW_CTRL = "Extractor Universal - Controles"
PROFILES_FILE = os.path.join(os.path.dirname(__file__), "perfiles_colisiones_rpg.json")


TYPE_SOLIDO = "solido"
TYPE_AGUA = "agua"
TYPE_TEJADO = "tejado"
TYPE_VEGETACION = "vegetacion"
COLLISION_TYPES = [TYPE_SOLIDO, TYPE_AGUA, TYPE_TEJADO, TYPE_VEGETACION]

MODE_BORDES = 0
MODE_HSV = 1
MODE_HIBRIDO = 2


@dataclass
class Rect:
    x: int
    y: int
    w: int
    h: int
    tipo: str
    fuente: str = "manual"

    def clamp_positive(self) -> None:
        self.w = max(1, int(self.w))
        self.h = max(1, int(self.h))

    def to_dict(self) -> Dict[str, int]:
        return {
            "x": int(self.x),
            "y": int(self.y),
            "w": int(self.w),
            "h": int(self.h),
            "tipo": self.tipo,
            "fuente": self.fuente,
        }


def odd_value(value: int, minimum: int = 1) -> int:
    value = max(minimum, int(value))
    if value % 2 == 0:
        value += 1
    return value


def rect_intersection_area(a: Rect, b: Rect) -> int:
    x1 = max(a.x, b.x)
    y1 = max(a.y, b.y)
    x2 = min(a.x + a.w, b.x + b.w)
    y2 = min(a.y + a.h, b.y + b.h)
    if x2 <= x1 or y2 <= y1:
        return 0
    return (x2 - x1) * (y2 - y1)


def rect_iou(a: Rect, b: Rect) -> float:
    inter = rect_intersection_area(a, b)
    if inter <= 0:
        return 0.0
    area_a = a.w * a.h
    area_b = b.w * b.h
    union = area_a + area_b - inter
    if union <= 0:
        return 0.0
    return float(inter) / float(union)


def merge_two_rects(a: Rect, b: Rect) -> Rect:
    x1 = min(a.x, b.x)
    y1 = min(a.y, b.y)
    x2 = max(a.x + a.w, b.x + b.w)
    y2 = max(a.y + a.h, b.y + b.h)
    return Rect(x1, y1, x2 - x1, y2 - y1, a.tipo, "manual")


def ensure_profiles_file() -> Dict[str, Dict[str, int]]:
    defaults = {
        "Bosque": {
            "mode": MODE_HIBRIDO,
            "blur": 5,
            "canny_low": 40,
            "canny_high": 130,
            "kernel": 5,
            "h_min": 20,
            "s_min": 50,
            "v_min": 40,
            "h_max": 95,
            "s_max": 255,
            "v_max": 255,
            "h2_min": 35,
            "s2_min": 40,
            "v2_min": 20,
            "h2_max": 130,
            "s2_max": 255,
            "v2_max": 255,
            "min_w": 6,
            "min_h": 6,
            "max_w_pct": 90,
            "max_h_pct": 90,
            "base_pct": 35,
            "margin_x_pct": 8,
        },
        "Ciudad": {
            "mode": MODE_BORDES,
            "blur": 3,
            "canny_low": 60,
            "canny_high": 180,
            "kernel": 3,
            "h_min": 0,
            "s_min": 0,
            "v_min": 0,
            "h_max": 179,
            "s_max": 255,
            "v_max": 255,
            "h2_min": 0,
            "s2_min": 0,
            "v2_min": 0,
            "h2_max": 179,
            "s2_max": 255,
            "v2_max": 255,
            "min_w": 8,
            "min_h": 8,
            "max_w_pct": 85,
            "max_h_pct": 85,
            "base_pct": 40,
            "margin_x_pct": 10,
        },
        "Costa": {
            "mode": MODE_HIBRIDO,
            "blur": 5,
            "canny_low": 35,
            "canny_high": 120,
            "kernel": 5,
            "h_min": 85,
            "s_min": 30,
            "v_min": 40,
            "h_max": 130,
            "s_max": 255,
            "v_max": 255,
            "h2_min": 15,
            "s2_min": 20,
            "v2_min": 40,
            "h2_max": 60,
            "s2_max": 255,
            "v2_max": 255,
            "min_w": 6,
            "min_h": 6,
            "max_w_pct": 90,
            "max_h_pct": 90,
            "base_pct": 30,
            "margin_x_pct": 6,
        },
        "Custom": {
            "mode": MODE_HIBRIDO,
            "blur": 3,
            "canny_low": 50,
            "canny_high": 150,
            "kernel": 3,
            "h_min": 0,
            "s_min": 0,
            "v_min": 0,
            "h_max": 179,
            "s_max": 255,
            "v_max": 255,
            "h2_min": 0,
            "s2_min": 0,
            "v2_min": 0,
            "h2_max": 179,
            "s2_max": 255,
            "v2_max": 255,
            "min_w": 4,
            "min_h": 4,
            "max_w_pct": 100,
            "max_h_pct": 100,
            "base_pct": 40,
            "margin_x_pct": 0,
        },
    }

    if not os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, "w", encoding="utf-8") as f:
            json.dump(defaults, f, indent=2, ensure_ascii=False)
        return defaults

    try:
        with open(PROFILES_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        for name, values in defaults.items():
            if name not in loaded:
                loaded[name] = values
            else:
                for k, v in values.items():
                    loaded[name].setdefault(k, v)
        return loaded
    except Exception:
        with open(PROFILES_FILE, "w", encoding="utf-8") as f:
            json.dump(defaults, f, indent=2, ensure_ascii=False)
        return defaults


def save_profiles(profiles: Dict[str, Dict[str, int]]) -> None:
    with open(PROFILES_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)


class CollisionExtractorApp:
    def __init__(self, image: np.ndarray):
        self.image_original = image
        self.image_h, self.image_w = image.shape[:2]

        self.current_type = TYPE_SOLIDO
        self.manual_rects: List[Rect] = []
        self.auto_rects: List[Rect] = []
        self.selected_idx = -1
        self.undo_stack: List[List[Rect]] = []

        self.drag_start: Optional[Tuple[int, int]] = None
        self.drag_mode: Optional[str] = None
        self.temp_rect: Optional[Rect] = None
        self.resize_origin: Optional[Tuple[int, int, int, int]] = None

        self.profiles = ensure_profiles_file()

        cv2.namedWindow(WINDOW_MAIN, cv2.WINDOW_NORMAL)
        cv2.namedWindow(WINDOW_MASK, cv2.WINDOW_NORMAL)
        cv2.namedWindow(WINDOW_CTRL, cv2.WINDOW_NORMAL)

        cv2.setMouseCallback(WINDOW_MAIN, self.on_mouse)

        self._create_trackbars()
        self._apply_profile("Custom")

    def _create_trackbars(self) -> None:
        cv2.createTrackbar("Modo 0B-1H-2X", WINDOW_CTRL, MODE_HIBRIDO, 2, lambda _v: None)
        cv2.createTrackbar("Blur", WINDOW_CTRL, 3, 31, lambda _v: None)
        cv2.createTrackbar("Canny Low", WINDOW_CTRL, 50, 255, lambda _v: None)
        cv2.createTrackbar("Canny High", WINDOW_CTRL, 150, 255, lambda _v: None)
        cv2.createTrackbar("Kernel", WINDOW_CTRL, 3, 31, lambda _v: None)

        cv2.createTrackbar("H min", WINDOW_CTRL, 0, 179, lambda _v: None)
        cv2.createTrackbar("S min", WINDOW_CTRL, 0, 255, lambda _v: None)
        cv2.createTrackbar("V min", WINDOW_CTRL, 0, 255, lambda _v: None)
        cv2.createTrackbar("H max", WINDOW_CTRL, 179, 179, lambda _v: None)
        cv2.createTrackbar("S max", WINDOW_CTRL, 255, 255, lambda _v: None)
        cv2.createTrackbar("V max", WINDOW_CTRL, 255, 255, lambda _v: None)

        cv2.createTrackbar("H2 min", WINDOW_CTRL, 0, 179, lambda _v: None)
        cv2.createTrackbar("S2 min", WINDOW_CTRL, 0, 255, lambda _v: None)
        cv2.createTrackbar("V2 min", WINDOW_CTRL, 0, 255, lambda _v: None)
        cv2.createTrackbar("H2 max", WINDOW_CTRL, 179, 179, lambda _v: None)
        cv2.createTrackbar("S2 max", WINDOW_CTRL, 255, 255, lambda _v: None)
        cv2.createTrackbar("V2 max", WINDOW_CTRL, 255, 255, lambda _v: None)

        cv2.createTrackbar("Min W", WINDOW_CTRL, 4, 1024, lambda _v: None)
        cv2.createTrackbar("Min H", WINDOW_CTRL, 4, 1024, lambda _v: None)
        cv2.createTrackbar("Max W %", WINDOW_CTRL, 100, 100, lambda _v: None)
        cv2.createTrackbar("Max H %", WINDOW_CTRL, 100, 100, lambda _v: None)
        cv2.createTrackbar("Base %", WINDOW_CTRL, 40, 100, lambda _v: None)
        cv2.createTrackbar("Margen X %", WINDOW_CTRL, 0, 49, lambda _v: None)

    def _set_slider(self, name: str, value: int) -> None:
        max_v = cv2.getTrackbarPos(name, WINDOW_CTRL)
        _ = max_v
        cv2.setTrackbarPos(name, WINDOW_CTRL, int(value))

    def _apply_profile(self, profile_name: str) -> None:
        profile = self.profiles.get(profile_name)
        if not profile:
            return

        mapping = {
            "Modo 0B-1H-2X": "mode",
            "Blur": "blur",
            "Canny Low": "canny_low",
            "Canny High": "canny_high",
            "Kernel": "kernel",
            "H min": "h_min",
            "S min": "s_min",
            "V min": "v_min",
            "H max": "h_max",
            "S max": "s_max",
            "V max": "v_max",
            "H2 min": "h2_min",
            "S2 min": "s2_min",
            "V2 min": "v2_min",
            "H2 max": "h2_max",
            "S2 max": "s2_max",
            "V2 max": "v2_max",
            "Min W": "min_w",
            "Min H": "min_h",
            "Max W %": "max_w_pct",
            "Max H %": "max_h_pct",
            "Base %": "base_pct",
            "Margen X %": "margin_x_pct",
        }

        for slider_name, key in mapping.items():
            if key in profile:
                cv2.setTrackbarPos(slider_name, WINDOW_CTRL, int(profile[key]))

    def _read_sliders(self) -> Dict[str, int]:
        d = {
            "mode": cv2.getTrackbarPos("Modo 0B-1H-2X", WINDOW_CTRL),
            "blur": odd_value(cv2.getTrackbarPos("Blur", WINDOW_CTRL), 1),
            "canny_low": cv2.getTrackbarPos("Canny Low", WINDOW_CTRL),
            "canny_high": cv2.getTrackbarPos("Canny High", WINDOW_CTRL),
            "kernel": odd_value(cv2.getTrackbarPos("Kernel", WINDOW_CTRL), 1),
            "h_min": cv2.getTrackbarPos("H min", WINDOW_CTRL),
            "s_min": cv2.getTrackbarPos("S min", WINDOW_CTRL),
            "v_min": cv2.getTrackbarPos("V min", WINDOW_CTRL),
            "h_max": cv2.getTrackbarPos("H max", WINDOW_CTRL),
            "s_max": cv2.getTrackbarPos("S max", WINDOW_CTRL),
            "v_max": cv2.getTrackbarPos("V max", WINDOW_CTRL),
            "h2_min": cv2.getTrackbarPos("H2 min", WINDOW_CTRL),
            "s2_min": cv2.getTrackbarPos("S2 min", WINDOW_CTRL),
            "v2_min": cv2.getTrackbarPos("V2 min", WINDOW_CTRL),
            "h2_max": cv2.getTrackbarPos("H2 max", WINDOW_CTRL),
            "s2_max": cv2.getTrackbarPos("S2 max", WINDOW_CTRL),
            "v2_max": cv2.getTrackbarPos("V2 max", WINDOW_CTRL),
            "min_w": cv2.getTrackbarPos("Min W", WINDOW_CTRL),
            "min_h": cv2.getTrackbarPos("Min H", WINDOW_CTRL),
            "max_w_pct": max(1, cv2.getTrackbarPos("Max W %", WINDOW_CTRL)),
            "max_h_pct": max(1, cv2.getTrackbarPos("Max H %", WINDOW_CTRL)),
            "base_pct": max(1, cv2.getTrackbarPos("Base %", WINDOW_CTRL)),
            "margin_x_pct": min(49, cv2.getTrackbarPos("Margen X %", WINDOW_CTRL)),
        }

        cv2.setTrackbarPos("Blur", WINDOW_CTRL, d["blur"])
        cv2.setTrackbarPos("Kernel", WINDOW_CTRL, d["kernel"])

        return d

    def _snapshot_undo(self) -> None:
        self.undo_stack.append(copy.deepcopy(self.manual_rects))
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)

    def _undo(self) -> None:
        if not self.undo_stack:
            return
        self.manual_rects = self.undo_stack.pop()
        if self.manual_rects:
            self.selected_idx = min(self.selected_idx, len(self.manual_rects) - 1)
        else:
            self.selected_idx = -1

    def _point_inside_rect(self, x: int, y: int, r: Rect) -> bool:
        return r.x <= x <= (r.x + r.w) and r.y <= y <= (r.y + r.h)

    def _point_on_resize_handle(self, x: int, y: int, r: Rect) -> bool:
        handle = 12
        return abs(x - (r.x + r.w)) <= handle and abs(y - (r.y + r.h)) <= handle

    def _select_at(self, x: int, y: int) -> int:
        for i in range(len(self.manual_rects) - 1, -1, -1):
            if self._point_inside_rect(x, y, self.manual_rects[i]):
                return i
        return -1

    def _delete_at(self, x: int, y: int) -> None:
        idx = self._select_at(x, y)
        if idx < 0:
            return
        self._snapshot_undo()
        self.manual_rects.pop(idx)
        if not self.manual_rects:
            self.selected_idx = -1
        else:
            self.selected_idx = min(idx, len(self.manual_rects) - 1)

    def _normalize_rect(self, x1: int, y1: int, x2: int, y2: int) -> Rect:
        xx1 = min(x1, x2)
        yy1 = min(y1, y2)
        xx2 = max(x1, x2)
        yy2 = max(y1, y2)
        w = max(1, xx2 - xx1)
        h = max(1, yy2 - yy1)
        return Rect(xx1, yy1, w, h, self.current_type, "manual")

    def on_mouse(self, event: int, x: int, y: int, _flags: int, _param: object) -> None:
        x = int(np.clip(x, 0, self.image_w - 1))
        y = int(np.clip(y, 0, self.image_h - 1))

        if event == cv2.EVENT_RBUTTONDOWN:
            self._delete_at(x, y)
            return

        if event == cv2.EVENT_LBUTTONDOWN:
            idx = self._select_at(x, y)
            if idx >= 0 and self._point_on_resize_handle(x, y, self.manual_rects[idx]):
                self.selected_idx = idx
                self.drag_mode = "resize"
                r = self.manual_rects[idx]
                self.resize_origin = (r.x, r.y, r.w, r.h)
                self.drag_start = (x, y)
                return

            self.drag_mode = "create"
            self.drag_start = (x, y)
            self.temp_rect = Rect(x, y, 1, 1, self.current_type, "manual")
            sel = self._select_at(x, y)
            if sel >= 0:
                self.selected_idx = sel

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drag_mode == "create" and self.drag_start is not None:
                self.temp_rect = self._normalize_rect(self.drag_start[0], self.drag_start[1], x, y)
            elif (
                self.drag_mode == "resize"
                and self.drag_start is not None
                and self.resize_origin is not None
                and self.selected_idx >= 0
                and self.selected_idx < len(self.manual_rects)
            ):
                ox, oy, ow, oh = self.resize_origin
                nw = max(1, ow + (x - self.drag_start[0]))
                nh = max(1, oh + (y - self.drag_start[1]))
                self.manual_rects[self.selected_idx] = Rect(ox, oy, nw, nh, self.manual_rects[self.selected_idx].tipo, "manual")

        elif event == cv2.EVENT_LBUTTONUP:
            if self.drag_mode == "create" and self.temp_rect is not None:
                self._snapshot_undo()
                self.temp_rect.clamp_positive()
                self.manual_rects.append(self.temp_rect)
                self.selected_idx = len(self.manual_rects) - 1
                self.temp_rect = None
            elif self.drag_mode == "resize":
                if self.selected_idx >= 0 and self.selected_idx < len(self.manual_rects):
                    self.manual_rects[self.selected_idx].clamp_positive()
            self.drag_mode = None
            self.drag_start = None
            self.resize_origin = None

    def _build_masks(self, sliders: Dict[str, int]) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        blur = sliders["blur"]
        kernel_size = sliders["kernel"]
        mode = sliders["mode"]

        hsv = cv2.cvtColor(self.image_original, cv2.COLOR_BGR2HSV)
        blur_img = cv2.GaussianBlur(self.image_original, (blur, blur), 0)
        gray = cv2.cvtColor(blur_img, cv2.COLOR_BGR2GRAY)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))

        edges = cv2.Canny(gray, sliders["canny_low"], sliders["canny_high"])
        mask_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        mask_edges = cv2.dilate(mask_edges, kernel, iterations=1)

        lower1 = np.array([sliders["h_min"], sliders["s_min"], sliders["v_min"]], dtype=np.uint8)
        upper1 = np.array([sliders["h_max"], sliders["s_max"], sliders["v_max"]], dtype=np.uint8)
        lower2 = np.array([sliders["h2_min"], sliders["s2_min"], sliders["v2_min"]], dtype=np.uint8)
        upper2 = np.array([sliders["h2_max"], sliders["s2_max"], sliders["v2_max"]], dtype=np.uint8)

        mask_hsv_1 = cv2.inRange(hsv, lower1, upper1)
        mask_hsv_2 = cv2.inRange(hsv, lower2, upper2)

        mask_hsv_1 = cv2.morphologyEx(mask_hsv_1, cv2.MORPH_OPEN, kernel)
        mask_hsv_1 = cv2.morphologyEx(mask_hsv_1, cv2.MORPH_CLOSE, kernel)

        mask_hsv_2 = cv2.morphologyEx(mask_hsv_2, cv2.MORPH_OPEN, kernel)
        mask_hsv_2 = cv2.morphologyEx(mask_hsv_2, cv2.MORPH_CLOSE, kernel)

        per_type = {
            TYPE_SOLIDO: np.zeros_like(mask_edges),
            TYPE_AGUA: np.zeros_like(mask_edges),
            TYPE_TEJADO: np.zeros_like(mask_edges),
            TYPE_VEGETACION: np.zeros_like(mask_edges),
        }

        if mode == MODE_BORDES:
            per_type[TYPE_SOLIDO] = mask_edges
            combined = mask_edges
        elif mode == MODE_HSV:
            per_type[TYPE_AGUA] = mask_hsv_1
            per_type[TYPE_VEGETACION] = mask_hsv_2
            combined = cv2.bitwise_or(mask_hsv_1, mask_hsv_2)
        else:
            per_type[TYPE_SOLIDO] = mask_edges
            per_type[TYPE_AGUA] = mask_hsv_1
            # Split second HSV range by brightness to separate vegetation and roof-like regions.
            v_channel = hsv[:, :, 2]
            vmid = int((sliders["v2_min"] + sliders["v2_max"]) / 2)
            mask_veg = cv2.bitwise_and(mask_hsv_2, cv2.inRange(v_channel, sliders["v2_min"], vmid))
            mask_roof = cv2.bitwise_and(mask_hsv_2, cv2.inRange(v_channel, vmid + 1, sliders["v2_max"]))
            per_type[TYPE_VEGETACION] = mask_veg
            per_type[TYPE_TEJADO] = mask_roof
            combined = cv2.bitwise_or(mask_edges, mask_hsv_1)
            combined = cv2.bitwise_or(combined, mask_hsv_2)

        combined = cv2.threshold(combined, 1, 255, cv2.THRESH_BINARY)[1]
        return combined, per_type

    def _contours_to_rects(self, per_type_masks: Dict[str, np.ndarray], sliders: Dict[str, int]) -> List[Rect]:
        min_w = max(1, sliders["min_w"])
        min_h = max(1, sliders["min_h"])
        max_w = int(self.image_w * (sliders["max_w_pct"] / 100.0))
        max_h = int(self.image_h * (sliders["max_h_pct"] / 100.0))

        base_factor = sliders["base_pct"] / 100.0
        margin_factor = sliders["margin_x_pct"] / 100.0

        rects: List[Rect] = []

        for tipo, mask in per_type_masks.items():
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if w < min_w or h < min_h:
                    continue
                if w > max_w or h > max_h:
                    continue

                margin_x = int(w * margin_factor)
                nx = x + margin_x
                nw = max(1, w - (2 * margin_x))

                nh = max(1, int(h * base_factor))
                ny = y + (h - nh)

                nx = int(np.clip(nx, 0, self.image_w - 1))
                ny = int(np.clip(ny, 0, self.image_h - 1))
                nw = int(min(nw, self.image_w - nx))
                nh = int(min(nh, self.image_h - ny))
                if nw <= 0 or nh <= 0:
                    continue

                rects.append(Rect(nx, ny, nw, nh, tipo, "auto"))

        return rects

    def _draw_rects(self, frame: np.ndarray, rects: List[Rect], selected: int = -1, alpha: float = 0.32) -> np.ndarray:
        colors = {
            TYPE_SOLIDO: (30, 30, 230),
            TYPE_AGUA: (230, 100, 30),
            TYPE_TEJADO: (30, 230, 230),
            TYPE_VEGETACION: (30, 180, 30),
        }

        overlay = frame.copy()
        for i, r in enumerate(rects):
            color = colors.get(r.tipo, (200, 200, 200))
            cv2.rectangle(overlay, (r.x, r.y), (r.x + r.w, r.y + r.h), color, -1)
            thickness = 2
            if i == selected:
                thickness = 3
                cv2.rectangle(frame, (r.x + r.w - 5, r.y + r.h - 5), (r.x + r.w + 5, r.y + r.h + 5), (255, 255, 255), -1)
            cv2.rectangle(frame, (r.x, r.y), (r.x + r.w, r.y + r.h), color, thickness)
            cv2.putText(
                frame,
                r.tipo[0].upper(),
                (r.x + 2, max(12, r.y + 12)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        return frame

    def _merge_manual_rects(self) -> None:
        if not self.manual_rects:
            return

        self._snapshot_undo()

        changed = True
        while changed:
            changed = False
            merged: List[Rect] = []
            used = [False] * len(self.manual_rects)

            for i in range(len(self.manual_rects)):
                if used[i]:
                    continue
                current = self.manual_rects[i]
                used[i] = True

                for j in range(i + 1, len(self.manual_rects)):
                    if used[j]:
                        continue
                    other = self.manual_rects[j]
                    if other.tipo != current.tipo:
                        continue
                    inter = rect_intersection_area(current, other)
                    iou = rect_iou(current, other)
                    if inter > 0 or iou > 0.01:
                        current = merge_two_rects(current, other)
                        used[j] = True
                        changed = True

                merged.append(current)

            self.manual_rects = merged

        if not self.manual_rects:
            self.selected_idx = -1
        else:
            self.selected_idx = min(self.selected_idx, len(self.manual_rects) - 1)

    def _current_profile_from_sliders(self) -> Dict[str, int]:
        return self._read_sliders()

    def _export(self, preview_frame: np.ndarray, all_rects: List[Rect]) -> None:
        root = tk.Tk()
        root.withdraw()
        root.update()

        preview_path = filedialog.asksaveasfilename(
            title="Guardar preview PNG",
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
        )
        if preview_path:
            cv2.imwrite(preview_path, preview_frame)

        json_path = filedialog.asksaveasfilename(
            title="Guardar colisiones JSON",
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
        )
        if json_path:
            payload = {
                "colisiones": [r.to_dict() for r in all_rects],
                "por_tipo": {tipo: [] for tipo in COLLISION_TYPES},
            }
            for r in all_rects:
                payload["por_tipo"][r.tipo].append(
                    {
                        "x": r.x,
                        "y": r.y,
                        "w": r.w,
                        "h": r.h,
                        "fuente": r.fuente,
                    }
                )
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)

        root.destroy()

    def run(self) -> None:
        help_text = (
            "1 Bosque | 2 Ciudad | 3 Costa | 4 Custom | G guardar Custom | "
            "O/A/T/V tipo | N/P sel | X borrar sel | C limpiar | Z undo | "
            "M merge | S exportar | Q/ESC salir"
        )

        while True:
            sliders = self._read_sliders()
            combined_mask, per_type_masks = self._build_masks(sliders)
            self.auto_rects = self._contours_to_rects(per_type_masks, sliders)

            frame = self.image_original.copy()
            frame = self._draw_rects(frame, self.auto_rects, -1, alpha=0.2)
            frame = self._draw_rects(frame, self.manual_rects, self.selected_idx, alpha=0.3)

            if self.temp_rect is not None:
                cv2.rectangle(
                    frame,
                    (self.temp_rect.x, self.temp_rect.y),
                    (self.temp_rect.x + self.temp_rect.w, self.temp_rect.y + self.temp_rect.h),
                    (255, 255, 255),
                    1,
                )

            cv2.putText(frame, f"Tipo actual: {self.current_type}", (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, help_text, (10, self.image_h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

            cv2.imshow(WINDOW_MAIN, frame)
            cv2.imshow(WINDOW_MASK, combined_mask)

            key = cv2.waitKey(16) & 0xFF
            if key == 255:
                continue

            if key in (27, ord("q")):
                break

            elif key == ord("1"):
                self._apply_profile("Bosque")
            elif key == ord("2"):
                self._apply_profile("Ciudad")
            elif key == ord("3"):
                self._apply_profile("Costa")
            elif key == ord("4"):
                self._apply_profile("Custom")
            elif key == ord("g"):
                self.profiles["Custom"] = self._current_profile_from_sliders()
                save_profiles(self.profiles)

            elif key == ord("o"):
                self.current_type = TYPE_SOLIDO
            elif key == ord("a"):
                self.current_type = TYPE_AGUA
            elif key == ord("t"):
                self.current_type = TYPE_TEJADO
            elif key == ord("v"):
                self.current_type = TYPE_VEGETACION

            elif key == ord("n"):
                if self.manual_rects:
                    self.selected_idx = (self.selected_idx + 1) % len(self.manual_rects)
            elif key == ord("p"):
                if self.manual_rects:
                    self.selected_idx = (self.selected_idx - 1) % len(self.manual_rects)
            elif key == ord("x"):
                if 0 <= self.selected_idx < len(self.manual_rects):
                    self._snapshot_undo()
                    self.manual_rects.pop(self.selected_idx)
                    if not self.manual_rects:
                        self.selected_idx = -1
                    else:
                        self.selected_idx = min(self.selected_idx, len(self.manual_rects) - 1)
            elif key == ord("c"):
                if self.manual_rects:
                    self._snapshot_undo()
                    self.manual_rects = []
                    self.selected_idx = -1
            elif key == ord("z"):
                self._undo()
            elif key == ord("m"):
                self._merge_manual_rects()
            elif key == ord("s"):
                all_rects = self.auto_rects + self.manual_rects
                self._export(frame, all_rects)

        cv2.destroyAllWindows()


def ask_image_path() -> Optional[str]:
    root = tk.Tk()
    root.withdraw()
    root.update()
    path = filedialog.askopenfilename(
        title="Selecciona imagen de mapa o tileset",
        filetypes=[
            ("Imagenes", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff;*.webp"),
            ("Todos", "*.*"),
        ],
    )
    root.destroy()
    if not path:
        return None
    return path


def main() -> None:
    image_path = ask_image_path()
    if not image_path:
        print("No se selecciono imagen.")
        return

    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        print("No se pudo cargar la imagen.")
        return

    app = CollisionExtractorApp(image)
    app.run()


if __name__ == "__main__":
    main()

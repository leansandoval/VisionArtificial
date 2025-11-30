# Funciones para dibujar overlays (Bounding Boxes, IDs, FPS, Zonas) sobre frames OpenCV.
import cv2
import numpy as np
from src.constantes import *

# region Constantes

RADIO_CIRCULO_EXTERIOR_ID_TRACKING = 8
RADIO_CIRCULO_INTERIOR_ID_TRACKING = 4
TRANSPARENCIA_ZONA = 0.1

# endregion

# region Funciones Auxiliares

def dibujar_texto_bounding_box(frame, label, color, x1, y1):
    # Background para el texto
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_SESENTA_PORCIENTO, GROSOR_DOS_PIXELES)
    punto_esquina_superior_izquierda_rectangulo = (x1, max(0, y1 - th - 8))
    punto_esquina_inferior_derecha_rectangulo = (x1 + tw + 6, y1)
    cv2.rectangle(frame, punto_esquina_superior_izquierda_rectangulo, punto_esquina_inferior_derecha_rectangulo, color, GROSOR_RELLENO_COMPLETO)
    punto_texto = (x1 + 3, max(th, y1 - 4))
    cv2.putText(frame, label, punto_texto, cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_SESENTA_PORCIENTO, COLOR_TUPLA_NEGRO, GROSOR_DOS_PIXELES, cv2.LINE_AA)


def dibujar_estadisticas(frame, estadisticas, x_start, y_start):
    y_offset = y_start + 20
    for key, value in estadisticas.items():
        text = f"{key}: {value}"
        cv2.putText(frame, text, (x_start + 10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_CINCUENTA_PORCIENTO, COLOR_TUPLA_BLANCO, GROSOR_UN_PIXEL, cv2.LINE_AA)
        y_offset += 25

# endregion

# region Funciones Principales

def dibujar_bounding_box(frame, bounding_box, label=None, color=COLOR_TUPLA_VERDE, grosor=GROSOR_DOS_PIXELES):
    x1, y1, x2, y2 = [int(v) for v in bounding_box]
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, grosor)
    if label:
        dibujar_texto_bounding_box(frame, label, color, x1, y1)

def dibujar_punto_de_tracking(frame, punto, track_id, color=COLOR_TUPLA_BLANCO):
    x, y = int(punto[0]), int(punto[1])
    cv2.circle(frame, (x, y), RADIO_CIRCULO_EXTERIOR_ID_TRACKING, color, GROSOR_DOS_PIXELES)
    cv2.circle(frame, (x, y), RADIO_CIRCULO_INTERIOR_ID_TRACKING, color, GROSOR_RELLENO_COMPLETO)
    (tw, th), _ = cv2.getTextSize(str(track_id), cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_CINCUENTA_PORCIENTO, GROSOR_UN_PIXEL)
    punto_texto = (x - tw // 2, y + 20)
    cv2.putText(frame, str(track_id), punto_texto, cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_CINCUENTA_PORCIENTO, color, GROSOR_DOS_PIXELES, cv2.LINE_AA)

def dibujar_zona(frame, poly, color=COLOR_TUPLA_ROJO, thickness=GROSOR_DOS_PIXELES, alpha=TRANSPARENCIA_ZONA, zone_name=None, zone_id=None):
    pts = np.array(poly, dtype=np.int32)
    overlay = frame.copy()
    # Borde doble (blanco exterior + color) para mayor contraste
    cv2.polylines(overlay, [pts], isClosed=True, color=COLOR_TUPLA_BLANCO, thickness=thickness + 30)
    cv2.polylines(overlay, [pts], isClosed=True, color=color, thickness=thickness)
    cv2.fillPoly(overlay, [pts], color)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    # Nombre de zona (esquina superior izquierda, texto mas chico)
    if zone_name or zone_id is not None:
        label = zone_name if zone_name else f"Zone {zone_id}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_CINCUENTA_PORCIENTO, GROSOR_DOS_PIXELES)
        min_xy = pts.min(axis=0)
        x_label = max(int(min_xy[0]) + 5, 0)
        y_label = max(int(min_xy[1]) + th + 5, th)
        overlay_text = frame.copy()
        punto_esquina_superior_izquierda_rectangulo = (x_label - 4, y_label - th - 6)
        punto_esquina_inferior_derecha_rectangulo = (x_label + tw + 4, y_label + 4)
        cv2.rectangle(overlay_text, punto_esquina_superior_izquierda_rectangulo, punto_esquina_inferior_derecha_rectangulo, COLOR_TUPLA_NEGRO, GROSOR_RELLENO_COMPLETO)
        cv2.addWeighted(overlay_text, 0.6, frame, 0.4, 0, frame)
        cv2.putText(frame, label, (x_label, y_label), cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_CINCUENTA_PORCIENTO, color, GROSOR_DOS_PIXELES, cv2.LINE_AA)

def dibujar_fps(frame, fps, frame_number=None):
    text = f"FPS: {fps:.1f}"
    if frame_number is not None:
        text += f" | Frame: {frame_number}"
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_SESENTA_PORCIENTO, GROSOR_DOS_PIXELES)
    # Fondo semi-transparente
    overlay = frame.copy()
    punto_esquina_superior_izquierda_rectangulo = (8, 8)
    punto_esquina_inferior_derecha_rectangulo = (tw + 22, th + 22)
    cv2.rectangle(overlay, punto_esquina_superior_izquierda_rectangulo, punto_esquina_inferior_derecha_rectangulo, COLOR_TUPLA_NEGRO, GROSOR_RELLENO_COMPLETO)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    # Texto
    punto_texto = (15, th + 15)
    cv2.putText(frame, text, punto_texto, cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_SESENTA_PORCIENTO, COLOR_TUPLA_VERDE, GROSOR_DOS_PIXELES, cv2.LINE_AA)

def dibujar_panel_estadisticas(frame, estadisticas, posicion="top-right"):
    h, w = frame.shape[:2]
    max_width = max([cv2.getTextSize(f"{k}: {v}", cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_CINCUENTA_PORCIENTO, GROSOR_UN_PIXEL)[0][0] for k, v in estadisticas.items()])
    panel_width = max_width + 30
    panel_height = len(estadisticas) * 25 + 20
    if posicion == "top-right":
        x_start = w - panel_width - 15
        y_start = 15
    else:
        x_start = 15
        y_start = 60
    overlay = frame.copy()
    punto_esquina_superior_izquierda_rectangulo = (x_start, y_start)
    punto_esquina_inferior_derecha_rectangulo = (x_start + panel_width, y_start + panel_height)
    cv2.rectangle(overlay, punto_esquina_superior_izquierda_rectangulo, punto_esquina_inferior_derecha_rectangulo, COLOR_TUPLA_NEGRO, GROSOR_RELLENO_COMPLETO)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    cv2.rectangle(frame, punto_esquina_superior_izquierda_rectangulo, punto_esquina_inferior_derecha_rectangulo, COLOR_TUPLA_BLANCO, GROSOR_DOS_PIXELES)
    dibujar_estadisticas(frame, estadisticas, x_start, y_start)

# Punto de alerta (esquina superior izquierda) - helper
def dibujar_punto_alerta(frame, x=8, y=8, size=26, color=(0,0,255), border_color=(20,0,0), border_thickness=3, offset_below_fps=True, fps_area_height=36):
    """
    Dibuja un punto de alerta en la esquina superior izquierda del frame.
    - offset_below_fps: si True, desplaza el punto hacia abajo para no solaparse con el HUD de FPS.
    - fps_area_height: altura estimada del HUD de FPS en píxeles.
    """
    if frame is None:
        return
    h, w = frame.shape[:2]
    # Ajustar posición si se solicita evitar solapamiento con el HUD de FPS
    draw_y = y + (fps_area_height + 6 if offset_below_fps else 0)
    # Calcular centro
    cx = int(max(0, min(w-1, x + size // 2)))
    cy = int(max(0, min(h-1, draw_y + size // 2)))
    radius = max(2, int(size / 2))
    # Dibujar borde exterior
    try:
        cv2.circle(frame, (cx, cy), radius + border_thickness, border_color, -1, lineType=cv2.LINE_AA)
        # Dibujar círculo interior (color de alerta)
        cv2.circle(frame, (cx, cy), radius, color, -1, lineType=cv2.LINE_AA)
    except Exception:
        # Failsafe: no hacer nada si el frame es inválido
        pass

# endregion

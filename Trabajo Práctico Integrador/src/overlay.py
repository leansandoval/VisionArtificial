# Funciones para dibujar overlays (Bounding Boxes, IDs, FPS, Zonas) sobre frames OpenCV.
import cv2
import numpy as np

#region Constantes

COLOR_TUPLA_BLANCO = (255, 255, 255)
COLOR_TUPLA_NEGRO = (0, 0, 0)
COLOR_TUPLA_VERDE = (0, 255, 0)
COLOR_TUPLA_ROJO = (0, 0, 255)
ESCALA_FUENTE_CINCUENTA_PORCIENTO = 0.5
ESCALA_FUENTE_SESENTA_PORCIENTO = 0.6
ESCALA_FUENTE_SETENTA_PORCIENTO = 0.7
GROSOR_BOUNDING_BOX = 2
GROSOR_RELLENO_COMPLETO = -1
GROSOR_CONTORNO_TEXTO_DOS_PIXELES = 2
GROSOR_CONTORNO_TEXTO_UN_PIXEL = 1
RADIO_CIRCULO_EXTERIOR_ID_TRACKING = 8
RADIO_CIRCULO_INTERIOR_ID_TRACKING = 4
TRANSPARENCIA_ZONA = 0.08

#endregion

#region Funciones

def dibujar_bounding_box(frame, bounding_box, label=None, color=COLOR_TUPLA_VERDE, grosor=GROSOR_BOUNDING_BOX):
    x1,y1,x2,y2 = [int(v) for v in bounding_box]
    cv2.rectangle(frame, (x1,y1), (x2,y2), color, grosor)
    if label:
        # Background para el texto
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_SESENTA_PORCIENTO, GROSOR_CONTORNO_TEXTO_DOS_PIXELES)
        punto_esquina_superior_izquierda_rectangulo = (x1, max(0,y1 - th - 8))
        punto_esquina_inferior_derecha_rectangulo = (x1 + tw + 6, y1)
        cv2.rectangle(frame, punto_esquina_superior_izquierda_rectangulo, punto_esquina_inferior_derecha_rectangulo, color, GROSOR_RELLENO_COMPLETO)
        punto_texto = (x1 + 3, max(th, y1 - 4))
        cv2.putText(frame, label, punto_texto, cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_SESENTA_PORCIENTO, COLOR_TUPLA_NEGRO, GROSOR_CONTORNO_TEXTO_DOS_PIXELES, cv2.LINE_AA)

# Dibuja punto de tracking con ID (círculo + número)
def dibujar_punto_de_tracking(frame, punto, track_id, color=COLOR_TUPLA_BLANCO):
    x, y = int(punto[0]), int(punto[1])
    cv2.circle(frame, (x, y), RADIO_CIRCULO_EXTERIOR_ID_TRACKING, color, GROSOR_CONTORNO_TEXTO_DOS_PIXELES) # Círculo exterior
    cv2.circle(frame, (x, y), RADIO_CIRCULO_INTERIOR_ID_TRACKING, color, GROSOR_RELLENO_COMPLETO)           # Círculo interior relleno
    (tw, th), _ = cv2.getTextSize(str(track_id), cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_CINCUENTA_PORCIENTO, GROSOR_CONTORNO_TEXTO_UN_PIXEL)
    punto_texto = (x - tw // 2, y + 20)
    cv2.putText(frame, str(track_id), punto_texto, cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_CINCUENTA_PORCIENTO, color, GROSOR_CONTORNO_TEXTO_DOS_PIXELES, cv2.LINE_AA)

# Dibuja zona poligonal con nombre opcional
def dibujar_zona(frame, poly, color=COLOR_TUPLA_ROJO, thickness=GROSOR_CONTORNO_TEXTO_DOS_PIXELES, alpha=TRANSPARENCIA_ZONA, zone_name=None, zone_id=None):
    pts = np.array(poly, dtype=np.int32)
    overlay = frame.copy()
    # Dibujar polígono con borde más visible
    cv2.polylines(overlay, [pts], isClosed=True, color=color, thickness=thickness+1)
    cv2.fillPoly(overlay, [pts], color)
    cv2.addWeighted(overlay, alpha, frame, 1-alpha, 0, frame)
    # Nombre de zona
    if zone_name or zone_id is not None:
        centroid = np.mean(pts, axis=0).astype(int)
        label = zone_name if zone_name else f"Zone {zone_id}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_SETENTA_PORCIENTO, GROSOR_CONTORNO_TEXTO_DOS_PIXELES)
        # Fondo semi-transparente para el texto
        overlay_text = frame.copy()
        punto_esquina_superior_izquierda_rectangulo = (centroid[0] - tw // 2 - 5, centroid[1] - th - 5)
        punto_esquina_inferior_derecha_rectangulo = (centroid[0] + tw // 2 + 5, centroid[1] + 5)
        punto_texto = (centroid[0] - tw // 2, centroid[1])
        cv2.rectangle(overlay_text, punto_esquina_superior_izquierda_rectangulo, punto_esquina_inferior_derecha_rectangulo, COLOR_TUPLA_NEGRO, GROSOR_RELLENO_COMPLETO)
        cv2.addWeighted(overlay_text, 0.6, frame, 0.4, 0, frame)
        cv2.putText(frame, label, punto_texto, cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_SETENTA_PORCIENTO, color, GROSOR_CONTORNO_TEXTO_DOS_PIXELES, cv2.LINE_AA)

# Dibuja FPS y frame number en estilo profesional
def draw_fps_professional(frame, fps, frame_number=None):
    text = f'FPS: {fps:.1f}'
    if frame_number is not None:
        text += f' | Frame: {frame_number}'
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_SESENTA_PORCIENTO, GROSOR_CONTORNO_TEXTO_DOS_PIXELES)
    # Fondo semi-transparente
    overlay = frame.copy()
    cv2.rectangle(overlay, (8, 8), (tw + 22, th + 22), COLOR_TUPLA_NEGRO, GROSOR_RELLENO_COMPLETO)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    # Texto
    punto_texto = (15, th + 15)
    cv2.putText(frame, text, punto_texto, cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_SESENTA_PORCIENTO, COLOR_TUPLA_VERDE, GROSOR_CONTORNO_TEXTO_DOS_PIXELES, cv2.LINE_AA)

# Dibuja panel de estadísticas estilo dashboard profesional
def draw_stats_panel(frame, stats_dict, position='top-right'):
    h, w = frame.shape[:2]
    # Calcular tamaño del panel
    max_width = max([cv2.getTextSize(f'{k}: {v}', cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_CINCUENTA_PORCIENTO, GROSOR_CONTORNO_TEXTO_UN_PIXEL)[0][0] 
                     for k, v in stats_dict.items()])
    panel_width = max_width + 30
    panel_height = len(stats_dict) * 25 + 20
    if position == 'top-right':
        x_start = w - panel_width - 15
        y_start = 15
    else:
        x_start = 15
        y_start = 60
    # Fondo del panel con transparencia
    overlay = frame.copy()
    punto_esquina_superior_izquierda_rectangulo = (x_start, y_start)
    punto_esquina_inferior_derecha_rectangulo = (x_start + panel_width, y_start + panel_height)
    cv2.rectangle(overlay, punto_esquina_superior_izquierda_rectangulo, punto_esquina_inferior_derecha_rectangulo, COLOR_TUPLA_NEGRO, GROSOR_RELLENO_COMPLETO)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    # Borde del panel
    cv2.rectangle(frame, punto_esquina_superior_izquierda_rectangulo, punto_esquina_inferior_derecha_rectangulo, COLOR_TUPLA_BLANCO, GROSOR_CONTORNO_TEXTO_DOS_PIXELES)
    # Dibujar estadísticas
    y_offset = y_start + 20
    for key, value in stats_dict.items():
        text = f'{key}: {value}'
        cv2.putText(frame, text, (x_start + 10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_CINCUENTA_PORCIENTO, COLOR_TUPLA_BLANCO, GROSOR_CONTORNO_TEXTO_UN_PIXEL, cv2.LINE_AA)
        y_offset += 25

# Wrapper para compatibilidad hacia atrás
def draw_fps(frame, fps):
    draw_fps_professional(frame, fps)

# Wrapper para compatibilidad hacia atrás
def draw_stats(frame, stats_dict):
    draw_stats_panel(frame, stats_dict)

#endregion

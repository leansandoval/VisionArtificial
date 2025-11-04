"""Funciones para dibujar overlays (bbox, ids, FPS, zonas) sobre frames OpenCV."""
import cv2
import numpy as np

def draw_bbox(frame, bbox, label=None, color=(0,255,0), thickness=2):
    x1,y1,x2,y2 = [int(v) for v in bbox]
    cv2.rectangle(frame, (x1,y1), (x2,y2), color, thickness)
    if label:
        # Background para el texto
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(frame, (x1, max(0,y1-th-8)), (x1+tw+6, y1), color, -1)
        cv2.putText(frame, label, (x1+3, max(th,y1-4)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2, cv2.LINE_AA)

def draw_tracking_point(frame, point, track_id, color=(255,255,255)):
    """Dibuja punto de tracking con ID (círculo + número)"""
    x, y = int(point[0]), int(point[1])
    # Círculo exterior
    cv2.circle(frame, (x, y), 8, color, 2)
    # Círculo interior relleno
    cv2.circle(frame, (x, y), 4, color, -1)
    # ID del track
    text = str(track_id)
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    cv2.putText(frame, text, (x - tw//2, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA)

def draw_zone(frame, poly, color=(0,0,255), thickness=2, alpha=0.15, zone_name=None, zone_id=None):
    """Dibuja zona poligonal con nombre opcional"""
    pts = np.array(poly, dtype=np.int32)
    overlay = frame.copy()
    
    # Dibujar polígono
    cv2.polylines(overlay, [pts], isClosed=True, color=color, thickness=thickness)
    cv2.fillPoly(overlay, [pts], color)
    cv2.addWeighted(overlay, alpha, frame, 1-alpha, 0, frame)
    
    # Nombre de zona
    if zone_name or zone_id is not None:
        centroid = np.mean(pts, axis=0).astype(int)
        label = zone_name if zone_name else f"Zone {zone_id}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        # Fondo para el texto
        cv2.rectangle(frame, (centroid[0]-tw//2-5, centroid[1]-th-5), 
                     (centroid[0]+tw//2+5, centroid[1]+5), (0,0,0), -1)
        cv2.putText(frame, label, (centroid[0]-tw//2, centroid[1]), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)

def draw_logo(frame, text="VA", position='top-left'):
    """Dibuja logo/marca en esquina"""
    h, w = frame.shape[:2]
    
    if position == 'top-left':
        x, y = 20, 40
    elif position == 'top-right':
        x, y = w - 80, 40
    else:
        x, y = 20, 40
    
    # Fondo negro con borde
    cv2.rectangle(frame, (x-10, y-35), (x+60, y+10), (0,0,0), -1)
    cv2.rectangle(frame, (x-10, y-35), (x+60, y+10), (0,255,0), 2)
    cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0,255,0), 2, cv2.LINE_AA)

def draw_fps_professional(frame, fps, frame_number=None):
    """Dibuja FPS y frame number en estilo profesional"""
    text = f'FPS: {fps:.1f}'
    if frame_number is not None:
        text += f' | Frame: {frame_number}'
    
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    # Fondo semi-transparente
    overlay = frame.copy()
    cv2.rectangle(overlay, (8, 8), (tw + 22, th + 22), (0,0,0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    # Texto
    cv2.putText(frame, text, (15, th + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2, cv2.LINE_AA)

def draw_stats_panel(frame, stats_dict, position='top-right'):
    """Dibuja panel de estadísticas estilo dashboard profesional"""
    h, w = frame.shape[:2]
    
    # Calcular tamaño del panel
    max_width = max([cv2.getTextSize(f'{k}: {v}', cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0][0] 
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
    cv2.rectangle(overlay, (x_start, y_start), 
                 (x_start + panel_width, y_start + panel_height), 
                 (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Borde del panel
    cv2.rectangle(frame, (x_start, y_start), 
                 (x_start + panel_width, y_start + panel_height), 
                 (255, 255, 255), 2)
    
    # Dibujar estadísticas
    y_offset = y_start + 20
    for key, value in stats_dict.items():
        text = f'{key}: {value}'
        cv2.putText(frame, text, (x_start + 10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        y_offset += 25

def draw_fps(frame, fps):
    """Wrapper para compatibilidad hacia atrás"""
    draw_fps_professional(frame, fps)

def draw_stats(frame, stats_dict):
    """Wrapper para compatibilidad hacia atrás"""
    draw_stats_panel(frame, stats_dict)

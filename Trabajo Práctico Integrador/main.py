"""Demo principal: captura video, detección de personas, tracking simple, zonas y alertas.

Uso mínimo:
    python main.py --source 0
    python main.py --source video.mp4 --weights path/to/yolov11.pt

Notas:
- Proyecto preparado para CPU (no CUDA). Puedes suministrar tus pesos YOLOv11 si los tienes.
"""
import argparse
import cv2
import os
import time
import numpy as np

from src.detector import Detector
from src.tracker import SimpleTracker
from src.zones import ZonesManager
from src.alerts import Alerts
from src.overlay import (draw_bbox, draw_zone, draw_fps_professional, 
                         draw_stats_panel, draw_logo, draw_tracking_point)
from src.utils import FPSCounter

# Importar ByteTrack si está disponible
try:
    from src.bytetrack_wrapper import ByteTrackWrapper
    BYTETRACK_AVAILABLE = True
except ImportError:
    BYTETRACK_AVAILABLE = False
    print('[WARNING] ByteTrack no disponible. Usando SimpleTracker.')


def bbox_center(b):
    x1,y1,x2,y2 = b
    return int((x1+x2)/2), int((y1+y2)/2)


def main(args):
    det = Detector(weights=args.weights, device='cpu', conf_thres=args.conf, imgsz=args.imgsz)
    
    # Seleccionar tracker según parámetro
    if args.tracker == 'bytetrack' and BYTETRACK_AVAILABLE:
        tracker = ByteTrackWrapper(
            track_activation_threshold=0.25, 
            lost_track_buffer=30, 
            minimum_matching_threshold=0.8,
            frame_rate=30
        )
        tracker_name = 'ByteTrack'
    else:
        tracker = SimpleTracker(iou_threshold=0.3)
        tracker_name = 'SimpleTracker'
        if args.tracker == 'bytetrack' and not BYTETRACK_AVAILABLE:
            print('[WARNING] ByteTrack solicitado pero no disponible. Usando SimpleTracker.')
    
    zones = ZonesManager(args.zones)
    zones.load()
    alerts = Alerts(cooldown_seconds=args.cooldown)
    fpsc = FPSCounter()

    cap = cv2.VideoCapture(int(args.source) if str(args.source).isdigit() else args.source)
    if not cap.isOpened():
        print('No se pudo abrir fuente:', args.source)
        return

    win = 'Sistema de Deteccion de Intrusiones'
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    
    # Stats
    total_alerts = 0
    tracks_in_zone = set()
    frame_count = 0
    last_dets = []
    last_tracks = []

    print('\n' + '='*50)
    print('SISTEMA DE DETECCIÓN DE INTRUSIONES ACTIVO')
    print('='*50)
    print(f'Modelo: {args.weights or "yolov8n.pt (default)"}')
    print(f'Tracker: {tracker_name}')
    print(f'Tamaño de inferencia: {args.imgsz}px')
    print(f'Skip frames: {args.skip_frames} (0=procesar todos)')
    print(f'Zonas configuradas: {len(zones.zones)}')
    print(f'Umbral de confianza: {args.conf}')
    print(f'Alertas WhatsApp: {"SÍ" if args.use_whatsapp else "NO (solo local)"}')
    print('Presiona Q o ESC para salir')
    print('='*50 + '\n')

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        fpsc.tick()
        frame_count += 1
        
        # Optimización: skip frames para mejorar FPS
        if args.skip_frames > 0 and frame_count % (args.skip_frames + 1) != 0:
            # Usar última detección/tracking
            dets = last_dets
            tracks = last_tracks
        else:
            # detect
            dets = det.detect(frame)
            last_dets = dets
            
            # tracker
            tracks = tracker.update(dets)
            last_tracks = tracks

        # overlay zones con nombres personalizados
        for zone_idx, poly in enumerate(zones.zones):
            zone_name = zones.get_zone_name(zone_idx)
            zone_color = (0, 0, 255)  # Rojo por defecto
            draw_zone(frame, poly, color=zone_color, zone_name=zone_name)

        # check tracks against zones
        current_in_zone = set()
        for i, t in enumerate(tracks):
            bid = t['track_id']
            bbox = t['bbox']
            x, y = bbox_center(bbox)
            
            # Buscar confianza en las detecciones originales
            conf = 0.0
            for d in dets:
                db = d['bbox']
                if abs(db[0]-bbox[0]) < 5 and abs(db[1]-bbox[1]) < 5:  # match aproximado
                    conf = d['conf']
                    break
            
            # Determinar si está dentro de zona
            inside = False
            if zones.zones:
                for poly in zones.zones:
                    if cv2.pointPolygonTest(np.array(poly, dtype=np.int32), (int(x), int(y)), False) >= 0:
                        inside = True
                        current_in_zone.add(bid)
                        break
            
            # Color y label según estado
            if inside:
                color = (0, 0, 255)  # Rojo si está en zona
                label = f'Person ({conf:.2f})'
            else:
                color = (0, 255, 0)  # Verde si está fuera
                label = f'Person ({conf:.2f})'
            
            draw_bbox(frame, bbox, label=label, color=color, thickness=2)
            
            # Punto de tracking en el centro
            point_color = (0, 0, 255) if inside else (0, 255, 255)  # Rojo si intrusion, amarillo si seguro
            draw_tracking_point(frame, (x, y), bid, color=point_color)
            
            # Alerta si está dentro
            if inside:
                if alerts.alert_for_track(bid, f'⚠️ INTRUSION: Persona {bid} detectada en zona restringida', use_whatsapp=args.use_whatsapp):
                    total_alerts += 1

        tracks_in_zone = current_in_zone
        
        # Overlay de estadísticas profesional
        draw_fps_professional(frame, fpsc.fps(), frame_number=frame_count)
        
        # Panel de estadísticas
        active_zones = sum(1 for _ in zones.zones if len(current_in_zone) > 0)
        avg_detections = len(tracks)
        stats = {
            'Fotograma': frame_count,
            'Zonas Activas': f'{active_zones}/{len(zones.zones)}',
            'Total Zonas': len(zones.zones),
            'Detecciones Prom': f'{avg_detections:.1f}'
        }
        draw_stats_panel(frame, stats, position='top-right')
        
        cv2.imshow(win, frame)
        k = cv2.waitKey(1) & 0xFF
        if k == 27 or k == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
    print('\n' + '='*50)
    print('SISTEMA DETENIDO')
    print(f'Total de alertas enviadas: {total_alerts}')
    print('='*50)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', default=0, help='Índice de cámara o ruta de video')
    parser.add_argument('--weights', default=None, help='Ruta a pesos YOLO (ej: yolov11.pt o yolov8n.pt)')
    parser.add_argument('--zones', default='zones.json', help='Archivo JSON con zonas')
    parser.add_argument('--conf', type=float, default=0.3, help='Umbral de confianza')
    parser.add_argument('--cooldown', type=int, default=10, help='Cooldown de alertas por track (s)')
    parser.add_argument('--use_whatsapp', action='store_true', help='Enviar alerta por WhatsApp via Twilio (requiere env vars)')
    parser.add_argument('--imgsz', type=int, default=640, help='Tamaño de imagen para inferencia (default: 640, usar 416 o 320 para más FPS)')
    parser.add_argument('--skip_frames', type=int, default=0, help='Procesar 1 de cada N frames (0=todos, 1=la mitad, 2=un tercio, etc)')
    parser.add_argument('--tracker', default='bytetrack', choices=['simple', 'bytetrack'], 
                        help='Algoritmo de tracking: simple (IoU básico) o bytetrack (robusto, default)')
    args = parser.parse_args()
    main(args)

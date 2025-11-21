"""Demo principal: captura video, detección de personas, tracking simple, zonas y alertas.

Uso mínimo:
    python main.py --source 0
    python main.py --source video.mp4 --weights path/to/yolov11.pt
    python main.py --source screen  # Captura de pantalla

Notas:
- Proyecto preparado para CPU (no CUDA). Puedes suministrar tus pesos YOLOv11 si los tienes.
- Usa --source screen para capturar la pantalla completa
- Usa --source screen:1 para capturar un monitor específico
- Usa --source screen:region:x,y,w,h para capturar una región específica
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
from src.geometric_filter import GeometricFilter
from src.screen_capture import create_screen_source, list_monitors

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
    
    # Inicializar filtro geométrico avanzado
    geo_filter = GeometricFilter(
        min_time_in_zone=args.min_time_zone,
        min_bbox_area=args.min_bbox_area,
        min_confidence=args.conf,
        trajectory_length=10,
        min_movement_threshold=5.0
    )

    # Usar create_screen_source para soportar captura de pantalla y RTSP
    cap = create_screen_source(args.source, rtsp_transport=args.rtsp_transport, timeout=args.timeout)
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

    print('\n' + '='*60)
    print('SISTEMA DE DETECCIÓN DE INTRUSIONES ACTIVO')
    print('='*60)
    print(f'Modelo: {args.weights or "yolov8n.pt (default)"}')
    print(f'Tracker: {tracker_name}')
    print(f'Filtrado Geométrico: {"ACTIVADO" if args.use_geometric_filter else "DESACTIVADO"}')
    if args.use_geometric_filter:
        print(f'  └─ Tiempo mínimo en zona: {args.min_time_zone}s')
        print(f'  └─ Área mínima bbox: {args.min_bbox_area}px²')
    print(f'Tamaño de inferencia: {args.imgsz}px')
    print(f'Skip frames: {args.skip_frames} (0=procesar todos)')
    print(f'Zonas configuradas: {len(zones.zones)}')
    print(f'Umbral de confianza: {args.conf}')
    print(f'Alertas WhatsApp: {"SÍ" if args.use_whatsapp else "NO (solo local)"}')
    print('Presiona Q o ESC para salir')
    print('='*60 + '\n')

    # Contador de reconexiones para streams RTSP
    consecutive_failures = 0
    is_stream = str(args.source).lower().startswith(('rtsp://', 'http://'))

    while True:
        ret, frame = cap.read()
        if not ret:
            # Si es un stream, intentar reconexión
            if is_stream and consecutive_failures < args.max_retries:
                consecutive_failures += 1
                print(f'\n[WARNING] Frame perdido. Intento de reconexión {consecutive_failures}/{args.max_retries}...')
                cap.release()
                time.sleep(2)  # Esperar antes de reconectar
                cap = create_screen_source(args.source, rtsp_transport=args.rtsp_transport, timeout=args.timeout)
                if cap.isOpened():
                    print('[SUCCESS] Reconectado exitosamente')
                    consecutive_failures = 0
                    continue
                else:
                    print('[ERROR] Fallo en reconexión')
                    continue
            else:
                # Si no es stream o se agotaron los reintentos
                if is_stream:
                    print(f'\n[ERROR] Máximo de reintentos alcanzado ({args.max_retries}). Cerrando...')
                break
        else:
            # Reset del contador si se lee frame exitosamente
            consecutive_failures = 0
            
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
        active_track_ids = [t['track_id'] for t in tracks]
        
        for i, t in enumerate(tracks):
            bid = t['track_id']
            bbox = t['bbox']
            x, y = bbox_center(bbox)
            
            # Buscar confianza en las detecciones originales
            conf = t.get('conf', 0.0)
            if conf == 0.0:
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
                        break
            
            # 🔹 APLICAR FILTRADO GEOMÉTRICO AVANZADO
            is_valid_intrusion = False
            validation_result = None
            
            if args.use_geometric_filter:
                validation_result = geo_filter.validate_intrusion(
                    track_id=bid,
                    bbox=bbox,
                    confidence=conf,
                    center=(x, y),
                    is_in_zone=inside
                )
                is_valid_intrusion = validation_result['is_valid']
            else:
                # Sin filtrado, confiar directamente en "inside"
                is_valid_intrusion = inside
            
            # Marcar como en zona solo si pasa validación
            if is_valid_intrusion:
                current_in_zone.add(bid)
            
            # Color y label según estado
            if is_valid_intrusion:
                color = (0, 0, 255)  # Rojo si está en zona validada
                label = f'Person ({conf:.2f})'
            elif inside and args.use_geometric_filter:
                # En zona pero no validado (aún esperando tiempo o filtrado)
                color = (0, 165, 255)  # Naranja (BGR)
                label = f'Person ({conf:.2f}) - Validando...'
            else:
                color = (0, 255, 0)  # Verde si está fuera
                label = f'Person ({conf:.2f})'
            
            draw_bbox(frame, bbox, label=label, color=color, thickness=2)
            
            # Punto de tracking en el centro
            if is_valid_intrusion:
                point_color = (0, 0, 255)  # Rojo: intrusión validada
            elif inside and args.use_geometric_filter:
                point_color = (0, 165, 255)  # Naranja: en validación
            else:
                point_color = (0, 255, 255)  # Amarillo: seguro
            
            draw_tracking_point(frame, (x, y), bid, color=point_color)
            
            # Alerta solo si pasa validación geométrica
            if is_valid_intrusion:
                if alerts.alert_for_track(bid, f'⚠️ INTRUSION: Persona {bid} detectada en zona restringida', use_whatsapp=args.use_whatsapp):
                    total_alerts += 1

        tracks_in_zone = current_in_zone
        
        # Limpiar tracks antiguos del filtro geométrico
        if args.use_geometric_filter:
            geo_filter.cleanup_old_tracks(active_track_ids)
        
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
    
    print('\n' + '='*60)
    print('SISTEMA DETENIDO')
    print('='*60)
    print(f'Total de alertas enviadas: {total_alerts}')
    
    # Mostrar estadísticas del filtro geométrico
    if args.use_geometric_filter:
        filter_stats = geo_filter.get_statistics()
        print('\nEstadísticas de Filtrado Geométrico:')
        print(f'  Total detecciones procesadas: {filter_stats["total_detections"]}')
        print(f'  Filtradas por tamaño: {filter_stats["filtered_by_size"]}')
        print(f'  Filtradas por confianza: {filter_stats["filtered_by_confidence"]}')
        print(f'  Filtradas por tiempo insuficiente: {filter_stats["filtered_by_time"]}')
        print(f'  Filtradas por objeto estático: {filter_stats["filtered_by_movement"]}')
        print(f'  Intrusiones válidas: {filter_stats["valid_intrusions"]}')
        print(f'  Tasa de filtrado: {filter_stats["filter_rate"]:.1f}%')
    
    print('='*60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', default=0, 
                        help='Fuente de video: índice de cámara (0), ruta de video, o "screen" para captura de pantalla. '
                             'Ejemplos: 0, video.mp4, screen, screen:1, screen:region:100,100,800,600')
    parser.add_argument('--weights', default=None, help='Ruta a pesos YOLO (ej: yolov11.pt o yolov8n.pt)')
    parser.add_argument('--zones', default='zones.json', help='Archivo JSON con zonas')
    parser.add_argument('--conf', type=float, default=0.3, help='Umbral de confianza')
    parser.add_argument('--cooldown', type=int, default=10, help='Cooldown de alertas por track (s)')
    parser.add_argument('--use_whatsapp', action='store_true', help='Enviar alerta por WhatsApp via Twilio (requiere env vars)')
    parser.add_argument('--imgsz', type=int, default=640, help='Tamaño de imagen para inferencia (default: 640, usar 416 o 320 para más FPS)')
    parser.add_argument('--skip_frames', type=int, default=0, help='Procesar 1 de cada N frames (0=todos, 1=la mitad, 2=un tercio, etc)')
    parser.add_argument('--tracker', default='bytetrack', choices=['simple', 'bytetrack'], 
                        help='Algoritmo de tracking: simple (IoU básico) o bytetrack (robusto, default)')
    parser.add_argument('--list_monitors', action='store_true', 
                        help='Listar monitores disponibles y salir')
    
    # Parámetros de filtrado geométrico avanzado
    parser.add_argument('--use_geometric_filter', action='store_true', 
                        help='Activar filtrado geométrico avanzado (reduce falsos positivos 40%+)')
    parser.add_argument('--min_time_zone', type=float, default=2.0,
                        help='Tiempo mínimo (segundos) en zona antes de alertar (default: 2.0)')
    parser.add_argument('--min_bbox_area', type=int, default=2000,
                        help='Área mínima del bbox en píxeles para validar detección (default: 2000)')
    
    # Parámetros RTSP/IP Camera
    parser.add_argument('--rtsp_transport', default='tcp', choices=['tcp', 'udp'], 
                        help='Protocolo de transporte RTSP (tcp o udp, default: tcp)')
    parser.add_argument('--max_retries', type=int, default=10,
                        help='Intentos máximos de reconexión para streams RTSP (default: 10)')
    parser.add_argument('--timeout', type=int, default=10000,
                        help='Timeout en milisegundos para conexión RTSP (default: 10000)')
    
    args = parser.parse_args()
    
    # Si se solicita listar monitores
    if args.list_monitors:
        list_monitors()
        exit(0)
    
    main(args)

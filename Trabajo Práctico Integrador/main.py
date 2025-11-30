"""Demo principal: captura video, deteccion de personas, tracking, zonas y alertas.

Uso minimo:
    python main.py --source 0
    python main.py --source video.mp4 --weights path/to/yolov11.pt
    python main.py --source screen  # Captura de pantalla

Notas:
- Usa --source screen para capturar la pantalla completa
- Usa --source screen:1 para capturar un monitor especifico
- Usa --source screen:region:x,y,w,h para capturar una region especifica
"""
import argparse
import time

import cv2
import numpy as np

from src.alerts import Alerts
from src.detector import Detector
from src.geometric_filter import GeometricFilter
from src.overlay import (
    dibujar_bounding_box,
    dibujar_fps,
    dibujar_panel_estadisticas,
    dibujar_zona
)
from src.screen_capture import create_screen_source, list_monitors
from src.tracker import SimpleTracker
from src.utils import ContadorFPS
from src.zones import ZonesManager

# Importar ByteTrack si esta disponible
try:
    from src.bytetrack_wrapper import ByteTrackWrapper

    BYTETRACK_AVAILABLE = True
except ImportError:
    BYTETRACK_AVAILABLE = False
    print("[WARNING] ByteTrack no disponible. Usando SimpleTracker.")


def bbox_center(bbox):
    x1, y1, x2, y2 = bbox
    return int((x1 + x2) / 2), int((y1 + y2) / 2)


def bbox_zone_overlap_ratio(bbox, zone_mask):
    """Calcula el porcentaje de solapamiento del bbox con la mascara de zonas."""
    if zone_mask is None:
        return 0.0
    height, width = zone_mask.shape[:2]
    x1 = max(int(bbox[0]), 0)
    y1 = max(int(bbox[1]), 0)
    x2 = min(int(bbox[2]), width)
    y2 = min(int(bbox[3]), height)
    box_width = x2 - x1
    box_height = y2 - y1
    if box_width <= 0 or box_height <= 0:
        return 0.0
    bbox_area = float(box_width * box_height)
    zone_area = float(np.count_nonzero(zone_mask[y1:y2, x1:x2]))
    return zone_area / bbox_area if bbox_area > 0 else 0.0


def main(args):
    detector = Detector(weights=args.weights, device="cuda", conf_thres=args.conf, imgsz=args.imgsz)

    # Seleccionar tracker segun parametro
    if args.tracker == "bytetrack" and BYTETRACK_AVAILABLE:
        tracker = ByteTrackWrapper(
            track_activation_threshold=0.25,
            lost_track_buffer=30,
            minimum_matching_threshold=0.8,
            frame_rate=30,
        )
        tracker_name = "ByteTrack"
    else:
        tracker = SimpleTracker(iou_threshold=0.3)
        tracker_name = "SimpleTracker"
        if args.tracker == "bytetrack" and not BYTETRACK_AVAILABLE:
            print("[WARNING] ByteTrack solicitado pero no disponible. Usando SimpleTracker.")

    zones = ZonesManager(args.zones)
    zones.cargar()
    alerts = Alerts(cooldown_seconds=args.cooldown)
    fps_counter = ContadorFPS()

    # Inicializar filtro geometrico avanzado
    geo_filter = GeometricFilter(
        min_time_in_zone=args.min_time_zone,
        min_bbox_area=args.min_bbox_area,
        min_confidence=args.conf,
        trajectory_length=10,
        min_movement_threshold=2.0,
    )

    # Usar create_screen_source para soportar captura de pantalla y RTSP
    cap = create_screen_source(args.source, rtsp_transport=args.rtsp_transport, timeout=args.timeout)
    if not cap.isOpened():
        print("No se pudo abrir fuente:", args.source)
        return

    window_title = "Sistema de Deteccion de Intrusiones"
    cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)

    total_alerts = 0
    frame_count = 0
    last_dets = []
    last_tracks = []
    zone_mask = None

    print("\n" + "=" * 60)
    print("SISTEMA DE DETECCION DE INTRUSIONES ACTIVO")
    print("=" * 60)
    print(f"Modelo: {args.weights or 'yolov8n.pt (default)'}")
    print(f"Tracker: {tracker_name}")
    print(f"Filtrado Geometrico: {'ACTIVADO' if args.use_geometric_filter else 'DESACTIVADO'}")
    if args.use_geometric_filter:
        print(f"  - Tiempo minimo en zona: {args.min_time_zone}s")
        print(f"  - Area minima bbox: {args.min_bbox_area}px^2")
    print(f"Tamano de inferencia: {args.imgsz}px")
    print(f"Skip frames: {args.skip_frames} (0=procesar todos)")
    print(f"Zonas configuradas: {len(zones.zonas)}")
    print(f"Umbral de confianza: {args.conf}")
    print(f"Porcentaje minimo de solapamiento bbox/zona: {args.zone_overlap_ratio * 100:.0f}%")
    print(f"Alertas locales: SI (solo local)")
    print("Presiona Q o ESC para salir")
    print("=" * 60 + "\n")

    consecutive_failures = 0
    is_stream = str(args.source).lower().startswith(("rtsp://", "http://"))

    while True:
        ret, frame = cap.read()
        if not ret:
            # Si es un stream, intentar reconexion
            if is_stream and consecutive_failures < args.max_retries:
                consecutive_failures += 1
                print(f"\n[WARNING] Frame perdido. Intento de reconexion {consecutive_failures}/{args.max_retries}...")
                cap.release()
                time.sleep(2)
                cap = create_screen_source(args.source, rtsp_transport=args.rtsp_transport, timeout=args.timeout)
                if cap.isOpened():
                    print("[SUCCESS] Reconectado exitosamente")
                    consecutive_failures = 0
                    zone_mask = None
                    continue
                else:
                    print("[ERROR] Fallo en reconexion")
                    continue
            else:
                if is_stream:
                    print(f"\n[ERROR] Maximo de reintentos alcanzado ({args.max_retries}). Cerrando...")
                break
        else:
            consecutive_failures = 0

        fps_counter.registrar_tiempo()
        frame_count += 1

        # Construir mascara combinada de zonas (una sola vez segun tamano del frame)
        if zone_mask is None and zones.zonas:
            height, width = frame.shape[:2]
            zone_mask = np.zeros((height, width), dtype=np.uint8)
            for poly in zones.zonas:
                cv2.fillPoly(zone_mask, [np.array(poly, dtype=np.int32)], 255)

        # Optimizacion: skip frames para mejorar FPS
        if args.skip_frames > 0 and frame_count % (args.skip_frames + 1) != 0:
            detections = last_dets
            tracks = last_tracks
        else:
            detections = detector.detect(frame)
            last_dets = detections

            tracks = tracker.update(detections)
            last_tracks = tracks

        # Overlay de zonas con nombres personalizados
        for indice_zona, poly in enumerate(zones.zonas):
            zone_name = zones.obtener_nombre_zona(indice_zona)
            zone_color = (0, 0, 255)
            dibujar_zona(frame, poly, color=zone_color, zone_name=zone_name)

        current_in_zone = set()
        active_track_ids = [track["track_id"] for track in tracks]

        for track in tracks:
            track_id = track["track_id"]
            bbox = track["bbox"]
            center_x, center_y = bbox_center(bbox)

            # Buscar confianza en las detecciones originales
            confidence = track.get("conf", 0.0)
            if confidence == 0.0:
                for detection in detections:
                    det_bbox = detection["bbox"]
                    if abs(det_bbox[0] - bbox[0]) < 5 and abs(det_bbox[1] - bbox[1]) < 5:
                        confidence = detection["conf"]
                        break

            overlap_ratio = 0.0
            inside_zone = False
            if zones.zonas and zone_mask is not None:
                overlap_ratio = bbox_zone_overlap_ratio(bbox, zone_mask)
                inside_zone = overlap_ratio >= args.zone_overlap_ratio

            is_valid_intrusion = False
            validation_result = None

            if args.use_geometric_filter:
                validation_result = geo_filter.validate_intrusion(
                    track_id=track_id,
                    bbox=bbox,
                    confidence=confidence,
                    center=(center_x, center_y),
                    is_in_zone=inside_zone,
                )
                is_valid_intrusion = validation_result["is_valid"]
            else:
                is_valid_intrusion = inside_zone

            if is_valid_intrusion:
                current_in_zone.add(track_id)

            if is_valid_intrusion:
                color = (0, 0, 255)
                label = f"Person ({confidence:.2f})"
            elif inside_zone and args.use_geometric_filter:
                color = (0, 165, 255)
                label = f"Person ({confidence:.2f}) - Validando..."
            else:
                color = (0, 255, 0)
                label = f"Person ({confidence:.2f})"

            dibujar_bounding_box(frame, bbox, label, color, grosor=2)

            if is_valid_intrusion:
                if alerts.alert_for_track(
                    track_id,
                    f"[ALERTA] INTRUSION: Persona {track_id} detectada en zona restringida",
                ):
                    total_alerts += 1

        if args.use_geometric_filter:
            geo_filter.cleanup_old_tracks(active_track_ids)

        # Actualizar estado del flash visual segun presencia en zona
        alerts.set_flash_state(len(current_in_zone) > 0)

        dibujar_fps(frame, fps_counter.obtener_fps(), frame_number=frame_count)

        active_zones = sum(1 for _ in zones.zonas if len(current_in_zone) > 0)
        avg_detections = len(tracks)
        estadisticas = {
            "Fotograma": frame_count,
            "Zonas Activas": f"{active_zones}/{len(zones.zonas)}",
            "Total Zonas": len(zones.zonas),
            "Detecciones Prom": f"{avg_detections:.1f}",
        }
        dibujar_panel_estadisticas(frame, estadisticas, posicion="top-right")

        # Flash visual de alerta (punto rojo persistente tras una alerta)
        if alerts.should_flash():
            cv2.circle(frame, (35, 70), 20, (0, 0, 255), -1)
            cv2.circle(frame, (35, 70), 24, (0, 0, 255), 2)

        cv2.imshow(window_title, frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    print("\n" + "=" * 60)
    print("SISTEMA DETENIDO")
    print("=" * 60)
    print(f"Total de alertas enviadas: {total_alerts}")

    if args.use_geometric_filter:
        filter_stats = geo_filter.get_statistics()
        print("\nEstadisticas de Filtrado Geometrico:")
        print(f"  Total detecciones procesadas: {filter_stats['total_detections']}")
        print(f"  Filtradas por tamano: {filter_stats['filtered_by_size']}")
        print(f"  Filtradas por confianza: {filter_stats['filtered_by_confidence']}")
        print(f"  Filtradas por tiempo insuficiente: {filter_stats['filtered_by_time']}")
        print(f"  Filtradas por objeto estatico: {filter_stats['filtered_by_movement']}")
        print(f"  Intrusiones validas: {filter_stats['valid_intrusions']}")
        print(f"  Tasa de filtrado: {filter_stats['filter_rate']:.1f}%")

    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        default=0,
        help='Fuente de video: indice de camara (0), ruta de video, o "screen" para captura de pantalla. '
        "Ejemplos: 0, video.mp4, screen, screen:1, screen:region:100,100,800,600",
    )
    parser.add_argument("--weights", default=None, help="Ruta a pesos YOLO (ej: yolov11.pt o yolov8n.pt)")
    parser.add_argument("--zones", default="zonas.json", help="Archivo JSON con zonas")
    parser.add_argument("--conf", type=float, default=0.53, help="Umbral de confianza")
    parser.add_argument("--cooldown", type=int, default=10, help="Cooldown de alertas por track (s)")
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Tamano de imagen para inferencia (default: 640, usar 416 o 320 para mas FPS)",
    )
    parser.add_argument(
        "--skip_frames",
        type=int,
        default=0,
        help="Procesar 1 de cada N frames (0=todos, 1=la mitad, 2=un tercio, etc)",
    )
    parser.add_argument(
        "--tracker",
        default="bytetrack",
        choices=["simple", "bytetrack"],
        help="Algoritmo de tracking: simple (IoU basico) o bytetrack (robusto, default)",
    )
    parser.add_argument("--list_monitors", action="store_true", help="Listar monitores disponibles y salir")

    # Parametros de filtrado geometrico avanzado
    parser.add_argument(
        "--use_geometric_filter",
        action="store_true",
        help="Activar filtrado geometrico avanzado (reduce falsos positivos 40%+)",
    )
    parser.add_argument(
        "--min_time_zone",
        type=float,
        default=1.0,
        help="Tiempo minimo (segundos) en zona antes de alertar (default: 2.0)",
    )
    parser.add_argument(
        "--min_bbox_area",
        type=int,
        default=2000,
        help="Area minima del bbox en pixeles para validar deteccion (default: 2000)",
    )
    parser.add_argument(
        "--zone_overlap_ratio",
        type=float,
        default=0.30,
        help="Porcentaje minimo de solapamiento bbox/zona (0-1, default: 0.30)",
    )

    # Parametros RTSP/IP Camera
    parser.add_argument(
        "--rtsp_transport",
        default="tcp",
        choices=["tcp", "udp"],
        help="Protocolo de transporte RTSP (tcp o udp, default: tcp)",
    )
    parser.add_argument(
        "--max_retries", type=int, default=10, help="Intentos maximos de reconexion para streams RTSP (default: 10)"
    )
    parser.add_argument("--timeout", type=int, default=10000, help="Timeout en milisegundos para conexion RTSP (default: 10000)")

    arguments = parser.parse_args()

    if arguments.list_monitors:
        list_monitors()
        exit(0)

    main(arguments)

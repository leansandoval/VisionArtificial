"""
Dashboard Web para Sistema de Detección de Intrusiones.
NO modifica la lógica existente, solo la envuelve en una interfaz web.

Uso: python webapp/app.py
Acceso: http://localhost:5000
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
import os
import sys
import cv2
import base64
import threading
import time
import numpy as np
from pathlib import Path

# Importar módulos existentes SIN modificarlos
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.detector import Detector
from src.zonas import GestorZonas
from src.alertas import Alertas
from src.utils import ContadorFPS
from src.geometric_filter import GeometricFilter
from src.screen_capture import create_screen_source, list_monitors
from src.overlay import dibujar_bounding_box, dibujar_zona

# Importar trackers
try:
    from src.bytetrack_wrapper import ByteTrackWrapper
    BYTETRACK_AVAILABLE = True
except ImportError:
    BYTETRACK_AVAILABLE = False
    from src.tracker import SimpleTracker

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vision-artificial-2025-secret'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Deshabilitar caché
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Recargar templates automáticamente
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Caché global para nombres de cámaras y monitores
camera_names_cache = {}
camera_names_cache_time = 0
monitor_names_cache = {}
monitor_names_cache_time = 0

# Estado global del sistema
system_state = {
    'running': False,
    'paused': False,
    'cap': None,
    'detector': None,
    'tracker': None,
    'zones_manager': None,
    'alerts': None,
    'geo_filter': None,
    'fps_counter': None,
    'thread': None,
    'connected_clients': 0,  # Contador de clientes conectados
    'config': {
        'source_type': 'webcam',
        'source_value': '0',
        'rtsp_url': '',
        'rtsp_transport': 'tcp',
        'video_file': '',
        'screen_monitor': '0',
        'weights': 'yolov8n.pt',
        'conf': 0.4,
        'imgsz': 640,
        'skip_frames': 0,
        'tracker': 'bytetrack',
        'use_geometric_filter': True,
        'min_time_zone': 2.0,
        'min_bbox_area': 2000,
        'zone_overlap_ratio': 0.30,
        'cooldown': 10,
        'timeout': 10000,
        'max_retries': 3
    },
    'stats': {
        'fps': 0,
        'frame_count': 0,
        'detections': 0,
        'alerts': 0,
        'in_zone': 0,
        'filtered': 0,
        'tracks_active': 0
    }
}

def load_config():
    """Cargar configuración desde archivo"""
    config_path = Path(__file__).parent / 'config.json'
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                saved_config = json.load(f)
                system_state['config'].update(saved_config)
                print(f'✓ Configuración cargada desde {config_path}')
        except Exception as e:
            print(f'⚠ Error cargando configuración: {e}')

def save_config():
    """Guardar configuración a archivo"""
    config_path = Path(__file__).parent / 'config.json'
    try:
        with open(config_path, 'w') as f:
            json.dump(system_state['config'], f, indent=2)
        print(f'✓ Configuración guardada en {config_path}')
    except Exception as e:
        print(f'⚠ Error guardando configuración: {e}')

# ==================== RUTAS HTML ====================

@app.route('/')
def index():
    """Dashboard principal"""
    response = render_template('index.html', 
                         config=system_state['config'],
                         bytetrack_available=BYTETRACK_AVAILABLE)
    return response

@app.route('/settings')
def settings():
    """Página de configuración"""
    response = render_template('settings.html', 
                         config=system_state['config'],
                         bytetrack_available=BYTETRACK_AVAILABLE)
    return response

@app.route('/zones')
def zones_editor():
    """Editor de zonas"""
    zm = GestorZonas()
    zm.cargar()
    return render_template('zones.html', 
                         zones=zm.zonas, 
                         zone_names=zm.nombres_zonas,
                         config=system_state['config'])

# ==================== API ENDPOINTS ====================

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """Obtener o actualizar configuración"""
    if request.method == 'GET':
        return jsonify(system_state['config'])
    
    elif request.method == 'POST':
        new_config = request.json
        system_state['config'].update(new_config)
        save_config()
        return jsonify({'status': 'ok', 'config': system_state['config']})

@app.route('/api/zones', methods=['GET', 'POST'])
def api_zones():
    """Gestionar zonas"""
    zm = GestorZonas()
    
    if request.method == 'GET':
        zm.cargar()
        return jsonify({'zones': zm.zonas, 'zone_names': zm.nombres_zonas})
    
    elif request.method == 'POST':
        data = request.json
        zm.zonas = data.get('zones', [])
        zm.nombres_zonas = data.get('zone_names', [])
        zm.guardar()
        
        # Recargar zonas si el sistema está corriendo
        if system_state['running'] and system_state['zones_manager']:
            system_state['zones_manager'].cargar()
        
        return jsonify({'status': 'ok'})

@app.route('/api/status')
def api_status():
    """Estado del sistema"""
    return jsonify({
        'running': system_state['running'],
        'paused': system_state['paused'],
        'stats': system_state['stats']
    })

@app.route('/api/monitors')
def api_monitors():
    """Listar monitores disponibles"""
    global monitor_names_cache, monitor_names_cache_time
    
    try:
        import mss
        import platform
        import subprocess
        
        # Usar caché de nombres si tiene menos de 30 segundos
        current_time = time.time()
        use_cache = (current_time - monitor_names_cache_time) < 30
        
        monitor_names = {}
        
        if use_cache and monitor_names_cache:
            print("[Monitors] Usando nombres en caché:", monitor_names_cache)
            monitor_names = monitor_names_cache.copy()
        elif platform.system() == 'Windows':
            try:
                # Obtener nombres de monitores usando PowerShell
                ps_command = r'''
                Get-CimInstance -Namespace root\wmi -ClassName WmiMonitorID | ForEach-Object {
                    $name = ($_.UserFriendlyName | Where-Object { $_ -ne 0 }) -join '' | ForEach-Object { [char]$_ }
                    if ($name) { $name } else { "Monitor" }
                }
                '''
                
                result = subprocess.run(
                    ['powershell', '-Command', ps_command],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    names = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
                    # Asignar nombres a índices (índice 0 es "all monitors" en mss)
                    for i, name in enumerate(names, start=1):
                        monitor_names[i] = name
                    print("[Monitors] Nombres detectados:", monitor_names)
                    
                    # Actualizar caché
                    monitor_names_cache = monitor_names.copy()
                    monitor_names_cache_time = current_time
                    
            except subprocess.TimeoutExpired:
                print("[Monitors] PowerShell timeout - usando caché si existe")
                if monitor_names_cache:
                    monitor_names = monitor_names_cache.copy()
            except Exception as e:
                print(f"[Monitors] Error al obtener nombres: {e}")
        
        # Obtener información de monitores con mss
        with mss.mss() as sct:
            monitors = []
            for i, mon in enumerate(sct.monitors):
                # Índice 0 es "all monitors", no lo incluimos en la lista
                if i == 0:
                    continue
                    
                # Construir nombre descriptivo
                if i in monitor_names and monitor_names[i] and monitor_names[i].strip() != "Monitor":
                    # Usar nombre detectado si es específico (no genérico "Monitor")
                    name = f"{monitor_names[i]} - {mon['width']}x{mon['height']}"
                else:
                    # Distinguir por Principal/Secundario si no hay nombre específico
                    if i == 1:
                        name = f"Monitor {i} (Principal) - {mon['width']}x{mon['height']}"
                    else:
                        name = f"Monitor {i} (Secundario) - {mon['width']}x{mon['height']}"
                
                monitors.append({
                    'index': i,
                    'name': name,
                    'width': mon['width'],
                    'height': mon['height'],
                    'left': mon['left'],
                    'top': mon['top']
                })
        
        return jsonify({'monitors': monitors})
    except Exception as e:
        print(f"[Monitors] Error general: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cameras')
def api_cameras():
    """Listar cámaras disponibles"""
    global camera_names_cache, camera_names_cache_time
    
    try:
        import platform
        cameras = []
        max_cameras_to_test = 3
        
        # Usar caché de nombres si tiene menos de 30 segundos
        current_time = time.time()
        use_cache = (current_time - camera_names_cache_time) < 30
        
        camera_names = {}
        if platform.system() == 'Windows':
            if use_cache and camera_names_cache:
                camera_names = camera_names_cache.copy()
                print(f'[Cameras] Usando nombres en caché: {camera_names}')
            else:
                try:
                    import subprocess
                    # Timeout más largo (5 segundos) para dar tiempo a PowerShell
                    result = subprocess.run(
                        ['powershell', '-Command', 
                         'Get-PnpDevice -Class Camera -Status OK | Select-Object -ExpandProperty FriendlyName'],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        names = result.stdout.strip().split('\n')
                        for idx, name in enumerate(names):
                            if name.strip():
                                camera_names[idx] = name.strip()
                        # Guardar en caché
                        camera_names_cache = camera_names.copy()
                        camera_names_cache_time = current_time
                        print(f'[Cameras] Nombres detectados y guardados en caché: {camera_names}')
                except subprocess.TimeoutExpired:
                    print('[Cameras] Timeout en PowerShell, usando caché anterior si existe')
                    if camera_names_cache:
                        camera_names = camera_names_cache.copy()
                except Exception as e:
                    print(f'[Cameras] Error obteniendo nombres: {e}')
                    if camera_names_cache:
                        camera_names = camera_names_cache.copy()
        
        # Probar cámaras
        consecutive_failures = 0
        for index in range(max_cameras_to_test):
            try:
                cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        fps = int(cap.get(cv2.CAP_PROP_FPS))
                        
                        # Usar el nombre obtenido si existe, sino usar genérico
                        camera_name = camera_names.get(index, f'Cámara {index}')
                        
                        camera_info = {
                            'index': index,
                            'name': camera_name,
                            'resolution': f'{width}x{height}',
                            'fps': fps if fps > 0 else 'N/A',
                            'backend': 'DirectShow'
                        }
                        
                        cameras.append(camera_info)
                        consecutive_failures = 0
                    else:
                        consecutive_failures += 1
                    cap.release()
                else:
                    consecutive_failures += 1
                    
                if consecutive_failures >= 2:
                    break
                    
            except Exception as e:
                print(f'[Cameras] Error probando cámara {index}: {e}')
                consecutive_failures += 1
                if consecutive_failures >= 2:
                    break
        
        print(f'[Cameras] Detección completada: {len(cameras)} cámara(s) encontrada(s)')
        return jsonify({'cameras': cameras})
        
    except Exception as e:
        print(f'[Error] Listando cámaras: {e}')
        return jsonify({'error': str(e)}), 500

# ==================== WEBSOCKET EVENTS ====================

@socketio.on('connect')
def handle_connect():
    """Cliente conectado"""
    system_state['connected_clients'] += 1
    print(f'[WebSocket] Cliente conectado (Total: {system_state["connected_clients"]})')
    emit('status', {
        'running': system_state['running'],
        'paused': system_state['paused'],
        'stats': system_state['stats']
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectado"""
    session_id = request.sid
    
    # Detener stream de zonas si existe
    if session_id in zones_stream_active:
        zones_stream_active[session_id] = False
        print(f'[Zones] Stream detenido por desconexión: {session_id}')
    
    system_state['connected_clients'] -= 1
    print(f'[WebSocket] Cliente desconectado (Restantes: {system_state["connected_clients"]})')
    
    # Si no quedan clientes conectados y el sistema está corriendo, detenerlo
    if system_state['connected_clients'] <= 0 and system_state['running']:
        print('[Sistema] No hay clientes conectados. Deteniendo sistema automáticamente...')
        system_state['running'] = False
        system_state['paused'] = False
        
        # Limpiar recursos
        if system_state['cap']:
            system_state['cap'].release()
            system_state['cap'] = None
        
        print('[Sistema] Sistema detenido por desconexión de clientes')

@socketio.on('start_detection')
def handle_start():
    """Iniciar detección o reanudar si está pausado"""
    if not system_state['running']:
        # Sistema detenido: iniciar
        print('[Sistema] Iniciando detección...')
        system_state['running'] = True
        system_state['paused'] = False
        
        # Iniciar thread de detección
        thread = threading.Thread(target=run_detection, daemon=True)
        system_state['thread'] = thread
        thread.start()
        
        socketio.emit('status', {'running': True, 'paused': False})
        socketio.emit('log', {'message': '✓ Sistema iniciado', 'level': 'success'})
    elif system_state['paused']:
        # Sistema pausado: reanudar
        print('[Sistema] Reanudando detección...')
        system_state['paused'] = False
        socketio.emit('status', {'running': True, 'paused': False})
        socketio.emit('log', {'message': '✓ Sistema reanudado', 'level': 'success'})
    else:
        emit('log', {'message': '⚠ Sistema ya está corriendo', 'level': 'warning'})

@socketio.on('stop_detection')
def handle_stop():
    """Detener detección"""
    if system_state['running']:
        print('[Sistema] Deteniendo detección...')
        system_state['running'] = False
        system_state['paused'] = False
        
        # Liberar recursos
        if system_state['cap']:
            system_state['cap'].release()
            system_state['cap'] = None
        
        socketio.emit('status', {'running': False, 'paused': False})
        socketio.emit('log', {'message': '✓ Sistema detenido', 'level': 'info'})
    else:
        emit('log', {'message': '⚠ Sistema no está corriendo', 'level': 'warning'})

@socketio.on('pause_detection')
def handle_pause():
    """Pausar/reanudar detección"""
    if system_state['running']:
        system_state['paused'] = not system_state['paused']
        status = 'pausado' if system_state['paused'] else 'reanudado'
        print(f'[Sistema] {status.capitalize()}')
        socketio.emit('status', {'paused': system_state['paused']})
        socketio.emit('log', {'message': f'✓ Sistema {status}', 'level': 'info'})

# ==================== LÓGICA DE DETECCIÓN ====================

def bbox_center(b):
    """Calcular centro de bbox"""
    x1, y1, x2, y2 = b
    return int((x1+x2)/2), int((y1+y2)/2)


def bbox_zone_overlap_ratio(bbox, zone_mask):
    """Calcula el porcentaje de solapamiento del bbox con la mascara de zonas.

    Devuelve un float entre 0.0 y 1.0.
    """
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

def run_detection():
    """
    Ejecuta la detección usando TU CÓDIGO EXISTENTE.
    NO modifica la lógica, solo la adapta para streaming web.
    """
    try:
        config = system_state['config']
        
        # Inicializar componentes
        print(f'[Detector] Cargando modelo {config["weights"]}...')
        system_state['detector'] = Detector(
            pesos=config['weights'],
            umbral_confianza=config['conf'],
            tam_imagen=config['imgsz']
        )
        
        # Inicializar tracker
        if config['tracker'] == 'bytetrack' and BYTETRACK_AVAILABLE:
            system_state['tracker'] = ByteTrackWrapper(
                track_activation_threshold=0.25,
                lost_track_buffer=30,
                minimum_matching_threshold=0.8,
                frame_rate=30
            )
            tracker_name = 'ByteTrack'
        else:
            system_state['tracker'] = SimpleTracker(iou_threshold=0.3)
            tracker_name = 'SimpleTracker'
        
        print(f'[Tracker] {tracker_name} inicializado')
        
        # Inicializar zonas
        system_state['zones_manager'] = GestorZonas()
        system_state['zones_manager'].cargar()
        print(f'[Zonas] {len(system_state["zones_manager"].zonas)} zona(s) cargada(s)')
        
        # Inicializar alertas
        system_state['alerts'] = Alertas(segundos_espera=config['cooldown'])
        
        # Inicializar filtro geométrico
        if config['use_geometric_filter']:
            system_state['geo_filter'] = GeometricFilter(
                min_time_in_zone=config['min_time_zone'],
                min_bbox_area=config['min_bbox_area'],
                min_confidence=config['conf'],
                trajectory_length=10,
                min_movement_threshold=5.0
            )
            print('[Filtro] Filtrado geométrico activado')
        
        # Inicializar FPS counter
        system_state['fps_counter'] = ContadorFPS()
        
        # Determinar source
        source_type = config['source_type']
        if source_type == 'webcam':
            source = int(config['source_value'])
        elif source_type == 'rtsp':
            source = config['rtsp_url']
        elif source_type == 'video':
            source = config['video_file']
        elif source_type == 'screen':
            monitor = config.get('screen_monitor', '0')
            source = f'screen:{monitor}' if monitor != '0' else 'screen'
        else:
            source = 0
        
        print(f'[Source] Abriendo: {source}')
        
        # Crear captura de video
        if source_type == 'rtsp':
            system_state['cap'] = create_screen_source(
                source,
                rtsp_transport=config.get('rtsp_transport', 'tcp'),
                timeout=config.get('timeout', 10000)
            )
        else:
            system_state['cap'] = create_screen_source(source)
        
        if not system_state['cap'].isOpened():
            socketio.emit('log', {'message': f'✗ Error: No se pudo abrir {source}', 'level': 'error'})
            system_state['running'] = False
            return
        
        print('[Sistema] ✓ Detección iniciada')
        socketio.emit('log', {'message': '✓ Sistema operativo', 'level': 'success'})
        
        # Variables de procesamiento
        frame_count = 0
        last_dets = []
        last_tracks = []
        total_alerts = 0
        zone_mask = None
        last_zone_count = 0
        
        # Loop principal
        while system_state['running']:
            if system_state['paused']:
                time.sleep(0.1)
                continue
            
            ret, frame = system_state['cap'].read()
            if not ret:
                print('[Source] Frame perdido o fin del video')
                if source_type in ['video', 'rtsp']:
                    # Intentar reconexión para streams
                    time.sleep(1)
                    continue
                else:
                    break
            
            system_state['fps_counter'].registrar_tiempo()
            frame_count += 1

            # Construir/reconstruir máscara combinada de zonas según tamaño del frame
            if (zone_mask is None) or (zone_mask.shape[0] != frame.shape[0]) or (zone_mask.shape[1] != frame.shape[1]) or (last_zone_count != len(system_state['zones_manager'].zonas)):
                if system_state['zones_manager'].zonas:
                    height, width = frame.shape[:2]
                    zone_mask = np.zeros((height, width), dtype=np.uint8)
                    for poly in system_state['zones_manager'].zonas:
                        cv2.fillPoly(zone_mask, [np.array(poly, dtype=np.int32)], 255)
                    last_zone_count = len(system_state['zones_manager'].zonas)
                else:
                    zone_mask = None
                    last_zone_count = 0
            
            # Skip frames según configuración
            if config['skip_frames'] > 0 and frame_count % (config['skip_frames'] + 1) != 0:
                dets = last_dets
                tracks = last_tracks
            else:
                # Detectar personas
                dets = system_state['detector'].detectar(frame)
                last_dets = dets
                
                # Tracking
                tracks = system_state['tracker'].update(dets)
                last_tracks = tracks
            
            # Dibujar zonas
            for zone_idx, poly in enumerate(system_state['zones_manager'].zonas):
                zone_name = system_state['zones_manager'].obtener_nombre_zona(zone_idx)
                dibujar_zona(frame, poly, color=(0, 0, 255), zone_name=zone_name)
            
            # Procesar tracks
            current_in_zone = set()
            active_track_ids = [t['track_id'] for t in tracks]
            filtered_count = 0
            
            for t in tracks:
                bid = t['track_id']
                bbox = t['bbox']
                x, y = bbox_center(bbox)
                
                # Buscar confianza
                conf = t.get('conf', 0.0)
                if conf == 0.0:
                    for d in dets:
                        db = d['bbox']
                        if abs(db[0]-bbox[0]) < 5 and abs(db[1]-bbox[1]) < 5:
                            conf = d['conf']
                            break
                
                # Verificar zona usando solapamiento bbox/mascara de zonas (más eficiente que pointPolygonTest)
                inside = False
                if system_state['zones_manager'].zonas and zone_mask is not None:
                    overlap_ratio = bbox_zone_overlap_ratio(bbox, zone_mask)
                    inside = overlap_ratio >= config.get('zone_overlap_ratio', 0.30)
                
                # Filtrado geométrico
                is_valid_intrusion = False
                if config['use_geometric_filter'] and system_state['geo_filter']:
                    validation_result = system_state['geo_filter'].validate_intrusion(
                        track_id=bid,
                        bbox=bbox,
                        confidence=conf,
                        center=(x, y),
                        is_in_zone=inside
                    )
                    is_valid_intrusion = validation_result['is_valid']
                    if not is_valid_intrusion and inside:
                        filtered_count += 1
                else:
                    is_valid_intrusion = inside
                
                if is_valid_intrusion:
                    current_in_zone.add(bid)
                
                # Color según estado
                if is_valid_intrusion:
                    color = (0, 0, 255)  # Rojo
                    label = f'ID:{bid} ({conf:.2f})'
                elif inside and config['use_geometric_filter']:
                    color = (0, 165, 255)  # Naranja
                    label = f'ID:{bid} ({conf:.2f}) - Validando'
                else:
                    color = (0, 255, 0)  # Verde
                    label = f'ID:{bid} ({conf:.2f})'
                
                dibujar_bounding_box(frame, bbox, label=label, color=color, grosor=2)
                
                # tracking point removed to match CLI visuals (only bounding box + flash)
                
                # Alertas
                if is_valid_intrusion and system_state['alerts']:
                    if system_state['alerts'].alertar_por_track(
                        bid,
                        f'⚠️ INTRUSION: Persona {bid} en zona'
                    ):
                        total_alerts += 1
                        socketio.emit('alert', {
                            'track_id': bid,
                            'message': f'Persona {bid} detectada en zona restringida'
                        })
            
            # Limpiar tracks antiguos
            if config['use_geometric_filter'] and system_state['geo_filter']:
                system_state['geo_filter'].cleanup_old_tracks(active_track_ids)
            
            # Actualizar estado del flash visual segun presencia en zona (coincide con CLI)
            if system_state.get('alerts'):
                system_state['alerts'].establecer_estado_flash(len(current_in_zone) > 0)

            # Actualizar estadísticas
            system_state['stats']['fps'] = round(system_state['fps_counter'].obtener_fps(), 1)
            system_state['stats']['frame_count'] = frame_count
            system_state['stats']['detections'] = len(dets)
            system_state['stats']['alerts'] = total_alerts
            system_state['stats']['in_zone'] = len(current_in_zone)
            system_state['stats']['filtered'] = filtered_count
            system_state['stats']['tracks_active'] = len(tracks)
            
            # Convertir frame a JPEG para streaming
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Emitir frame y stats vía WebSocket
            socketio.emit('video_frame', {
                'frame': frame_base64,
                'stats': system_state['stats']
            })
            
            # Control de framerate
            time.sleep(0.01)
        
    except Exception as e:
        print(f'[Error] {e}')
        import traceback
        traceback.print_exc()
        socketio.emit('log', {'message': f'✗ Error: {str(e)}', 'level': 'error'})
    
    finally:
        # Limpiar recursos
        if system_state['cap']:
            system_state['cap'].release()
            system_state['cap'] = None
        system_state['running'] = False
        print('[Sistema] Detección finalizada')
        socketio.emit('status', {'running': False})

# ==================== STREAM DE VIDEO PARA EDITOR DE ZONAS ====================

zones_stream_active = {}  # Diccionario para controlar streams por sesión

@socketio.on('start_zones_stream')
def handle_start_zones_stream():
    """Inicia stream de video continuo para el editor de zonas"""
    session_id = request.sid
    
    if session_id in zones_stream_active and zones_stream_active[session_id]:
        print(f'[Zones] Stream ya activo para sesión {session_id}')
        return
    
    zones_stream_active[session_id] = True
    
    def stream_worker():
        try:
            config = system_state['config']
            
            # Determinar source
            source_type = config['source_type']
            if source_type == 'webcam':
                source = int(config['source_value'])
            elif source_type == 'rtsp':
                source = config['rtsp_url']
            elif source_type == 'video':
                source = config['video_file']
            elif source_type == 'screen':
                monitor = config.get('screen_monitor', '1')
                source = f'screen:{monitor}'
            else:
                source = 0
            
            print(f'[Zones] Iniciando stream desde: {source}')
            
            # Crear captura
            if source_type == 'rtsp':
                cap = create_screen_source(
                    source,
                    rtsp_transport=config.get('rtsp_transport', 'tcp'),
                    timeout=config.get('timeout', 10000)
                )
            else:
                cap = create_screen_source(source)
            
            if not cap.isOpened():
                socketio.emit('stream_error', {'message': 'No se pudo abrir la fuente de video'}, room=session_id)
                zones_stream_active[session_id] = False
                return
            
            print(f'[Zones] Stream activo para sesión {session_id}')
            
            while zones_stream_active.get(session_id, False):
                ret, frame = cap.read()
                
                if not ret or frame is None:
                    break
                
                # Convertir a JPEG y codificar en base64
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # Enviar frame
                socketio.emit('video_frame', {
                    'frame': frame_base64,
                    'width': frame.shape[1],
                    'height': frame.shape[0]
                }, room=session_id)
                
                # Control de frame rate (~15 FPS)
                socketio.sleep(0.066)
            
            cap.release()
            print(f'[Zones] Stream detenido para sesión {session_id}')
            
        except Exception as e:
            print(f'[Error] Stream de zonas: {e}')
            import traceback
            traceback.print_exc()
            socketio.emit('stream_error', {'message': f'Error en stream: {str(e)}'}, room=session_id)
        finally:
            zones_stream_active[session_id] = False
    
    # Iniciar thread de streaming
    socketio.start_background_task(stream_worker)

@socketio.on('stop_zones_stream')
def handle_stop_zones_stream():
    """Detiene el stream de video para el editor de zonas"""
    session_id = request.sid
    if session_id in zones_stream_active:
        zones_stream_active[session_id] = False
        print(f'[Zones] Solicitado detener stream para sesión {session_id}')

# ==================== CAPTURA DE FRAME PARA EDITOR DE ZONAS (LEGACY) ====================

@socketio.on('capture_background')
def handle_capture_background():
    """Captura un frame de la fuente configurada para usar como fondo del editor de zonas"""
    try:
        config = system_state['config']
        
        # Determinar source
        source_type = config['source_type']
        if source_type == 'webcam':
            source = int(config['source_value'])
        elif source_type == 'rtsp':
            source = config['rtsp_url']
        elif source_type == 'video':
            source = config['video_file']
        elif source_type == 'screen':
            monitor = config.get('screen_monitor', '0')
            source = f'screen:{monitor}' if monitor != '0' else 'screen'
        else:
            source = 0
        
        print(f'[Zones] Capturando frame de fondo desde: {source}')
        
        # Crear captura temporal
        if source_type == 'rtsp':
            cap = create_screen_source(
                source,
                rtsp_transport=config.get('rtsp_transport', 'tcp'),
                timeout=config.get('timeout', 10000)
            )
        else:
            cap = create_screen_source(source)
        
        if not cap.isOpened():
            emit('background_error', {'message': 'No se pudo abrir la fuente de video'})
            return
        
        # Capturar frame
        ret, frame = cap.read()
        cap.release()
        
        if not ret or frame is None:
            emit('background_error', {'message': 'No se pudo capturar frame'})
            return
        
        # Convertir a JPEG y codificar en base64
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Enviar frame de fondo
        emit('background_frame', {
            'frame': frame_base64,
            'width': frame.shape[1],
            'height': frame.shape[0]
        })
        print(f'[Zones] Frame capturado: {frame.shape[1]}x{frame.shape[0]}')
        
    except Exception as e:
        print(f'[Error] Captura de fondo: {e}')
        import traceback
        traceback.print_exc()
        emit('background_error', {'message': f'Error al capturar: {str(e)}'})

# ==================== INICIO ====================

if __name__ == '__main__':
    # Cargar configuración guardada
    load_config()
    
    print('='*70)
    print('🌐 DASHBOARD WEB - Sistema de Detección de Intrusiones')
    print('='*70)
    print(f'📡 Servidor: http://localhost:5000')
    print(f'📊 Dashboard: http://localhost:5000/')
    print(f'⚙️  Configuración: http://localhost:5000/settings')
    print(f'🗺️  Editor de Zonas: http://localhost:5000/zones')
    print(f'🔧 ByteTrack: {"✓ Disponible" if BYTETRACK_AVAILABLE else "✗ No disponible"}')
    print('='*70)
    print('Presiona Ctrl+C para detener el servidor\n')
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print('\n[Sistema] Servidor detenido por el usuario')

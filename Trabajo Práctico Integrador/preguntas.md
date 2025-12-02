# Preguntas TP Vision Artificial

## Como se realiza el calculo de la deteccion de la persona?
Con el modelo YOLO (yolov8n.pt) sobre cada frame se evalua el umbral de confianza predefinido y tamaño de la "persona detectada" a traves de cordenadas de bbox y el filtrado geometrico, devolviendo bounding boxes con su conf.

## Que es el filtrado geometrico?
- Calcula ancho y alto del bbox (width = x2 - x1, height = y2 - y1) y su área (area = width * height).
- Si el área es menor a min_bbox_area (default 2000 px²), descarta la detección si es demasiado pequeña y suma a las estadísticas de filtrado.
- min_movement_threshold está en píxeles de la imagen: es el desplazamiento acumulado (distancia euclídea) del centro del bbox a lo largo de la trayectoria reciente. Si la suma de ese movimiento es menor a ese valor, el filtro lo considera estático. Ajusta según tu escala: 2 px es muy permisivo (acepta movimientos mínimos), valores mayores exigen más desplazamiento para no ser filtrado.

## Como armamos el dataset?
No tenemos dataset porque usamos un modelo preentrenado de YOLO

## Como nos basamos para crear el poligo (zona)
- Cada clic se guarda como coordenadas de píxel (x, y) sobre el frame que ves, en la resolución actual de la fuente.
- Al cerrar o pulsar s, esos vértices se almacenan como listas de puntos en el JSON (zones.json/zonas.json) vía ZonesManager. No hay normalización ni proporciones: son valores absolutos en píxeles.
- Luego, en main.py, se reconstruye una máscara con esos mismos puntos sobre cada frame (usando el tamaño del frame en ese momento) y se calcula el solapamiento de los bboxes con esa máscara.

## Como manejamos los falsos positivos
Se descartan y no se evaluan, solo se evaluan los que pasen el filtro geometrico.

## Como se concidera que una persona esta dentro de la zona? es decir que pase a rojo la box?
Solapamiento con la zona: se construye una máscara de las zonas y se calcula bbox_zone_overlap_ratio (porcentaje de área del bbox que cae dentro de la máscara). Si supera --zone_overlap_ratio (ej. 0.30), se considera “en zona”.
+ filtro geometrico

## Cuantos frames son necesarios para que el modelo detecte la persona?

## Se utiliza openCV?
Sí. El proyecto usa OpenCV (cv2) en todo el pipeline: lectura de video/captura de pantalla (create_screen_source), dibujo de zonas/bounding boxes/FPS (overlay.py), herramienta de zonas (zones_tool.py) y la propia inferencia/visualización en main.py.

## Que hace el bytetrack?
ByteTrack es un tracker multi‑objeto basado en detecciones cuadro a cuadro. Usa matching por IoU/score entre detecciones consecutivas (incluye las de baja confianza) para mantener IDs estables, manejar oclusiones cortas y reducir cambios de identidad. En este proyecto, si seleccionas --tracker bytetrack, sustituye al SimpleTracker para seguir personas de forma más robusta.

## Parámetros configurables en tu TP (los que expone main.py):
--source (default 0): cámara, archivo o captura de pantalla (screen, screen:N, screen:region:x,y,w,h, RTSP).
--weights (default None, usa yolov8n.pt): ruta a los pesos YOLO.
--zones (default zones.json): archivo JSON con las zonas.
--conf (default 0.5): umbral de confianza para detecciones.
--cooldown (default 10): segundos de enfriamiento por track entre alertas.
--use_whatsapp (flag): envía alerta por WhatsApp vía Twilio (si está configurado).
--imgsz (default 640): tamaño de inferencia (reduce para más FPS).
--skip_frames (default 0): procesa 1 de cada N+1 frames.
--tracker (default bytetrack, opciones simple/bytetrack): algoritmo de tracking.
--list_monitors (flag): lista monitores y sale.
--use_geometric_filter (flag): activa filtrado geométrico avanzado.
--min_time_zone (default 2.0): tiempo mínimo en zona antes de alertar.
--min_bbox_area (default 2000): área mínima del bbox.
--zone_overlap_ratio (default 0.30): porcentaje mínimo de solapamiento bbox/zona.
--rtsp_transport (default tcp, opciones tcp/udp): transporte RTSP.
--max_retries (default 10): reintentos de reconexión RTSP.
--timeout (default 10000): timeout RTSP en ms.
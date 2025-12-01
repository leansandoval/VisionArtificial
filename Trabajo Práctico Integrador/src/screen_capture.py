# Módulo de captura de pantalla para usar como fuente de video.
# Compatible con la interfaz de cv2.VideoCapture para integración transparente.
import cv2
import mss
import numpy as np
import time

LIMITE_FPS_POR_DEFECTO = 30  # Límite de FPS para captura de pantalla
TIMEOUT_RTSP_DEFECTO = 10000  # Timeout por defecto para RTSP en ms

# Clase que captura la pantalla y la presenta como fuente de video.
# Compatible con la interfaz de cv2.VideoCapture.
class ScreenCapture:

    """
    Inicializa el capturador de pantalla.
    Args:   indice_monitor (int): Índice del monitor a capturar (1 = principal)
            region (dict): Región específica {'left': x, 'top': y, 'width': w, 'height': h}
            limite_fps (int): Límite de FPS para la captura (0 = sin límite)
    """
    def __init__(self, indice_monitor=1, region=None, limite_fps=LIMITE_FPS_POR_DEFECTO):
        self.sct = mss.mss()
        self.indice_monitor = indice_monitor
        self.region = region
        self.limite_fps = limite_fps
        self._esta_abierto = True
        self._tiempo_frame = 1.0 / limite_fps if limite_fps > 0 else 0
        self._ultimo_tiempo_captura = 0
        # Obtener información del monitor
        if region is None:
            self.monitor = self.sct.monitors[indice_monitor]
        else:
            self.monitor = region
        print(f"[ScreenCapture] Inicializado")
        print(f"  - Monitor: {indice_monitor}")
        print(f"  - Región: {self.monitor}")
        print(f"  - FPS Límite: {limite_fps if limite_fps > 0 else 'Sin límite'}")
    
    def isOpened(self):
        return self._esta_abierto
    
    # Lee un frame de la pantalla.
    # Returns: tuple: (success, frame) donde success es bool y frame es numpy array
    def read(self):
        if not self._esta_abierto:
            return False, None
        try:
            # Controlar FPS si está configurado
            if self.limite_fps > 0:
                tiempo_actual = time.time()
                transcurrido = tiempo_actual - self._ultimo_tiempo_captura
                if transcurrido < self._tiempo_frame:
                    tiempo_espera = self._tiempo_frame - transcurrido
                    time.sleep(tiempo_espera)
                self._ultimo_tiempo_captura = time.time()
            # Capturar pantalla
            captura = self.sct.grab(self.monitor)
            # Convertir a formato OpenCV (BGR)
            frame = np.array(captura)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            return True, frame
        except Exception as e:
            print(f"[ScreenCapture ERROR] {e}")
            return False, None
    
    # Libera los recursos de captura
    def release(self):
        self._esta_abierto = False
        if self.sct:
            self.sct.close()
        print("[ScreenCapture] Liberado")
    
    # Obtiene propiedades del video (compatible con cv2.VideoCapture).        
    # Args: propId: ID de la propiedad (cv2.CAP_PROP_*)
    def get(self, propId):
        if propId == cv2.CAP_PROP_FRAME_WIDTH:
            return self.monitor.get('width', 1920)
        elif propId == cv2.CAP_PROP_FRAME_HEIGHT:
            return self.monitor.get('height', 1080)
        elif propId == cv2.CAP_PROP_FPS:
            return self.limite_fps if self.limite_fps > 0 else 30
        else:
            return 0
    
    # Establece propiedades del video (compatible con cv2.VideoCapture).
    # Args: propId: ID de la propiedad (cv2.CAP_PROP_*), value: valor a establecer
    def set(self, propId, value):
        return False

"""
Factory function para crear fuente de captura.
Retorna ScreenCapture si argumento_fuente es 'screen', sino cv2.VideoCapture normal.

Args:
    argumento_fuente: Argumento de fuente ('screen', 'screen:1', '0', 'video.mp4', 'rtsp://...', etc.)
    transporte_rtsp: Protocolo de transporte para RTSP ('tcp' o 'udp')
    timeout: Timeout en milisegundos para streams RTSP

Returns: Objeto compatible con cv2.VideoCapture

Ejemplos:
    'screen' -> ScreenCapture del monitor principal
    'screen:1' -> ScreenCapture del monitor 1
    'screen:2' -> ScreenCapture del monitor 2
    'screen:region:100,100,800,600' -> Región específica (x,y,w,h)
    '0' -> cv2.VideoCapture(0) - webcam
    'video.mp4' -> cv2.VideoCapture('video.mp4')
    'rtsp://...' -> cv2.VideoCapture optimizado para RTSP
"""
def crear_fuente_pantalla(argumento_fuente, transporte_rtsp='tcp', timeout=TIMEOUT_RTSP_DEFECTO):
    fuente_str = str(argumento_fuente).lower()
    if fuente_str.startswith('screen'):
        partes = fuente_str.split(':')
        # screen:region:x,y,w,h
        if len(partes) >= 3 and partes[1] == 'region':
            coordenadas = partes[2].split(',')
            if len(coordenadas) == 4:
                x, y, w, h = map(int, coordenadas)
                region = {'left': x, 'top': y, 'width': w, 'height': h}
                return ScreenCapture(indice_monitor=1, region=region)
        # screen:N (monitor específico)
        elif len(partes) == 2:
            try:
                indice_monitor = int(partes[1])
                return ScreenCapture(indice_monitor=indice_monitor)
            except ValueError:
                pass
        # screen (monitor principal)
        return ScreenCapture(indice_monitor=1)
    # Fuente RTSP (URL con rtsp://)
    if fuente_str.startswith('rtsp://') or fuente_str.startswith('http://'):
        print(f'[INFO] Conectando a stream: {argumento_fuente}')
        print(f'[INFO] Transporte: {transporte_rtsp.upper()}, Timeout: {timeout}ms')
        captura = cv2.VideoCapture(argumento_fuente, cv2.CAP_FFMPEG)
        # Configuración optimizada para RTSP
        captura.set(cv2.CAP_PROP_BUFFERSIZE, 0)  # Sin buffer para baja latencia
        captura.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, timeout)
        captura.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, timeout)
        # Opciones FFMPEG para baja latencia
        if transporte_rtsp.lower() == 'tcp':
            # TCP es más confiable pero puede tener más latencia
            pass  # OpenCV usa TCP por defecto con FFMPEG
        elif transporte_rtsp.lower() == 'udp':
            # UDP es más rápido pero menos confiable
            # Nota: OpenCV no expone directamente rtsp_transport en CAP_PROP
            print('[WARNING] UDP transport no completamente soportado en OpenCV, usando TCP')
        if captura.isOpened():
            print('[SUCCESS] Stream RTSP conectado exitosamente')
            # Mostrar info del stream
            width = int(captura.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(captura.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = captura.get(cv2.CAP_PROP_FPS)
            print(f'[INFO] Resolución: {width}x{height}, FPS: {fps:.1f}')
        else:
            print('[ERROR] No se pudo conectar al stream RTSP')
        return captura
    # Fuente normal (webcam o archivo)
    if fuente_str.isdigit(): return cv2.VideoCapture(int(fuente_str))
    else: return cv2.VideoCapture(argumento_fuente)

# Lista todos los monitores disponibles
def listar_monitores():
    with mss.mss() as sct:
        monitores = sct.monitors
        print("\n=== Monitores Disponibles ===")
        for i, monitor in enumerate(monitores):
            if i == 0: print(f"Monitor {i}: Todos los monitores combinados")
            else: print(f"Monitor {i}: {monitor}")
        print("=============================\n")
        return monitores

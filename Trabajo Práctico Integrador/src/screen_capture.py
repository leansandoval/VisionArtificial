"""
Módulo de captura de pantalla para usar como fuente de video.
Compatible con la interfaz de cv2.VideoCapture para integración transparente.
"""
import cv2
import numpy as np
import mss
import time


class ScreenCapture:
    """
    Clase que captura la pantalla y la presenta como fuente de video.
    Compatible con la interfaz de cv2.VideoCapture.
    """
    
    def __init__(self, monitor_index=1, region=None, fps_limit=30):
        """
        Inicializa el capturador de pantalla.
        
        Args:
            monitor_index (int): Índice del monitor a capturar (1 = principal)
            region (dict): Región específica {'left': x, 'top': y, 'width': w, 'height': h}
            fps_limit (int): Límite de FPS para la captura (0 = sin límite)
        """
        self.sct = mss.mss()
        self.monitor_index = monitor_index
        self.region = region
        self.fps_limit = fps_limit
        self._is_opened = True
        self._frame_time = 1.0 / fps_limit if fps_limit > 0 else 0
        self._last_capture_time = 0
        
        # Obtener información del monitor
        if region is None:
            self.monitor = self.sct.monitors[monitor_index]
        else:
            self.monitor = region
        
        print(f"[ScreenCapture] Inicializado")
        print(f"  - Monitor: {monitor_index}")
        print(f"  - Región: {self.monitor}")
        print(f"  - FPS Límite: {fps_limit if fps_limit > 0 else 'Sin límite'}")
    
    def isOpened(self):
        """Retorna si la captura está abierta"""
        return self._is_opened
    
    def read(self):
        """
        Lee un frame de la pantalla.
        
        Returns:
            tuple: (success, frame) donde success es bool y frame es numpy array
        """
        if not self._is_opened:
            return False, None
        
        try:
            # Controlar FPS si está configurado
            if self.fps_limit > 0:
                current_time = time.time()
                elapsed = current_time - self._last_capture_time
                if elapsed < self._frame_time:
                    sleep_time = self._frame_time - elapsed
                    time.sleep(sleep_time)
                self._last_capture_time = time.time()
            
            # Capturar pantalla
            screenshot = self.sct.grab(self.monitor)
            
            # Convertir a formato OpenCV (BGR)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
            return True, frame
            
        except Exception as e:
            print(f"[ScreenCapture ERROR] {e}")
            return False, None
    
    def release(self):
        """Libera los recursos de captura"""
        self._is_opened = False
        if self.sct:
            self.sct.close()
        print("[ScreenCapture] Liberado")
    
    def get(self, propId):
        """
        Obtiene propiedades del video (compatible con cv2.VideoCapture).
        
        Args:
            propId: ID de la propiedad (cv2.CAP_PROP_*)
        """
        if propId == cv2.CAP_PROP_FRAME_WIDTH:
            return self.monitor.get('width', 1920)
        elif propId == cv2.CAP_PROP_FRAME_HEIGHT:
            return self.monitor.get('height', 1080)
        elif propId == cv2.CAP_PROP_FPS:
            return self.fps_limit if self.fps_limit > 0 else 30
        else:
            return 0
    
    def set(self, propId, value):
        """
        Establece propiedades del video (compatible con cv2.VideoCapture).
        Implementación básica.
        """
        return False


def create_screen_source(source_arg):
    """
    Factory function para crear fuente de captura.
    Retorna ScreenCapture si source_arg es 'screen', sino cv2.VideoCapture normal.
    
    Args:
        source_arg: Argumento de fuente ('screen', 'screen:1', '0', 'video.mp4', etc.)
    
    Returns:
        Objeto compatible con cv2.VideoCapture
    
    Ejemplos:
        'screen' -> ScreenCapture del monitor principal
        'screen:1' -> ScreenCapture del monitor 1
        'screen:2' -> ScreenCapture del monitor 2
        'screen:region:100,100,800,600' -> Región específica (x,y,w,h)
        '0' -> cv2.VideoCapture(0) - webcam
        'video.mp4' -> cv2.VideoCapture('video.mp4')
    """
    source_str = str(source_arg).lower()
    
    if source_str.startswith('screen'):
        parts = source_str.split(':')
        
        # screen:region:x,y,w,h
        if len(parts) >= 3 and parts[1] == 'region':
            coords = parts[2].split(',')
            if len(coords) == 4:
                x, y, w, h = map(int, coords)
                region = {'left': x, 'top': y, 'width': w, 'height': h}
                return ScreenCapture(monitor_index=1, region=region)
        
        # screen:N (monitor específico)
        elif len(parts) == 2:
            try:
                monitor_idx = int(parts[1])
                return ScreenCapture(monitor_index=monitor_idx)
            except ValueError:
                pass
        
        # screen (monitor principal)
        return ScreenCapture(monitor_index=1)
    
    # Fuente normal (webcam o archivo)
    if source_str.isdigit():
        return cv2.VideoCapture(int(source_str))
    else:
        return cv2.VideoCapture(source_arg)


def list_monitors():
    """Lista todos los monitores disponibles"""
    with mss.mss() as sct:
        monitors = sct.monitors
        print("\n=== Monitores Disponibles ===")
        for i, monitor in enumerate(monitors):
            if i == 0:
                print(f"Monitor {i}: Todos los monitores combinados")
            else:
                print(f"Monitor {i}: {monitor}")
        print("=============================\n")
        return monitors

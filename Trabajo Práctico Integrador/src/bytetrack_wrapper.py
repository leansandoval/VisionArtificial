# Wrapper para ByteTrack usando Supervision library.
# ByteTrack es un algoritmo de tracking robusto que mantiene IDs consistentes
# incluso con oclusiones, detecciones perdidas y movimientos rápidos.

from typing import List, Dict
import numpy as np

try:
    import supervision as sv
    SUPERVISION_AVAILABLE = True
except ImportError:
    SUPERVISION_AVAILABLE = False
    print("[WARNING] supervision no instalado. Instalar con: pip install supervision")

# Wrapper para ByteTrack que mantiene la misma interfaz que SimpleTracker
class ByteTrackWrapper:
    
    # Args:
    # * umbral_activacion_track: Umbral de confianza para activar tracking
    # * buffer_tracks_perdidos: Número de frames para mantener tracks perdidos
    # * umbral_minimo_emparejamiento: Umbral de IoU para matching
    # * tasa_frame: FPS esperado del video
    def __init__(self,
                 umbral_activacion_track: float = 0.25,
                 buffer_tracks_perdidos: int = 30, 
                 umbral_minimo_emparejamiento: float = 0.8,
                 tasa_frame: int = 30):
        if not SUPERVISION_AVAILABLE:
            raise ImportError("supervision library no disponible. Instalar con: pip install supervision")
        self.tracker = sv.ByteTrack(
            track_activation_threshold=umbral_activacion_track,
            lost_track_buffer=buffer_tracks_perdidos,
            minimum_matching_threshold=umbral_minimo_emparejamiento,
            frame_rate=tasa_frame
        )
    
    # Actualiza el tracker con nuevas detecciones.
    # Args: detecciones: Lista de dicts con 'bbox' y 'conf'
    # Returns: Lista de tracks con 'track_id', 'bbox', 'conf'
    def actualizar(self, detecciones: List[Dict]) -> List[Dict]:
        if len(detecciones) == 0:
            # Actualizar con detecciones vacías para mantener tracks existentes
            detecciones_vacias = sv.Detections.empty()
            tracked = self.tracker.update_with_detections(detecciones_vacias)
            return []
        # Convertir detections al formato Supervision
        xyxy = np.array([d['bbox'] for d in detecciones], dtype=np.float32)
        confianza = np.array([d['conf'] for d in detecciones], dtype=np.float32)
        # Crear objeto Detections de supervision
        # Todos son clase 0 (person)
        detecciones_sv = sv.Detections(xyxy=xyxy, confidence=confianza, class_id=np.zeros(len(detecciones), dtype=int))
        # Ejecutar ByteTrack
        detecciones_rastreadas = self.tracker.update_with_detections(detecciones_sv)
        # Convertir de vuelta a nuestro formato
        tracks = []
        if detecciones_rastreadas.tracker_id is not None:
            for i in range(len(detecciones_rastreadas.xyxy)):
                bbox = detecciones_rastreadas.xyxy[i].tolist()
                id_track = int(detecciones_rastreadas.tracker_id[i])
                confianza = float(detecciones_rastreadas.confidence[i]) if detecciones_rastreadas.confidence is not None else 1.0
                tracks.append({'track_id': id_track, 'bbox': bbox, 'conf': confianza, 'lost': 0 })
        return tracks

if __name__ == '__main__':
    if SUPERVISION_AVAILABLE:
        print('ByteTrack wrapper disponible')
        tracker = ByteTrackWrapper()
        print('Tracker inicializado correctamente')
    else:
        print('ERROR: supervision no está instalado')

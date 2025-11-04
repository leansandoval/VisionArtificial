"""Wrapper para ByteTrack usando Supervision library.

ByteTrack es un algoritmo de tracking robusto que mantiene IDs consistentes
incluso con oclusiones, detecciones perdidas y movimientos rápidos.
"""
from typing import List, Dict
import numpy as np

try:
    import supervision as sv
    SUPERVISION_AVAILABLE = True
except ImportError:
    SUPERVISION_AVAILABLE = False
    print("[WARNING] supervision no instalado. Instalar con: pip install supervision")


class ByteTrackWrapper:
    """Wrapper para ByteTrack que mantiene la misma interfaz que SimpleTracker"""
    
    def __init__(self, track_activation_threshold: float = 0.25, lost_track_buffer: int = 30, 
                 minimum_matching_threshold: float = 0.8, frame_rate: int = 30):
        """
        Args:
            track_activation_threshold: Umbral de confianza para activar tracking
            lost_track_buffer: Número de frames para mantener tracks perdidos
            minimum_matching_threshold: Umbral de IoU para matching
            frame_rate: FPS esperado del video
        """
        if not SUPERVISION_AVAILABLE:
            raise ImportError("supervision library no disponible. Instalar con: pip install supervision")
        
        self.tracker = sv.ByteTrack(
            track_activation_threshold=track_activation_threshold,
            lost_track_buffer=lost_track_buffer,
            minimum_matching_threshold=minimum_matching_threshold,
            frame_rate=frame_rate
        )
    
    def update(self, detections: List[Dict]) -> List[Dict]:
        """
        Actualiza el tracker con nuevas detecciones.
        
        Args:
            detections: Lista de dicts con 'bbox' y 'conf'
        
        Returns:
            Lista de tracks con 'track_id', 'bbox', 'conf'
        """
        if len(detections) == 0:
            # Actualizar con detecciones vacías para mantener tracks existentes
            empty_detections = sv.Detections.empty()
            tracked = self.tracker.update_with_detections(empty_detections)
            return []
        
        # Convertir detections al formato Supervision
        xyxy = np.array([d['bbox'] for d in detections], dtype=np.float32)
        confidence = np.array([d['conf'] for d in detections], dtype=np.float32)
        
        # Crear objeto Detections de supervision
        sv_detections = sv.Detections(
            xyxy=xyxy,
            confidence=confidence,
            class_id=np.zeros(len(detections), dtype=int)  # Todos son clase 0 (person)
        )
        
        # Ejecutar ByteTrack
        tracked_detections = self.tracker.update_with_detections(sv_detections)
        
        # Convertir de vuelta a nuestro formato
        tracks = []
        if tracked_detections.tracker_id is not None:
            for i in range(len(tracked_detections.xyxy)):
                bbox = tracked_detections.xyxy[i].tolist()
                track_id = int(tracked_detections.tracker_id[i])
                conf = float(tracked_detections.confidence[i]) if tracked_detections.confidence is not None else 1.0
                
                tracks.append({
                    'track_id': track_id,
                    'bbox': bbox,
                    'conf': conf,
                    'lost': 0  # ByteTrack maneja esto internamente
                })
        
        return tracks


if __name__ == '__main__':
    if SUPERVISION_AVAILABLE:
        print('ByteTrack wrapper disponible')
        tracker = ByteTrackWrapper()
        print('Tracker inicializado correctamente')
    else:
        print('ERROR: supervision no está instalado')

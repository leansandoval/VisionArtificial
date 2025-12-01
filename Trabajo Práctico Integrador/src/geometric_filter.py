"""Filtrado geométrico avanzado para reducir falsos positivos en detección de intrusiones.

Este módulo implementa múltiples estrategias de filtrado:
- Tiempo mínimo en zona antes de alertar
- Validación de tamaño de detección
- Análisis de trayectoria y movimiento
- Filtrado por confianza adaptativa
"""
import time
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional
import numpy as np


class GeometricFilter:
    """Filtro geométrico avanzado para validar intrusiones reales."""
    
    def __init__(self, 
                 min_time_in_zone: float = 2.0,
                 min_bbox_area: int = 2000,
                 min_confidence: float = 0.25,
                 trajectory_length: int = 10,
                 min_movement_threshold: float = 5.0):
        """
        Args:
            min_time_in_zone: Segundos mínimos que una persona debe estar en zona antes de alertar
            min_bbox_area: Área mínima del bbox en píxeles (ancho * alto)
            min_confidence: Confianza mínima para considerar detección válida
            trajectory_length: Número de posiciones a mantener en historial
            min_movement_threshold: Píxeles mínimos de movimiento para considerar "en movimiento"
        """
        self.min_time_in_zone = min_time_in_zone
        self.min_bbox_area = min_bbox_area
        self.min_confidence = min_confidence
        self.trajectory_length = trajectory_length
        self.min_movement_threshold = min_movement_threshold
        
        # Historial de tracks en zonas: {track_id: timestamp_primera_detección}
        self.track_zone_entry_time: Dict[int, float] = {}
        
        # Trayectorias: {track_id: deque([(x, y, timestamp), ...])}
        self.track_trajectories: Dict[int, deque] = defaultdict(
            lambda: deque(maxlen=self.trajectory_length)
        )
        
        # Estadísticas para análisis
        self.stats = {
            'total_detections': 0,
            'filtered_by_size': 0,
            'filtered_by_confidence': 0,
            'filtered_by_time': 0,
            'filtered_by_movement': 0,
            'valid_intrusions': 0
        }
    
    def validate_detection_size(self, bbox: List[float]) -> bool:
        """
        Valida que el bbox tenga un tamaño mínimo razonable.
        
        Args:
            bbox: [x1, y1, x2, y2]
        
        Returns:
            True si el bbox es suficientemente grande
        """
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        area = width * height
        
        if area < self.min_bbox_area:
            self.stats['filtered_by_size'] += 1
            return False
        
        # Validar aspect ratio razonable para una persona (no muy ancho ni muy alto)
        aspect_ratio = height / width if width > 0 else 0
        if aspect_ratio < 0.5 or aspect_ratio > 5.0:
            self.stats['filtered_by_size'] += 1
            return False
        
        return True
    
    def validate_confidence(self, confidence: float) -> bool:
        """
        Valida que la confianza sea suficiente.
        
        Args:
            confidence: Confianza de la detección (0-1)
        
        Returns:
            True si la confianza es suficiente
        """
        if confidence < self.min_confidence:
            self.stats['filtered_by_confidence'] += 1
            return False
        return True
    
    def update_trajectory(self, track_id: int, center: Tuple[int, int]):
        """
        Actualiza la trayectoria de un track.
        
        Args:
            track_id: ID del track
            center: (x, y) centro del bbox
        """
        timestamp = time.time()
        self.track_trajectories[track_id].append((center[0], center[1], timestamp))
    
    def calculate_movement(self, track_id: int) -> float:
        """
        Calcula el movimiento total en la trayectoria reciente.
        
        Args:
            track_id: ID del track
        
        Returns:
            Distancia total recorrida en píxeles
        """
        trajectory = self.track_trajectories.get(track_id)
        if not trajectory or len(trajectory) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(1, len(trajectory)):
            x1, y1, _ = trajectory[i-1]
            x2, y2, _ = trajectory[i]
            distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            total_distance += distance
        
        return total_distance
    
    def is_stationary(self, track_id: int) -> bool:
        """
        Determina si un track está estacionario (sin movimiento significativo).
        
        Args:
            track_id: ID del track
        
        Returns:
            True si el track está prácticamente estático
        """
        trajectory = self.track_trajectories.get(track_id)
        if not trajectory or len(trajectory) < 3:
            return False  # No hay suficiente información
        
        # Calcular movimiento reciente
        movement = self.calculate_movement(track_id)
        
        # Si el movimiento es menor al umbral, está estacionario
        return movement < self.min_movement_threshold
    
    def validate_time_in_zone(self, track_id: int, is_in_zone: bool) -> bool:
        """
        Valida que el track haya estado suficiente tiempo en la zona.
        
        Args:
            track_id: ID del track
            is_in_zone: Si actualmente está en zona
        
        Returns:
            True si ha estado suficiente tiempo en zona para generar alerta
        """
        current_time = time.time()
        
        if is_in_zone:
            # Registrar entrada si es la primera vez
            if track_id not in self.track_zone_entry_time:
                self.track_zone_entry_time[track_id] = current_time
                return False  # Primera detección, esperar
            
            # Calcular tiempo transcurrido
            time_in_zone = current_time - self.track_zone_entry_time[track_id]
            
            if time_in_zone < self.min_time_in_zone:
                self.stats['filtered_by_time'] += 1
                return False  # No ha estado suficiente tiempo
            
            return True  # Validado
        else:
            # Si ya no está en zona, limpiar registro
            if track_id in self.track_zone_entry_time:
                del self.track_zone_entry_time[track_id]
            return False
    
    def validate_intrusion(self, 
                          track_id: int, 
                          bbox: List[float], 
                          confidence: float,
                          center: Tuple[int, int],
                          is_in_zone: bool) -> Dict:
        """
        Valida una posible intrusión aplicando todos los filtros.
        
        Args:
            track_id: ID del track
            bbox: [x1, y1, x2, y2]
            confidence: Confianza de detección
            center: (x, y) centro del bbox
            is_in_zone: Si está en zona restringida
        
        Returns:
            Dict con resultado de validación:
            {
                'is_valid': bool,
                'reason': str,  # Si no es válido, razón del filtrado
                'time_in_zone': float,  # Tiempo en zona (si aplica)
                'movement': float  # Movimiento total
            }
        """
        self.stats['total_detections'] += 1
        
        # Actualizar trayectoria siempre
        self.update_trajectory(track_id, center)
        
        # Filtro 1: Validar tamaño del bbox
        if not self.validate_detection_size(bbox):
            return {
                'is_valid': False,
                'reason': 'bbox_too_small',
                'time_in_zone': 0.0,
                'movement': 0.0
            }
        
        # Filtro 2: Validar confianza
        if not self.validate_confidence(confidence):
            return {
                'is_valid': False,
                'reason': 'low_confidence',
                'time_in_zone': 0.0,
                'movement': 0.0
            }
        
        # Si no está en zona, no hay intrusión
        if not is_in_zone:
            return {
                'is_valid': False,
                'reason': 'not_in_zone',
                'time_in_zone': 0.0,
                'movement': self.calculate_movement(track_id)
            }
        
        # Filtro 3: Validar tiempo en zona
        time_valid = self.validate_time_in_zone(track_id, is_in_zone)
        time_in_zone = 0.0
        if track_id in self.track_zone_entry_time:
            time_in_zone = time.time() - self.track_zone_entry_time[track_id]
        
        if not time_valid:
            return {
                'is_valid': False,
                'reason': 'insufficient_time_in_zone',
                'time_in_zone': time_in_zone,
                'movement': self.calculate_movement(track_id)
            }
        
        # Filtro 4: Validar que no esté completamente estacionario (opcional)
        # Esto filtra objetos estáticos mal clasificados como personas
        if self.is_stationary(track_id):
            self.stats['filtered_by_movement'] += 1
            return {
                'is_valid': False,
                'reason': 'stationary_object',
                'time_in_zone': time_in_zone,
                'movement': self.calculate_movement(track_id)
            }
        
        # ✅ Validación exitosa
        self.stats['valid_intrusions'] += 1
        return {
            'is_valid': True,
            'reason': 'valid_intrusion',
            'time_in_zone': time_in_zone,
            'movement': self.calculate_movement(track_id)
        }
    
    def cleanup_old_tracks(self, active_track_ids: List[int]):
        """
        Limpia tracks que ya no están activos.
        
        Args:
            active_track_ids: Lista de IDs de tracks actualmente activos
        """
        # Limpiar tiempos de entrada
        inactive_ids = set(self.track_zone_entry_time.keys()) - set(active_track_ids)
        for track_id in inactive_ids:
            if track_id in self.track_zone_entry_time:
                del self.track_zone_entry_time[track_id]
        
        # Limpiar trayectorias muy antiguas (más de 30 segundos sin actualizar)
        current_time = time.time()
        tracks_to_remove = []
        for track_id, trajectory in self.track_trajectories.items():
            if trajectory and len(trajectory) > 0:
                last_timestamp = trajectory[-1][2]
                if current_time - last_timestamp > 30.0:
                    tracks_to_remove.append(track_id)
        
        for track_id in tracks_to_remove:
            del self.track_trajectories[track_id]
    
    def get_statistics(self) -> Dict:
        """
        Obtiene estadísticas del filtrado.
        
        Returns:
            Dict con estadísticas detalladas
        """
        stats = self.stats.copy()
        if stats['total_detections'] > 0:
            stats['filter_rate'] = (
                (stats['total_detections'] - stats['valid_intrusions']) / 
                stats['total_detections'] * 100
            )
        else:
            stats['filter_rate'] = 0.0
        
        return stats
    
    def reset_statistics(self):
        """Resetea las estadísticas."""
        self.stats = {
            'total_detections': 0,
            'filtered_by_size': 0,
            'filtered_by_confidence': 0,
            'filtered_by_time': 0,
            'filtered_by_movement': 0,
            'valid_intrusions': 0
        }


if __name__ == '__main__':
    # Test básico
    gf = GeometricFilter(min_time_in_zone=2.0, min_bbox_area=2000)
    
    # Simular detección pequeña (debería filtrar)
    result = gf.validate_intrusion(
        track_id=1,
        bbox=[10, 10, 30, 40],  # 20x30 = 600 píxeles (< 2000)
        confidence=0.8,
        center=(20, 25),
        is_in_zone=True
    )
    print(f"Test 1 (bbox pequeño): {result}")
    assert not result['is_valid'], "Debería filtrar bbox pequeño"
    
    # Simular detección válida pero poco tiempo
    result = gf.validate_intrusion(
        track_id=2,
        bbox=[10, 10, 60, 110],  # 50x100 = 5000 píxeles
        confidence=0.8,
        center=(35, 60),
        is_in_zone=True
    )
    print(f"Test 2 (poco tiempo): {result}")
    assert not result['is_valid'], "Debería filtrar por poco tiempo"
    
    # Simular paso del tiempo (2 segundos)
    import time
    time.sleep(2.1)
    
    # Ahora debería pasar
    result = gf.validate_intrusion(
        track_id=2,
        bbox=[10, 10, 60, 110],
        confidence=0.8,
        center=(35, 60),
        is_in_zone=True
    )
    print(f"Test 3 (suficiente tiempo): {result}")
    assert result['is_valid'], "Debería pasar después de 2 segundos"
    
    print("\nGeometricFilter funcionando correctamente")
    print(f"Estadísticas: {gf.get_statistics()}")

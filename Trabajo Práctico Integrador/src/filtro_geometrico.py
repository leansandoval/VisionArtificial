# Filtrado geométrico avanzado para reducir falsos positivos en detección de intrusiones.
# Este módulo implementa múltiples estrategias de filtrado:
# - Tiempo mínimo en zona antes de alertar
# - Validación de tamaño de detección
# - Análisis de trayectoria y movimiento
# - Filtrado por confianza adaptativa
import numpy as np
import time
from collections import defaultdict, deque
from typing import Dict, List, Tuple

SEGUNDOS_SIN_ACTUALIZAR_PARA_ELIMINAR = 30
TIEMPO_MINIMO_EN_ZONA_POR_DEFECTO = 2.0  # Segundos mínimos en zona antes de alertar

class FiltroGeometrico:
    """Filtro geométrico avanzado para validar intrusiones reales."""
    
    def __init__(self, 
                 tiempo_minimo_en_zona: float = TIEMPO_MINIMO_EN_ZONA_POR_DEFECTO,
                 area_minima_bbox: int = 2000,
                 confianza_minima: float = 0.25,
                 longitud_trayectoria: int = 10,
                 umbral_movimiento_minimo: float = 5.0):
        """
        Args:
            tiempo_minimo_en_zona: Segundos mínimos que una persona debe estar en zona antes de alertar
            area_minima_bbox: Área mínima del bbox en píxeles (ancho * alto)
            confianza_minima: Confianza mínima para considerar detección válida
            longitud_trayectoria: Número de posiciones a mantener en historial
            umbral_movimiento_minimo: Píxeles mínimos de movimiento para considerar "en movimiento"
        """
        self.tiempo_minimo_en_zona = tiempo_minimo_en_zona
        self.area_minima_bbox = area_minima_bbox
        self.confianza_minima = confianza_minima
        self.longitud_trayectoria = longitud_trayectoria
        self.umbral_movimiento_minimo = umbral_movimiento_minimo
        
        # Historial de tracks en zonas: {id_track: timestamp_primera_detección}
        self.tiempo_entrada_zona_track: Dict[int, float] = {}
        
        # Trayectorias: {id_track: deque([(x, y, timestamp), ...])}
        self.trayectorias_track: Dict[int, deque] = defaultdict(lambda: deque(maxlen=self.longitud_trayectoria))
        
        # Estadísticas para análisis
        self.estadisticas = {
            'total_detections': 0,
            'filtered_by_size': 0,
            'filtered_by_confidence': 0,
            'filtered_by_time': 0,
            'filtered_by_movement': 0,
            'valid_intrusions': 0
        }
    
    # Valida que el bbox tenga un tamaño mínimo razonable.
    # Args: bbox: [x1, y1, x2, y2]
    # Returns: True si el bbox es suficientemente grande
    def validar_tamano_deteccion(self, bounding_box: List[float]) -> bool:
        x1, y1, x2, y2 = bounding_box
        ancho = x2 - x1
        alto = y2 - y1
        area = ancho * alto
        if area < self.area_minima_bbox:
            self.estadisticas['filtered_by_size'] += 1
            return False
        # Validar aspect ratio razonable para una persona (no muy ancho ni muy alto)
        relacion_aspecto = alto / ancho if ancho > 0 else 0
        if relacion_aspecto < 0.5 or relacion_aspecto > 5.0:
            self.estadisticas['filtered_by_size'] += 1
            return False
        return True
    
    # Valida que la confianza sea suficiente.
    # Args: confianza: Confianza de la detección (0-1)
    # Returns: True si la confianza es suficiente
    def validar_confianza(self, confianza: float) -> bool:
        if confianza < self.confianza_minima:
            self.estadisticas['filtered_by_confidence'] += 1
            return False
        return True
    
    # Actualiza la trayectoria de un track.  
    # Args: id_track: ID del track
    #       centro: (x, y) centro del bbox
    def actualizar_trayectoria(self, id_track: int, centro: Tuple[int, int]):
        marca_tiempo = time.time()
        self.trayectorias_track[id_track].append((centro[0], centro[1], marca_tiempo))
    
    # Calcula el movimiento total en la trayectoria reciente.
    # Args: id_track: ID del track
    # Returns: Distancia total recorrida en píxeles
    def calcular_movimiento(self, id_track: int) -> float:
        trayectoria = self.trayectorias_track.get(id_track)
        if not trayectoria or len(trayectoria) < 2:
            return 0.0
        distancia_total = 0.0
        for i in range(1, len(trayectoria)):
            x1, y1, _ = trayectoria[i - 1]
            x2, y2, _ = trayectoria[i]
            distancia = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            distancia_total += distancia
        return distancia_total
    
    # Determina si un track está estacionario (sin movimiento significativo).
    # Args: id_track: ID del track
    # Returns: True si el track está prácticamente estático
    def esta_estacionario(self, id_track: int) -> bool:
        trayectoria = self.trayectorias_track.get(id_track)
        if not trayectoria or len(trayectoria) < 3:
            return False  # No hay suficiente información
        # Calcular movimiento reciente
        movimiento = self.calcular_movimiento(id_track)
        # Si el movimiento es menor al umbral, está estacionario
        return movimiento < self.umbral_movimiento_minimo
    
    # Valida que el track haya estado suficiente tiempo en la zona.
    # Args: id_track: ID del track
    #       esta_en_zona: Si actualmente está en zona
    # Returns: True si ha estado suficiente tiempo en zona para generar alerta
    def validar_tiempo_en_zona(self, id_track: int, esta_en_zona: bool) -> bool:
        tiempo_actual = time.time()
        if esta_en_zona:
            # Registrar entrada si es la primera vez
            if id_track not in self.tiempo_entrada_zona_track:
                self.tiempo_entrada_zona_track[id_track] = tiempo_actual
                return False  # Primera detección, esperar 
            # Calcular tiempo transcurrido
            tiempo_en_zona = tiempo_actual - self.tiempo_entrada_zona_track[id_track]
            if tiempo_en_zona < self.tiempo_minimo_en_zona:
                self.estadisticas['filtered_by_time'] += 1
                return False    # No ha estado suficiente tiempo
            return True         # Validado
        else:
            # Si ya no está en zona, limpiar registro
            if id_track in self.tiempo_entrada_zona_track:
                del self.tiempo_entrada_zona_track[id_track]
            return False
    
    def validar_intrusion(self, 
                          id_track: int, 
                          bbox: List[float], 
                          confianza: float,
                          centro: Tuple[int, int],
                          esta_en_zona: bool) -> Dict:
        """
        Valida una posible intrusión aplicando todos los filtros.
        Args:
            id_track: ID del track
            bbox: [x1, y1, x2, y2]
            confianza: Confianza de detección
            centro: (x, y) centro del bbox
            esta_en_zona: Si está en zona restringida
        Returns:
            Dict con resultado de validación:
            {
                'is_valid': bool,
                'reason': str,  # Si no es válido, razón del filtrado
                'time_in_zone': float,  # Tiempo en zona (si aplica)
                'movement': float  # Movimiento total
            }
        """
        self.estadisticas['total_detections'] += 1
        
        # Actualizar trayectoria siempre
        self.actualizar_trayectoria(id_track, centro)
        
        # Filtro 1: Validar tamaño del bbox
        if not self.validar_tamano_deteccion(bounding_box=bbox):
            return {'is_valid': False, 'reason': 'bbox_too_small', 'time_in_zone': 0.0, 'movement': 0.0}
        
        # Filtro 2: Validar confianza
        if not self.validar_confianza(confianza):
            return {'is_valid': False, 'reason': 'low_confidence', 'time_in_zone': 0.0, 'movement': 0.0}
        
        # Si no está en zona, no hay intrusión
        if not esta_en_zona:
            return {'is_valid': False, 'reason': 'not_in_zone', 'time_in_zone': 0.0, 'movement': self.calcular_movimiento(id_track)}
        
        # Filtro 3: Validar tiempo en zona
        tiempo_valido = self.validar_tiempo_en_zona(id_track, esta_en_zona)
        tiempo_en_zona = 0.0
        if id_track in self.tiempo_entrada_zona_track:
            tiempo_en_zona = time.time() - self.tiempo_entrada_zona_track[id_track]
        if not tiempo_valido:
            return {'is_valid': False, 'reason': 'insufficient_time_in_zone', 'time_in_zone': tiempo_en_zona, 'movement': self.calcular_movimiento(id_track)}
        
        # Filtro 4: Validar que no esté completamente estacionario (opcional)
        # Esto filtra objetos estáticos mal clasificados como personas
        if self.esta_estacionario(id_track):
            self.estadisticas['filtered_by_movement'] += 1
            return {'is_valid': False, 'reason': 'stationary_object', 'time_in_zone': tiempo_en_zona, 'movement': self.calcular_movimiento(id_track)}
        
        # Validación exitosa
        self.estadisticas['valid_intrusions'] += 1
        return {'is_valid': True, 'reason': 'valid_intrusion', 'time_in_zone': tiempo_en_zona, 'movement': self.calcular_movimiento(id_track)}
        
    # Limpia tracks que ya no están activos.
    # Args: ids_tracks_activos: Lista de IDs de tracks actualmente activos
    def limpiar_tracks_antiguos(self, ids_tracks_activos: List[int]):
        # Limpiar tiempos de entrada
        ids_inactivos = set(self.tiempo_entrada_zona_track.keys()) - set(ids_tracks_activos)
        for id_track in ids_inactivos:
            if id_track in self.tiempo_entrada_zona_track:
                del self.tiempo_entrada_zona_track[id_track]
        # Limpiar trayectorias muy antiguas (más de 30 segundos sin actualizar)
        tiempo_actual = time.time()
        tracks_a_eliminar = []
        for id_track, trayectoria in self.trayectorias_track.items():
            if trayectoria and len(trayectoria) > 0:
                ultima_marca_tiempo = trayectoria[-1][2]
                if tiempo_actual - ultima_marca_tiempo > SEGUNDOS_SIN_ACTUALIZAR_PARA_ELIMINAR:
                    tracks_a_eliminar.append(id_track)
        for id_track in tracks_a_eliminar:
            del self.trayectorias_track[id_track]

    def obtener_estadisticas(self) -> Dict:
        estadisticas = self.estadisticas.copy()
        if estadisticas['total_detections'] > 0:
            estadisticas['filter_rate'] = ((estadisticas['total_detections'] - estadisticas['valid_intrusions']) / estadisticas['total_detections'] * 100)
        else:
            estadisticas['filter_rate'] = 0.0
        return estadisticas
    
    def reiniciar_estadisticas(self):
        self.estadisticas = {
            'total_detections': 0,
            'filtered_by_size': 0,
            'filtered_by_confidence': 0,
            'filtered_by_time': 0,
            'filtered_by_movement': 0,
            'valid_intrusions': 0
        }

if __name__ == '__main__':
    # Test básico
    gf = FiltroGeometrico(tiempo_minimo_en_zona=2.0, area_minima_bbox=2000)
    
    # Simular detección pequeña (debería filtrar)
    result = gf.validar_intrusion(
        id_track=1,
        bbox=[10, 10, 30, 40],  # 20x30 = 600 píxeles (< 2000)
        confianza=0.8,
        centro=(20, 25),
        esta_en_zona=True
    )
    print(f"Test 1 (bbox pequeño): {result}")
    assert not result['is_valid'], "Debería filtrar bbox pequeño"
    
    # Simular detección válida pero poco tiempo
    result = gf.validar_intrusion(
        id_track=2,
        bbox=[10, 10, 60, 110],  # 50x100 = 5000 píxeles
        confianza=0.8,
        centro=(35, 60),
        esta_en_zona=True
    )
    print(f"Test 2 (poco tiempo): {result}")
    assert not result['is_valid'], "Debería filtrar por poco tiempo"
    
    # Simular paso del tiempo (2 segundos)
    import time
    time.sleep(2.1)
    
    # Ahora debería pasar
    result = gf.validar_intrusion(
        id_track=2,
        bbox=[10, 10, 60, 110],
        confianza=0.8,
        centro=(35, 60),
        esta_en_zona=True
    )
    print(f"Test 3 (suficiente tiempo): {result}")
    assert result['is_valid'], "Debería pasar después de 2 segundos"
    
    print("\nFiltroGeometrico funcionando correctamente")
    print(f"Estadísticas: {gf.obtener_estadisticas()}")

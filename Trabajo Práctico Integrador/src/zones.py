"""Gestión de zonas poligonales: dibujo interactivo y operaciones espaciales.
Zonas se guardan/recuperan en JSON con lista de polígonos (lista de puntos x,y).
"""
import json
import cv2
import numpy as np
import os
from typing import List, Tuple

class ZonesManager:
    def __init__(self, path: str = 'zones.json'):
        self.path = path
        self.zones: List[List[Tuple[int,int]]] = []
        self.zone_names: List[str] = []  # Nombres opcionales para zonas

    def save(self):
        data = {
            'zones': self.zones,
            'zone_names': self.zone_names
        }
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load(self):
        if not os.path.exists(self.path):
            self.zones = []
            self.zone_names = []
            return
        with open(self.path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Compatibilidad con formato antiguo (solo lista de zonas)
            if isinstance(data, list):
                self.zones = data
                self.zone_names = [f"Zona {i+1}: Área Restringida" for i in range(len(self.zones))]
            else:
                self.zones = data.get('zones', [])
                self.zone_names = data.get('zone_names', [f"Zona {i+1}: Área Restringida" for i in range(len(self.zones))])
    
    def get_zone_name(self, index: int) -> str:
        """Obtiene el nombre de una zona por índice"""
        if index < len(self.zone_names):
            return self.zone_names[index]
        return f"Zona {index+1}: Área Restringida"

    def point_in_zone(self, point: Tuple[int,int]):
        # Devuelve True si point está dentro de alguna zona
        x, y = point
        for poly in self.zones:
            if cv2.pointPolygonTest(np.array(poly, dtype=np.int32), (int(x), int(y)), False) >= 0:
                return True
        return False

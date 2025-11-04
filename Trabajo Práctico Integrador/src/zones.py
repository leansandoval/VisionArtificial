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

    def save(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.zones, f)

    def load(self):
        if not os.path.exists(self.path):
            self.zones = []
            return
        with open(self.path, 'r', encoding='utf-8') as f:
            self.zones = json.load(f)

    def point_in_zone(self, point: Tuple[int,int]):
        # Devuelve True si point está dentro de alguna zona
        x, y = point
        for poly in self.zones:
            if cv2.pointPolygonTest(np.array(poly, dtype=np.int32), (int(x), int(y)), False) >= 0:
                return True
        return False

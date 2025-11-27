# Gestión de zonas poligonales: Dibujo interactivo y operaciones espaciales.
# Zonas se guardan/recuperan en JSON con lista de polígonos (Lista de puntos X,Y).
import cv2
import json
import numpy as np
import os
from typing import List, Tuple

#region Constantes

ARCHIVO_ZONAS = 'zonas.json'
ETIQUETA_ZONAS = 'zonas'
ETIQUETA_NOMBRES_ZONAS = 'nombres_zonas'
MODO_APERTURA_ESCRITURA_ARCHIVO = 'w'
MODO_APERTURA_LECTURA_ARCHIVO = 'r'
UTF8 = 'utf-8'

#endregion

class ZonesManager:
    def __init__(self, ruta: str = ARCHIVO_ZONAS):
        self.ruta = ruta
        self.zonas: List[List[Tuple[int,int]]] = []
        # Nombres opcionales para zonas
        self.nombres_zonas: List[str] = []  

    def guardar(self):
        data = {
            ETIQUETA_ZONAS: self.zonas,
            ETIQUETA_NOMBRES_ZONAS: self.nombres_zonas
        }
        with open(self.ruta, MODO_APERTURA_ESCRITURA_ARCHIVO, encoding=UTF8) as archivo:
            json.dump(data, archivo, indent=2)

    def cargar(self):
        if not os.path.exists(self.ruta):
            self.zonas = []
            self.nombres_zonas = []
            return
        with open(self.ruta, MODO_APERTURA_LECTURA_ARCHIVO, encoding=UTF8) as archivo:
            data = json.load(archivo)
            # Compatibilidad con formato antiguo (solo lista de zonas)
            if isinstance(data, list):
                self.zonas = data
                self.nombres_zonas = [f"Zona {i + 1}: Área Restringida" for i in range(len(self.zonas))]
            else:
                self.zonas = data.get(ETIQUETA_ZONAS, [])
                self.nombres_zonas = data.get(ETIQUETA_NOMBRES_ZONAS, [f"Zona {i + 1}: Área Restringida" for i in range(len(self.zonas))])
    
    # Obtiene el nombre de una zona por índice
    def obtener_nombre_zona(self, indice: int) -> str:
        if indice < len(self.nombres_zonas):
            return self.nombres_zonas[indice]
        return f"Zona {indice + 1}: Área Restringida"

    # Devuelve True si point está dentro de alguna zona
    def punto_en_zona(self, point: Tuple[int,int]):
        x, y = point
        for poly in self.zonas:
            if cv2.pointPolygonTest(np.array(poly, dtype=np.int32), (int(x), int(y)), False) >= 0:
                return True
        return False

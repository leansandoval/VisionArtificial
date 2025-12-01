# Gestión de zonas poligonales: Dibujo interactivo y operaciones espaciales.
# Zonas se guardan/recuperan en JSON con lista de polígonos (Lista de puntos X,Y).
import json
import os
from typing import List, Tuple
from src.constantes import ARCHIVO_ZONAS, ETIQUETA_NOMBRES_ZONAS, ETIQUETA_ZONAS

#region Constantes

MODO_APERTURA_ESCRITURA_ARCHIVO = 'w'
MODO_APERTURA_LECTURA_ARCHIVO = 'r'
UTF8 = 'utf-8'

#endregion

class GestorZonas:
    def __init__(self, ruta: str = ARCHIVO_ZONAS):
        self.ruta = ruta
        self.zonas: List[List[Tuple[int,int]]] = []
        # Nombres opcionales para zonas
        self.nombres_zonas: List[str] = []  

    def guardar(self):
        datos = {
            ETIQUETA_ZONAS: self.zonas,
            ETIQUETA_NOMBRES_ZONAS: self.nombres_zonas
        }
        with open(self.ruta, MODO_APERTURA_ESCRITURA_ARCHIVO, encoding=UTF8) as archivo:
            json.dump(datos, archivo, indent=2)

    def cargar(self):
        if not os.path.exists(self.ruta):
            self.zonas = []
            self.nombres_zonas = []
            return
        with open(self.ruta, MODO_APERTURA_LECTURA_ARCHIVO, encoding=UTF8) as archivo:
            datos = json.load(archivo)
            # Compatibilidad con formato antiguo (solo lista de zonas)
            if isinstance(datos, list):
                self.zonas = datos
                self.nombres_zonas = [f"Zona {i + 1}: Área Restringida" for i in range(len(self.zonas))]
            else:
                self.zonas = datos.get(ETIQUETA_ZONAS, [])
                self.nombres_zonas = datos.get(ETIQUETA_NOMBRES_ZONAS, [f"Zona {i + 1}: Área Restringida" for i in range(len(self.zonas))])
    
    # Obtiene el nombre de una zona por índice
    def obtener_nombre_zona(self, indice: int) -> str:
        if indice < len(self.nombres_zonas):
            return self.nombres_zonas[indice]
        return f"Zona {indice + 1}: Área Restringida"

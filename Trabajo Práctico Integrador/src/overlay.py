# Funciones para dibujar overlays (Bounding Boxes, IDs, FPS, Zonas) sobre frames OpenCV.
import cv2
import numpy as np
from src.constantes import *

# region Funciones Auxiliares

def dibujar_texto_bounding_box(frame, etiqueta, color, x1, y1):
    # Background para el texto
    (tw, th), _ = cv2.getTextSize(etiqueta, cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_SESENTA_PORCIENTO, GROSOR_DOS_PIXELES)
    punto_esquina_superior_izquierda_rectangulo = (x1, max(0, y1 - th - 8))
    punto_esquina_inferior_derecha_rectangulo = (x1 + tw + 6, y1)
    cv2.rectangle(frame, punto_esquina_superior_izquierda_rectangulo, punto_esquina_inferior_derecha_rectangulo, color, GROSOR_RELLENO_COMPLETO)
    punto = (x1 + 3, max(th, y1 - 4))
    cv2.putText(frame, etiqueta, punto, cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_SESENTA_PORCIENTO, COLOR_TUPLA_NEGRO, GROSOR_DOS_PIXELES, cv2.LINE_AA)

def dibujar_estadisticas(frame, estadisticas, x_inicio, y_inicio):
    desplazamiento_y = y_inicio + 20
    for clave, valor in estadisticas.items():
        texto = f"{clave}: {valor}"
        punto = (x_inicio + 10, desplazamiento_y)
        cv2.putText(frame, texto, punto, cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_CINCUENTA_PORCIENTO, COLOR_TUPLA_BLANCO, GROSOR_UN_PIXEL, cv2.LINE_AA)
        desplazamiento_y += 25

# endregion

# region Funciones Principales

def dibujar_bounding_box(frame, bounding_box, etiqueta=None, color=COLOR_TUPLA_VERDE, grosor=GROSOR_DOS_PIXELES):
    x1, y1, x2, y2 = [int(v) for v in bounding_box]
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, grosor)
    if etiqueta:
        dibujar_texto_bounding_box(frame, etiqueta, color, x1, y1)

def dibujar_zona(frame, poligono, color=COLOR_TUPLA_ROJO, grosor=GROSOR_DOS_PIXELES, transparencia=TRANSPARENCIA_DIEZ_PORCIENTO, nombre_zona=None, id_zona=None):
    puntos = np.array(poligono, dtype=np.int32)
    overlay = frame.copy()
    # Borde doble (blanco exterior + color) para mayor contraste
    cv2.polylines(overlay, [puntos], isClosed=True, color=COLOR_TUPLA_BLANCO, thickness=grosor + 30)
    cv2.polylines(overlay, [puntos], isClosed=True, color=color, thickness=grosor)
    cv2.fillPoly(overlay, [puntos], color)
    cv2.addWeighted(overlay, transparencia, frame, 1 - transparencia, 0, frame)
    # Nombre de zona (esquina superior izquierda, texto mas chico)
    if nombre_zona or id_zona is not None:
        etiqueta = nombre_zona if nombre_zona else f"Zone {id_zona}"
        (tw, th), _ = cv2.getTextSize(etiqueta, cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_CINCUENTA_PORCIENTO, GROSOR_DOS_PIXELES)
        min_xy = puntos.min(axis=0)
        x_etiqueta = max(int(min_xy[0]) + 5, 0)
        y_etiqueta = max(int(min_xy[1]) + th + 5, th)
        overlay_text = frame.copy()
        punto_esquina_superior_izquierda_rectangulo = (x_etiqueta - 4, y_etiqueta - th - 6)
        punto_esquina_inferior_derecha_rectangulo = (x_etiqueta + tw + 4, y_etiqueta + 4)
        cv2.rectangle(overlay_text, punto_esquina_superior_izquierda_rectangulo, punto_esquina_inferior_derecha_rectangulo, COLOR_TUPLA_NEGRO, GROSOR_RELLENO_COMPLETO)
        cv2.addWeighted(overlay_text, TRANSPARENCIA_SESENTA_PORCIENTO, frame, 0.4, 0, frame)
        cv2.putText(frame, etiqueta, (x_etiqueta, y_etiqueta), cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_CINCUENTA_PORCIENTO, color, GROSOR_DOS_PIXELES, cv2.LINE_AA)

def dibujar_fps(frame, fps, numero_de_frame=None):
    texto = f"FPS: {fps:.1f}"
    if numero_de_frame is not None:
        texto += f" | Frame: {numero_de_frame}"
    (tw, th), _ = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_SESENTA_PORCIENTO, GROSOR_DOS_PIXELES)
    # Fondo semi-transparente
    overlay = frame.copy()
    punto_esquina_superior_izquierda_rectangulo = (8, 8)
    punto_esquina_inferior_derecha_rectangulo = (tw + 22, th + 22)
    cv2.rectangle(overlay, punto_esquina_superior_izquierda_rectangulo, punto_esquina_inferior_derecha_rectangulo, COLOR_TUPLA_NEGRO, GROSOR_RELLENO_COMPLETO)
    cv2.addWeighted(overlay, TRANSPARENCIA_SETENTA_PORCIENTO, frame, 0.3, 0, frame)
    # Texto
    punto_texto = (15, th + 15)
    cv2.putText(frame, texto, punto_texto, cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_SESENTA_PORCIENTO, COLOR_TUPLA_VERDE, GROSOR_DOS_PIXELES, cv2.LINE_AA)

def dibujar_panel_estadisticas(frame, estadisticas, posicion="top-right"):
    h, w = frame.shape[:2]
    ancho_maximo = max([cv2.getTextSize(f"{k}: {v}", cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_CINCUENTA_PORCIENTO, GROSOR_UN_PIXEL)[0][0] for k, v in estadisticas.items()])
    ancho_panel = ancho_maximo + 30
    alto_panel = len(estadisticas) * 25 + 20
    if posicion == "top-right":
        x_inicio = w - ancho_panel - 15
        y_inicio = 15
    else:
        x_inicio = 15
        y_inicio = 60
    overlay = frame.copy()
    punto_esquina_superior_izquierda_rectangulo = (x_inicio, y_inicio)
    punto_esquina_inferior_derecha_rectangulo = (x_inicio + ancho_panel, y_inicio + alto_panel)
    cv2.rectangle(overlay, punto_esquina_superior_izquierda_rectangulo, punto_esquina_inferior_derecha_rectangulo, COLOR_TUPLA_NEGRO, GROSOR_RELLENO_COMPLETO)
    cv2.addWeighted(overlay, TRANSPARENCIA_SETENTA_PORCIENTO, frame, 0.3, 0, frame)
    cv2.rectangle(frame, punto_esquina_superior_izquierda_rectangulo, punto_esquina_inferior_derecha_rectangulo, COLOR_TUPLA_BLANCO, GROSOR_DOS_PIXELES)
    dibujar_estadisticas(frame, estadisticas, x_inicio, y_inicio)

# endregion

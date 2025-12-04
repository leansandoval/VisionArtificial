# Funciones para dibujar overlays (Bounding Boxes, IDs, FPS, Zonas) sobre frames OpenCV.
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from src.constantes import *

# region Funciones Auxiliares

def cv2_put_text_utf8(frame, text, position, font_scale, color, thickness):
    """Dibuja texto con soporte UTF-8 usando PIL."""
    # Convertir frame BGR a RGB para PIL
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    # Intentar usar fuente TrueType, fallback a fuente por defecto
    try:
        # Tamaño de fuente basado en font_scale (aproximación)
        font_size = int(24 * font_scale)
        # Usar Arial Bold para efecto de negrita
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except:
        try:
            # Fallback a Arial normal si arialbd no existe
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # PIL usa RGB, convertir color BGR a RGB
    color_rgb = (color[2], color[1], color[0])
    
    # Dibujar el texto
    draw.text(position, text, font=font, fill=color_rgb)
    
    # Convertir de vuelta a BGR y actualizar frame
    frame_updated = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    frame[:] = frame_updated

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
    # Nombre de zona (esquina superior izquierda)
    if nombre_zona or id_zona is not None:
        etiqueta = nombre_zona if nombre_zona else f"Zone {id_zona}"
        # Usar ASCII aproximado para cv2.getTextSize (más rápido)
        etiqueta_ascii = etiqueta.encode('ascii', 'ignore').decode('ascii')
        (tw, th), _ = cv2.getTextSize(etiqueta_ascii if etiqueta_ascii else etiqueta, cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_SETENTA_PORCIENTO, GROSOR_TRES_PIXELES)
        min_xy = puntos.min(axis=0)
        x_etiqueta = max(int(min_xy[0]) + 8, 0)
        # Calcular posición base
        y_base = max(int(min_xy[1]) + 8, 0)
        # Dibujar rectángulo de fondo
        overlay_text = frame.copy()
        punto_esquina_superior_izquierda_rectangulo = (x_etiqueta - 6, y_base)
        punto_esquina_inferior_derecha_rectangulo = (x_etiqueta + tw + 6, y_base + th + 14)
        cv2.rectangle(overlay_text, punto_esquina_superior_izquierda_rectangulo, punto_esquina_inferior_derecha_rectangulo, COLOR_TUPLA_NEGRO, GROSOR_RELLENO_COMPLETO)
        cv2.addWeighted(overlay_text, TRANSPARENCIA_SESENTA_PORCIENTO, frame, 0.4, 0, frame)
        # Centrar texto verticalmente en el rectángulo (y_base + altura_rect/2 - th/2)
        y_etiqueta = y_base - 10 + th
        # Usar cv2_put_text_utf8 para soportar acentos
        cv2_put_text_utf8(frame, etiqueta, (x_etiqueta, y_etiqueta), ESCALA_FUENTE_SETENTA_PORCIENTO, color, GROSOR_TRES_PIXELES)

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

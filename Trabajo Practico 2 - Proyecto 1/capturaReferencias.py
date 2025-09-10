import cv2
import json
import numpy as np
from pathlib import Path
from typing import Dict, List

#region Constantes

NOMBRE_ARCHIVO_ETIQUETAS = "labels.json"
NOMBRE_ARCHIVO_REFERENCIAS = "referencias.json"

INDICE_CAMARA = 0  # Índice de la cámara (0 para la cámara por defecto)
RESOLUCION_VENTANA_ANCHO = 960
RESOLUCION_VENTANA_ALTO = 600

AREA_MINIMA_CONTORNO = 1000  # Área mínima del contorno para considerarlo válido

NUMERO_UNO_ASCII = 49  # Código ASCII de '1'
NUMERO_TRES_ASCII = 51  # Código ASCII de '3'
NUMERO_ESCAPE_ASCII = 27  # Código ASCII de 'Escape'

TRIPLA_COLOR_VERDE = (0, 255, 0)
TRIPLA_COLOR_ROJO = (0, 0, 255)

#endregion

#region Funciones

def cargar_etiquetas(path: Path) -> Dict[str, str]:
    # Carga el diccionario de etiquetas desde un archivo JSON.
    # Si el archivo no existe, devuelve un diccionario por defecto con las figuras básicas.
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    # Valores por defecto
    return {
        "1": "triangulo",
        "2": "rectangulo",
        "3": "circulo"
    }

def guardar_referencias(path: Path, referencias: Dict[str, List[List[List[int]]]]) -> None:
    # Guarda el diccionario de referencias en formato JSON.
    path.write_text(json.dumps(referencias, indent=2, ensure_ascii=False), encoding="utf-8")

#endregion

#region Main

def main() -> None:
    # Rutas a archivos
    ruta_etiquetas = Path(NOMBRE_ARCHIVO_ETIQUETAS)
    referencias_path = Path(NOMBRE_ARCHIVO_REFERENCIAS)

    # Carga etiquetas y referencias existentes
    etiquetas = cargar_etiquetas(ruta_etiquetas)
    if referencias_path.exists():
        try:
            referencias = json.loads(referencias_path.read_text(encoding="utf-8"))
        except Exception:
            referencias = {}
    else:
        referencias = {}

    # Inicializa la cámara.
    cam = cv2.VideoCapture(INDICE_CAMARA, cv2.CAP_DSHOW)
    if not cam.isOpened():
        raise RuntimeError("No se pudo abrir la cámara. Asegúrese de que esté conectada y disponible.")

    print("Presione las teclas numéricas (1-3) para guardar la figura actual.")
    print("Etiquetas disponibles:")
    for k, v in etiquetas.items():
        print(f"  {k}: {v}")
    print("Presione 'Esc' para salir.")

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        # Preprocesamiento: Gris -> Desenfoque -> Umbralizado Otsu Invertido
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, mask = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Cierre morfológico para rellenar huecos en el contorno
        # Apertura morfológica para reducir ruido
        # Esto ayuda a que las figuras con pequeñas rupturas en el borde se cierren correctamente
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

        # Detectar el contorno de mayor área (solo contornos externos)
        # Si quisiera detectar agujeros internos se podría usar cv2.RETR_TREE y filtra por jerarquía
        contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        mejor_contorno = None
        area_maxima = 0
        for c in contornos:
            area = cv2.contourArea(c)
            if area > area_maxima:
                area_maxima = area
                mejor_contorno = c

        # Preparar Imagen de Salida
        vista = frame.copy()
        mensaje = "No se detecta un contorno claro"
        color_texto = TRIPLA_COLOR_ROJO
        if mejor_contorno is not None and area_maxima >= AREA_MINIMA_CONTORNO:
            x, y, w, h = cv2.boundingRect(mejor_contorno)
            cv2.rectangle(vista, (x, y), (x + w, y + h), TRIPLA_COLOR_VERDE, 2)
            mensaje = "Presiona tecla (1-3) para guardar"
            color_texto = TRIPLA_COLOR_VERDE

        cv2.putText(vista, mensaje, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_texto, 2)

        vista_redimensionada = cv2.resize(vista, (RESOLUCION_VENTANA_ANCHO, RESOLUCION_VENTANA_ALTO))
        cv2.imshow("Captura de referencias", vista_redimensionada)
        
        mascara_redimensionada = cv2.resize(mask, (RESOLUCION_VENTANA_ANCHO, RESOLUCION_VENTANA_ALTO))
        cv2.imshow("Mascara", mascara_redimensionada)

        tecla = cv2.waitKey(1) & 0xFF
        if tecla == NUMERO_ESCAPE_ASCII:
            break
        
        # Si hay contorno válido y se presiona una tecla numérica entre 1 y 3
        if mejor_contorno is not None and area_maxima >= AREA_MINIMA_CONTORNO and NUMERO_UNO_ASCII <= tecla <= NUMERO_TRES_ASCII:
            numero_de_etiqueta = chr(tecla)
            if numero_de_etiqueta in etiquetas:
                # Convertir contorno a lista de listas [x, y]
                lista_de_contornos: List[List[int]] = []
                for punto in mejor_contorno:
                    # Punto tiene forma [[x, y]]
                    lista_de_contornos.append([int(punto[0][0]), int(punto[0][1])])
                # Añadir a las referencias
                referencias.setdefault(numero_de_etiqueta, []).append(lista_de_contornos)
                guardar_referencias(referencias_path, referencias)
                print(f"Guardado contorno (puntos={len(lista_de_contornos)}) para etiqueta {numero_de_etiqueta} ({etiquetas[numero_de_etiqueta]})")

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

#endregion

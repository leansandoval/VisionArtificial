import cv2
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple

#region Constantes

NOMBRE_ARCHIVO_ETIQUETAS = "labels.json"
NOMBRE_ARCHIVO_REFERENCIAS = "referencias.json"

INDICE_CAMARA = 0  # Índice de la cámara (0 para la cámara por defecto)

NUMERO_ESCAPE_ASCII = 27  # Código ASCII de 'Escape'

RESOLUCION_VENTANA_ANCHO = 960
RESOLUCION_VENTANA_ALTO = 600

TRIPLA_COLOR_VERDE = (0, 255, 0)
TRIPLA_COLOR_AZUL = (255, 0, 0)
TRIPLA_COLOR_ROJO = (0, 0, 255)

#endregion

#region Funciones

def cargar_etiquetas(path: Path) -> Dict[str, str]:
    # Carga el diccionario de etiquetas desde un archivo JSON.
    # Si el archivo no existe, devuelve un diccionario por defecto con algunas figuras básicas.
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    # Valores por defecto
    return {
        "1": "triangulo",
        "2": "rectangulo",
        "3": "circulo",
    }

def cargar_referencias(path: Path) -> List[Tuple[str, np.ndarray]]:
    # Carga los contornos de referencia desde un archivo JSON.
    # Devuelve una lista de tuplas (etiqueta, contorno), donde cada contorno es un array (n, 1, 2).
    # Si el archivo no existe o está vacío, se devuelve una lista vacía.
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    referencias = []
    for etiqueta, contornos in data.items():
        for contorno in contornos:
            # Cada contorno es una lista de [x, y]
            arr = np.array(contorno, dtype=np.int32).reshape((-1, 1, 2))
            referencias.append((etiqueta, arr))
    return referencias

#endregion

#region Main

def main() -> None:
    etiquetas = cargar_etiquetas(Path(NOMBRE_ARCHIVO_ETIQUETAS))
    referencias = cargar_referencias(Path(NOMBRE_ARCHIVO_REFERENCIAS))
    if not referencias:
        raise RuntimeError("No se encontraron referencias. Ejecute captura_referencias.py para guardar contornos de referencia.")

    # Crear ventana de configuración y barras deslizantes
    config_win = "Configuracion"
    cv2.namedWindow(config_win, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(config_win, 400, 200)
    cv2.createTrackbar("Umbral", config_win, 127, 255, lambda x: None)
    cv2.createTrackbar("Auto", config_win, 1, 1, lambda x: None)
    cv2.createTrackbar("Kernel", config_win, 3, 20, lambda x: None)
    cv2.createTrackbar("MatchTh", config_win, 15, 100, lambda x: None)
    cv2.createTrackbar("AreaMin", config_win, 500, 10000, lambda x: None)

    # Abrir cámara
    cam = cv2.VideoCapture(INDICE_CAMARA, cv2.CAP_DSHOW)
    if not cam.isOpened():
        raise RuntimeError("No se pudo abrir la cámara. Asegúrese de que esté conectada y disponible.")

    while True:
        ret, frame = cam.read()
        if not ret:
            break
        
        # Obtener parámetros de configuración
        thresh_val = cv2.getTrackbarPos("Umbral", config_win)
        auto = cv2.getTrackbarPos("Auto", config_win)
        kernel_size = cv2.getTrackbarPos("Kernel", config_win)
        match_val = cv2.getTrackbarPos("MatchTh", config_win)
        area_min = cv2.getTrackbarPos("AreaMin", config_win)

        # Asegurar valores válidos
        if kernel_size < 1:
            kernel_size = 1
        
        # El kernel debe ser impar para operaciones morfológicas
        kernel_size = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
        match_threshold = match_val / 100.0  # Normalizar a [0,1]

        # Preprocesamiento: gris, desenfoque
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Umbralización manual o automática (Otsu)
        if auto:
            _, mask = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        else:
            _, mask = cv2.threshold(blur, thresh_val, 255, cv2.THRESH_BINARY_INV)

        # Operaciones morfológicas para limpiar la máscara
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        
        # Cierre para rellenar huecos
        # Apertura para quitar pequeños objetos
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Detectar contornos externos
        contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Copia de la imagen para anotaciones
        annotated = frame.copy()

        for c in contornos:
            area = cv2.contourArea(c)
            if area < area_min:
                continue  # Descartar contornos pequeños

            # Calcular bounding box para dibujar
            x, y, w, h = cv2.boundingRect(c)
            color = TRIPLA_COLOR_ROJO
            etiqueta = "Desconocido"

            # Comparar con referencias
            minima_distancia = float("inf")
            mejor_label = None
            for ref_label, ref_contour in referencias:
                dist = cv2.matchShapes(c, ref_contour, cv2.CONTOURS_MATCH_I3, 0.0)
                if dist < minima_distancia:
                    minima_distancia = dist
                    mejor_label = ref_label

            # Decidir si es una coincidencia válida
            if minima_distancia < match_threshold and mejor_label is not None:
                color = TRIPLA_COLOR_VERDE
                #color = TRIPLA_COLOR_AZUL
                nombre = etiquetas.get(mejor_label, mejor_label)
                etiqueta = nombre
            else:
                etiqueta = "Desconocido"

            # Dibujar rectángulo y etiqueta
            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
            cv2.putText(
                annotated,
                etiqueta,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2,
            )

        # Mostrar resultados
        vista_redimensionada = cv2.resize(annotated, (RESOLUCION_VENTANA_ANCHO, RESOLUCION_VENTANA_ALTO))
        cv2.imshow("Clasificador de formas", vista_redimensionada)

        mascara_redimensionada = cv2.resize(mask, (RESOLUCION_VENTANA_ANCHO, RESOLUCION_VENTANA_ALTO))
        cv2.imshow("Mascara", mascara_redimensionada)

        tecla = cv2.waitKey(1) & 0xFF
        if tecla == NUMERO_ESCAPE_ASCII:
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

#endregion

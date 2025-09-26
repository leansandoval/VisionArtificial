import cv2
import numpy as np
import glob
import os
import yaml
from datetime import datetime

#region Constantes

ANCHO_VENTANA = 800 # Ancho para mostrar las imágenes a calibrar
CANTIDAD_IMAGENES_MINIMA_RECOMENDADA = 10
DELAY_ENTRE_IMAGENES_MS = 500  # Tiempo para mostrar cada imágen con esquinas detectadas
EXTENSION_IMAGEN = ".jpeg"
RUTA_IMAGENES = "fotos_calibracion" # Carpeta donde se encuentran las imágenes
# Número de esquinas internas (no de cuadros)
TAMANIO_TABLERO_AJEDREZ = (7, 7)    # 7x7 esquinas internas (Para un tablero 8x8 cuadros) - 9x6 suele ser estándar
TAMANIO_CUADRADO_MM = 25    # Tamaño del cuadrado en mm (Solo informativo)
TITULO_VENTANA = "Calibracion de Camara"

#endregion

os.makedirs(RUTA_IMAGENES, exist_ok=True)

def calibrar():
    # Preparar puntos del mundo (0,0,0), (1,0,0), ...
    puntos_objeto = np.zeros((TAMANIO_TABLERO_AJEDREZ[0] * TAMANIO_TABLERO_AJEDREZ[1], 3), np.float32)
    puntos_objeto[:, :2] = np.mgrid[0:TAMANIO_TABLERO_AJEDREZ[0], 0:TAMANIO_TABLERO_AJEDREZ[1]].T.reshape(-1, 2)
    puntos_objeto *= TAMANIO_CUADRADO_MM  # Tamaño Físico (opcional)

    puntos_objeto_3d, puntos_imagen_2d = [], []
    imagenes = glob.glob(os.path.join(RUTA_IMAGENES, f"*{EXTENSION_IMAGEN}"))

    if len(imagenes) < CANTIDAD_IMAGENES_MINIMA_RECOMENDADA:
        print(f"Se recomienda al menos {CANTIDAD_IMAGENES_MINIMA_RECOMENDADA}-{CANTIDAD_IMAGENES_MINIMA_RECOMENDADA + 5} imágenes para buena calibración.")
        
    for archivo_imagen in imagenes:
        imagen = cv2.imread(archivo_imagen)
        if imagen is None:
            print(f"Error al cargar imagen: {archivo_imagen}")
            continue
        
        imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        encontrado, esquinas = cv2.findChessboardCorners(imagen_gris, TAMANIO_TABLERO_AJEDREZ, None)
        if encontrado:
            puntos_objeto_3d.append(puntos_objeto)
            esquinas_refinadas = cv2.cornerSubPix(
                imagen_gris, esquinas, (11, 11), (-1, -1),
                (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            )
            puntos_imagen_2d.append(esquinas_refinadas)
            cv2.drawChessboardCorners(imagen, TAMANIO_TABLERO_AJEDREZ, esquinas_refinadas, encontrado)
            escala = ANCHO_VENTANA / imagen.shape[1]
            imagen_a_mostrar = cv2.resize(imagen, (ANCHO_VENTANA, int(imagen.shape[0] * escala)))
            cv2.imshow(TITULO_VENTANA, imagen_a_mostrar)
            cv2.waitKey(DELAY_ENTRE_IMAGENES_MS)

    cv2.destroyAllWindows()

    if not puntos_objeto_3d:
        print("No se detectaron patrones de ajedrez.")
        return None

    # Calibrar cámara
    resultado, matriz_camara, coeficientes_distorsion, vectores_rotacion, vectores_traslacion = cv2.calibrateCamera(
        puntos_objeto_3d, puntos_imagen_2d, imagen_gris.shape[::-1], None, None
    )

    print("\n=== RESULTADOS DE CALIBRACIÓN ===")
    print(f"Éxito en calibración: {resultado}")
    print(f"fx = {matriz_camara[0, 0]:.2f}   fy = {matriz_camara[1, 1]:.2f}")
    print(f"cx = {matriz_camara[0, 2]:.2f}   cy = {matriz_camara[1, 2]:.2f}")
    print(f"Distorsión = {coeficientes_distorsion.ravel()}")

    # Guardar YAML compatible
    datos_calibracion = {
        "Camera": {
            "name": "Mi camara calibrada",
            "setup": "monocular",
            "model": "perspective",
            "fx": float(matriz_camara[0, 0]),
            "fy": float(matriz_camara[1, 1]),
            "cx": float(matriz_camara[0, 2]),
            "cy": float(matriz_camara[1, 2]),
            "k1": float(coeficientes_distorsion[0][0]),
            "k2": float(coeficientes_distorsion[0][1]),
            "p1": float(coeficientes_distorsion[0][2]),
            "p2": float(coeficientes_distorsion[0][3]),
            "k3": float(coeficientes_distorsion[0][4]) if coeficientes_distorsion.shape[1] >= 5 else 0.0,
            "cols": int(imagen_gris.shape[1]),
            "rows": int(imagen_gris.shape[0]),
            "fps": 30,
            "color_order": "BGR"
        },
        "Mapping": {}  # Podés dejarlo vacío o agregar parámetros más adelante
    }

    archivo_de_salida = f"config_calibracion_{datetime.now().strftime('%Y%m%d_%H%M')}.yaml"
    with open(archivo_de_salida, "w") as archivo:
        yaml.dump(datos_calibracion, archivo,  default_flow_style=False)
    print(f"Archivo guardado: {archivo_de_salida}")

    return matriz_camara, coeficientes_distorsion

if __name__ == "__main__":
    calibrar()

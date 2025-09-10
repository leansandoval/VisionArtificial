import cv2
import numpy as np
import json
from pathlib import Path
from joblib import load

ruta_modelo = Path("modelo.joblib")
ruta_etiquetas = Path("labels.json")
indice_camara = 0
area_minima = 3000  # no encuentro con cual numero queda mejor, me sigue tomando ruido

# === CARGA MODELO ENTRENADO ===
if not ruta_modelo.exists():
    raise FileNotFoundError("No se encontró el modelo entrenado. Ejecutá 'entrenador.py' primero.")
modelo = load(ruta_modelo)

etiquetas = {
    "1": "triángulo",
    "2": "rectángulo",
    "3": "círculo"
}
if ruta_etiquetas.exists():
    etiquetas = json.loads(ruta_etiquetas.read_text(encoding="utf-8"))

def calcular_invariantes_hu(contorno):
    #Devuelve los 7 invariantes de Hu de la imagen que detecta
    momentos = cv2.moments(contorno)
    hu = cv2.HuMoments(momentos).flatten()
    hu_log = np.sign(hu) * np.log10(np.abs(hu) + 1e-30)
    return hu_log.reshape(1, -1)

def preprocesar_imagen(frame):
    #Mascara que convierte la imagen a binaria
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    desenfoque = cv2.GaussianBlur(gris, (5, 5), 0)
    _, binaria = cv2.threshold(desenfoque, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    binaria = cv2.morphologyEx(binaria, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return binaria

def obtener_contorno_principal(mascara, area_min):
    #Devuelve el contorno más grande
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contornos_grandes = [c for c in contornos if cv2.contourArea(c) >= area_min]
    if contornos_grandes:
        return max(contornos_grandes, key=cv2.contourArea)
    return None

# === Camara ===
camara = cv2.VideoCapture(indice_camara, cv2.CAP_DSHOW)
if not camara.isOpened():
    raise RuntimeError("No se pudo acceder a la cámara. Cerrá otras aplicaciones que la estén usando.")

while True:
    ok, imagen = camara.read()
    if not ok:
        break

    mascara = preprocesar_imagen(imagen)
    contorno = obtener_contorno_principal(mascara, area_minima)
    vista = imagen.copy()

    if contorno is not None:
        # Calcula descriptores
        hu = calcular_invariantes_hu(contorno)
        clase_predicha = modelo.predict(hu)[0]
        nombre_figura = etiquetas.get(str(int(clase_predicha)), f"Etiqueta {int(clase_predicha)}")

        # Dibuja el rectángulo alrededor
        x, y, ancho, alto = cv2.boundingRect(contorno)
        cv2.rectangle(vista, (x, y), (x + ancho, y + alto), (0, 255, 0), 2)

        # Muestra la etiqueta con el nombre de la figura
        cv2.rectangle(vista, (0, 0), (vista.shape[1], 60), (0, 0, 0), -1)
        cv2.putText(vista, f"FIGURA: {nombre_figura.upper()}", (20, 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 2)

    else:
        # No se detecta ninguna figura clara
        cv2.rectangle(vista, (0, 0), (vista.shape[1], 60), (0, 0, 0), -1)
        cv2.putText(vista, "NO SE DETECTA UNA FIGURA CLARA", (20, 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (100, 100, 255), 2)

    # Res:
    cv2.imshow("Vista de Clasificación", vista)
    cv2.imshow("Máscara binaria", mascara)

    # Sale con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camara.release()
cv2.destroyAllWindows()

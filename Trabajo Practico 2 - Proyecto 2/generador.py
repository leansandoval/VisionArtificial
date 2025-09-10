import cv2
import numpy as np
import csv
import json
from pathlib import Path

ruta_dataset = Path("dataset.csv")
ruta_etiquetas = Path("labels.json")
indice_camara = 0
area_minima = 3000
etiqueta_activa = "1"  # por defecto
mostrar_mascara = True

etiquetas = {
    "1": "triángulo",
    "2": "rectángulo",
    "3": "círculo"
}
if ruta_etiquetas.exists():
    etiquetas = json.loads(ruta_etiquetas.read_text(encoding="utf-8"))

def calcular_invariantes_hu(contorno):
    #Devuelve los 7 invariantes de Hu
    momentos = cv2.moments(contorno)
    hu = cv2.HuMoments(momentos).flatten()
    hu_log = np.sign(hu) * np.log10(np.abs(hu) + 1e-30)
    return hu_log

def preprocesar_imagen(frame):
    #Convierte la imagen a escala de grises y luego binaria
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    desenfoque = cv2.GaussianBlur(gris, (5, 5), 0)
    _, binaria = cv2.threshold(desenfoque, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    binaria = cv2.morphologyEx(binaria, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return binaria

def obtener_mayor_contorno(mascara, area_min):
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contornos_validos = [c for c in contornos if cv2.contourArea(c) >= area_min]
    if contornos_validos:
        return max(contornos_validos, key=cv2.contourArea)
    return None

def guardar_en_csv(ruta, fila):
    #Guarda una fila en el archivo CSV y si no existe, crea el encabezado
    crear_encabezado = not ruta.exists()
    with open(ruta, "a", newline="") as archivo:
        escritor = csv.writer(archivo)
        if crear_encabezado:
            escritor.writerow([f"h{i}" for i in range(1, 8)] + ["etiqueta"])
        escritor.writerow(fila)

# Camara
camara = cv2.VideoCapture(indice_camara, cv2.CAP_DSHOW)
if not camara.isOpened():
    raise RuntimeError("No se pudo abrir la cámara. Cerrá otras aplicaciones que la estén usando.")

print("Presioná 1, 2 o 3 para cambiar la figura activa.")
print("Presioná ESPACIO para guardar una muestra.")
print("Presioná M para ocultar/mostrar la máscara.")
print("Presioná Q para salir.")

while True:
    ok, imagen = camara.read()
    if not ok:
        break

    mascara = preprocesar_imagen(imagen)
    contorno = obtener_mayor_contorno(mascara, area_minima)
    vista = imagen.copy()

    # Dibuja el contorno si existe
    if contorno is not None:
        x, y, ancho, alto = cv2.boundingRect(contorno)
        cv2.rectangle(vista, (x, y), (x + ancho, y + alto), (0, 255, 0), 2)
        texto = "LISTO PARA GUARDAR (ESPACIO)"
        color = (0, 255, 0)
    else:
        texto = "NO SE DETECTA UNA FIGURA GRANDE"
        color = (0, 0, 255)

    # Muestra etiqueta activa
    nombre = etiquetas.get(etiqueta_activa, "¿?")
    cv2.putText(vista, f"Etiqueta activa: {etiqueta_activa} ({nombre})", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(vista, texto, (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # Muestra imágenes
    cv2.imshow("Vista del Generador", vista)
    if mostrar_mascara:
        cv2.imshow("Máscara binaria", mascara)
    else:
        cv2.destroyWindow("Máscara binaria")

    # Captura teclado
    tecla = cv2.waitKey(1) & 0xFF
    if tecla == ord('q'):
        break
    elif tecla == ord('m'):
        mostrar_mascara = not mostrar_mascara
    elif tecla in [ord(str(i)) for i in range(1, 10)]:
        etiqueta_activa = chr(tecla)
        print(f"Etiqueta activa cambiada a: {etiqueta_activa} ({etiquetas.get(etiqueta_activa, '?')})")
    elif tecla == 32 and contorno is not None:  # ESPACIO
        hu = calcular_invariantes_hu(contorno)
        fila = list(hu) + [int(etiqueta_activa)]
        guardar_en_csv(ruta_dataset, fila)
        print("Muestra guardada:", fila)

camara.release()
cv2.destroyAllWindows()

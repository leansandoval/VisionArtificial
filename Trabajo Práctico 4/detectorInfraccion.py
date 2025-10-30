from ultralytics import YOLO
import cv2
import math
from collections import deque
import time

MODELO = "yolov8n.pt"
INDICE_CAMARA = 0
UMBRAL_DISTANCIA = 0.45 #jugar con la distancia para mejorar precision
FRAMES_CONSECUTIVOS = 4 #cada tantos frames verifica, jugar con este valor tmb capaz mejora o empeora
MOSTRAR_FPS = True

def centro(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2, (y1 + y2) / 2)

def dimensiones(box):
    x1, y1, x2, y2 = box
    return (x2 - x1, y2 - y1)

def distancia_normalizada(p, q, ref):
    #distancia normal respecto a una referencia, tomamos la cara
    return math.dist(p, q) / ref if ref > 0 else float('inf')

modelo = YOLO(MODELO)
camara = cv2.VideoCapture(INDICE_CAMARA)
if not camara.isOpened():
    raise RuntimeError("No se pudo acceder a la cámara.")

historial = deque(maxlen=FRAMES_CONSECUTIVOS)
prev_time = time.time()

color_fondo_alerta = (0, 0, 255)
color_texto_alerta = (255, 255, 255)
color_fondo_info = (50, 50, 50)
color_texto_info = (255, 255, 0)

while True:
    ret, frame = camara.read()
    if not ret:
        break

    resultados = modelo(frame, verbose=False)[0]
    personas, celulares = [], []

    for box, cls in zip(resultados.boxes.xyxy.tolist(), resultados.boxes.cls.tolist()):
        x1, y1, x2, y2 = map(int, box)
        etiqueta = modelo.names[int(cls)]
        if etiqueta == "person":
            personas.append((x1, y1, x2, y2))
        elif etiqueta in ("cell phone", "mobile phone", "phone"):
            celulares.append((x1, y1, x2, y2))

    imagen = frame.copy()
    uso_celular = False

    for pbox in personas:
        px1, py1, px2, py2 = pbox
        pcentro = centro(pbox)
        ph = py2 - py1
        ancho, alto = dimensiones(pbox)
        ex = int(ancho * 0.25)
        ey = int(alto * 0.25)
        ex1, ey1, ex2, ey2 = px1 - ex, py1 - ey, px2 + ex, py2 + ey

        for phbox in celulares:
            phcentro = centro(phbox)
            d = distancia_normalizada(pcentro, phcentro, max(1, ph))
            dentro = (phcentro[0] >= ex1 and phcentro[0] <= ex2 and phcentro[1] >= ey1 and phcentro[1] <= ey2)
            if d < UMBRAL_DISTANCIA or dentro:
                uso_celular = True
                cv2.line(imagen, (int(pcentro[0]), int(pcentro[1])), (int(phcentro[0]), int(phcentro[1])), (0, 0, 255), 2)
                cv2.circle(imagen, (int(phcentro[0]), int(phcentro[1])), 6, (0, 0, 255), -1)
                break
        if uso_celular:
            break

    historial.append(1 if uso_celular else 0)
    evento_confirmado = sum(historial) >= int(0.7 * historial.maxlen)

    if uso_celular:
        cv2.rectangle(imagen, (20, 20), (580, 70), color_fondo_info, -1)
        cv2.putText(imagen, "Posible uso de celular detectado", (30, 55),
                    cv2.FONT_HERSHEY_DUPLEX, 0.8, color_texto_info, 2, cv2.LINE_AA)

    if evento_confirmado:
        cv2.rectangle(imagen, (15, 80), (620, 135), color_fondo_alerta, -1)
        cv2.putText(imagen, "Distraccion confirmada: uso de celular", (25, 120),
                    cv2.FONT_HERSHEY_DUPLEX, 0.9, color_texto_alerta, 2, cv2.LINE_AA)

    #Se puede sacar de ultima, sirve a modo referencia nomas
    if MOSTRAR_FPS:
        now = time.time()
        fps = 1.0 / (now - prev_time)
        prev_time = now
        cv2.putText(imagen, f"FPS: {fps:.1f}", (20, frame.shape[0]-20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 2)

    cv2.imshow("Deteccion de uso de celular", imagen)
    tecla = cv2.waitKey(1) & 0xFF
    if tecla == 27:
        break

camara.release()
cv2.destroyAllWindows()

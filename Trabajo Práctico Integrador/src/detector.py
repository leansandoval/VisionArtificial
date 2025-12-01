# Detector modular usando Ultralytics YOLO.
# Esta clase carga un modelo Ultralytics y expone un método detect(frame)
# que devuelve detecciones filtradas para la clase 'person'.
# Se soporta pasar una ruta a pesos personalizados (por ejemplo, tu YOLOv11.pt).

from ultralytics import YOLO
import numpy as np

#region Constantes

DISPOSITIVO_POR_DEFECTO = 'cpu'
TAMANO_IMAGEN = 640  # Tamaño de imagen para inferencia
ETIQUETA_PERSONA = 'person'
UMBRAL_CONFIANZA_DEFECTO = 0.3
YOLO_DEFAULT_WEIGHTS = 'yolov8n.pt'  # Modelo ligero por defecto

#endregion

class Detector:
    
    # Si pesos es None se carga un modelo ligero por defecto
    def __init__(self, pesos: str = None, dispositivo: str = DISPOSITIVO_POR_DEFECTO, umbral_confianza: float = UMBRAL_CONFIANZA_DEFECTO, tam_imagen: int = TAMANO_IMAGEN):
        self.pesos = pesos or YOLO_DEFAULT_WEIGHTS
        self.dispositivo = dispositivo
        self.umbral_confianza = umbral_confianza
        self.tam_imagen = tam_imagen
        self.modelo = None
        self._cargar_modelo()

    # Cargar modelo Ultralytics. Si tenes un .pt personalizado (p.e. YOLOv11), pone la ruta en pesos.
    # Forzar a CPU si no hay hardware compatible (CUDA)
    def _cargar_modelo(self):
        self.modelo = YOLO(self.pesos)
        try:
            self.modelo.to(self.dispositivo)
        except Exception:
            pass

    # Ejecuta inferencia y devuelve lista de detections:
    # [{bbox: [x1,y1,x2,y2], conf: float, cls: int, label: str}]
    # Solo devuelve detecciones con label 'person' para este proyecto.
    def detectar(self, frame: np.ndarray):
        resultados = self.modelo.predict(frame, verbose=False, imgsz=self.tam_imagen, half=False)  
        salida = []
        if len(resultados) == 0:
            return salida
        resultado = resultados[0]
        cajas = resultado.boxes
        # cajas.xyxy, cajas.conf, cajas.cls
        for i in range(len(cajas)):
            confianza = float(cajas.conf[i])
            id_clase = int(cajas.cls[i])
            etiqueta = self.modelo.names.get(id_clase, str(id_clase))
            if confianza < self.umbral_confianza:
                continue
            # Algunos modelos usan diferentes nombres; dejamos solo 'person'
            if etiqueta.lower() != ETIQUETA_PERSONA and etiqueta.lower() != ETIQUETA_PERSONA.lower():
                continue
            xyxy = cajas.xyxy[i].cpu().numpy().tolist()
            salida.append({'bbox': [float(x) for x in xyxy], 'conf': confianza, 'cls': id_clase, 'label': etiqueta})
        return salida

if __name__ == '__main__':
    print('Detector module')

# Detector modular usando Ultralytics YOLO.
# Esta clase carga un modelo Ultralytics y expone un método detect(frame)
# que devuelve detecciones filtradas para la clase 'person'.
# Se soporta pasar una ruta a pesos personalizados (por ejemplo, tu YOLOv11.pt).

from ultralytics import YOLO
import numpy as np

YOLO_DEFAULT_WEIGHTS = 'yolov8n.pt'  # Modelo ligero por defecto
IMAGE_SIZE = 640  # Tamaño de imagen para inferencia
LABEL_PERSON = 'person'

class Detector:
    
    # Si weights es None se carga un modelo ligero por defecto
    def __init__(self, weights: str = None, device: str = 'cpu', conf_thres: float = 0.3, imgsz: int = IMAGE_SIZE):
        self.weights = weights or YOLO_DEFAULT_WEIGHTS
        self.device = device
        self.conf_thres = conf_thres
        self.imgsz = imgsz
        self.model = None
        self._load()

    # Cargar modelo Ultralytics. Si tenes un .pt personalizado (p.e. YOLOv11), pon la ruta en weights.
    # Forzar a CPU si no hay hardware compatible
    def _load(self):
        self.model = YOLO(self.weights)
        try:
            self.model.to(self.device)
        except Exception:
            pass

    # Ejecuta inferencia y devuelve lista de detections:
    # [{bbox: [x1,y1,x2,y2], conf: float, cls: int, label: str}]
    # Solo devuelve detecciones con label 'person' para este proyecto.
    def detect(self, frame: np.ndarray):
        # Retorna una lista de Results
        results = self.model.predict(frame, verbose=False, imgsz=self.imgsz, half=False)  
        out = []
        if len(results) == 0:
            return out
        r = results[0]
        boxes = r.boxes
        # boxes.xyxy, boxes.conf, boxes.cls
        for i in range(len(boxes)):
            conf = float(boxes.conf[i])
            cls_id = int(boxes.cls[i])
            label = self.model.names.get(cls_id, str(cls_id))
            if conf < self.conf_thres: continue
            # Algunos modelos usan diferentes nombres; dejamos solo 'person'
            if label.lower() != LABEL_PERSON and label.lower() != LABEL_PERSON.lower(): continue
            xyxy = boxes.xyxy[i].cpu().numpy().tolist()
            out.append({
                'bbox': [float(x) for x in xyxy],
                'conf': conf,
                'cls': cls_id,
                'label': label
            })
        return out

if __name__ == '__main__':
    print('Detector module')

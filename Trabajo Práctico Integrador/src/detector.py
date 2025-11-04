"""Detector modular usando Ultralytics YOLO.

Esta clase carga un modelo Ultralytics y expone un método detect(frame)
que devuelve detecciones filtradas para la clase 'person'.
Se soporta pasar una ruta a pesos personalizados (por ejemplo, tu YOLOv11.pt).
"""
from ultralytics import YOLO
import numpy as np

class Detector:
    def __init__(self, weights: str = None, device: str = 'cpu', conf_thres: float = 0.3, imgsz: int = 640):
        # Si weights es None se carga un modelo ligero por defecto
        self.weights = weights or 'yolov8n.pt'
        self.device = device
        self.conf_thres = conf_thres
        self.imgsz = imgsz
        self.model = None
        self._load()

    def _load(self):
        # Cargar modelo Ultralytics. Si tienes un .pt personalizado (p.e. YOLOv11), pon la ruta en weights.
        self.model = YOLO(self.weights)
        # Forzar a cpu si no hay hardware compatible
        try:
            self.model.to(self.device)
        except Exception:
            pass

    def detect(self, frame: np.ndarray):
        """Ejecuta inferencia y devuelve lista de detections:
        [{bbox: [x1,y1,x2,y2], conf: float, cls: int, label: str}]
        Solo devuelve detecciones con label 'person' para este proyecto.
        """
        results = self.model.predict(frame, verbose=False, imgsz=self.imgsz, half=False)  # retorna una lista de Results
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
            if conf < self.conf_thres:
                continue
            if label.lower() != 'person' and label.lower() != 'person'.lower():
                # Algunos modelos usan diferentes nombres; dejamos solo 'person'
                continue
            xyxy = boxes.xyxy[i].cpu().numpy().tolist()
            out.append({'bbox': [float(x) for x in xyxy], 'conf': conf, 'cls': cls_id, 'label': label})
        return out


if __name__ == '__main__':
    print('Detector module')

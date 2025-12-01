"""Tracker sencillo basado en IoU / centroid matching.
Este tracker no es ByteTrack, pero ofrece IDs consistentes entre frames
y una interfaz para reemplazar la implementación por ByteTrack más adelante.
"""
from typing import List, Dict
import numpy as np

def iou(boxA, boxB):
    # box: [x1,y1,x2,y2]
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interW = max(0, xB - xA)
    interH = max(0, yB - yA)
    interArea = interW * interH
    boxAArea = max(0, boxA[2]-boxA[0]) * max(0, boxA[3]-boxA[1])
    boxBArea = max(0, boxB[2]-boxB[0]) * max(0, boxB[3]-boxB[1])
    if boxAArea + boxBArea - interArea == 0:
        return 0.0
    return interArea / (boxAArea + boxBArea - interArea)

class SimpleTracker:
    def __init__(self, iou_threshold: float = 0.3, max_lost: int = 30):
        self.iou_th = iou_threshold
        self.max_lost = max_lost
        self.next_id = 1
        self.tracks: Dict[int, Dict] = {}  # id -> {bbox, lost}

    def update(self, detections: List[Dict]):
        # detections: list of dicts with 'bbox'
        boxes = [d['bbox'] for d in detections]
        assigned = {}

        # Match existing tracks to new boxes by IoU
        if len(self.tracks) > 0 and len(boxes) > 0:
            track_ids = list(self.tracks.keys())
            iou_matrix = np.zeros((len(track_ids), len(boxes)), dtype=np.float32)
            for i, tid in enumerate(track_ids):
                tb = self.tracks[tid]['bbox']
                for j, b in enumerate(boxes):
                    iou_matrix[i, j] = iou(tb, b)
            # Greedy match
            for _ in range(min(iou_matrix.shape[0], iou_matrix.shape[1])):
                idx = np.unravel_index(np.argmax(iou_matrix), iou_matrix.shape)
                i, j = idx
                if iou_matrix[i, j] < self.iou_th:
                    break
                tid = track_ids[i]
                assigned[tid] = j
                iou_matrix[i, :] = -1
                iou_matrix[:, j] = -1

        # Update assigned tracks
        updated_tracks = {}
        used_boxes = set()
        for tid, data in self.tracks.items():
            if tid in assigned:
                j = assigned[tid]
                bbox = boxes[j]
                updated_tracks[tid] = {'bbox': bbox, 'lost': 0}
                used_boxes.add(j)
            else:
                # increment lost
                l = data.get('lost', 0) + 1
                if l <= self.max_lost:
                    updated_tracks[tid] = {'bbox': data['bbox'], 'lost': l}

        # Create new tracks for unassigned boxes
        for j, b in enumerate(boxes):
            if j in used_boxes:
                continue
            tid = self.next_id
            self.next_id += 1
            updated_tracks[tid] = {'bbox': b, 'lost': 0}

        self.tracks = updated_tracks

        # Build list of tracks with their last bbox
        out = []
        for tid, data in self.tracks.items():
            out.append({'track_id': tid, 'bbox': data['bbox'], 'lost': data['lost']})
        return out


if __name__ == '__main__':
    print('SimpleTracker module')

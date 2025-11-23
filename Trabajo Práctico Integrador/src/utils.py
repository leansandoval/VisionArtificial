import collections
import time

TAMANIO_VENTANA_PROMEDIO_FPS = 16

# Calcula los FPS promedio usando una ventana deslizante de timestamps.
class ContadorFPS:
    def __init__(self, tamanio_ventana_promedio_fps=TAMANIO_VENTANA_PROMEDIO_FPS):
        self.timestamps = collections.deque(maxlen=tamanio_ventana_promedio_fps)

    # Registra el timestamp actual (momento de procesamiento del frame)
    # Se debe llamar una vez por frame procesado
    def registrar_tiempo(self):
        self.timestamps.append(time.time())

    # Retorna el FPS promedio calculado
    def obtener_fps(self):
        if len(self.timestamps) < 2:
            return 0.0
        duracion = self.timestamps[-1] - self.timestamps[0]
        if duracion == 0:
            return 0.0
        return (len(self.timestamps) - 1) / duracion
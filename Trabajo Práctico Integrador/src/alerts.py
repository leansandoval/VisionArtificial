# Módulo de alertas: implementa alertas locales (beep/flash/log).
# Este módulo mantiene un cooldown por identificador de track y una señal
# visual simple (flash) que puede consultarse desde la UI.
import time
from threading import Lock

class Alerts:
    def __init__(self, cooldown_seconds: int = 10):
        self.cooldown = cooldown_seconds
        self.last_alert_time = {}  # key -> timestamp
        self.lock = Lock()
        # Flash visual (punto rojo en pantalla) persistente tras una alerta
        self.flash_on = False

    def _can_alert(self, key: str):
        with self.lock:
            t = time.time()
            last = self.last_alert_time.get(key, 0)
            if t - last >= self.cooldown:
                self.last_alert_time[key] = t
                return True
            return False

    def local_beep(self):
        # Reemplazo del beep: activar flash visual persistente (punto rojo)
        self.flash_on = True

    def set_flash_state(self, state: bool):
        """Permite activar/desactivar el flash visual segun haya personas en zona."""
        self.flash_on = state

    def should_flash(self) -> bool:
        """Indica si el punto rojo debe mostrarse/parpadear en este momento."""
        return self.flash_on

    #Genera una alerta local para el `track_id` con `text`.
    # Retorna True si la alerta fue emitida (respetando cooldown), False si fue ignorada.
    def alert_for_track(self, track_id: int, text: str):
        key = f'track_{track_id}'
        if not self._can_alert(key):
            return False
        # Local
        print(f'[ALERTA] {text}')
        try:
            self.local_beep()
        except Exception:
            pass
        return True

if __name__ == '__main__':
    a = Alerts(5)
    a.alert_for_track(1, 'Prueba de alerta')

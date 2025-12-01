# Módulo de alertas: implementa alertas locales (beep/flash/log).
# Este módulo mantiene un cooldown por identificador de track y una señal
# visual simple (flash) que puede consultarse desde la UI.
import time
from threading import Lock

SEGUNDOS_ESPERA_DEFECTO = 10  # Espera entre alertas del mismo track

class Alertas:
    
    def __init__(self, segundos_espera: int = SEGUNDOS_ESPERA_DEFECTO):
        self.espera = segundos_espera
        self.ultima_alerta_tiempo = {}  # key -> timestamp
        self.lock = Lock()
        # Flash visual (punto rojo en pantalla) persistente tras una alerta
        self.flash_activo = False

    def _puede_alertar(self, key: str):
        with self.lock:
            t = time.time()
            last = self.ultima_alerta_tiempo.get(key, 0)
            if t - last >= self.espera:
                self.ultima_alerta_tiempo[key] = t
                return True
            return False

    # Reemplazo del beep: activar flash visual persistente (punto rojo)
    def beep_local(self):
        self.flash_activo = True

    # Permite activar/desactivar el flash visual segun haya personas en zona.
    def establecer_estado_flash(self, estado: bool):
        self.flash_activo = estado

    # Indica si el punto rojo debe mostrarse/parpadear en este momento.
    def debe_mostrar_flash(self) -> bool:
        return self.flash_activo

    # Genera una alerta local para el `id_track` con `texto`.
    # Retorna True si la alerta fue emitida (respetando espera), False si fue ignorada.
    def alertar_por_track(self, id_track: int, texto: str):
        key = f'track_{id_track}'
        if not self._puede_alertar(key):
            return False
        # Local
        print(f'[ALERTA] {texto}')
        try:
            self.beep_local()
        except Exception:
            pass
        return True

if __name__ == '__main__':
    a = Alertas(5)
    a.alertar_por_track(1, 'Prueba de alerta')

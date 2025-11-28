"""Módulo de alertas: local (beep/log) y WhatsApp via Twilio.
Configurar variables de entorno para Twilio: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,
TWILIO_WHATSAPP_FROM (p.e. 'whatsapp:+1415XXXX'), ALERT_WHATSAPP_TO ('whatsapp:+54...')
"""
import os
import time
from threading import Lock
try:
    from twilio.rest import Client
    _TWILIO_AVAILABLE = True
except Exception:
    _TWILIO_AVAILABLE = False

class Alerts:
    def __init__(self, cooldown_seconds: int = 10):
        self.cooldown = cooldown_seconds
        self.last_alert_time = {}  # key -> timestamp
        self.lock = Lock()
        # Flash visual (punto rojo en pantalla) persistente tras una alerta
        self.flash_on = False
        # Twilio client init
        if _TWILIO_AVAILABLE:
            sid = os.environ.get('TWILIO_ACCOUNT_SID')
            token = os.environ.get('TWILIO_AUTH_TOKEN')
            if sid and token:
                self.twilio = Client(sid, token)
            else:
                self.twilio = None
        else:
            self.twilio = None

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

    def send_whatsapp(self, body: str):
        if not self.twilio:
            print('[Alerts] Twilio no configurado. Mensaje:', body)
            return False
        from_ = os.environ.get('TWILIO_WHATSAPP_FROM')
        to = os.environ.get('ALERT_WHATSAPP_TO')
        if not from_ or not to:
            print('[Alerts] Variables TWILIO_WHATSAPP_FROM o ALERT_WHATSAPP_TO no configuradas')
            return False
        try:
            self.twilio.messages.create(body=body, from_=from_, to=to)
            return True
        except Exception as e:
            print('[Alerts] Error enviando WhatsApp:', e)
            return False

    def alert_for_track(self, track_id: int, text: str, use_whatsapp: bool = True):
        key = f'track_{track_id}'
        if not self._can_alert(key):
            return False
        # Local
        print(f'[ALERTA] {text}')
        try:
            self.local_beep()
        except Exception:
            pass
        # Remota
        if use_whatsapp:
            self.send_whatsapp(text)
        return True


if __name__ == '__main__':
    a = Alerts(5)
    a.alert_for_track(1, 'Prueba de alerta')

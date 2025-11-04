# Sistema de Detección de Intrusiones en Zonas Restringidas (Demo)

Proyecto demo que detecta personas en un stream de video, mantiene IDs simples de tracking,
permite definir zonas poligonales y envía alertas locales y por WhatsApp (Twilio).

Requisitos
- Python 3.8+
- Instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

Notas importantes
- El repositorio soporta cargar pesos personalizados para YOLO (por ejemplo `yolov11.pt`) — si tienes esos pesos, pásalos con `--weights`.
- No se asume disponibilidad de CUDA: el demo correrá en CPU por defecto (tu iGPU AMD no está soportada por PyTorch/Ultralytics en la mayoría de setups).
- **Twilio (WhatsApp)**: El paquete `twilio` está comentado en `requirements.txt` porque requiere habilitar soporte de rutas largas en Windows. Para instalarlo:
  1. Abre PowerShell como Administrador
  2. Ejecuta: `New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force`
  3. Reinicia la terminal y ejecuta: `pip install twilio`
  4. Define estas variables de entorno:
     - TWILIO_ACCOUNT_SID
     - TWILIO_AUTH_TOKEN
     - TWILIO_WHATSAPP_FROM  (ej: "whatsapp:+1415...")
     - ALERT_WHATSAPP_TO (ej: "whatsapp:+54...")
- **Sin Twilio**: El sistema funciona perfectamente sin Twilio, usando alertas locales (beep + log en consola)

Cómo usar
1. Dibujar zonas sobre video en vivo:
   ```powershell
   python zones_tool.py --source 0
   ```
   - Click izquierdo: agregar punto
   - ESPACIO: pausar/reanudar video (recomendado para dibujar con precisión)
   - `n`: guardar zona y empezar otra
   - `s`: guardar todas las zonas
   - `q`: salir

2. Ejecutar sistema de detección:
   
   **Modo estándar** (10-15 FPS en CPU):
   ```powershell
   python main.py --source 0
   ```
   
   **Modo optimizado** (20-30 FPS en CPU):
   ```powershell
   python main.py --source 0 --imgsz 416 --skip_frames 1
   ```
   O simplemente ejecutar:
   ```powershell
   .\run_optimized.ps1
   ```
   
   **Con video en lugar de cámara**:
   ```powershell
   python main.py --source video.mp4 --weights path/to/yolov11.pt
   ```
   
   **Con alertas WhatsApp**:
   ```powershell
   $env:TWILIO_ACCOUNT_SID = "ACxxxx"
   $env:TWILIO_AUTH_TOKEN = "xxxx"
   $env:TWILIO_WHATSAPP_FROM = "whatsapp:+1415..."
   $env:ALERT_WHATSAPP_TO = "whatsapp:+54..."
   python main.py --source 0 --use_whatsapp
   ```

Parámetros disponibles
- `--source`: Cámara (0, 1, 2...) o ruta a video
- `--weights`: Ruta a pesos YOLO personalizados (default: yolov8n.pt)
- `--tracker`: Algoritmo de tracking - `bytetrack` (robusto, default) o `simple` (IoU básico)
- `--conf`: Umbral de confianza (default: 0.3)
- `--imgsz`: Tamaño de imagen para inferencia - menor = más rápido (default: 640, recomendado 416 para CPU)
- `--skip_frames`: Procesar 1 de cada N frames (default: 0 = todos, 1 = la mitad, 2 = un tercio)
- `--cooldown`: Segundos entre alertas por persona (default: 10)
- `--use_whatsapp`: Activar envío de WhatsApp via Twilio

Características visuales profesionales
- ✅ Logo personalizable en esquina superior izquierda
- ✅ Nombres de zonas editables (editar `zones.json` manualmente)
- ✅ Puntos de tracking con IDs en el centro de cada persona
- ✅ Panel de estadísticas estilo dashboard (frame, zonas activas, detecciones)
- ✅ FPS y contador de frames en tiempo real
- ✅ Código de colores: verde (seguro) / rojo (intrusión)
- ✅ Overlay semi-transparente para zonas

Personalización de nombres de zonas
Edita el archivo `zones.json` manualmente para cambiar nombres:
```json
{
  "zones": [
    [[x1,y1], [x2,y2], ...]
  ],
  "zone_names": [
    "Zona 1: Entrada Principal",
    "Zona 2: Estacionamiento"
  ]
}
```

Algoritmos de Tracking

**ByteTrack (default, recomendado)**
- Tracking robusto de múltiples objetos con persistencia de IDs
- Mantiene IDs estables incluso con oclusiones o detecciones perdidas
- Reduce falsos positivos al reasignar IDs correctamente
- Ideal para producción y entornos con movimientos rápidos
- Uso: `python main.py --tracker bytetrack` (o sin especificar, es el default)

**SimpleTracker (alternativa básica)**
- Tracking basado en IoU (Intersection over Union)
- Más rápido pero menos robusto
- Puede perder IDs con oclusiones o cambios rápidos
- Útil para pruebas rápidas o recursos muy limitados
- Uso: `python main.py --tracker simple`

Próximos pasos sugeridos
- ✅ ByteTrack integrado para tracking robusto
- Implementar filtrado geométrico avanzado y conversión de coordenadas multi-cámara
- Añadir grabación de video con timestamps
- Dashboard web para monitoreo remoto

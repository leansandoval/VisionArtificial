# 📘 Sistema de Detección de Intrusiones en Zonas Restringidas

Sistema profesional de detección de intrusiones mediante visión artificial con **doble interfaz**: CLI tradicional y Dashboard Web moderno.

---

## 🚀 Inicio Rápido

### **Opción 1: Dashboard Web (Recomendado)** 🌐

```powershell
.\run_webapp.ps1
```

Abre automáticamente el navegador en `http://localhost:5000`

### **Opción 2: Interfaz CLI** 💻

```powershell
# Modo optimizado (20-30 FPS en CPU)
.\run_optimized.ps1

# O con parámetros personalizados
python main.py --source 0 --imgsz 416 --use_geometric_filter
```

---

## 📋 Requisitos e Instalación

### **1. Python 3.8+**

### **2. Instalar Dependencias**

```powershell
# Sistema base (obligatorio)
pip install -r requirements.txt

# Dashboard web (opcional - solo si usarás la interfaz web)
pip install -r webapp\requirements-web.txt
```

**Dependencias principales:**
- `opencv-python` - Procesamiento de video
- `ultralytics` - Modelos YOLO
- `supervision` - ByteTrack tracking
- `numpy` - Operaciones numéricas
- `mss` - Captura de pantalla
- `flask`, `flask-socketio` - Dashboard web (opcional)
- `twilio` - Alertas WhatsApp (opcional)

### **3. Configurar Twilio (Opcional - Solo para WhatsApp)**

**Habilitar rutas largas en Windows:**
1. Abrir PowerShell como Administrador
2. Ejecutar:
   ```powershell
   New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
   ```
3. Reiniciar terminal

**Instalar Twilio:**
```powershell
pip install twilio
```

**Variables de entorno:**
```powershell
$env:TWILIO_ACCOUNT_SID = "ACxxxx"
$env:TWILIO_AUTH_TOKEN = "tu_token"
$env:TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"
$env:TWILIO_WHATSAPP_TO = "whatsapp:+5491112345678"
```

> **Nota:** El sistema funciona perfectamente sin Twilio usando alertas locales (beep + log)

---

## 🎯 Uso del Sistema

### **A. Dashboard Web (Interfaz Visual)** 🌐

#### **Paso 1: Iniciar Dashboard**
```powershell
.\run_webapp.ps1
```

#### **Paso 2: Configurar Sistema** (`/settings`)

1. **Fuente de Video:**
   - 📹 **Webcam:** Seleccionar cámara disponible
   - 📡 **Cámara IP (RTSP):** Ingresar usuario, contraseña, IP, puerto y ruta del stream
   - 🖥️ **Captura de Pantalla:** Seleccionar monitor
   - 📁 **Archivo de Video:** Ruta completa

2. **Parámetros de Detección:**
   - Modelo YOLO (path personalizado)
   - Confianza: 0.1 - 0.9 (slider)
   - Tamaño inferencia: 416px / 640px / 1280px
   - Skip frames: 0-5

3. **Tracking y Filtrado:**
   - Algoritmo: ByteTrack / SimpleTracker
   - ✅ Filtrado geométrico
   - Tiempo mínimo en zona: 1-10s
   - Área mínima bbox: 500-10000px²

4. **Alertas:**
   - ✅ Alertas locales (beep)
   - ✅ WhatsApp (Twilio)
   - Cooldown: 1-60s

5. **Guardar Configuración**

#### **Paso 3: Definir Zonas Restringidas** (`/zones`)

1. **Video en vivo automático**
   - Se muestra el stream de la fuente configurada

2. **Dibujar zonas:**
   - Click izquierdo para agregar puntos
   - Mínimo 3 puntos por zona
   - "Nueva Zona" para guardar y empezar otra

3. **Gestionar zonas:**
   - Click en lista para seleccionar
   - Editar nombre (✏️) - se guarda automáticamente
   - Eliminar (🗑️) - se guarda automáticamente

4. **Pausar/Reanudar** para dibujar con precisión

#### **Paso 4: Iniciar Detección** (`/`)

1. Click **"Iniciar"**
2. Observar stream en tiempo real
3. Controles:
   - **Pausar:** Congela procesamiento
   - **Detener:** Finaliza detección

---

### **B. Interfaz CLI (Terminal)** 💻

#### **Paso 1: Definir Zonas**

```powershell
# Con webcam
python zones_tool.py --source 0

# Con cámara IP
python zones_tool.py --source "rtsp://admin:pass@192.168.1.42:554/stream"

# Con captura de pantalla
python zones_tool.py --source screen
```

**Controles:**
- **Click izquierdo:** Agregar punto
- **ESPACIO:** Pausar/reanudar video
- **n:** Nueva zona (guardar actual)
- **c:** Limpiar zona actual
- **d:** Eliminar última zona
- **s:** Guardar todas las zonas
- **q/ESC:** Salir

#### **Paso 2: Ejecutar Detección**

**Scripts preconfigurados:**

```powershell
# Webcam optimizado
.\run_optimized.ps1

# Cámara IP (tu Hikvision)
.\run_my_ipcamera.ps1

# Cámara IP genérica (interactivo)
.\run_ip_camera.ps1

# Dashboard Web
.\run_webapp.ps1
```

**Modo manual con parámetros:**

```powershell
# Básico
python main.py --source 0

# Optimizado para CPU
python main.py --source 0 --imgsz 416 --skip_frames 1 --use_geometric_filter

# Con cámara IP
python main.py --source "rtsp://admin:pass@IP:554/stream" --tracker bytetrack

# Con alertas WhatsApp
python main.py --source 0 --use_whatsapp --use_geometric_filter

# Con modelo personalizado
python main.py --source video.mp4 --weights path/to/yolov11.pt
```

---

## ⚙️ Parámetros de Configuración

### **Fuentes de Video**

| Tipo | Argumento | Ejemplo |
|------|-----------|---------|
| **Webcam** | `--source N` | `--source 0` |
| **Video** | `--source path` | `--source video.mp4` |
| **RTSP** | `--source url` | `--source "rtsp://..."` |
| **Pantalla** | `--source screen` | `--source screen:2` |

**URLs RTSP comunes:**
```
# Hikvision HD
rtsp://admin:password@192.168.1.42:554/Streaming/Channels/101

# Hikvision SD (recomendado CPU)
rtsp://admin:password@192.168.1.42:554/Streaming/Channels/102

# Dahua
rtsp://admin:password@IP:554/cam/realmonitor?channel=1&subtype=0

# HTTP genérico
http://192.168.1.100:8080/video
```

### **Detección y Tracking**

| Parámetro | Valores | Default | Descripción |
|-----------|---------|---------|-------------|
| `--weights` | path | `yolov8n.pt` | Modelo YOLO personalizado |
| `--conf` | 0.1-0.9 | `0.3` | Confianza mínima |
| `--tracker` | `bytetrack`/`simple` | `bytetrack` | Algoritmo tracking |
| `--zones` | path | `zones.json` | Archivo de zonas |

### **Optimización de Rendimiento**

| Parámetro | Valores | Default | Impacto FPS |
|-----------|---------|---------|-------------|
| `--imgsz` | 320/416/640/1280 | `640` | +40% (416px) |
| `--skip_frames` | 0-5 | `0` | +200% (skip=2) |

**Perfiles de rendimiento:**

```powershell
# RÁPIDO (30-40 FPS en CPU)
python main.py --source 0 --imgsz 416 --skip_frames 3 --conf 0.5

# BALANCEADO (20-30 FPS)
python main.py --source 0 --imgsz 640 --skip_frames 1 --conf 0.4

# PRECISO (10-15 FPS)
python main.py --source 0 --imgsz 1280 --skip_frames 0 --conf 0.3
```

### **Filtrado Geométrico Avanzado** ⭐

**Reduce falsos positivos en 40%+**

| Parámetro | Valores | Default | Función |
|-----------|---------|---------|---------|
| `--use_geometric_filter` | flag | off | Activar filtrado |
| `--min_time_zone` | 1.0-10.0s | `2.0` | Tiempo mínimo en zona |
| `--min_bbox_area` | 500-10000px² | `2000` | Área mínima detección |

**Características:**
- ✅ Validación de tiempo de permanencia
- ✅ Filtrado por tamaño de bbox
- ✅ Análisis de trayectoria (10 posiciones)
- ✅ Detección de objetos estáticos
- ✅ Validación de aspect ratio

**Código de colores:**
- 🟢 **Verde:** Fuera de zona (seguro)
- 🟠 **Naranja:** En zona, validando
- 🔴 **Rojo:** INTRUSIÓN VALIDADA

```powershell
# Ejemplo con filtrado
python main.py --source 0 --use_geometric_filter --min_time_zone 3.0 --min_bbox_area 3000
```

### **Sistema de Alertas**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `--use_whatsapp` | flag | Activar alertas WhatsApp |
| `--cooldown` | 1-60s | Tiempo entre alertas (default: 10) |

**Alertas locales:** Siempre activas (beep + log)

### **Parámetros RTSP/IP Camera**

| Parámetro | Valores | Default | Descripción |
|-----------|---------|---------|-------------|
| `--rtsp_transport` | `tcp`/`udp` | `tcp` | Protocolo transporte |
| `--max_retries` | 1-10 | `10` | Intentos reconexión |
| `--timeout` | 5000-30000ms | `10000` | Timeout conexión |

---

## 🎨 Características Visuales

### **Dashboard Web**
- ✅ Stream de video en tiempo real
- ✅ Estadísticas en vivo (FPS, detecciones, alertas)
- ✅ Log de eventos con timestamps
- ✅ Editor de zonas interactivo con video en vivo
- ✅ Configuración dinámica sin código
- ✅ Acceso desde red local

### **Interfaz CLI**
- ✅ Logo personalizable (esquina superior izquierda)
- ✅ Nombres de zonas editables
- ✅ IDs de tracking sobre personas
- ✅ Panel de estadísticas estilo dashboard
- ✅ FPS en tiempo real
- ✅ Overlay semi-transparente para zonas

---

## 🔍 Algoritmos de Tracking

### **ByteTrack (Default - Recomendado)** ⭐

**Características:**
- ✅ Tracking robusto multi-objeto
- ✅ IDs persistentes con oclusiones
- ✅ Reasignación inteligente de IDs
- ✅ Ideal para producción

**Uso:**
```powershell
python main.py --tracker bytetrack  # o sin especificar (default)
```

### **SimpleTracker (Alternativa Básica)**

**Características:**
- ✅ Tracking basado en IoU
- ✅ Más rápido pero menos robusto
- ⚠️ Puede perder IDs con oclusiones

**Uso:**
```powershell
python main.py --tracker simple
```

---

## 📁 Gestión de Zonas

### **Formato JSON** (`zones.json`)

```json
{
  "zones": [
    [[x1,y1], [x2,y2], [x3,y3], ...]
  ],
  "zone_names": [
    "Zona 1: Entrada Principal",
    "Zona 2: Estacionamiento"
  ]
}
```

### **Edición Manual**

```json
{
  "zones": [
    [[358,934], [740,470], [986,129], [1494,267]],
    [[100,200], [300,200], [300,400], [100,400]]
  ],
  "zone_names": [
    "Puerta Principal",
    "Área Restringida"
  ]
}
```

---

## 📊 Comparación: Dashboard Web vs CLI

| Característica | Dashboard Web | CLI |
|---------------|--------------|-----|
| **Interfaz** | Visual moderna | Terminal |
| **Configuración** | Dinámica (formularios) | Argumentos CLI |
| **Zonas** | Editor gráfico integrado | `zones_tool.py` separado |
| **Video** | Stream navegador | Ventana OpenCV |
| **Estadísticas** | Panel en vivo | Overlay en video |
| **Acceso remoto** | ✅ Red local | ❌ Solo local |
| **Curva aprendizaje** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Performance** | Ligeramente menor | Óptimo |
| **Multi-sesión** | ✅ Varios navegadores | ❌ |

---

## 🛠️ Arquitectura del Sistema

### **Módulos Principales** (compartidos por ambas interfaces)

```
src/
├── detector.py           # Detección YOLO
├── tracker.py            # SimpleTracker (IoU)
├── bytetrack_wrapper.py  # ByteTrack (robusto)
├── zones.py              # Gestión de zonas
├── geometric_filter.py   # Filtrado avanzado ⭐
├── alerts.py             # Sistema de alertas
├── overlay.py            # Visualización
├── screen_capture.py     # Fuentes de video
└── utils.py              # FPS counter
```

### **Dashboard Web (Adicional)**

```
webapp/
├── app.py                # Flask + SocketIO
├── config.json           # Configuración persistente
├── requirements-web.txt  # Dependencias web
├── templates/            # HTML (Jinja2)
│   ├── index.html       # Dashboard
│   ├── settings.html    # Configuración
│   └── zones.html       # Editor zonas
└── static/               # CSS/JS
    ├── css/dashboard.css
    └── js/
        ├── main.js
        ├── settings.js
        └── zones.js
```

### **Flujo de Datos**

```
┌─────────────────────────────────────────────┐
│         ENTRADA (Fuentes de Video)          │
│  📹 Webcam | 📡 RTSP | 🖥️ Screen | 📁 Video │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│           PROCESAMIENTO CORE                │
│  ┌────────────┐  ┌────────────┐            │
│  │  Detector  │→ │  Tracker   │            │
│  │  (YOLO)    │  │ (ByteTrack)│            │
│  └────────────┘  └────────────┘            │
│         ↓               ↓                   │
│  ┌────────────────────────────┐            │
│  │  Geometric Filter ⭐       │            │
│  │  - Validación tiempo       │            │
│  │  - Validación tamaño       │            │
│  │  - Análisis trayectoria    │            │
│  └────────────────────────────┘            │
│         ↓                                   │
│  ┌────────────┐  ┌────────────┐            │
│  │   Zones    │  │   Alerts   │            │
│  │  Manager   │  │  (Local +  │            │
│  │            │  │  WhatsApp) │            │
│  └────────────┘  └────────────┘            │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│             SALIDA (Interfaces)             │
│  🌐 Dashboard Web  |  💻 CLI (OpenCV)       │
└─────────────────────────────────────────────┘
```

---

## 🐛 Solución de Problemas

### **Errores Comunes**

#### **"No module named [paquete]"**
```powershell
# Sistema base
pip install -r requirements.txt

# Dashboard web
pip install -r webapp\requirements-web.txt
```

#### **Video no se muestra**
1. Verificar fuente configurada correctamente
2. Probar con webcam simple (`--source 0`)
3. Revisar log del sistema
4. Para RTSP: verificar URL con VLC primero

#### **ByteTrack no disponible**
```powershell
pip install supervision
```
El sistema usa SimpleTracker automáticamente como fallback.

#### **Error RTSP: "Frame perdido"**
- Verificar URL de cámara (probar en VLC)
- Cambiar TCP ↔ UDP: `--rtsp_transport udp`
- Aumentar timeout: `--timeout 20000`
- Verificar red: `ping 192.168.1.XX`

#### **FPS muy bajo**
```powershell
# Optimización agresiva
python main.py --source 0 --imgsz 416 --skip_frames 3 --conf 0.5
```

- Reducir `--imgsz` a 416 o 320
- Aumentar `--skip_frames` a 2-3
- Desactivar filtrado geométrico temporalmente
- Cerrar otras aplicaciones

#### **Twilio: Rutas largas**
```powershell
# PowerShell como Admin
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```
Reiniciar terminal después.

---

## 🔒 Consideraciones de Seguridad

### **Dashboard Web (Localhost)**
- ✅ Diseñado para uso local
- ✅ No exponer a internet público
- ✅ Usar solo en red local confiable
- ⚠️ No incluye autenticación (localhost)

**Acceso desde red local:**
```
http://[tu-ip-local]:5000
# Ejemplo: http://192.168.1.100:5000
```

**Para producción:** Agregar autenticación + HTTPS

---

## 📈 Estadísticas de Rendimiento

### **Filtrado Geométrico**

Ejemplo de salida al finalizar:
```
Estadísticas de Filtrado Geométrico:
  Total detecciones procesadas: 1247
  Filtradas por tamaño: 89 (7.1%)
  Filtradas por confianza: 34 (2.7%)
  Filtradas por tiempo: 312 (25.0%)
  Filtradas por movimiento: 67 (5.4%)
  Intrusiones válidas: 745 (59.7%)
  Tasa de filtrado: 40.3%
```

### **Comparativa FPS (CPU Intel i5)**

| Configuración | FPS Promedio |
|--------------|--------------|
| Default (640px, todos frames) | 10-15 |
| Optimizado (416px, skip=1) | 20-30 |
| Agresivo (416px, skip=3) | 30-40 |
| Preciso (1280px, todos frames) | 5-10 |

---

## 📚 Recursos Adicionales

### **Archivos de Configuración**
- `requirements.txt` - Dependencias base
- `webapp/requirements-web.txt` - Dependencias web
- `zones.json` - Zonas configuradas
- `webapp/config.json` - Configuración dashboard

### **Scripts Auxiliares**
- `zones_tool.py` - Editor de zonas CLI
- `run_optimized.ps1` - Ejecución optimizada
- `run_ip_camera.ps1` - Cámara IP interactivo
- `run_webapp.ps1` - Dashboard web

### **Documentación de Módulos**
- `src/detector.py` - Detección YOLO
- `src/geometric_filter.py` - Filtrado avanzado
- `src/bytetrack_wrapper.py` - Tracking robusto
- `src/alerts.py` - Sistema de alertas

---

## 🚀 Roadmap / Próximas Mejoras

- ✅ ByteTrack tracking robusto
- ✅ Filtrado geométrico avanzado
- ✅ Dashboard web con configuración dinámica
- ⬜ Sistema de coordenadas multi-cámara
- ⬜ Grabación de eventos con timestamps
- ⬜ Dashboard con autenticación
- ⬜ Soporte 4K con baja latencia
- ⬜ Deployment Docker (cloud/edge)
- ⬜ API REST para integración externa

---

## 🎓 Casos de Uso

✅ **Seguridad industrial** - Zonas de peligro en fábricas  
✅ **Retail** - Áreas restringidas en tiendas  
✅ **Hogares** - Monitoreo de áreas sensibles  
✅ **Instituciones educativas** - Control de accesos  
✅ **Estacionamientos** - Detección de intrusos  

---

## 📝 Notas Importantes

1. **Compatibilidad:** No requiere GPU (optimizado para CPU)
2. **Configuración persistente:** Dashboard web guarda en `webapp/config.json`
3. **Zonas compartidas:** Mismo `zones.json` para CLI y web
4. **Multi-sesión:** Dashboard soporta múltiples navegadores simultáneos
5. **Sin modificar código:** Dashboard es un wrapper sobre módulos existentes

---

## 💡 Ejemplos de Uso Completo

### **Caso 1: Monitoreo de Oficina (Dashboard Web)**

```powershell
# 1. Iniciar dashboard
.\run_webapp.ps1

# 2. En navegador (http://localhost:5000/settings):
#    - Fuente: Cámara IP RTSP
#    - Confianza: 0.4
#    - Skip frames: 1
#    - Filtrado geométrico: ON
#    - Guardar

# 3. En /zones:
#    - Dibujar zonas sobre video en vivo
#    - Guardar

# 4. En /:
#    - Iniciar detección
#    - Observar stream
```

### **Caso 2: Monitoreo Industrial (CLI)**

```powershell
# 1. Definir zonas
python zones_tool.py --source "rtsp://admin:pass@192.168.1.50:554/stream"

# 2. Ejecutar con filtrado avanzado
python main.py `
    --source "rtsp://admin:pass@192.168.1.50:554/stream" `
    --tracker bytetrack `
    --use_geometric_filter `
    --min_time_zone 3.0 `
    --min_bbox_area 3000 `
    --imgsz 416 `
    --skip_frames 2 `
    --use_whatsapp
```

### **Caso 3: Demo Rápida con Webcam**

```powershell
# 1. Zonas rápidas
python zones_tool.py --source 0

# 2. Detección optimizada
.\run_optimized.ps1
```

---

**¡Sistema listo para producción! 🎉**

Para más información, consulta los archivos de código fuente o ejecuta `python main.py --help`

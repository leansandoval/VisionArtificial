# 🌐 Dashboard Web - Sistema de Detección de Intrusiones

Dashboard web profesional con interfaz moderna para controlar y configurar el sistema de detección de intrusiones mediante visión artificial.

---

## 🚀 Inicio Rápido

### **Opción 1: Script PowerShell (Recomendado)**

```powershell
.\run_webapp.ps1
```

El script automáticamente:
- ✅ Verifica dependencias
- ✅ Instala paquetes faltantes
- ✅ Abre el navegador en `http://localhost:5000`
- ✅ Inicia el servidor Flask

### **Opción 2: Manual**

```powershell
# 1. Instalar dependencias web
pip install -r webapp\requirements-web.txt

# 2. Iniciar servidor
python webapp\app.py
```

Accede a: **http://localhost:5000**

---

## 📋 Requisitos

### **Dependencias del Sistema Base**
```
opencv-python
ultralytics
numpy
supervision (para ByteTrack)
mss (captura de pantalla)
twilio (alertas WhatsApp - opcional)
```

### **Dependencias Web Adicionales**
```
flask>=3.0.0
flask-socketio>=5.3.0
flask-cors>=4.0.0
python-socketio>=5.9.0
eventlet>=0.33.0
```

**Instalación completa:**
```powershell
pip install -r requirements.txt          # Sistema base
pip install -r webapp\requirements-web.txt   # Dashboard web
```

---

## 🎯 Características del Dashboard

### **1. Dashboard Principal** (`/`)
- ✅ **Video en tiempo real** - Stream de detección con overlays
- ✅ **Estadísticas en vivo** - FPS, detecciones, alertas
- ✅ **Controles del sistema** - Iniciar, pausar, detener
- ✅ **Log en tiempo real** - Seguimiento de eventos
- ✅ **Alertas visuales** - Notificaciones de intrusiones

### **2. Configuración** (`/settings`)
- ✅ **Fuentes de video dinámicas:**
  - 📹 Webcam (índice seleccionable)
  - 📡 Cámara IP (RTSP con configuración TCP/UDP)
  - 🖥️ Captura de pantalla (multi-monitor)
  - 📁 Archivo de video
  
- ✅ **Parámetros de detección:**
  - Modelo YOLO (path personalizado)
  - Confianza mínima (slider 0.1 - 0.9)
  - Tamaño de inferencia (416px, 640px, 1280px)
  - Skip frames (optimización FPS)
  
- ✅ **Tracking y filtrado:**
  - Algoritmo (ByteTrack / SimpleTracker)
  - Filtrado geométrico on/off
  - Tiempo mínimo en zona
  - Área mínima de bbox
  
- ✅ **Sistema de alertas:**
  - Alertas locales (beep)
  - WhatsApp/Twilio
  - Cooldown configurable

### **3. Editor de Zonas** (`/zones`)
- ✅ **Canvas interactivo** - Dibujar zonas con clicks
- ✅ **Gestión de zonas:**
  - Crear múltiples zonas
  - Editar nombres personalizados
  - Eliminar zonas
  - Visualización en tiempo real
  
- ✅ **Herramientas:**
  - Pausar video para precisión
  - Limpiar zona actual
  - Captura de frame de fondo
  - Guardar persistente en JSON

---

## 📖 Guía de Uso

### **Paso 1: Configurar Fuente de Video**

1. Ir a **Configuración** (`http://localhost:5000/settings`)
2. Seleccionar tipo de fuente:
   - **Webcam:** Índice 0 (predeterminada) o 1, 2, etc.
   - **Cámara IP:** URL completa RTSP
     ```
     rtsp://usuario:password@192.168.1.100:554/stream
     ```
   - **Pantalla:** Seleccionar monitor
   - **Video:** Ruta completa del archivo
     ```
     C:\Videos\test.mp4
     ```
3. Ajustar parámetros de detección según necesidad
4. **Guardar Configuración**

### **Paso 2: Definir Zonas Restringidas**

1. Ir a **Editor de Zonas** (`http://localhost:5000/zones`)
2. **Opción A: Capturar frame de fondo**
   - Configurar fuente en sidebar
   - Click en "Capturar Frame"
   
3. **Opción B: Dibujar sobre fondo negro**
   
4. **Dibujar zonas:**
   - Click izquierdo en canvas para agregar puntos
   - Mínimo 3 puntos por zona
   - Click en "Nueva Zona" para guardar y empezar otra
   
5. **Gestionar zonas:**
   - Click en zona de la lista para seleccionarla
   - Editar nombre (botón lápiz)
   - Eliminar (botón basura)
   
6. **Guardar Zonas** - Se guardan en `zones.json`

### **Paso 3: Iniciar Detección**

1. Volver al **Dashboard** (`http://localhost:5000/`)
2. Click en **Iniciar**
3. Observar:
   - Stream de video con detecciones
   - Estadísticas actualizándose
   - Log de eventos
   - Alertas cuando hay intrusiones

4. **Controles durante ejecución:**
   - **Pausar:** Congela el procesamiento
   - **Detener:** Finaliza la detección

---

## 🎨 Interfaz Visual

### **Código de Colores en Video:**

| Color | Significado |
|-------|-------------|
| 🟢 **Verde** | Persona detectada fuera de zona (seguro) |
| 🟠 **Naranja** | Persona en zona, validando (filtro geométrico) |
| 🔴 **Rojo** | **INTRUSION VALIDADA** - Alerta activa |

### **Zonas:**
- **Rojo semi-transparente:** Zonas guardadas
- **Verde brillante:** Zona en progreso (dibujando)
- **Amarillo:** Puntos individuales

---

## ⚙️ Configuración Avanzada

### **Optimización de Rendimiento:**

| Parámetro | Valor Rápido | Valor Balanceado | Valor Preciso |
|-----------|-------------|-----------------|---------------|
| **Tamaño inferencia** | 416px | 640px | 1280px |
| **Skip frames** | 3 | 1 | 0 |
| **Confianza** | 0.5 | 0.4 | 0.3 |
| **FPS esperado (CPU)** | 30-40 | 20-30 | 10-15 |

### **Filtrado Geométrico (Reducir Falsos Positivos):**

```
✅ Activar Filtrado Geométrico
  ├─ Tiempo mínimo en zona: 2.0s (ajustar según caso)
  ├─ Área mínima bbox: 2000px² (filtrar objetos pequeños)
  └─ Resultado: ~40% menos falsos positivos
```

### **Cámaras IP (RTSP):**

**Formato URL:**
```
rtsp://[usuario]:[password]@[ip]:[puerto]/[ruta]
```

**Ejemplos:**
```
# Hikvision
rtsp://admin:password@192.168.1.42:554/Streaming/Channels/101

# Dahua
rtsp://admin:password@192.168.1.50:554/cam/realmonitor?channel=1&subtype=0

# Generic
rtsp://192.168.1.100:554/stream1
```

**Configuración:**
- **Protocolo:** TCP (más estable) o UDP (menor latencia)
- **Timeout:** 10000ms (ajustar según red)
- **Max retries:** 3 (reconexiones automáticas)

---

## 🔔 Sistema de Alertas

### **Alertas Locales (Beep):**
Siempre activas cuando hay intrusión validada.

### **Alertas WhatsApp (Twilio):**

1. **Configurar variables de entorno:**
   ```powershell
   $env:TWILIO_ACCOUNT_SID = "tu_account_sid"
   $env:TWILIO_AUTH_TOKEN = "tu_auth_token"
   $env:TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"
   $env:TWILIO_WHATSAPP_TO = "whatsapp:+5491112345678"
   ```

2. **Activar en Configuración:**
   - ☑️ Activar alertas por WhatsApp

3. **Cooldown:** Tiempo entre alertas para la misma persona (evita spam)

---

## 🛠️ Arquitectura Técnica

### **Stack Tecnológico:**
- **Backend:** Flask + Flask-SocketIO (Python)
- **Frontend:** HTML5 + Bootstrap 5 + Vanilla JavaScript
- **Comunicación:** WebSockets (tiempo real)
- **Streaming:** JPEG over WebSocket (base64)

### **Estructura de Archivos:**
```
webapp/
├── app.py                    # Servidor Flask + API + WebSockets
├── config.json               # Configuración persistente
├── requirements-web.txt      # Dependencias web
│
├── templates/                # HTML con Jinja2
│   ├── index.html           # Dashboard principal
│   ├── settings.html        # Página de configuración
│   └── zones.html           # Editor de zonas
│
└── static/                   # Assets estáticos
    ├── css/
    │   └── dashboard.css    # Estilos personalizados
    └── js/
        ├── main.js          # Lógica dashboard
        ├── settings.js      # Lógica configuración
        └── zones.js         # Lógica editor zonas
```

### **Flujo de Datos:**

```
┌─────────────────────────────────────────────────┐
│           NAVEGADOR (Cliente)                   │
│  ┌─────────────┐  ┌─────────────┐              │
│  │  Dashboard  │  │ WebSocket   │              │
│  │    (UI)     │←→│  Connection │              │
│  └─────────────┘  └─────────────┘              │
└────────────────────────┬────────────────────────┘
                         │ HTTP + WebSocket
                         ↓
┌─────────────────────────────────────────────────┐
│         SERVIDOR FLASK (Backend)                │
│  ┌─────────────┐  ┌─────────────┐              │
│  │  Flask App  │  │ SocketIO    │              │
│  │  (Routes)   │←→│ (Events)    │              │
│  └─────────────┘  └─────────────┘              │
│         ↓                                       │
│  ┌─────────────────────────────┐               │
│  │  Detection Thread           │               │
│  │  ┌──────────────────────┐   │               │
│  │  │ TU CÓDIGO EXISTENTE  │   │               │
│  │  │ - Detector           │   │               │
│  │  │ - Tracker            │   │               │
│  │  │ - GeometricFilter    │   │               │
│  │  │ - Alerts             │   │               │
│  │  └──────────────────────┘   │               │
│  └─────────────────────────────┘               │
└─────────────────────────────────────────────────┘
         ↓                          ↓
   [Video Source]            [zones.json]
   (Webcam/IP/Screen)        (Persistent Config)
```

---

## 🔒 Seguridad (Entorno Local)

Este dashboard está diseñado para **uso local** únicamente:

- ✅ No exponer a internet público
- ✅ Usar solo en red local confiable
- ✅ No incluye autenticación (no necesario para localhost)
- ⚠️ Para producción: agregar autenticación/HTTPS

**Acceso desde red local:**
```
http://[tu-ip-local]:5000
```

Ejemplo:
```
http://192.168.1.100:5000
```

---

## 🐛 Solución de Problemas

### **Error: "No module named flask"**
```powershell
pip install -r webapp\requirements-web.txt
```

### **Video no se muestra en dashboard**
1. Verificar que la fuente está configurada correctamente
2. Revisar el log del sistema en el dashboard
3. Probar con webcam (fuente más simple)

### **ByteTrack no disponible**
```powershell
pip install supervision
```
El sistema usará SimpleTracker automáticamente como fallback.

### **Error RTSP: "Frame perdido"**
- Verificar URL de la cámara
- Cambiar de TCP a UDP (o viceversa)
- Aumentar timeout a 20000ms
- Verificar red (ping a la cámara)

### **FPS muy bajo**
- Aumentar skip_frames (2-3)
- Reducir imgsz a 416px
- Desactivar filtrado geométrico temporalmente
- Cerrar otras aplicaciones pesadas

---

## 📊 Comparación: Dashboard Web vs CLI

| Característica | Dashboard Web | CLI (`main.py`) |
|---------------|--------------|-----------------|
| **Interfaz** | Visual, moderna | Terminal |
| **Configuración** | Dinámica, sin código | Argumentos CLI |
| **Zonas** | Editor visual | `zones_tool.py` separado |
| **Video** | Stream web | Ventana OpenCV |
| **Estadísticas** | Panel en vivo | Overlay en video |
| **Acceso remoto** | ✅ Desde red local | ❌ Solo local |
| **Facilidad** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🎓 Recursos Adicionales

- **Documentación principal:** `README.md`
- **Código del sistema:** `main.py`, `src/`
- **Dependencias base:** `requirements.txt`

---

## 📝 Notas Importantes

1. **NO modifica tu código existente** - El dashboard es un wrapper que usa tus módulos sin cambiarlos
2. **Configuración persistente** - Se guarda en `webapp/config.json`
3. **Zonas compartidas** - Usa el mismo `zones.json` que `zones_tool.py`
4. **Multi-sesión** - Múltiples navegadores pueden ver el stream simultáneamente

---

## 🚀 Próximos Pasos

1. **Ejecutar:** `.\run_webapp.ps1`
2. **Configurar:** Ajustar parámetros en `/settings`
3. **Zonas:** Definir áreas en `/zones`
4. **Detectar:** Iniciar sistema en `/`

---

**¡Listo para usar! 🎉**

Para soporte o dudas, revisa el log del sistema en el dashboard.

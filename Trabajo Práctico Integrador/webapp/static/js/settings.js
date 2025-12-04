// settings.js - Configuración dinámica del sistema

// Referencias DOM
const settingsForm = document.getElementById('settings-form');
const btnReset = document.getElementById('btn-reset');

// Source type radios
const sourceWebcam = document.getElementById('source-webcam');
const sourceRtsp = document.getElementById('source-rtsp');
const sourceScreen = document.getElementById('source-screen');

// Configs por tipo de source
const webcamConfig = document.getElementById('webcam-config');
const rtspConfig = document.getElementById('rtsp-config');
const screenConfig = document.getElementById('screen-config');

// Geometric filter
const useGeometricFilter = document.getElementById('use_geometric_filter');
const geometricFilterConfig = document.getElementById('geometric-filter-config');

// Range inputs con valores
const confInput = document.getElementById('conf');
const confValue = document.getElementById('conf-value');
const skipInput = document.getElementById('skip_frames');
const skipValue = document.getElementById('skip-value');
const minTimeInput = document.getElementById('min_time_zone');
const minTimeValue = document.getElementById('min-time-value');
const minAreaInput = document.getElementById('min_bbox_area');
const minAreaValue = document.getElementById('min-area-value');
const cooldownInput = document.getElementById('cooldown');
const cooldownValue = document.getElementById('cooldown-value');

// Nuevos inputs para filtro geométrico avanzado
const movementInput = document.getElementById('umbral_movimiento_minimo');
const movementValue = document.getElementById('movement-value');
const overlapInput = document.getElementById('zone_overlap_ratio');
const overlapValue = document.getElementById('overlap-value');
const trajectoryInput = document.getElementById('longitud_trayectoria');
const trajectoryValue = document.getElementById('trajectory-value');
const minConfFilterInput = document.getElementById('min_detection_confidence');
const minConfFilterValue = document.getElementById('min-conf-filter-value');

// Estado de carga
let camerasLoaded = false;
let monitorsLoaded = false;

// ==================== CONTROL DE ESTADO DEL FORMULARIO ====================

function disableAllControls() {
    // Mostrar indicador de carga
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) loadingIndicator.style.display = 'block';
    
    // Deshabilitar todos los inputs, selects, botones y radios del formulario
    const allInputs = settingsForm.querySelectorAll('input, select, button, textarea');
    allInputs.forEach(element => {
        element.disabled = true;
    });
    
    // Deshabilitar botones externos al form
    const btnSubmit = settingsForm.querySelector('button[type="submit"]');
    const btnCancel = settingsForm.querySelector('a.btn-outline-secondary');
    if (btnReset) btnReset.disabled = true;
    if (btnSubmit) btnSubmit.disabled = true;
    if (btnCancel) btnCancel.classList.add('disabled');
    
    console.log('[Settings] Todos los controles deshabilitados hasta completar carga');
}

function enableAllControls() {
    // Ocultar indicador de carga
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) loadingIndicator.style.display = 'none';
    
    // Habilitar todos los inputs, selects, botones y radios del formulario
    const allInputs = settingsForm.querySelectorAll('input, select, button, textarea');
    allInputs.forEach(element => {
        element.disabled = false;
    });
    
    // Habilitar botones externos
    const btnSubmit = settingsForm.querySelector('button[type="submit"]');
    const btnCancel = settingsForm.querySelector('a.btn-outline-secondary');
    if (btnReset) btnReset.disabled = false;
    if (btnSubmit) btnSubmit.disabled = false;
    if (btnCancel) btnCancel.classList.remove('disabled');
    
    console.log('[Settings] Todos los controles habilitados');
}

function checkLoadingComplete() {
    if (camerasLoaded && monitorsLoaded) {
        enableAllControls();
        console.log('[Settings] ✓ Carga completa - Formulario habilitado');
    }
}

// ==================== INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', async () => {
    // Deshabilitar todo inicialmente
    disableAllControls();
    
    // Cargar configuración actual
    await loadConfig();
    
    // Cargar cámaras disponibles
    await loadCameras();
    
    // Cargar monitores disponibles para screen capture
    await loadMonitors();
    
    // Setup event listeners
    setupEventListeners();
});

// ==================== CARGAR CÁMARAS ====================

async function loadCameras() {
    const select = document.getElementById('source-webcam-select');
    const btnRefresh = document.getElementById('btn-refresh-cameras');
    const radioWebcam = document.getElementById('source-webcam');
    const radioRtsp = document.getElementById('source-rtsp');
    const radioScreen = document.getElementById('source-screen');
    
    select.innerHTML = '<option value="">🔍 Detectando cámaras...</option>';
    select.disabled = true;
    if (btnRefresh) btnRefresh.disabled = true;
    if (radioWebcam) radioWebcam.disabled = true;
    if (radioRtsp) radioRtsp.disabled = true;
    if (radioScreen) radioScreen.disabled = true;
    
    try {
        console.log('[Cameras] Iniciando detección...');
        const startTime = Date.now();
        
        const response = await fetch('/api/cameras');
        const data = await response.json();
        
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
        console.log(`[Cameras] Detección completada en ${elapsed}s`);
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        select.innerHTML = '';
        
        if (data.cameras && data.cameras.length > 0) {
            data.cameras.forEach(camera => {
                const option = document.createElement('option');
                option.value = camera.index;
                option.textContent = `${camera.name} (${camera.resolution})`;
                option.dataset.fps = camera.fps;
                option.dataset.backend = camera.backend;
                select.appendChild(option);
            });
            
            console.log(`[Cameras] ${data.cameras.length} cámara(s) detectada(s)`);
            showNotification(`${data.cameras.length} cámara(s) detectada(s)`, 'success');
        } else {
            // No se encontraron cámaras, agregar opción por defecto
            const option = document.createElement('option');
            option.value = '0';
            option.textContent = 'Cámara 0 (predeterminada)';
            select.appendChild(option);
            
            console.warn('[Cameras] No se detectaron cámaras, usando índice 0 por defecto');
            showNotification('No se detectaron cámaras. Usando predeterminada.', 'warning');
        }
        
        select.disabled = false;
        if (btnRefresh) btnRefresh.disabled = false;
        if (radioWebcam) radioWebcam.disabled = false;
        if (radioRtsp) radioRtsp.disabled = false;
        if (radioScreen) radioScreen.disabled = false;
        
    } catch (error) {
        console.error('[Cameras] Error cargando cámaras:', error);
        select.innerHTML = '<option value="0">Cámara 0 (predeterminada)</option>';
        select.disabled = false;
        if (btnRefresh) btnRefresh.disabled = false;
        if (radioWebcam) radioWebcam.disabled = false;
        if (radioRtsp) radioRtsp.disabled = false;
        if (radioScreen) radioScreen.disabled = false;
        showNotification('Error detectando cámaras. Usando predeterminada.', 'error');
    } finally {
        // Marcar cámaras como cargadas
        camerasLoaded = true;
        checkLoadingComplete();
    }
}

// ==================== CARGAR CONFIGURACIÓN ====================

async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        
        // Aplicar configuración al formulario
        applyConfigToForm(config);
    } catch (error) {
        console.error('Error cargando configuración:', error);
        showNotification('Error cargando configuración', 'error');
    }
}

function applyConfigToForm(config) {
    // Source type
    const sourceType = config.source_type || 'webcam';
    document.getElementById(`source-${sourceType}`).checked = true;
    updateSourceConfig(sourceType);
    
    // Source values - para webcam, NO seleccionar aún, esperar a que carguen las cámaras
    const webcamSelect = document.getElementById('source-webcam-select');
    if (webcamSelect) {
        const sourceValue = config.source_value || '0';
        // Esperar a que se carguen las cámaras antes de seleccionar
        const checkAndSelect = setInterval(() => {
            // Verificar si ya terminó de cargar (no está "Cargando cámaras...")
            const firstOption = webcamSelect.options[0];
            if (firstOption && !firstOption.textContent.includes('🔍') && !firstOption.textContent.includes('Cargando')) {
                clearInterval(checkAndSelect);
                webcamSelect.value = sourceValue;
                // Si el valor no existe en las opciones, agregarlo como fallback
                if (webcamSelect.value !== sourceValue) {
                    const option = document.createElement('option');
                    option.value = sourceValue;
                    option.textContent = `Cámara ${sourceValue}`;
                    webcamSelect.appendChild(option);
                    webcamSelect.value = sourceValue;
                }
            }
        }, 200);
        
        // Timeout de seguridad después de 5 segundos
        setTimeout(() => clearInterval(checkAndSelect), 5000);
    }
    
    // Parsear URL RTSP si existe
    const rtspUrl = config.rtsp_url || '';
    if (rtspUrl) {
        try {
            // Parsear rtsp://usuario:password@IP:puerto/path
            const match = rtspUrl.match(/rtsp:\/\/([^:]+):([^@]+)@([^:\/]+):(\d+)(.*)/);
            if (match) {
                document.getElementById('rtsp-user').value = match[1];
                document.getElementById('rtsp-password').value = match[2];
                document.getElementById('rtsp-ip').value = match[3];
                document.getElementById('rtsp-port').value = match[4];
                document.getElementById('rtsp-path').value = match[5];
            }
        } catch (e) {
            console.error('[RTSP] Error parseando URL:', e);
        }
    }
    
    document.getElementById('rtsp-transport').value = config.rtsp_transport || 'tcp';
    document.getElementById('rtsp-timeout').value = config.timeout || 10000;
    
    // Actualizar preview de URL
    updateRtspPreview();
    
    // Para monitores, esperar a que se carguen antes de seleccionar
    const monitorSelect = document.getElementById('source-screen-monitor');
    if (monitorSelect) {
        const monitorValue = config.screen_monitor || '1';
        const checkAndSelectMonitor = setInterval(() => {
            const firstOption = monitorSelect.options[0];
            if (firstOption && !firstOption.textContent.includes('🔍') && !firstOption.textContent.includes('Detectando')) {
                clearInterval(checkAndSelectMonitor);
                monitorSelect.value = monitorValue;
                // Si el valor no existe en las opciones, agregarlo como fallback
                if (monitorSelect.value !== monitorValue) {
                    const option = document.createElement('option');
                    option.value = monitorValue;
                    option.textContent = `Monitor ${monitorValue}`;
                    monitorSelect.appendChild(option);
                    monitorSelect.value = monitorValue;
                }
            }
        }, 200);
        
        // Timeout de seguridad después de 5 segundos
        setTimeout(() => clearInterval(checkAndSelectMonitor), 5000);
    }
    
    // Detection
    document.getElementById('weights').value = config.weights || 'yolov8n.pt';
    document.getElementById('imgsz').value = config.imgsz || 640;
    confInput.value = config.conf || 0.53;
    confValue.textContent = config.conf || 0.53;
    skipInput.value = config.skip_frames || 0;
    skipValue.textContent = config.skip_frames || 0;
    
    // Tracking
    document.getElementById('tracker').value = config.tracker || 'bytetrack';
    useGeometricFilter.checked = config.use_geometric_filter !== false;
    geometricFilterConfig.style.display = useGeometricFilter.checked ? 'block' : 'none';
    
    minTimeInput.value = config.min_time_zone || 2.0;
    minTimeValue.textContent = config.min_time_zone || 2.0;
    minAreaInput.value = config.min_bbox_area || 2000;
    minAreaValue.textContent = config.min_bbox_area || 2000;
    
    // Parámetros avanzados del filtro geométrico
    if (movementInput) {
        movementInput.value = config.umbral_movimiento_minimo || 2.0;
        movementValue.textContent = config.umbral_movimiento_minimo || 2.0;
    }
    if (overlapInput) {
        overlapInput.value = config.zone_overlap_ratio || 0.30;
        overlapValue.textContent = ((config.zone_overlap_ratio || 0.30) * 100).toFixed(0);
    }
    if (trajectoryInput) {
        trajectoryInput.value = config.longitud_trayectoria || 10;
        trajectoryValue.textContent = config.longitud_trayectoria || 10;
    }
    if (minConfFilterInput) {
        minConfFilterInput.value = config.min_detection_confidence || 0.25;
        minConfFilterValue.textContent = config.min_detection_confidence || 0.25;
    }
    
    // Alerts
    cooldownInput.value = config.cooldown || 10;
    cooldownValue.textContent = config.cooldown || 10;
}

// ==================== CARGAR MONITORES ====================

async function loadMonitors() {
    const select = document.getElementById('source-screen-monitor');
    const btnRefresh = document.getElementById('btn-refresh-monitors');
    const radioWebcam = document.getElementById('source-webcam');
    const radioRtsp = document.getElementById('source-rtsp');
    const radioScreen = document.getElementById('source-screen');
    
    select.innerHTML = '<option value="">🔍 Detectando monitores...</option>';
    select.disabled = true;
    if (btnRefresh) btnRefresh.disabled = true;
    if (radioWebcam) radioWebcam.disabled = true;
    if (radioRtsp) radioRtsp.disabled = true;
    if (radioScreen) radioScreen.disabled = true;
    
    try {
        console.log('[Monitors] Iniciando detección...');
        const startTime = Date.now();
        
        const response = await fetch('/api/monitors');
        const data = await response.json();
        
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
        console.log(`[Monitors] Detección completada en ${elapsed}s`);
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        select.innerHTML = '';
        
        if (data.monitors && data.monitors.length > 0) {
            data.monitors.forEach(monitor => {
                const option = document.createElement('option');
                option.value = monitor.index;
                option.textContent = monitor.name;
                select.appendChild(option);
            });
            
            console.log(`[Monitors] ${data.monitors.length} monitores detectados`);
            showNotification(`${data.monitors.length} monitores detectados`, 'success');
        } else {
            const option = document.createElement('option');
            option.value = '1';
            option.textContent = 'Monitor 1 (Principal)';
            select.appendChild(option);
            showNotification('No se detectaron monitores. Usando predeterminado.', 'warning');
        }
        
        select.disabled = false;
        if (btnRefresh) btnRefresh.disabled = false;
        if (radioWebcam) radioWebcam.disabled = false;
        if (radioRtsp) radioRtsp.disabled = false;
        if (radioScreen) radioScreen.disabled = false;
        
    } catch (error) {
        console.error('[Monitors] Error cargando monitores:', error);
        select.innerHTML = '<option value="1">Monitor 1 (Principal)</option>';
        select.disabled = false;
        if (btnRefresh) btnRefresh.disabled = false;
        if (radioWebcam) radioWebcam.disabled = false;
        if (radioRtsp) radioRtsp.disabled = false;
        if (radioScreen) radioScreen.disabled = false;
        showNotification('Error detectando monitores. Usando predeterminado.', 'error');
    } finally {
        // Marcar monitores como cargados
        monitorsLoaded = true;
        checkLoadingComplete();
    }
}

// ==================== RTSP URL BUILDER ====================

function buildRtspUrl() {
    const user = document.getElementById('rtsp-user').value.trim();
    const password = document.getElementById('rtsp-password').value.trim();
    const ip = document.getElementById('rtsp-ip').value.trim();
    const port = document.getElementById('rtsp-port').value || '554';
    const path = document.getElementById('rtsp-path').value.trim();
    
    if (!ip) return '';
    
    // Construir URL: rtsp://usuario:password@IP:puerto/path
    let url = 'rtsp://';
    
    if (user && password) {
        url += `${user}:${password}@`;
    }
    
    url += `${ip}:${port}`;
    
    if (path) {
        // Asegurar que path empiece con /
        url += path.startsWith('/') ? path : '/' + path;
    }
    
    return url;
}

function updateRtspPreview() {
    const preview = document.getElementById('rtsp-url-preview');
    if (!preview) return;
    
    const url = buildRtspUrl();
    if (url) {
        // Censurar password en preview
        const user = document.getElementById('rtsp-user').value.trim();
        const password = document.getElementById('rtsp-password').value.trim();
        let displayUrl = url;
        
        if (user && password) {
            displayUrl = url.replace(`:${password}@`, ':****@');
        }
        
        preview.textContent = displayUrl;
    } else {
        preview.textContent = 'rtsp://usuario:password@IP:puerto/path';
    }
}

// ==================== EVENT LISTENERS ====================

function setupEventListeners() {
    // Source type cambios
    sourceWebcam.addEventListener('change', () => updateSourceConfig('webcam'));
    sourceRtsp.addEventListener('change', () => updateSourceConfig('rtsp'));
    sourceScreen.addEventListener('change', () => updateSourceConfig('screen'));
    
    // Botón refresh cámaras
    const btnRefresh = document.getElementById('btn-refresh-cameras');
    if (btnRefresh) {
        btnRefresh.addEventListener('click', async () => {
            btnRefresh.disabled = true;
            btnRefresh.innerHTML = '<i class="bi bi-arrow-clockwise spin"></i>';
            await loadCameras();
            btnRefresh.innerHTML = '<i class="bi bi-arrow-clockwise"></i>';
        });
    }
    
    // Botón refresh monitores
    const btnRefreshMonitors = document.getElementById('btn-refresh-monitors');
    if (btnRefreshMonitors) {
        btnRefreshMonitors.addEventListener('click', async () => {
            btnRefreshMonitors.disabled = true;
            btnRefreshMonitors.innerHTML = '<i class="bi bi-arrow-clockwise spin"></i>';
            await loadMonitors();
            btnRefreshMonitors.innerHTML = '<i class="bi bi-arrow-clockwise"></i>';
        });
    }
    
    // Geometric filter toggle
    useGeometricFilter.addEventListener('change', (e) => {
        geometricFilterConfig.style.display = e.target.checked ? 'block' : 'none';
    });
    
    // Range inputs con live update
    confInput.addEventListener('input', (e) => confValue.textContent = e.target.value);
    skipInput.addEventListener('input', (e) => skipValue.textContent = e.target.value);
    minTimeInput.addEventListener('input', (e) => minTimeValue.textContent = e.target.value);
    minAreaInput.addEventListener('input', (e) => minAreaValue.textContent = e.target.value);
    cooldownInput.addEventListener('input', (e) => cooldownValue.textContent = e.target.value);
    
    // Nuevos listeners para parámetros avanzados
    if (movementInput) {
        movementInput.addEventListener('input', (e) => movementValue.textContent = e.target.value);
    }
    if (overlapInput) {
        overlapInput.addEventListener('input', (e) => {
            overlapValue.textContent = (parseFloat(e.target.value) * 100).toFixed(0);
        });
    }
    if (trajectoryInput) {
        trajectoryInput.addEventListener('input', (e) => trajectoryValue.textContent = e.target.value);
    }
    if (minConfFilterInput) {
        minConfFilterInput.addEventListener('input', (e) => minConfFilterValue.textContent = e.target.value);
    }
    
    // RTSP inputs - actualizar preview en tiempo real
    const rtspInputs = ['rtsp-user', 'rtsp-password', 'rtsp-ip', 'rtsp-port', 'rtsp-path'];
    rtspInputs.forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('input', updateRtspPreview);
        }
    });
    
    // Form submit
    settingsForm.addEventListener('submit', handleSubmit);
    
    // Reset button
    btnReset.addEventListener('click', handleReset);
}

function updateSourceConfig(type) {
    // Ocultar todos
    webcamConfig.style.display = 'none';
    rtspConfig.style.display = 'none';
    screenConfig.style.display = 'none';
    
    // Mostrar el activo
    switch(type) {
        case 'webcam':
            webcamConfig.style.display = 'block';
            break;
        case 'rtsp':
            rtspConfig.style.display = 'block';
            break;
        case 'screen':
            screenConfig.style.display = 'block';
            break;
    }
}

// ==================== GUARDAR CONFIGURACIÓN ====================

async function handleSubmit(e) {
    e.preventDefault();
    
    // Obtener source type
    const sourceType = document.querySelector('input[name="source_type"]:checked').value;
    
    // Construir objeto de configuración
    const config = {
        source_type: sourceType,
        source_value: sourceType === 'webcam' ? 
            document.getElementById('source-webcam-select').value : '0',
        rtsp_url: buildRtspUrl(),
        rtsp_transport: document.getElementById('rtsp-transport').value,
        timeout: parseInt(document.getElementById('rtsp-timeout').value),
        screen_monitor: document.getElementById('source-screen-monitor').value,
        
        weights: document.getElementById('weights').value,
        conf: parseFloat(confInput.value),
        imgsz: parseInt(document.getElementById('imgsz').value),
        skip_frames: parseInt(skipInput.value),
        
        tracker: document.getElementById('tracker').value,
        use_geometric_filter: useGeometricFilter.checked,
        min_time_zone: parseFloat(minTimeInput.value),
        min_bbox_area: parseInt(minAreaInput.value),
        min_detection_confidence: minConfFilterInput ? parseFloat(minConfFilterInput.value) : 0.25,
        longitud_trayectoria: trajectoryInput ? parseInt(trajectoryInput.value) : 10,
        umbral_movimiento_minimo: movementInput ? parseFloat(movementInput.value) : 2.0,
        zone_overlap_ratio: overlapInput ? parseFloat(overlapInput.value) : 0.30,
        
        cooldown: parseInt(cooldownInput.value),
        timeout: parseInt(document.getElementById('rtsp-timeout').value),
        max_retries: 3
    };
    
    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        if (response.ok) {
            showNotification('Configuración guardada correctamente', 'success');
            
            // Redirigir al dashboard después de 1 segundo
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
        } else {
            throw new Error('Error al guardar');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al guardar configuración', 'error');
    }
}

// ==================== RESET ====================

function handleReset() {
    // Mostrar modal de confirmación en lugar de confirm() nativo
    const modal = new bootstrap.Modal(document.getElementById('resetConfirmModal'));
    modal.show();
}

// Evento del botón de confirmación dentro del modal
document.getElementById('btn-confirm-reset')?.addEventListener('click', () => {
    const defaultConfig = {
        source_type: 'webcam',
        source_value: '0',
        rtsp_url: '',
        rtsp_user: 'admin',
        rtsp_password: '',
        rtsp_ip: '192.168.1.100',
        rtsp_port: 554,
        rtsp_path: '/Streaming/Channels/101',
        rtsp_transport: 'tcp',
        timeout: 10000,
        screen_monitor: '1',
        weights: 'yolov8n.pt',
        conf: 0.53,
        imgsz: 640,
        skip_frames: 0,
        tracker: 'bytetrack',
        use_geometric_filter: true,
        min_time_zone: 2.0,
        min_bbox_area: 2000,
        min_detection_confidence: 0.25,
        longitud_trayectoria: 10,
        umbral_movimiento_minimo: 2.0,
        zone_overlap_ratio: 0.30,
        cooldown: 10,
        max_retries: 3
    };
    
    applyConfigToForm(defaultConfig);
    showNotification('Valores restaurados a predeterminados', 'info');
    
    // Cerrar el modal
    bootstrap.Modal.getInstance(document.getElementById('resetConfirmModal')).hide();
});

// ==================== NOTIFICACIONES ====================

function showNotification(message, type = 'success') {
    const toast = document.getElementById('notification-toast');
    const toastBody = toast.querySelector('.toast-body');
    const toastIcon = toast.querySelector('i');
    
    // Actualizar mensaje
    toastBody.textContent = message;
    
    // Actualizar icono según tipo
    const iconClasses = {
        'success': 'bi-check-circle-fill text-success',
        'error': 'bi-x-circle-fill text-danger',
        'info': 'bi-info-circle-fill text-info'
    };
    
    toastIcon.className = `bi ${iconClasses[type] || iconClasses.success} me-2`;
    
    // Mostrar toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

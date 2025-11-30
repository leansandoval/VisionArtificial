// main.js - Dashboard principal con WebSocket y streaming de video

const socket = io();

// Referencias a elementos DOM
const videoStream = document.getElementById('video-stream');
const noStreamMessage = document.getElementById('no-stream-message');
const statusBadge = document.getElementById('status-badge');
const btnStart = document.getElementById('btn-start');
const btnPause = document.getElementById('btn-pause');
const btnStop = document.getElementById('btn-stop');
const logContainer = document.getElementById('log-container');
const alertsContainer = document.getElementById('alerts-container');

// Stats
const statFps = document.getElementById('stat-fps');
const statFrames = document.getElementById('stat-frames');
const statDetections = document.getElementById('stat-detections');
const statTracks = document.getElementById('stat-tracks');
const statInZone = document.getElementById('stat-in-zone');
const statFiltered = document.getElementById('stat-filtered');
const statAlerts = document.getElementById('stat-alerts');

// Estado
let isRunning = false;
let isPaused = false;

// ==================== WEBSOCKET EVENTS ====================

socket.on('connect', () => {
    addLog('Conectado al servidor', 'success');
    btnStart.disabled = false;
});

socket.on('disconnect', () => {
    addLog('Desconectado del servidor', 'warning');
    updateUIState(false, false);
});

socket.on('status', (data) => {
    isRunning = data.running;
    isPaused = data.paused || false;
    updateUIState(isRunning, isPaused);
    
    if (data.stats) {
        updateStats(data.stats);
    }
});

socket.on('video_frame', (data) => {
    // Actualizar imagen del video stream
    videoStream.src = 'data:image/jpeg;base64,' + data.frame;
    videoStream.style.display = 'block';
    noStreamMessage.style.display = 'none';
    
    // Actualizar estadísticas
    if (data.stats) {
        updateStats(data.stats);
    }
});

socket.on('alert', (data) => {
    addAlert(data.track_id, data.message);
    addLog(`🚨 ALERTA: ${data.message}`, 'danger');
    // Mostrar punto DOM en esquina superior izquierda
    try {
        const dot = document.getElementById('alert-dot');
        if (dot) {
            dot.style.display = 'block';
            if (window._alertDotTimer) clearTimeout(window._alertDotTimer);
            window._alertDotTimer = setTimeout(() => { dot.style.display = 'none'; }, 3500);
        }
    } catch (e) {
        console.warn('No se pudo mostrar alert-dot:', e);
    }
});

socket.on('log', (data) => {
    addLog(data.message, data.level);
});

// ==================== BOTONES ====================

btnStart.addEventListener('click', () => {
    if (!isRunning) {
        socket.emit('start_detection');
        addLog('Iniciando sistema...', 'info');
    } else if (isPaused) {
        // Si está pausado, reanudar
        socket.emit('pause_detection');
        addLog('Reanudando...', 'info');
    }
});

btnPause.addEventListener('click', () => {
    if (isRunning && !isPaused) {
        socket.emit('pause_detection');
        addLog('Pausando sistema...', 'info');
    }
});

btnStop.addEventListener('click', () => {
    socket.emit('stop_detection');
    addLog('Deteniendo sistema...', 'info');
});

// ==================== FUNCIONES UI ====================

function updateUIState(running, paused) {
    isRunning = running;
    isPaused = paused;
    
    // Actualizar botones según el estado
    if (running) {
        if (paused) {
            // Sistema pausado: permitir reanudar con Iniciar, ocultar Pausar, permitir Detener
            btnStart.disabled = false;
            btnStart.innerHTML = '<i class="bi bi-play-fill"></i> Reanudar';
            btnPause.disabled = true;
            btnStop.disabled = false;
        } else {
            // Sistema corriendo: ocultar Iniciar, permitir Pausar y Detener
            btnStart.disabled = true;
            btnStart.innerHTML = '<i class="bi bi-play-fill"></i> Iniciar';
            btnPause.disabled = false;
            btnStop.disabled = false;
        }
    } else {
        // Sistema detenido: permitir Iniciar, ocultar Pausar y Detener
        btnStart.disabled = false;
        btnStart.innerHTML = '<i class="bi bi-play-fill"></i> Iniciar';
        btnPause.disabled = true;
        btnStop.disabled = true;
    }
    
    // Actualizar badge de estado
    if (running) {
        if (paused) {
            statusBadge.className = 'badge bg-warning';
            statusBadge.innerHTML = '<i class="bi bi-pause-fill"></i> Pausado';
        } else {
            statusBadge.className = 'badge bg-success';
            statusBadge.innerHTML = '<i class="bi bi-circle-fill"></i> Activo';
        }
    } else {
        statusBadge.className = 'badge bg-secondary';
        statusBadge.innerHTML = '<i class="bi bi-circle-fill"></i> Detenido';
        
        // Ocultar video stream
        videoStream.style.display = 'none';
        noStreamMessage.style.display = 'block';
    }
}

function updateStats(stats) {
    statFps.textContent = stats.fps.toFixed(1);
    statFrames.textContent = stats.frame_count.toLocaleString();
    statDetections.textContent = stats.detections;
    statTracks.textContent = stats.tracks_active;
    statInZone.textContent = stats.in_zone;
    statFiltered.textContent = stats.filtered;
    statAlerts.textContent = stats.alerts;
}

function addLog(message, level = 'info') {
    const timestamp = new Date().toLocaleTimeString('es-AR');
    const colorClass = {
        'success': 'text-success',
        'info': 'text-info',
        'warning': 'text-warning',
        'danger': 'text-danger',
        'error': 'text-danger'
    }[level] || 'text-white';
    
    const logEntry = document.createElement('div');
    logEntry.className = colorClass;
    logEntry.innerHTML = `[${timestamp}] ${message}`;
    
    logContainer.appendChild(logEntry);
    logContainer.scrollTop = logContainer.scrollHeight;
    
    // Limitar logs a últimas 100 entradas
    while (logContainer.children.length > 100) {
        logContainer.removeChild(logContainer.firstChild);
    }
}

function addAlert(trackId, message) {
    // Si es el primer alert, limpiar el mensaje de "No hay alertas"
    if (alertsContainer.children.length === 1 && 
        alertsContainer.children[0].classList.contains('text-muted')) {
        alertsContainer.innerHTML = '';
    }
    
    const timestamp = new Date().toLocaleTimeString('es-AR');
    const alertItem = document.createElement('div');
    alertItem.className = 'list-group-item list-group-item-danger';
    alertItem.innerHTML = `
        <div class="d-flex w-100 justify-content-between">
            <h6 class="mb-1">
                <i class="bi bi-exclamation-triangle-fill"></i> 
                Persona ID:${trackId}
            </h6>
            <small>${timestamp}</small>
        </div>
        <p class="mb-0 small">${message}</p>
    `;
    
    alertsContainer.insertBefore(alertItem, alertsContainer.firstChild);
    
    // Limitar a últimas 10 alertas
    while (alertsContainer.children.length > 10) {
        alertsContainer.removeChild(alertsContainer.lastChild);
    }
}

function playAlertSound() {
    // Desactivado: reemplazado por alerta visual permanente en servidor
    return;
}

// ==================== NAVEGACIÓN Y CIERRE ====================

let navigationTarget = null;
let exitModal = null;

function getDestinationName(url) {
    if (url.includes('/settings')) return 'Configuración';
    if (url.includes('/zones')) return 'Editor de Zonas';
    return 'otra página';
}

function showExitConfirmation(targetUrl) {
    console.log('[Modal] Mostrando confirmación para navegar a:', targetUrl);
    navigationTarget = targetUrl;
    
    const modalElement = document.getElementById('exitConfirmModal');
    console.log('[Modal] Elemento del modal encontrado:', !!modalElement);
    
    if (!modalElement) {
        console.error('[Modal] No se encontró el elemento exitConfirmModal');
        // Fallback si el modal no existe
        const confirmed = confirm('El sistema está en ejecución. Se detendrá antes de continuar. ¿Deseas salir?');
        if (confirmed) {
            socket.emit('stop_detection');
            setTimeout(() => {
                window.location.href = targetUrl;
            }, 300);
        }
        return;
    }
    
    if (!exitModal) {
        console.log('[Modal] Inicializando Bootstrap Modal...');
        exitModal = new bootstrap.Modal(modalElement, {
            backdrop: 'static',
            keyboard: false
        });
    }
    
    // Actualizar contenido del modal según el destino
    const destinationName = getDestinationName(targetUrl);
    const modalTitle = document.getElementById('exitConfirmModalLabel');
    const modalBody = document.getElementById('exitConfirmModalBody');
    
    if (modalTitle) {
        modalTitle.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-2"></i>¿Ir a ${destinationName}?`;
    }
    
    if (modalBody) {
        modalBody.innerHTML = `
            <p class="mb-2">El sistema de detección está activo y se detendrá antes de continuar.</p>
            <p class="text-muted small mb-0">Podrás reiniciarlo después desde el Dashboard.</p>
        `;
    }
    
    console.log('[Modal] Mostrando modal...');
    exitModal.show();
}

function handleNavigation(e) {
    console.log('[Nav] Click detectado, isRunning:', isRunning);
    
    if (isRunning) {
        e.preventDefault();
        e.stopPropagation();
        
        const target = e.target.href || e.target.closest('a')?.href;
        console.log('[Nav] Target URL:', target);
        
        if (target) {
            showExitConfirmation(target);
        } else {
            console.warn('[Nav] No se pudo determinar la URL destino');
        }
    }
}

// ==================== INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', () => {
    addLog('Dashboard cargado. Esperando conexión...', 'info');
    updateUIState(false, false);
    
    // Interceptar navegación en enlaces del navbar
    document.querySelectorAll('a[href^="/"]').forEach(link => {
        link.addEventListener('click', handleNavigation);
    });
    
    // Configurar modal de confirmación
    const btnCancelExit = document.getElementById('btnCancelExit');
    const btnConfirmExit = document.getElementById('btnConfirmExit');
    
    if (btnCancelExit) {
        btnCancelExit.addEventListener('click', () => {
            if (exitModal) {
                exitModal.hide();
            }
            navigationTarget = null;
        });
    }
    
    if (btnConfirmExit) {
        btnConfirmExit.addEventListener('click', () => {
            console.log('[Modal] Confirmado - Deteniendo sistema y navegando a:', navigationTarget);
            
            // SIEMPRE detener el sistema antes de navegar
            if (isRunning) {
                socket.emit('stop_detection');
                addLog('Deteniendo sistema antes de navegar...', 'warning');
                
                // Esperar a que se detenga
                setTimeout(() => {
                    if (exitModal) {
                        exitModal.hide();
                    }
                    if (navigationTarget) {
                        window.location.href = navigationTarget;
                    }
                }, 500);
            } else {
                // Si por alguna razón no está corriendo, navegar directamente
                if (exitModal) {
                    exitModal.hide();
                }
                if (navigationTarget) {
                    window.location.href = navigationTarget;
                }
            }
        });
    }
});

// Prevenir que la página se recargue/cierre cuando el sistema está corriendo
window.addEventListener('beforeunload', (e) => {
    if (isRunning) {
        e.preventDefault();
        e.returnValue = 'El sistema de detección está en ejecución. ¿Deseas cerrar el navegador? El sistema se detendrá.';
        return e.returnValue;
    }
});

// zones.js - Editor interactivo de zonas

// Socket.IO connection
const socket = io();

// Referencias DOM
const canvas = document.getElementById('zones-canvas');
const ctx = canvas.getContext('2d');
const zonesList = document.getElementById('zones-list');
const zonesCount = document.getElementById('zones-count');
const currentPointsSpan = document.getElementById('current-points');

const btnNewZone = document.getElementById('btn-new-zone');
const btnClearCurrent = document.getElementById('btn-clear-current');
const btnPause = document.getElementById('btn-pause');
const btnSaveZones = document.getElementById('btn-save-zones');

// Estado
let zones = [];  // Array de zonas guardadas: [{points: [[x,y],...], name: "..."}]
let currentZone = [];  // Puntos de la zona en progreso
let backgroundImage = null;
let isPaused = false;
let selectedZoneIndex = -1;
let editingZoneIndex = -1;

// Colores
const COLOR_SAVED_ZONE = 'rgba(255, 0, 0, 0.3)';
const COLOR_CURRENT_ZONE = 'rgba(0, 255, 0, 0.5)';
const COLOR_ZONE_BORDER = '#ff0000';
const COLOR_CURRENT_BORDER = '#00ff00';
const COLOR_POINT = '#00ffff';

// ==================== SOCKET.IO EVENTS ====================

socket.on('connect', () => {
    console.log('[WebSocket] Conectado al servidor');
    // Solicitar inicio de stream de video
    socket.emit('start_zones_stream');
});

socket.on('video_frame', (data) => {
    if (isPaused) return; // No actualizar si está pausado
    
    // Crear imagen desde base64
    const img = new Image();
    img.onload = () => {
        backgroundImage = img;
        
        // Ajustar canvas al tamaño del frame solo la primera vez
        if (canvas.width !== data.width || canvas.height !== data.height) {
            canvas.width = data.width;
            canvas.height = data.height;
            console.log(`[Zones] Canvas ajustado a: ${data.width}x${data.height}`);
        }
        
        redrawCanvas();
    };
    img.src = 'data:image/jpeg;base64,' + data.frame;
});

socket.on('stream_error', (data) => {
    console.error('[Stream] Error:', data.message);
    showNotification('Error en stream: ' + data.message, 'error');
});

// ==================== INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', () => {
    // Cargar zonas existentes desde el servidor
    if (typeof initialZones !== 'undefined' && typeof initialZoneNames !== 'undefined') {
        zones = initialZones.map((points, idx) => ({
            points: points,
            name: initialZoneNames[idx] || `Zona ${idx + 1}: Área Restringida`
        }));
    }
    
    updateZonesList();
    redrawCanvas();
    
    // Event listeners
    canvas.addEventListener('click', handleCanvasClick);
    btnNewZone.addEventListener('click', handleNewZone);
    btnClearCurrent.addEventListener('click', handleClearCurrent);
    btnPause.addEventListener('click', handlePause);
    btnSaveZones.addEventListener('click', handleSaveZones);
    
    // Modal de edición de nombre
    const btnSaveZoneName = document.getElementById('btn-save-zone-name');
    btnSaveZoneName.addEventListener('click', handleSaveZoneName);
    
    // Detener stream al salir de la página
    window.addEventListener('beforeunload', () => {
        socket.emit('stop_zones_stream');
    });
});

// ==================== CANVAS INTERACTIVO ====================

function handleCanvasClick(e) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    const x = Math.round((e.clientX - rect.left) * scaleX);
    const y = Math.round((e.clientY - rect.top) * scaleY);
    
    currentZone.push([x, y]);
    currentPointsSpan.textContent = currentZone.length;
    
    redrawCanvas();
}

function redrawCanvas() {
    // Limpiar canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Dibujar imagen de fondo si existe
    if (backgroundImage) {
        ctx.drawImage(backgroundImage, 0, 0, canvas.width, canvas.height);
    } else {
        // Fondo negro si no hay imagen
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    
    // Dibujar zonas guardadas
    zones.forEach((zone, idx) => {
        drawZone(zone.points, COLOR_SAVED_ZONE, COLOR_ZONE_BORDER, idx === selectedZoneIndex);
        
        // Dibujar nombre de zona
        if (zone.points.length >= 3) {
            const centroid = calculateCentroid(zone.points);
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(`Z${idx + 1}`, centroid[0], centroid[1]);
        }
    });
    
    // Dibujar zona en progreso
    if (currentZone.length > 0) {
        drawZone(currentZone, COLOR_CURRENT_ZONE, COLOR_CURRENT_BORDER, false);
        
        // Dibujar puntos individuales
        currentZone.forEach(point => {
            ctx.fillStyle = COLOR_POINT;
            ctx.beginPath();
            ctx.arc(point[0], point[1], 5, 0, 2 * Math.PI);
            ctx.fill();
        });
    }
}

function drawZone(points, fillColor, strokeColor, isSelected) {
    if (points.length < 2) return;
    
    ctx.strokeStyle = strokeColor;
    ctx.lineWidth = isSelected ? 4 : 2;
    ctx.fillStyle = fillColor;
    
    ctx.beginPath();
    ctx.moveTo(points[0][0], points[0][1]);
    
    for (let i = 1; i < points.length; i++) {
        ctx.lineTo(points[i][0], points[i][1]);
    }
    
    if (points.length >= 3) {
        ctx.closePath();
        ctx.fill();
    }
    
    ctx.stroke();
}

function calculateCentroid(points) {
    let sumX = 0, sumY = 0;
    points.forEach(p => {
        sumX += p[0];
        sumY += p[1];
    });
    return [sumX / points.length, sumY / points.length];
}

// ==================== GESTIÓN DE ZONAS ====================

function handleNewZone() {
    if (currentZone.length < 3) {
        showNotification('Se necesitan al menos 3 puntos para crear una zona', 'warning');
        return;
    }
    
    // Agregar zona actual a zonas guardadas
    const zoneName = `Zona ${zones.length + 1}: Área Restringida`;
    zones.push({
        points: [...currentZone],
        name: zoneName
    });
    
    // Limpiar zona actual
    currentZone = [];
    currentPointsSpan.textContent = 0;
    
    updateZonesList();
    redrawCanvas();
    
    showNotification(`Zona ${zones.length} creada. Total: ${zones.length} zona(s)`, 'success');
}

function handleClearCurrent() {
    if (currentZone.length === 0) {
        showNotification('No hay zona en progreso para limpiar', 'info');
        return;
    }
    
    const pointsCount = currentZone.length;
    currentZone = [];
    currentPointsSpan.textContent = 0;
    
    redrawCanvas();
    showNotification(`${pointsCount} punto(s) descartado(s)`, 'info');
}

function handlePause() {
    isPaused = !isPaused;
    btnPause.innerHTML = isPaused ? 
        '<i class="bi bi-play"></i> Reanudar' :
        '<i class="bi bi-pause"></i> Pausar';
    
    showNotification(isPaused ? 'Video pausado' : 'Video reanudado', 'info');
}

// ==================== GUARDAR ZONAS ====================

async function saveZonesToServer() {
    if (zones.length === 0) {
        showNotification('No hay zonas para guardar', 'warning');
        return false;
    }
    
    // Preparar datos para enviar
    const data = {
        zones: zones.map(z => z.points),
        zone_names: zones.map(z => z.name)
    };
    
    try {
        const response = await fetch('/api/zones', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showNotification(`✓ ${zones.length} zona(s) guardada(s) correctamente`, 'success');
            updateZonesList();
            redrawCanvas();
            return true;
        } else {
            throw new Error('Error al guardar');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al guardar zonas', 'error');
        return false;
    }
}

async function handleSaveZones() {
    // Si hay zona en progreso con 3+ puntos, agregarla
    if (currentZone.length >= 3) {
        const zoneName = `Zona ${zones.length + 1}: Área Restringida`;
        zones.push({
            points: [...currentZone],
            name: zoneName
        });
        currentZone = [];
        currentPointsSpan.textContent = 0;
    }
    
    await saveZonesToServer();
}

function deleteZone(index) {
    if (confirm(`¿Eliminar "${zones[index].name}"?`)) {
        zones.splice(index, 1);
        selectedZoneIndex = -1;
        updateZonesList();
        redrawCanvas();
        
        // Guardar automáticamente en el servidor
        saveZonesToServer();
    }
}

function editZoneName(index) {
    editingZoneIndex = index;
    const modal = new bootstrap.Modal(document.getElementById('edit-zone-modal'));
    document.getElementById('zone-name-input').value = zones[index].name;
    modal.show();
}

function handleSaveZoneName() {
    const newName = document.getElementById('zone-name-input').value.trim();
    
    if (newName && editingZoneIndex >= 0) {
        zones[editingZoneIndex].name = newName;
        updateZonesList();
        
        const modal = bootstrap.Modal.getInstance(document.getElementById('edit-zone-modal'));
        modal.hide();
        
        // Guardar automáticamente en el servidor
        saveZonesToServer();
        
        editingZoneIndex = -1;
    }
}

function selectZone(index) {
    selectedZoneIndex = selectedZoneIndex === index ? -1 : index;
    
    // Actualizar UI de lista
    document.querySelectorAll('.zone-item').forEach((item, idx) => {
        if (idx === selectedZoneIndex) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
    
    redrawCanvas();
}

// ==================== LISTA DE ZONAS ====================

function updateZonesList() {
    zonesCount.textContent = zones.length;
    
    if (zones.length === 0) {
        zonesList.innerHTML = '<div class="list-group-item text-muted text-center"><small>No hay zonas guardadas</small></div>';
        return;
    }
    
    zonesList.innerHTML = '';
    
    zones.forEach((zone, idx) => {
        const item = document.createElement('div');
        item.className = 'list-group-item zone-item';
        if (idx === selectedZoneIndex) {
            item.classList.add('active');
        }
        
        item.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div class="flex-grow-1" style="cursor: pointer;">
                    <strong>Zona ${idx + 1}</strong><br>
                    <small class="text-muted">${zone.points.length} puntos</small><br>
                    <small>${zone.name}</small>
                </div>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary btn-edit" data-index="${idx}">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-outline-danger btn-delete" data-index="${idx}">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
        
        // Click en zona para seleccionarla
        item.querySelector('.flex-grow-1').addEventListener('click', () => selectZone(idx));
        
        // Botón editar
        item.querySelector('.btn-edit').addEventListener('click', (e) => {
            e.stopPropagation();
            editZoneName(idx);
        });
        
        // Botón eliminar
        item.querySelector('.btn-delete').addEventListener('click', (e) => {
            e.stopPropagation();
            deleteZone(idx);
        });
        
        zonesList.appendChild(item);
    });
}

// ==================== NOTIFICACIONES ====================

function showNotification(message, type = 'success') {
    const toast = document.getElementById('notification-toast');
    const toastBody = toast.querySelector('.toast-body');
    const toastIcon = toast.querySelector('i');
    
    toastBody.textContent = message;
    
    const iconClasses = {
        'success': 'bi-check-circle-fill text-success',
        'error': 'bi-x-circle-fill text-danger',
        'warning': 'bi-exclamation-triangle-fill text-warning',
        'info': 'bi-info-circle-fill text-info'
    };
    
    toastIcon.className = `bi ${iconClasses[type] || iconClasses.success} me-2`;
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// ==================== UTILIDADES ====================

// Ajustar tamaño del canvas al viewport
function resizeCanvas() {
    const container = canvas.parentElement;
    const maxWidth = container.clientWidth - 40;
    const aspectRatio = canvas.height / canvas.width;
    
    if (maxWidth < canvas.width) {
        canvas.style.width = maxWidth + 'px';
        canvas.style.height = (maxWidth * aspectRatio) + 'px';
    }
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();

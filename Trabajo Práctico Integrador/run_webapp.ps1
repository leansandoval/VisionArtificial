#!/usr/bin/env pwsh
# Script para iniciar el Dashboard Web del Sistema de Detección de Intrusiones

Write-Host "`n=========================================="
Write-Host "  DASHBOARD WEB - Sistema de Detección"
Write-Host "==========================================`n" -ForegroundColor Cyan

# Verificar si Python está instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python detectado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Error: Python no encontrado" -ForegroundColor Red
    Write-Host "Instala Python desde https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# Verificar dependencias web
Write-Host "`nVerificando dependencias web..." -ForegroundColor Yellow

$webRequirements = "webapp\requirements-web.txt"
if (Test-Path $webRequirements) {
    Write-Host "Instalando dependencias Flask..." -ForegroundColor Yellow
    pip install -r $webRequirements --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Dependencias web instaladas" -ForegroundColor Green
    } else {
        Write-Host "⚠ Error instalando dependencias. Continuando..." -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ No se encontró requirements-web.txt" -ForegroundColor Yellow
}

# Información del dashboard
Write-Host "`n=========================================="
Write-Host "  INFORMACIÓN DEL DASHBOARD"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📡 URL Local:      http://localhost:5000" -ForegroundColor White
Write-Host "📊 Dashboard:      http://localhost:5000/" -ForegroundColor White
Write-Host "⚙️  Configuración:  http://localhost:5000/settings" -ForegroundColor White
Write-Host "🗺️  Editor Zonas:   http://localhost:5000/zones" -ForegroundColor White
Write-Host "`n🌐 Acceso desde red: http://<tu-ip>:5000" -ForegroundColor Gray
Write-Host "==========================================`n"

Write-Host "Instrucciones:" -ForegroundColor Yellow
Write-Host "1. El dashboard se abrirá en tu navegador automáticamente"
Write-Host "2. Configura la fuente de video en 'Configuración'"
Write-Host "3. Define zonas en 'Editor de Zonas'"
Write-Host "4. Presiona 'Iniciar' en el Dashboard para comenzar"
Write-Host "`nPresiona Ctrl+C para detener el servidor`n"

# Esperar 2 segundos antes de abrir el navegador
Start-Sleep -Seconds 2

# Abrir navegador automáticamente (en background)
Start-Process "http://localhost:5000"

# Iniciar servidor Flask
Write-Host "Iniciando servidor Flask..." -ForegroundColor Green
Write-Host "==========================================`n"

python webapp\app.py

Write-Host "`n=========================================="
Write-Host "  Servidor detenido"
Write-Host "==========================================" -ForegroundColor Cyan

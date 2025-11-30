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

$webRequirements = "requirements.txt"
if (Test-Path $webRequirements) {
    Write-Host "Instalando dependencias Flask..." -ForegroundColor Yellow
    pip install -r $webRequirements --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Dependencias web instaladas" -ForegroundColor Green
    } else {
        Write-Host "⚠ Error instalando dependencias. Continuando..." -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ No se encontró requirements.txt" -ForegroundColor Yellow
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

# Iniciar un job en background que espere a que el servidor responda
$uri = 'http://localhost:5000'
$timeoutSeconds = 30
Write-Host "Iniciando job que esperará a que $uri responda (timeout ${timeoutSeconds}s)..." -ForegroundColor Yellow

# El job hará polling y abrirá el navegador cuando el servidor responda
Start-Job -ScriptBlock {
    param($uri, $timeout)
    $start = Get-Date
    while (((Get-Date) - $start).TotalSeconds -lt $timeout) {
        try {
            $resp = Invoke-WebRequest -Uri $uri -TimeoutSec 2 -ErrorAction Stop
            if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 400) {
                Start-Process $uri
                return
            }
        } catch {
            Start-Sleep -Milliseconds 500
        }
    }
    # Si timeout, abrir de todos modos (opcional)
    Start-Process $uri
} -ArgumentList $uri, $timeoutSeconds | Out-Null

# Iniciar servidor Flask en primer plano (para mostrar logs en la consola)
Write-Host "Iniciando servidor Flask (verás los logs aquí)..." -ForegroundColor Green
Write-Host "==========================================`n"

python webapp\app.py

Write-Host "`n=========================================="
Write-Host "  Servidor detenido"
Write-Host "==========================================" -ForegroundColor Cyan

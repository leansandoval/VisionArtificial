#!/usr/bin/env pwsh
# Script para ejecutar la aplicación usando la cámara integrada del notebook
# Uso: .\run_camera_notebook.ps1 [-Index 0] [-ExtraArgs "--option val"]

param(
    [int]$Index = 0,
    [string]$ExtraArgs = ""
)

Write-Host "`n=== INICIO: Cámara integrada (notebook) ===`n" -ForegroundColor Cyan

# Verificar Python
try {
    $pv = python --version 2>&1
    Write-Host "✓ Python detectado: $pv" -ForegroundColor Green
} catch {
    Write-Host "✗ Python no encontrado. Instala Python antes de continuar." -ForegroundColor Red
    exit 1
}

# Probar acceso a la cámara (requiere OpenCV instalado)
$env:CAM_INDEX = $Index
$pyCheck = "import os,sys
try:
    import cv2
except Exception as e:
    print('NO_CV2'); sys.exit(3)
i=int(os.environ.get('CAM_INDEX','0'))
cap=cv2.VideoCapture(i)
if not cap or not cap.isOpened():
    print('NO_OPEN')
    sys.exit(2)
ret,frame=cap.read()
cap.release()
print('OK' if ret else 'NO_FRAME')"

Write-Host "Comprobando cámara index $Index (esto requiere opencv-python)..." -ForegroundColor Yellow
$checkOut = & python -c $pyCheck 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Resultado prueba cámara: $checkOut" -ForegroundColor Yellow
    Write-Host "Puedes continuar, pero puede que la cámara no esté disponible o falte opencv." -ForegroundColor Yellow
    Write-Host "Presiona Ctrl+C para cancelar o espera 3s para continuar..."
    Start-Sleep -Seconds 3
} else {
    Write-Host "✓ Cámara disponible (prueba OK)" -ForegroundColor Green
}

# Ejecutar la aplicación con la cámara (por defecto usa main.py --source <index>)
# Ajusta el comando si tu entrypoint es distinto (p.ej. webapp/app.py u otro).
$cmd = "python main.py --source $Index $ExtraArgs"
Write-Host "`nEjecutando: $cmd`n" -ForegroundColor Cyan

# Lanzar en primer plano para ver logs
Invoke-Expression $cmd

Write-Host "`n=== FIN: ejecución finalizada ===`n" -ForegroundColor Cyan
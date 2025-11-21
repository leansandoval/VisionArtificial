# Script PowerShell para ejecutar con cámara IP - Modo interactivo
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Sistema de Detección - Cámara IP" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# URL por defecto (tu cámara Hikvision)
$defaultIpCamera = "rtsp://admin:Leandro_22@192.168.1.42:554/Streaming/Channels/102"

Write-Host "Ejemplos de URLs de cámara IP:" -ForegroundColor Yellow
Write-Host "  Hikvision HD: rtsp://admin:Leandro_22@192.168.1.42:554/Streaming/Channels/101" -ForegroundColor Gray
Write-Host "  Hikvision SD: rtsp://admin:Leandro_22@192.168.1.42:554/Streaming/Channels/102" -ForegroundColor Gray
Write-Host "  HTTP Stream: http://192.168.1.42:8080/video" -ForegroundColor Gray
Write-Host "  DroidCam: http://192.168.1.XXX:4747/video" -ForegroundColor Gray
Write-Host ""

# Pedir URL de cámara o usar default
$ipCamera = Read-Host "URL de cámara IP (Enter para usar Hikvision SD)"
if ([string]::IsNullOrWhiteSpace($ipCamera)) {
    $ipCamera = $defaultIpCamera
    Write-Host "Usando cámara Hikvision SD (recomendado)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Configuración:" -ForegroundColor Yellow
Write-Host "- Fuente: Cámara IP RTSP" -ForegroundColor Green
Write-Host "- URL: $ipCamera" -ForegroundColor Green
Write-Host "- Tracker: ByteTrack (robusto)" -ForegroundColor Green
Write-Host "- Filtrado Geométrico: ACTIVADO" -ForegroundColor Green
Write-Host "- Resolución procesamiento: 416px" -ForegroundColor Green
Write-Host "- Visualización: Resolución original" -ForegroundColor Green
Write-Host ""

python main.py --source "$ipCamera" `
  --use_geometric_filter `
  --tracker bytetrack `
  --imgsz 416 `
  --skip_frames 2 `
  --rtsp_transport tcp `
  --conf 0.4 `
  --min_time_zone 2.0 `
  --max_retries 5 `
  --timeout 15000

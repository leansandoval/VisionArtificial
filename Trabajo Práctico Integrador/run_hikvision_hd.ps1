#!/usr/bin/env pwsh
# Script optimizado para Hikvision - CALIDAD HD COMPLETA (1280x720)

Write-Host "`n=========================================="
Write-Host "  Cámara Hikvision - MODO HD (720p)"
Write-Host "==========================================`n"

Write-Host "Conectando a:"
Write-Host "- IP: 192.168.1.42"
Write-Host "- Usuario: admin"
Write-Host "- Canal: Stream PRINCIPAL HD (1280x720)"
Write-Host ""
Write-Host "Configuración optimizada:"
Write-Host "- ByteTrack tracking"
Write-Host "- Filtrado geométrico"
Write-Host "- Resolución visual: 1280x720 (COMPLETA)"
Write-Host "- Procesamiento YOLO: 416px (rápido)"
Write-Host "- Skip frames: 3 (procesa 1 de cada 4)"
Write-Host ""

$rtspUrl = "rtsp://admin:Leandro_22@192.168.1.42:554/Streaming/Channels/101"

python main.py `
    --source $rtspUrl `
    --conf 0.4 `
    --tracker bytetrack `
    --imgsz 416 `
    --skip_frames 3 `
    --use_geometric_filter `
    --min_time_zone 2.0 `
    --min_bbox_area 2000 `
    --rtsp_transport tcp `
    --max_retries 5 `
    --timeout 15000

Write-Host "`nSistema detenido."

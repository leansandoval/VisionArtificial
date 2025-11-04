# Script PowerShell para ejecutar optimizado con ByteTrack
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Sistema de Detección - Modo OPTIMIZADO" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Optimizaciones activas:" -ForegroundColor Yellow
Write-Host "- Tracker: ByteTrack (robusto)" -ForegroundColor Green
Write-Host "- Tamaño de inferencia: 416px (más rápido)" -ForegroundColor Green
Write-Host "- Skip frames: 1 (procesa 1 de cada 2)" -ForegroundColor Green
Write-Host ""

python main.py --source 0 --imgsz 416 --skip_frames 1 --conf 0.35 --tracker bytetrack

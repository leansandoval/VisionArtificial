@echo off
REM Script para ejecutar con configuración optimizada en CPU + ByteTrack
echo ==========================================
echo Sistema de Detección - Modo OPTIMIZADO
echo ==========================================
echo.
echo Optimizaciones activas:
echo - Tracker: ByteTrack (robusto)
echo - Tamaño de inferencia: 416px (más rápido)
echo - Skip frames: 1 (procesa 1 de cada 2)
echo.
python main.py --source 0 --imgsz 416 --skip_frames 1 --conf 0.35 --tracker bytetrack

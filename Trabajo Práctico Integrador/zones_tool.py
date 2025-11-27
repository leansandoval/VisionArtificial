"""Herramienta interactiva para dibujar/editar zonas poligonales usando OpenCV.
Ejecutar: python zones_tool.py [--source 0]
         python zones_tool.py --source screen
         python zones_tool.py --source screen:2
Instrucciones:
- Click izquierdo: agregar punto al polígono
- 'n': nueva zona (completar zona actual y empezar otra)
- 'c': limpiar zona actual (borrar puntos sin guardar)
- 'd': eliminar última zona guardada
- 's': guardar todas las zonas a zones.json
- 'q' o ESC: salir
"""
import cv2
import json
import os
import argparse
import numpy as np
from src.zones import ZonesManager
from src.screen_capture import create_screen_source, list_monitors

WINDOW = 'Zones Tool - Dibuja zonas sobre video en vivo'

def main(source=0, out_path='zones.json'):
    zm = ZonesManager(out_path)
    zm.cargar()

    # Abrir cámara, video o pantalla usando create_screen_source
    cap = create_screen_source(source)
    if not cap.isOpened():
        print(f'ERROR: No se pudo abrir la fuente: {source}')
        print('Tip: usa --source 0 para webcam, --source video.mp4 para un archivo, o --source screen para captura de pantalla')
        return

    current = []
    paused_frame = None

    def on_mouse(event, x, y, flags, param):
        nonlocal current
        if event == cv2.EVENT_LBUTTONDOWN:
            current.append((int(x), int(y)))
            print(f'  Punto añadido: ({x}, {y}) - Total: {len(current)} puntos')

    cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(WINDOW, on_mouse)

    print('\n=== HERRAMIENTA DE ZONAS ===')
    print(f'Fuente: {source}')
    print(f'Zonas cargadas: {len(zm.zones)}')
    print('\nControles:')
    print('  Click izquierdo: agregar punto')
    print('  n: nueva zona (guardar actual y empezar otra)')
    print('  c: limpiar zona actual')
    print('  d: eliminar última zona guardada')
    print('  s: guardar zonas a archivo')
    print('  ESPACIO: pausar/reanudar video')
    print('  q/ESC: salir')
    print('='*30 + '\n')

    while True:
        if paused_frame is None:
            ret, frame = cap.read()
            if not ret:
                print('No se pudo leer frame, fin del video o error de cámara')
                # Si es video, reiniciar
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
                if not ret:
                    break
        else:
            frame = paused_frame.copy()

        disp = frame.copy()
        
        # Dibujar zonas guardadas (rojo semi-transparente)
        overlay = disp.copy()
        for i, poly in enumerate(zm.zones):
            if len(poly) >= 3:
                pts = np.array(poly, dtype=np.int32)
                cv2.polylines(overlay, [pts], True, (0,0,255), 3)
                cv2.fillPoly(overlay, [pts], (0,0,255))
                # Número de zona
                centroid = np.mean(pts, axis=0).astype(int)
                cv2.putText(overlay, f'Z{i+1}', tuple(centroid), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        cv2.addWeighted(overlay, 0.3, disp, 0.7, 0, disp)
        
        # Dibujar zona actual en progreso (verde brillante)
        if len(current) > 0:
            pts = np.array(current, dtype=np.int32)
            if len(current) > 1:
                cv2.polylines(disp, [pts], False, (0,255,0), 2)
            for p in current:
                cv2.circle(disp, p, 6, (0,255,0), -1)
            # Línea de preview al cursor (opcional, se ve bien)
            if len(current) >= 1:
                cv2.circle(disp, current[-1], 8, (0,255,255), 2)

        # HUD (overlay de instrucciones)
        hud_y = 25
        cv2.rectangle(disp, (5, 5), (disp.shape[1]-5, 140), (0,0,0), -1)
        cv2.rectangle(disp, (5, 5), (disp.shape[1]-5, 140), (255,255,255), 2)
        cv2.putText(disp, "LMB: agregar punto | n: nueva zona | c: limpiar | d: borrar ultima | s: guardar | ESPACIO: pausar", 
                    (15, hud_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)
        cv2.putText(disp, f"Zona actual: {len(current)} puntos (min. 3 para guardar)", 
                    (15, hud_y+25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)
        cv2.putText(disp, f"Zonas guardadas: {len(zm.zones)}", 
                    (15, hud_y+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)
        status = "PAUSADO" if paused_frame is not None else "EN VIVO"
        cv2.putText(disp, f"Estado: {status}", 
                    (15, hud_y+75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 1, cv2.LINE_AA)
        cv2.putText(disp, "q/ESC: salir", 
                    (15, hud_y+100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100,100,255), 1, cv2.LINE_AA)

        cv2.imshow(WINDOW, disp)
        k = cv2.waitKey(1 if paused_frame is None else 30) & 0xFF
        
        if k == ord('q') or k == 27:
            print('\nSaliendo...')
            break
        elif k == ord('n'):
            if len(current) >= 3:
                zm.zones.append(current.copy())
                print(f'✓ Zona guardada con {len(current)} puntos. Total zonas: {len(zm.zones)}')
                current = []
            else:
                print(f'✗ Necesitas al menos 3 puntos (tienes {len(current)})')
        elif k == ord('c'):
            if len(current) > 0:
                print(f'Limpiando zona actual ({len(current)} puntos descartados)')
                current = []
        elif k == ord('d'):
            if len(zm.zones) > 0:
                removed = zm.zones.pop()
                print(f'✓ Última zona eliminada ({len(removed)} puntos). Zonas restantes: {len(zm.zones)}')
            else:
                print('✗ No hay zonas guardadas para eliminar')
        elif k == ord('s'):
            # Guardar zona en progreso si tiene 3+ puntos
            if len(current) >= 3:
                zm.zones.append(current.copy())
                # Asegurar que tenemos nombres para todas las zonas
                while len(zm.zone_names) < len(zm.zones):
                    zm.zone_names.append(f"Zona {len(zm.zone_names)+1}: Área Restringida")
                print(f'✓ Zona actual guardada con {len(current)} puntos')
                current = []
            # Asegurar que tenemos nombres para todas las zonas existentes
            while len(zm.zone_names) < len(zm.zones):
                zm.zone_names.append(f"Zona {len(zm.zone_names)+1}: Área Restringida")
            zm.guardar()
            print(f'✓✓ Todas las zonas guardadas en {out_path} ({len(zm.zones)} zonas)')
        elif k == 32:  # ESPACIO
            if paused_frame is None:
                paused_frame = frame.copy()
                print('|| Video PAUSADO - puedes dibujar con calma')
            else:
                paused_frame = None
                print('▶ Video REANUDADO')

    cap.release()
    cv2.destroyAllWindows()
    print(f'\nFinalizado. Zonas guardadas: {len(zm.zones)}')
    if len(current) >= 3:
        print(f'AVISO: Tienes una zona sin guardar con {len(current)} puntos. Vuelve a ejecutar y presiona "s" para guardarla.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Herramienta para dibujar zonas sobre video en vivo o captura de pantalla')
    parser.add_argument('--source', default=0, 
                        help='Fuente de video: 0 para webcam, ruta a archivo, "screen" para captura de pantalla, '
                             '"screen:1" para monitor específico, "screen:region:x,y,w,h" para región específica')
    parser.add_argument('--output', default='zones.json', help='Archivo de salida para zonas')
    parser.add_argument('--list_monitors', action='store_true', help='Listar monitores disponibles y salir')
    args = parser.parse_args()
    
    # Si se solicita listar monitores
    if args.list_monitors:
        list_monitors()
        exit(0)
    
    # Convertir source a int si es un número
    source = args.source
    if isinstance(source, str) and source.isdigit():
        source = int(source)
    
    main(source=source, out_path=args.output)

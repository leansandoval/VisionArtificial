"""Herramienta interactiva para dibujar/editar zonas poligonales usando OpenCV.
Ejecutar:   python zones_tool.py [--source 0]
            python zones_tool.py --source screen
            python zones_tool.py --source screen:2
Instrucciones:
- Click izquierdo: agregar punto al poligono
- 'n': nueva zona (completar zona actual y empezar otra)
- 'c': limpiar zona actual (borrar puntos sin guardar)
- 'd': eliminar ultima zona guardada
- 's': guardar todas las zonas a zonas.json
- ESC: salir
"""
import argparse
import cv2
import numpy as np
from src.constantes import *
from src.screen_capture import create_screen_source, list_monitors
from src.zonas import GestorZonas

#region Constantes

RADIO_CIRCULO_EXTERIOR = 8
RADIO_CIRCULO_INTERIOR = 6
TECLA_ESCAPE = 27
WINDOW = "Zones Tool - Dibuja zonas sobre video en vivo"

#endregion

#region Funciones Auxiliares

def mostrar_instrucciones_por_consola(source, zm):
    print("\n=== HERRAMIENTA DE ZONAS ===")
    print(f"Fuente: {source}")
    print(f"Zonas cargadas: {len(zm.zonas)}")
    print("\nControles:")
    print("  Click izquierdo: agregar punto")
    print("  n: nueva zona (guardar actual y empezar otra)")
    print("  c: limpiar zona actual")
    print("  d: eliminar ultima zona guardada")
    print("  s: guardar zonas a archivo")
    print("  ESC: salir")
    print("=" * 30 + "\n")

def dibujar_zona_actual(current, disp):
    if len(current) > 0:
        pts = np.array(current, dtype=np.int32)
        if len(current) > 1:
            cv2.polylines(disp, [pts], False, COLOR_TUPLA_VERDE, GROSOR_DOS_PIXELES)
        for p in current:
            cv2.circle(disp, p, RADIO_CIRCULO_INTERIOR, COLOR_TUPLA_VERDE, GROSOR_RELLENO_COMPLETO)
        if len(current) >= 1:
            cv2.circle(disp, current[-1], RADIO_CIRCULO_EXTERIOR, COLOR_TUPLA_CIAN, GROSOR_DOS_PIXELES)

def dibujar_zonas_guardadas(zm, disp):
    overlay = disp.copy()
    for i, poly in enumerate(zm.zonas):
        if len(poly) >= 3:
            pts = np.array(poly, dtype=np.int32)
            cv2.polylines(overlay, [pts], True, COLOR_TUPLA_ROJO, GROSOR_TRES_PIXELES)
            cv2.fillPoly(overlay, [pts], COLOR_TUPLA_ROJO)
            centroid = np.mean(pts, axis=0).astype(int)
            cv2.putText(overlay, f"Z{i+1}", tuple(centroid), cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_CIEN_PORCIENTO, COLOR_TUPLA_BLANCO, GROSOR_DOS_PIXELES)
    cv2.addWeighted(overlay, 0.3, disp, 0.7, 0, disp)

def mostrar_hud(zm, current, disp):
    hud_y = 25
    # HUD semi-transparente: Dibujar en un overlay y mezclar para no ocultar totalmente la cámara
    overlay = disp.copy()
    cv2.rectangle(overlay, (5, 5), (disp.shape[1] - 5, 115), COLOR_TUPLA_NEGRO, GROSOR_RELLENO_COMPLETO)
    alpha = 0.45  # 0.0 transparente -> 1.0 opaco
    cv2.addWeighted(overlay, alpha, disp, 1 - alpha, 0, disp)
    # Borde blanc
    cv2.rectangle(disp, (5, 5), (disp.shape[1] - 5, 115), COLOR_TUPLA_BLANCO, GROSOR_DOS_PIXELES)
    cv2.putText(disp, "Click izquierdo: agregar punto | n: definir nueva zona | c: limpiar zona actual | d: borrar ultima zona guardada | s: guardar en json", (15, hud_y), cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_CINCUENTA_PORCIENTO, COLOR_TUPLA_BLANCO, GROSOR_UN_PIXEL, cv2.LINE_AA)
    cv2.putText(disp, f"Zona actual: {len(current)} puntos (min. 3 para guardar)", (15, hud_y + 25), cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_CINCUENTA_PORCIENTO, COLOR_TUPLA_VERDE, GROSOR_UN_PIXEL, cv2.LINE_AA)
    cv2.putText(disp, f"Zonas guardadas: {len(zm.zonas)}", (15, hud_y + 50), cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_CINCUENTA_PORCIENTO, COLOR_TUPLA_ROJO, GROSOR_UN_PIXEL, cv2.LINE_AA)
    cv2.putText(disp, "ESC: salir", (15, hud_y + 75), cv2.FONT_HERSHEY_SIMPLEX, ESCALA_FUENTE_CINCUENTA_PORCIENTO, COLOR_TUPLA_CIAN, GROSOR_UN_PIXEL, cv2.LINE_AA)

#endregion

#region Funciones Principales

def main(source=0, out_path=ARCHIVO_ZONAS):
    zm = GestorZonas(out_path)
    zm.cargar()
    
    # Abrir camara, video o pantalla usando create_screen_source
    cap = create_screen_source(source)
    if not cap.isOpened():
        print(f"ERROR: No se pudo abrir la fuente: {source}")
        print("Tip: usa --source 0 para webcam, --source video.mp4 para un archivo, "
                "o --source screen para captura de pantalla")
        return
    
    current = []
    
    def on_mouse(event, x, y, flags, param):
        nonlocal current
        if event == cv2.EVENT_LBUTTONDOWN:
            current.append((int(x), int(y)))
            print(f"  Punto anadido: ({x}, {y}) - Total: {len(current)} puntos")

    cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(WINDOW, on_mouse)

    mostrar_instrucciones_por_consola(source, zm)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo leer frame, fin del video o error de camara")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            if not ret:
                break

        disp = frame.copy()

        dibujar_zonas_guardadas(zm, disp)
        
        dibujar_zona_actual(current, disp)
        
        mostrar_hud(zm, current, disp)

        cv2.imshow(WINDOW, disp)
        k = cv2.waitKey(1) & 0xFF

        if k == TECLA_ESCAPE:
            print("\nSaliendo...")
            break
        elif k == ord("n"):
            if len(current) >= 3:
                zm.zonas.append(current.copy())
                print(f"Zona guardada con {len(current)} puntos. Total zonas: {len(zm.zonas)}")
                current = []
            else:
                print(f"Necesitas al menos 3 puntos (tienes {len(current)})")
        elif k == ord("c"):
            if len(current) > 0:
                print(f"Limpiando zona actual ({len(current)} puntos descartados)")
                current = []
        elif k == ord("d"):
            if len(zm.zonas) > 0:
                removed = zm.zonas.pop()
                print(f"Ultima zona eliminada ({len(removed)} puntos). Zonas restantes: {len(zm.zonas)}")
            else:
                print("No hay zonas guardadas para eliminar")
        elif k == ord("s"):
            if len(current) >= 3:
                zm.zonas.append(current.copy())
                while len(zm.nombres_zonas) < len(zm.zonas):
                    zm.nombres_zonas.append(f"Zona {len(zm.nombres_zonas)+1}: Area Restringida")
                print(f"Zona actual guardada con {len(current)} puntos")
                current = []
            while len(zm.nombres_zonas) < len(zm.zonas):
                zm.nombres_zonas.append(f"Zona {len(zm.nombres_zonas)+1}: Area Restringida")
            zm.guardar()
            print(f"Todas las zonas guardadas en {out_path} ({len(zm.zonas)} zonas)")

    cap.release()
    cv2.destroyAllWindows()
    print(f"\nFinalizado. Zonas guardadas: {len(zm.zonas)}")
    if len(current) >= 3:
        print(f"AVISO: Tienes una zona sin guardar con {len(current)} puntos. "
            'Vuelve a ejecutar y presiona "s" para guardarla.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Herramienta para dibujar zonas sobre video en vivo o captura de pantalla")
    parser.add_argument("--source", default=0, help='Fuente de video: 0 para webcam, ruta a archivo, "screen" para captura de pantalla, '
        '"screen:1" para monitor especifico, "screen:region:x,y,w,h" para region especifica')
    parser.add_argument("--output", default=ARCHIVO_ZONAS, help="Archivo de salida para zonas")
    parser.add_argument("--list_monitors", action="store_true", help="Listar monitores disponibles y salir")
    args = parser.parse_args()
    if args.list_monitors:
        list_monitors()
        exit(0)
    source = args.source
    if isinstance(source, str) and source.isdigit():
        source = int(source)
    main(source=source, out_path=args.output)

#endregion

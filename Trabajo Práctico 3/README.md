# Trabajo Práctico 3

Basado en el repostorio [UNSLAM](https://github.com/UNSLAM25).

## Instrucciones

Se siguieron los pasos como indica el  [README de Stella Vslam](https://github.com/UNSLAM25/stella_vslam/blob/main/build-docker.md).

## Calibración de la Cámara

Se utilizaron 15 fotos sacadas del celular utilizando un [tablero de ajedrez](https://github.com/leansandoval/VisionArtificial/blob/main/Trabajo%20Pr%C3%A1ctico%203/TableroAjedrezCalibracion.pdf) tomado desde distintos angulos y se ejecuto el script [`calibrar_camara.py`](https://github.com/leansandoval/VisionArtificial/blob/main/Trabajo%20Pr%C3%A1ctico%203/calibrar_camara.py). Este script procesa cada imágen tomada y genera el [archivo de configuración](https://github.com/leansandoval/VisionArtificial/blob/main/Trabajo%20Pr%C3%A1ctico%203/config_calibracion_20250921_2338.yaml) que servirá para el sistema.

Al copiarlo a la ruta del repositorio donde se indica renombrar el archivo de configuración como **config.yaml**.

## Ejecucion de la imágen una vez creada

`docker run -it --rm --privileged --name unslam-cont -p 8000:8000 -p 8765:8765 -e DISPLAY=<IP_PC>:0.0 -v "<RUTA_DONDE_SE_CLONO_EL_REPOSITORIO>\stella_vslam\vslam-backend\vslam\config.yaml:/stella_vslam/vslam-backend/config.yaml" unslam`

## Imagen Docker

También se encuentra la [imágen para descargar](https://github.com/leansandoval/VisionArtificial/blob/main/Trabajo%20Pr%C3%A1ctico%203/unslam.tar) directamente y no buildear.

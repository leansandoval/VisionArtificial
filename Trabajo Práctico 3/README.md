# Trabajo Práctico 3

## Instrucciones

Se siguieron los pasos como indica el  [README de Stella Vslam](https://github.com/UNSLAM25/stella_vslam/blob/main/build-docker.md).

## Calibración de la Cámara

Se utilizaron 15 fotos sacadas del celular y se ejecuto el script `calibrar_camara.py`. Este script procesa cada imágen tomada y genera el archivo de configuración que servirá para el sistema.

Al copiarlo a la ruta del repositorio donde se indica renombrarlo como **config.yaml**.

## Ejecucion de la imágen una vez creada

`docker run -it --rm --privileged --name unslam-cont -p 8000:8000 -p 8765:8765 -e DISPLAY=<IP_PC>:0.0 -v "<RUTA_DONDE_SE_CLONO_EL_REPOSITORIO>\stella_vslam\vslam-backend\vslam\config.yaml:/stella_vslam/vslam-backend/config.yaml" unslam`

## Imagen Docker

También se encuentra la imágen para descargar directamente y no buildear.

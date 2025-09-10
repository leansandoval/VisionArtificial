## Trabajo Práctico 1
Hasta la fecha que se creo el repositorio no funciona MediaPipe con la ultima version de Python 3.13, por lo tanto la 3.12 es la que se deberia usar.

No es necesario desinstalar la ultima version de Python, se puede descargar la 3.12 y luego trabajar en un entorno virtual. En este mismo entorno se deberan descargar las librerias correspondientes.

### 1 - Crear y activar un entorno (usa Python 3.12)
`py -3.12 -m venv mpenv`  
`mpenv\Scripts\activate`

### 2 - Actualizar herramientas
`python -m pip install --upgrade pip setuptools wheel`

### 3 - Instalar paquetes
`pip install mediapipe opencv-python numpy`

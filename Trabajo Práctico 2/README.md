# Trabajo Práctico 2

## Proyecto 1

### capturaReferencias.py

Este script permite capturar contornos de figuras de referencia para el Proyecto 1 (detección y clasificación de formas sin aprendizaje automático). Abre la webcam, detecta el contorno más grande presente en la escena y, al pulsar una tecla numérica (por ejemplo 1, 2, 3, …), almacena ese contorno en un archivo JSON junto con la etiqueta correspondiente. Más adelante, la
aplicación de clasificación utilizará estos contornos guardados con `cv2.matchShapes()` para determinar a qué clase pertenece cada figura detectada.

#### Características principales:

* Se leen las etiquetas disponibles de labels.json (si existe) para asociar las teclas numéricas con nombres de figuras (por ejemplo "1": "triangulo").
* El preprocesamiento convierte cada fotograma a escala de grises, aplica desenfoque, umbralización Otsu invertida y una apertura morfológica para eliminar ruido. El contorno de referencia se extrae como el contorno externo de mayor área.
* Para cada figura detectada se dibuja un rectángulo delimitador y se muestra un mensaje indicando que se puede guardar presionando una tecla entre 1 y 3.
* Cuando se presiona una tecla numérica válida y hay un contorno claro, sus puntos se guardan en el archivo referencias.json. Cada entrada del JSON es una lista de contornos capturados para esa etiqueta, y cada contorno es una lista de pares de coordenadas [x, y].

#### Instrucciones de uso:

1. Asegúrese de tener un archivo labels.json con las etiquetas y descripciones de las figuras. Por defecto se utiliza un diccionario básico con "1": "triangulo", "2": "rectangulo" y "3": "circulo".
2. Prepare las figuras de referencia (dibujadas o impresas) y colóquelas frente a la cámara en un ambiente controlado.
3. Ejecute este script. Verá dos ventanas: la imagen de la cámara con indicaciones y la máscara binaria.
4. Para guardar una figura, asegúrese de que el contorno se vea en verde y pulse la tecla correspondiente (1‑3). El contorno se añadirá al archivo referencias.json.
5. Presione Esc para cerrar el programa.

### clasificadorFiguras.py

Este script implementa la clasificación de contornos en tiempo real para el Proyecto 1 de detección y clasificación de formas (sin aprendizaje automático). En lugar de utilizar un modelo entrenado, compara cada contorno detectado con un conjunto de contornos de referencia previamente capturados mediante `matchShapes` de OpenCV. El contorno de referencia con la menor distancia se toma como candidato de clasificación siempre que dicha distancia sea menor a un umbral configurable. En caso contrario, la figura se considera desconocida.


El flujo de trabajo sigue las recomendaciones del proyecto: convertir la imagen a monocromática, umbralizar con un valor ajustable o automático, aplicar operaciones morfológicas para eliminar ruido y procesar todos los contornos relevantes. Cada contorno se compara con todos los objetos de referencia usando `cv2.matchShapes` y se clasifica según la menor distancia, descartando aquellos cuya distancia supere el umbral. El resultado se anota sobre la imagen original con colores distintos para objetos reconocidos y desconocidos.

#### Uso:
1. Ejecute captura_referencias.py para guardar los contornos de referencia en referencias.json. Asegúrese de definir las etiquetas en labels.json.
2. Ejecute este script. Se abrirán ventanas para configurar el umbral, el uso de umbral automático, el tamaño del kernel morfológico y el umbral de coincidencia de formas. Ajuste los deslizadores hasta conseguir una detección confiable. En la ventana principal se mostrará la clasificación de cada contorno detectado.
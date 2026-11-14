# Visión Artificial
Trabajos prácticos de la materia Visión Artificial (3679) - 2C 2025 - UNLaM. 

## Información de la Asignatura
* **Carrera**: Ingeniería en Informática
* **Asignatura**: Visión Artificial (3679)
* **Cuatrimestre**: Segundo Cuatrimestre
* **Año**: 2025
* **Grupo**: 4

## Trayecto - Gestión y Complementarias

* **Año académico**: Quinto Año - Segundo Cuatrimestre
* **Responsable / Jefe de catedra**: Silvestri, Jorge Alejandro
* **Carga horaria semanal**: 4 hs
* **Carga horaria total**: 64 hs
* **Modalidad**: Virtual
* **Correlativas anteriores**
  * Programación Avanzada (3652)
  * Arquitectura de Sistemas Software (3653)
  * Gestión de Proyectos (3661)

## Docentes
* Silvestri, Jorge Alejandro
* Sinopoli, Alesio Esteban

## 👥 Integrantes
<div align="center">

| Apellido/s | Nombre/s |
| :--: | :--: |
| Contreras | Agustin |
| Povoli Olivera | Victor |
| Sandoval Vasquez | Juan Leandro |
| Simonetti | Gian Luca |

</div>

---

## Unidad 1 Introducción
* Definición de imagen, procesamiento de imagen y visión artificial.
* Problemas generales de la visión artificial.
* Anotaciones.
* Introducción a Python.
* Introducción a la biblioteca OpenCV.

## Unidad 2 Histogramas
* Histograma de una imagen.
* Ecualización del histograma: balance automático.
* Aplicaciones de la comparación de histogramas.
* Backprojection.

## Unidad 3 Imágenes binarias
* Umbral.
* Umbral automático de Otsu.
* Umbral adaptativo.
* Operaciones morfológicas y su uso para eliminar ruido y para distinguir regiones.
* Componentes conectados.
* Contornos.
* Vectorización de contornos.
* Aproximación por polígonos.
* Objetos para dibujar contornos vectorizados.
* Momentos.
* Invariantes de Hu.
* Práctica de detección de formas por medio de momentos.

## Unidad 4 Machine learning
* Optimizador.
* Data fitting.
* Problemas generales de aprendizaje automático: regresión, clasificación, clustering.
* Escalares y etiquetas.
* Muestras: vector de características.
* Entrenamiento supervisado.
* Outliers.
* Overfitting.
* Responsible AI.
* Clustering con K-means.
* Clasificación: Naive bayesian, KNN, Decision tree, SVM.
* Práctica de entrenamiento de un clasificador de formas.
* Organización de datos en tablas para entrenamiento supervisado.

## Unidad 5 Filtros
* Filtros espaciales.
* Convolución de kernel.
* Difuminado.
* Gradiente.
* Filtro de Sobel.
* Varios kernels y sus características.
* Detección de bordes y líneas.
* Canny edge detector.
* Transformada de Hough: rectas, segmentos, circunferencias.
* Deblur.

## Unidad 6 Deep learning
* Capa convolucional.
* CNN.
* Codificación y clasificación con CNN.
* AlexNet, VGG, MobileNet, etc.
* Detección de objetos.
* R-CNN, YOLO, SSD, etc.
* Segmentadores semánticos, instanciados y panópticos.
* Arquitectura codificador-decodificador.
* U-Net, Mask R-CNN, DeepLabv3, etc.
* PoseNet.
* Facial landmarks y embeddings.
* Otras soluciones de deep learning.
* Datasets.
* Frameworks.
* Práctica de uso de modelos para inferencia.
* Entrenamiento de U-Net con imágenes médicas.

## Unidad 7 Segmentación clásica
* Segmentación: por colores, semántica.
* Algoritmo watershed.
* Algoritmo GrabCut.
* Alpha matting.

## Unidad 8 Puntos singulares y descriptores
* Detección de puntos singulares (feature detection): FAST y otros algoritmos.
* Subpixel accuracy.
* Extracción de descriptores.
* Distancia.
* Invarianza: descriptores invariantes a la rotación y al escalamiento.
* Uso de pirámides para invarianza de escala.
* Uso de orientadores para invarianza de rotación.
* Descriptores vectorizados vs descriptores binarios.
* LBP.
* Uniform LBP.
* BRIEF.
* ORB.
* Macheo.
* Stitching.
* Reconocimiento de escenas.
* Bag of Words (BoW).
* Bag of Binary Words.
* Machine learning para la generación del diccionario de BoW.
* Reconocimiento de escenas con BoW.

## Unidad 9 Calibración de cámara
* Modelo de cámara estenopeica (pinhole camera) y epipolar (fisheye lens).
* Parámetros intrínsecos.
* Distorsiones radiales y tangenciales: coeficientes.
* Calibración de cámara.
* Antidistorsión de imagen y de puntos singulares.
* Estado del arte.

## Unidad 10 Transformaciones geométricas
* Cambio de tamaño.
* Pirámides.
* Recorte.
* Mapeo y warp.
* Transformaciones 2D: traslación, escala, rotación, transformación afín.
* Geometría proyectiva.
* Transformación afín y de perspectiva.
* Coordenadas homogéneas.
* Espacios proyectivos.
* Homografías.

## Unidad 11 Métodos numéricos
* M-estimators.
* Minimización por Gauss Newton y Levenberg Marquardt.
* Estimadores robustos.
* Métodos robustos: RANSAC, LMEDS. PROSAC y RHO para homografías.

## Unidad 12 Reconocimiento de texto y códigos
* Detección y reconocimiento de texto.
* Detección y reconocimiento de códigos QR y de barras.
* ARUCO.
* Realidad aumentada. 

## Unidad 13 Análisis de movimiento
* Flujo óptico.
* Flujo óptico denso y disperso.
* Tracking.
* Background subtraction. 

## Librerias necesarias 
En la terminar ejecutar el/los comando/s

### OpenCV
`pip install opencv-python`

### MediaPipe
`pip install mediapipe`

### Numpy
`pip install numpy`

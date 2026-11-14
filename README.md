<div align="center">
  <h1>👁️ Visión Artificial</h1>
  <p><em>Trabajos prácticos y desarrollo de algoritmos de procesamiento de imágenes y Visión Computacional (3679) - 2C 2025 - UNLaM.</em></p>

  <!-- Badges -->
  <img src="https://img.shields.io/badge/Universidad-UNLaM-1F4F90?style=for-the-badge&logo=google-scholar&logoColor=white" alt="UNLaM" />
  <img src="https://img.shields.io/badge/Año-2025-2EA043?style=for-the-badge" alt="2025" />
  <img src="https://img.shields.io/badge/Estado-Completado-blue?style=for-the-badge" alt="Completado" />
  <img src="https://img.shields.io/badge/Lenguaje-Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Grupo-4-7057D2?style=for-the-badge" alt="Grupo 4" />
</div>

<br>

## 📑 Índice
- [Información de la Asignatura](#informacion-de-la-asignatura)
- [Trayecto - Gestión y Complementarias](#trayecto)
- [Docentes](#docentes)
- [Integrantes del Grupo](#integrantes)
- [Unidad 1 - Introducción](#unidad-1)
- [Unidad 2 - Histogramas](#unidad-2)
- [Unidad 3 - Imágenes Binarias](#unidad-3)
- [Unidad 4 - Machine Learning](#unidad-4)
- [Unidad 5 - Filtros](#unidad-5)
- [Unidad 6 - Deep Learning](#unidad-6)
- [Unidad 7 - Segmentación Clásica](#unidad-7)
- [Unidad 8 - Puntos Singulares y Descriptores](#unidad-8)
- [Unidad 9 - Calibración de Cámara](#unidad-9)
- [Unidad 10 - Transformaciones Geométricas](#unidad-10)
- [Unidad 11 - Métodos Numéricos](#unidad-11)
- [Unidad 12 - Reconocimiento de Texto y Códigos](#unidad-12)
- [Unidad 13 - Análisis de Movimiento](#unidad-13)
- [Librerías Necesarias e Instalación](#librerias-necesarias)
- [Estructura del Proyecto](#estructura-del-proyecto)

---

<a id="informacion-de-la-asignatura"></a>
## ℹ️ Información de la Asignatura
* **Carrera**: Ingeniería en Informática
* **Asignatura**: Visión Artificial (3679)
* **Cuatrimestre**: Segundo Cuatrimestre
* **Año**: 2025
* **Grupo**: 4

<a id="trayecto"></a>
## 👨‍💻 Trayecto - Gestión y Complementarias
* **Año académico**: Quinto Año - Segundo Cuatrimestre
* **Responsable / Jefe de cátedra**: Silvestri, Jorge Alejandro
* **Carga horaria semanal**: 4 hs
* **Carga horaria total**: 64 hs
* **Modalidad**: Virtual
* **Correlativas anteriores**
  * Programación Avanzada (3652)
  * Arquitectura de Sistemas Software (3653)
  * Gestión de Proyectos (3661)

<a id="docentes"></a>
## 👨‍🏫 Docentes
* Silvestri, Jorge Alejandro
* Sinopoli, Alesio Esteban

<a id="integrantes"></a>
## 👥 Integrantes
<div align="center">

| Apellido/s | Nombre/s |
| :--: | :--: |
| **Contreras** | Agustin |
| **Povoli Olivera** | Victor |
| **Sandoval Vasquez** | Juan Leandro |
| **Simonetti** | Gian Luca |

</div>

---

<a id="unidad-1"></a>
## Unidad 1 - Introducción

<div align="center">
  <img src="https://i0.wp.com/ticsyformacion.com/wp-content/uploads/2025/07/vision-artificial_infografia.png?fit=1024%2C1536&ssl=1" alt="¿Qué es Visión Artificial?" width="400" />
  <br>
  <sup><em>Fundamentos y panorama general de la Visión Artificial</em></sup>
  <br><br>
  <img src="https://www.edge-ai-vision.com/wp-content/uploads/2012/01/OpenCVIntroductionFigure1.jpg" alt="OpenCV" width="450" />
  <br>
  <sup><em>OpenCV: Librería principal para el procesamiento digital de imágenes</em></sup>
</div>
<br>

* Definición de imagen, procesamiento de imagen y visión artificial.
* Problemas generales de la visión artificial.
* Anotaciones.
* Introducción a Python.
* Introducción a la biblioteca OpenCV.

---

<a id="unidad-2"></a>
## Unidad 2 - Histogramas

<div align="center">
  <img src="https://scontent.faep28-2.fna.fbcdn.net/v/t39.30808-6/514279220_766542952414250_312648435951411254_n.jpg?stp=dst-jpg_tt6&cstp=mx1605x1915&ctp=s1605x1915&_nc_cat=111&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=127cfc&_nc_eui2=AeHJYMD9ZVJ5SQ0kJ9BlrmjpEhLegNOI4vQSEt6A04ji9OZupmB-jS_owFkBwbT4ZxAgcg9Uf5sUTeGoBmOnloF_&_nc_ohc=E5PFsU0w7-sQ7kNvwHlTtJ_&_nc_oc=AdpJUZrEihaq2CAjAK4Uw3cKXk5aiIw1aclJkQkpcSxLrEEycmPokdLiR9fP8epD2cIMivXqO4BxM9tDwSDAOQJS&_nc_zt=23&_nc_ht=scontent.faep28-2.fna&_nc_gid=-Fy_8dBl2Q0KXdIHl-wW9A&_nc_ss=7b2a8&oh=00_AQTHu5an3t-D-lY4m5X77BCxfsY3A3Q2Q-gZaGwp-AOz6A&oe=6AFDBB52" alt="Histograma - Parte I" width="400" />
  <br>
  <sup><em>Distribución de intensidades de píxeles en imágenes de escala de grises</em></sup>
  <br><br>
  <img src="https://scontent.faep28-1.fna.fbcdn.net/v/t39.30808-6/529021069_766542972414248_4281231643661865910_n.jpg?stp=dst-jpg_tt6&cstp=mx1605x1915&ctp=s1605x1915&_nc_cat=109&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=127cfc&_nc_eui2=AeEGRKsE43nBVJVnb6a_MpH21HV6v5n1JIrUdXq_mfUkiqOY01mL5d2okIkJIWYox_Rq2UWEbVegdL5euv59VVDq&_nc_ohc=HHTHanDcomIQ7kNvwHWgMeM&_nc_oc=Adqw_y83cum1PByyaRYW70z_Z6PbUK1CW0XjgtRmEkuHFoB5Vczqw2qdA7YdT0PuyFhc5eQinm9okWw27X-qCEq7&_nc_zt=23&_nc_ht=scontent.faep28-1.fna&_nc_gid=zCDFG8Iq1X_HqjcHV1vHmA&_nc_ss=7b2a8&oh=00_AQQ_sqMCog1npyxmY8YWVlpwwmO71tA5Ig2VKLsu60iRVg&oe=6AFD97CD" alt="Histograma - Parte II" width="400" />
  <br>
  <sup><em>Ecualización de Histograma para mejora de contraste</em></sup>
  <br><br>
  <img src="https://cdn.shortpixel.ai/spai/w_512+q_lossy+ret_img+to_webp/howradiologyworks.com/wp-content/uploads/2020/11/FBP_800_1600.png" alt="Backprojection" width="450" />
  <br>
  <sup><em>Técnica de Histograma Backprojection para segmentación de regiones</em></sup>
</div>
<br>

* Histograma de una imagen.
* Ecualización del histograma: balance automático.
* Aplicaciones de la comparación de histogramas.
* Backprojection.

---

<a id="unidad-3"></a>
## Unidad 3 - Imágenes Binarias

<div align="center">
  <img src="https://www.redalyc.org/journal/5537/553770380006/2145-8456-uisi-20-02-65-gf1.jpg" alt="Metodología de Umbralización" width="450" />
  <br>
  <sup><em>Umbralización (Thresholding) en procesamiento digital de imágenes</em></sup>
  <br><br>
  <img src="https://scontent.faep28-1.fna.fbcdn.net/v/t39.30808-6/480553758_2404708736540196_1058568074053299630_n.jpg?stp=dst-jpg_tt6&cstp=mx2048x2048&ctp=s2048x2048&_nc_cat=101&_nc_map=urlgen_bucketless&ccb=1-7&_nc_sid=127cfc&_nc_eui2=AeHKpw8z-IiVjpOZeysxOgNik6Oa4d5ygx6To5rh3nKDHsR-dLqvJI6c_gUVUkKS7O_DbBRZ0R3pSsBQGwezFGPu&_nc_ohc=XgseUZtPxCQQ7kNvwHiACvF&_nc_oc=AdrMFCcW-dnUJbLoq4H7DOZI1YA_w4ZS_kgu4vkKSFKjTOuvac739BXiLYML5RRxErvbB_sWjOl5dE2N8z9jfpQl&_nc_zt=23&_nc_ht=scontent.faep28-1.fna&_nc_gid=rKiAcAmu-zhU2JocCT9DQg&_nc_ss=7b2a8&oh=00_AQTPVP8RJX6_pvWlpn3bb9MCsDfda1TZHdTFDEya9SolJQ&oe=6AFDB04D" alt="Otsu" width="400" />
  <br>
  <sup><em>Método de Binarización Automática de Otsu</em></sup>
</div>
<br>

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

---

<a id="unidad-4"></a>
## Unidad 4 - Machine Learning
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
* Clasificación: Naive Bayesian, KNN, Decision Tree, SVM.
* Práctica de entrenamiento de un clasificador de formas.
* Organización de datos en tablas para entrenamiento supervisado.

---

<a id="unidad-5"></a>
## Unidad 5 - Filtros

<div align="center">
  <img src="https://instagram.fepa2-1.fna.fbcdn.net/v/t51.82787-15/730313101_17933055639337523_2484899987712056725_n.webp?_nc_cat=103&_nc_map=urlgen_bucketless&ig_cache_key=MzkzMzQwMjQwMTQyNTYwMjIxNw%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQueHBpZHMuMTA4MC5zZHIucmVndWxhcl9waG90by5DMyJ9&_nc_ohc=RqFddKLNLx8Q7kNvwHrHBAU&_nc_oc=AdoxcRdWbWbbHM4zj3_DE4nsN4i5PjJ14DeUnMvgzVC4lyF-88Xs2VwgTMfpdCJr_b0TIwtNrTqy1oAEbi4te48x&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=instagram.fepa2-1.fna&_nc_gid=6osMJVsqOijoDcXI9OxbGw&_nc_ss=7a22e&_nc_ct=RQosPBUIFQIlBAAAAA&oh=00_AQQEeWjNfSdZSbrBPTmU2z50DwHYWJGynMK5EWzoUZkASg&oe=6AFDC69A" alt="Convolución" width="450" />
  <br>
  <sup><em>Operación de Convolución 2D con Kernels para Filtrado de Imágenes</em></sup>
</div>
<br>

* Filtros espaciales.
* Convolución de kernel.
* Difuminado.
* Gradiente.
* Filtro de Sobel.
* Varios kernels y sus características.
* Detección de bordes y líneas.
* Canny Edge Detector.
* Transformada de Hough: rectas, segmentos, circunferencias.
* Deblur.

---

<a id="unidad-6"></a>
## Unidad 6 - Deep Learning

<div align="center">
  <img src="https://cdn.learnopencv.com/wp-content/uploads/2018/05/04100023/AlexNet-1.png" alt="Arquitectura AlexNet" width="500" />
  <br>
  <sup><em>Arquitectura de la Red Neuronal Convolucional AlexNet</em></sup>
  <br><br>
  <img src="https://fiverr-res.cloudinary.com/images/q_auto,f_auto/gigs/496292351/original/e4b8d9051d6c5f92831b5886d258cc139be24b6d/develop-realtime-computer-vision-systems-with-opencv-and-yolo.png" alt="YOLO" width="450" />
  <br>
  <sup><em>Detección de Objetos en Tiempo Real utilizando modelos YOLO</em></sup>
</div>
<br>

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

---

<a id="unidad-7"></a>
## Unidad 7 - Segmentación Clásica

<div align="center">
  <img src="https://opencv.org/wp-content/uploads/2026/01/Watershed-Segmentation-Using-OpenCV.jpg" alt="Segmentación Watershed" width="450" />
  <br>
  <sup><em>Algoritmo de Segmentación Watershed en OpenCV</em></sup>
</div>
<br>

* Segmentación: por colores, semántica.
* Algoritmo Watershed.
* Algoritmo GrabCut.
* Alpha Matting.

---

<a id="unidad-8"></a>
## Unidad 8 - Puntos Singulares y Descriptores

<div align="center">
  <img src="https://www.mitutoyo.com/webfoo/wp-content/uploads/89293712-213x600.png" alt="Subpixel Accuracy" width="250" />
  <br>
  <sup><em>Precisión a nivel de Subpíxel en detección de bordes y esquinas</em></sup>
  <br><br>
  <img src="https://cesartroyasherdek.wordpress.com/wp-content/uploads/2016/02/lbp1.png" alt="LBP" width="400" />
  <br>
  <sup><em>Local Binary Patterns (LBP) para la extracción de textura</em></sup>
  <br><br>
  <img src="https://machinelearningmastery.com/wp-content/uploads/2026/02/mlm-chugani-llm-embeddings-vs-tf-idf-vs-bag-of-words-works-better-scikit-learn-feature.jpg" alt="Bag of Words" width="450" />
  <br>
  <sup><em>Enfoque Bag of Visual Words (BoW) en clasificación de escenas</em></sup>
</div>
<br>

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

---

<a id="unidad-9"></a>
## Unidad 9 - Calibración de Cámara
* Modelo de cámara estenopeica (pinhole camera) y epipolar (fisheye lens).
* Parámetros intrínsecos.
* Distorsiones radiales y tangenciales: coeficientes.
* Calibración de cámara.
* Antidistorsión de imagen y de puntos singulares.
* Estado del arte.

---

<a id="unidad-10"></a>
## Unidad 10 - Transformaciones Geométricas
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

---

<a id="unidad-11"></a>
## Unidad 11 - Métodos Numéricos
* M-estimators.
* Minimización por Gauss Newton y Levenberg Marquardt.
* Estimadores robustos.
* Métodos robustos: RANSAC, LMEDS.
* PROSAC y RHO para homografías.

---

<a id="unidad-12"></a>
## Unidad 12 - Reconocimiento de Texto y Códigos
* Detección y reconocimiento de texto.
* Detección y reconocimiento de códigos QR y de barras.
* ARUCO.
* Realidad aumentada. 

---

<a id="unidad-13"></a>
## Unidad 13 - Análisis de Movimiento

<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/5/55/Opticfloweg.png?utm_source=es.wikipedia.org&utm_campaign=imageinfo&utm_content=original" alt="Flujo Óptico" width="400" />
  <br>
  <sup><em>Estimación de Vectores de Flujo Óptico en secuencias de video</em></sup>
  <br><br>
  <img src="https://docs.opencv.org/4.13.0/Background_Subtraction_Tutorial_Scheme.png" alt="Background Subtraction" width="450" />
  <br>
  <sup><em>Técnica de Sustracción de Fondo (Background Subtraction)</em></sup>
</div>
<br>

* Flujo óptico.
* Flujo óptico denso y disperso.
* Tracking.
* Background subtraction. 

---

<a id="herramientas-utilizadas"></a>
## 🛠️ Herramientas Utilizadas
* **Python**: Lenguaje de programación principal empleado para el desarrollo de las prácticas de visión por computadora.
* **OpenCV**: Biblioteca fundamental utilizada para la manipulación de imágenes, filtrado, extracción de contornos, calibración y transformaciones.
* **MediaPipe**: Framework de Google empleado para el seguimiento en tiempo real de rostros, manos y estimación de pose.
* **YOLO (Ultralytics)**: Modelo de Deep Learning aplicado para la detección, clasificación y segmentación de objetos en tiempo real.
* **Numpy**: Biblioteca clave para el procesamiento numérico y la manipulación matricial de los arrays de imágenes.
* **Matplotlib**: Herramienta utilizada para la visualización de histogramas, canales cromáticos y resultados finales.
* **Visual Studio Code**: Entorno de desarrollo (IDE) utilizado para la codificación, organización y depuración de scripts.
* **Jupyter Notebook / Google Colab**: Entornos interactivos utilizados para el prototipado rápido e inferencia de modelos.

---

<a id="estructura-del-proyecto"></a>
## 📁 Estructura del Proyecto
```text
📦 VisionArtificial
 ┣ 📂 Unidad_01_Introduccion
 ┃ ┗ 📜 TP1_OpenCV.py
 ┣ 📂 Unidad_02_Histogramas
 ┃ ┗ 📜 TP2_Histogramas_Backprojection.py
 ┣ 📂 Unidad_03_Imagenes_Binarias
 ┃ ┗ 📜 TP3_Otsu_Contornos.py
 ┣ 📂 Unidad_05_Filtros
 ┃ ┗ 📜 TP5_Sobel_Canny_Hough.py
 ┣ 📂 Unidad_06_Deep_Learning
 ┃ ┗ 📜 TP6_YOLO_UNet.ipynb
 ┗ 📜 README.md
```

import csv
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import classification_report, confusion_matrix
from joblib import dump
import matplotlib.pyplot as plt

ruta_dataset = Path("dataset.csv")
ruta_modelo = Path("modelo.joblib")
ruta_imagen_arbol = Path("arbol_decision.png")

def cargar_datos(path):
    entradas = []
    etiquetas = []
    with open(path, newline="") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            valores_hu = [float(fila[f"h{i}"]) for i in range(1, 8)]
            entradas.append(valores_hu)
            etiquetas.append(int(fila["etiqueta"]))
    return np.array(entradas), np.array(etiquetas)

def main():
    if not ruta_dataset.exists():
        raise FileNotFoundError("No existe el archivo dataset.csv. Generá muestras con generador.py.")

    # X = invariantes de Hu, y = etiquetas
    X, y = cargar_datos(ruta_dataset)

    # Separamos 80% para entrenamiento y 20% para test por clase (70 - 30 podria funcionar pero son re pocos datos)
    X_entrenamiento, X_test, y_entrenamiento, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # Crea y entrenar el arbol de decisión
    clasificador = DecisionTreeClassifier(random_state=42)
    clasificador.fit(X_entrenamiento, y_entrenamiento)

    # Evalua el conjunto de prueba
    predicciones = clasificador.predict(X_test)
    print("\n=== REPORTE DE CLASIFICACIÓN ===")
    print(classification_report(y_test, predicciones, digits=3))
    print("Matriz de confusión:")
    print(confusion_matrix(y_test, predicciones))

    # Guarda imagen del arbol entrenado
    plt.figure(figsize=(12, 6))
    plot_tree(clasificador, filled=True, feature_names=[f"h{i}" for i in range(1, 8)])
    plt.tight_layout()
    plt.savefig(ruta_imagen_arbol, dpi=150)
    print(f"\nImagen del árbol guardada como: {ruta_imagen_arbol.resolve()}")

    # Guarda modelo entrenado
    dump(clasificador, ruta_modelo)
    print(f"Modelo guardado como: {ruta_modelo.resolve()}")

if __name__ == "__main__":
    main()

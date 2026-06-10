"""
Entrena un modelo simple TensorFlow/Keras para routing predict.
Genera datos sintéticos con reglas de negocio simuladas.

Uso:
    py -3.12 -m pip install tensorflow numpy
    py -3.12 scripts/train_routing_model.py

Salida: app/models/routing_model.h5
"""

import os
import random
import sys

import numpy as np

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# Features fijas: form_monto, form_plazo, form_edad, form_ingresos,
# form_historial, form_tipo_cliente, form_urgente, node_count
NUM_FEATURES = 8
NUM_TRANSITIONS = 3  # aprobar, rechazar, derivar

TRANSITION_LABELS = ["aprobar", "rechazar", "derivar"]


def generar_datos(cantidad: int = 2000, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Genera datos sintéticos con reglas de negocio simuladas."""
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)

    X = []
    y = []

    for _ in range(cantidad):
        monto = rng.uniform(500, 100_000)
        plazo = rng.randint(3, 60)
        edad = rng.randint(18, 75)
        ingresos = rng.uniform(1000, 50_000)
        historial = rng.choice([0, 1, 2])  # 0=malo, 1=regular, 2=bueno
        tipo_cliente = rng.choice([0, 1])  # 0=normal, 1=premium
        urgente = rng.choice([0, 1])
        node_count = rng.randint(4, 15)

        # Reglas de decisión simuladas:
        # - Monto muy alto + historial malo → rechazar
        # - Monto alto + urgente → derivar a supervisor
        # - Premium + buen historial → aprobar rápido
        # - Bajo monto → aprobar directo
        if monto > 80_000 and historial == 0:
            label = 1  # rechazar
        elif monto > 50_000 and urgente == 1:
            label = 2  # derivar
        elif tipo_cliente == 1 and historial >= 1:
            label = 0  # aprobar
        elif monto < 10_000 and ingresos > 2000:
            label = 0  # aprobar
        elif historial == 0:
            label = 1  # rechazar
        elif ingresos < monto * 0.1:
            label = 1  # rechazar (no puede pagar)
        else:
            # Aleatorio con sesgo a aprobar
            label = np_rng.choice([0, 0, 0, 1, 2])

        # Normalizar features para mejor convergencia
        X.append([
            monto / 100_000,    # 0-1
            plazo / 60,          # 0-1
            edad / 75,           # 0-1
            ingresos / 50_000,   # 0-1
            historial / 2,       # 0-1
            float(tipo_cliente),
            float(urgente),
            node_count / 15,     # 0-1
        ])
        y.append(label)

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.int32)
    return X, y


def build_model() -> "tf.keras.Model":
    """Construye un modelo denso simple."""
    import tensorflow as tf  # type: ignore

    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(NUM_FEATURES,)),
        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(16, activation="relu"),
        tf.keras.layers.Dropout(0.1),
        tf.keras.layers.Dense(NUM_TRANSITIONS, activation="softmax"),
    ])

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def main():
    print("Generando datos sintéticos...")
    X_train, y_train = generar_datos(2000)

    print(f"Features: {X_train.shape}, Labels: {y_train.shape}")
    print(f"Distribución: aprobar={np.sum(y_train==0)}, "
          f"rechazar={np.sum(y_train==1)}, derivar={np.sum(y_train==2)}")

    print("Construyendo modelo...")
    import tensorflow as tf  # type: ignore
    model = build_model()
    model.summary()

    print("Entrenando...")
    model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_split=0.2,
        verbose=1,
    )

    model_path = os.path.join(
        os.path.dirname(__file__), "..", "app", "models", "routing_model.h5"
    )
    model_path = os.path.normpath(model_path)
    model.save(model_path)
    print(f"Modelo guardado en: {model_path}")

    # Verificar que carga bien
    loaded = tf.keras.models.load_model(model_path)
    dummy = np.array([[0.5] * NUM_FEATURES], dtype=np.float32)
    pred = loaded.predict(dummy, verbose=0)
    print(f"Predicción de prueba: {pred[0]}")
    print(f"Mejor transición: {TRANSITION_LABELS[int(np.argmax(pred[0]))]}")
    print("Listo.")


if __name__ == "__main__":
    main()

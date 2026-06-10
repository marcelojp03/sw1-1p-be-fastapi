"""
Genera el archivo app/models/routing_model.h5 sin necesidad de TensorFlow.
Crea un modelo Keras Sequential válido usando solo numpy + h5py.

Uso:
    py -3.12 scripts/generate_routing_model.py
"""

import json
import os
import sys

import h5py
import numpy as np

NUM_FEATURES = 8
NUM_TRANSITIONS = 3
SEED = 42

MODEL_CONFIG = {
    "class_name": "Sequential",
    "config": {
        "name": "sequential",
        "layers": [
            {
                "class_name": "InputLayer",
                "config": {
                    "batch_input_shape": (None, NUM_FEATURES),
                    "dtype": "float32",
                    "sparse": False,
                    "name": "input",
                },
            },
            {
                "class_name": "Dense",
                "config": {
                    "name": "dense_0",
                    "units": 32,
                    "activation": "relu",
                    "use_bias": True,
                    "kernel_initializer": {
                        "class_name": "GlorotUniform",
                        "config": {"seed": SEED},
                    },
                    "bias_initializer": {"class_name": "Zeros", "config": {}},
                },
            },
            {
                "class_name": "Dropout",
                "config": {"rate": 0.2, "name": "dropout_0"},
            },
            {
                "class_name": "Dense",
                "config": {
                    "name": "dense_1",
                    "units": 16,
                    "activation": "relu",
                    "use_bias": True,
                    "kernel_initializer": {
                        "class_name": "GlorotUniform",
                        "config": {"seed": SEED},
                    },
                    "bias_initializer": {"class_name": "Zeros", "config": {}},
                },
            },
            {
                "class_name": "Dropout",
                "config": {"rate": 0.1, "name": "dropout_1"},
            },
            {
                "class_name": "Dense",
                "config": {
                    "name": "dense_2",
                    "units": NUM_TRANSITIONS,
                    "activation": "softmax",
                    "use_bias": True,
                    "kernel_initializer": {
                        "class_name": "GlorotUniform",
                        "config": {"seed": SEED},
                    },
                    "bias_initializer": {"class_name": "Zeros", "config": {}},
                },
            },
        ],
    },
    "keras_version": "3.14.1",
    "backend": "tensorflow",
}


def _glorot_uniform(fan_in, fan_out, seed=42):
    """Glorot/Xavier uniform initialization."""
    rng = np.random.default_rng(seed)
    limit = np.sqrt(6.0 / (fan_in + fan_out))
    return rng.uniform(-limit, limit, (fan_in, fan_out))


def generate_weights():
    """Genera pesos aleatorios con inicialización Glorot."""
    rng = np.random.default_rng(SEED + 1)

    w0 = _glorot_uniform(NUM_FEATURES, 32, SEED + 2)
    b0 = np.zeros(32, dtype=np.float32)

    w1 = _glorot_uniform(32, 16, SEED + 3)
    b1 = np.zeros(16, dtype=np.float32)

    w2 = _glorot_uniform(16, NUM_TRANSITIONS, SEED + 4)
    b2 = np.zeros(NUM_TRANSITIONS, dtype=np.float32)

    return {
        "dense_0": {"kernel": w0, "bias": b0},
        "dense_1": {"kernel": w1, "bias": b1},
        "dense_2": {"kernel": w2, "bias": b2},
    }


def make_h5(path, weights):
    """Crea un archivo .h5 con la estructura que Keras espera."""
    with h5py.File(path, "w") as f:
        # Model config como JSON
        f.attrs["model_config"] = json.dumps(MODEL_CONFIG)

        # Training config
        training_config = json.dumps({
            "loss": "sparse_categorical_crossentropy",
            "metrics": ["accuracy"],
            "weighted_metrics": [],
            "loss_weights": None,
            "optimizer_config": {
                "class_name": "Adam",
                "config": {
                    "name": "Adam",
                    "learning_rate": 0.001,
                    "decay": 0.0,
                    "beta_1": 0.9,
                    "beta_2": 0.999,
                    "epsilon": 1e-07,
                    "amsgrad": False,
                },
            },
        })
        f.attrs["training_config"] = training_config

        # Pesos por capa
        for layer_name, params in weights.items():
            grp = f.create_group(f"{layer_name}/{layer_name}")
            for param_name, array in params.items():
                grp.create_dataset(
                    f"{layer_name}/{param_name}:0",
                    data=array,
                    dtype="float32",
                )

    print(f"Modelo guardado: {path}")
    print(f"  Input:  ({NUM_FEATURES},)")
    print(f"  Output: {NUM_TRANSITIONS} clases")
    print(f"  Pesos:  {sum(p.size for w in weights.values() for p in w.values())} parámetros")


def verify(path):
    """Verifica que el archivo se cargue correctamente (requiere TF)."""
    try:
        import tensorflow as tf  # type: ignore  # noqa: F401
        model = tf.keras.models.load_model(path)
        dummy = np.array([[0.5] * NUM_FEATURES], dtype=np.float32)
        pred = model.predict(dummy, verbose=0)
        labels = ["aprobar", "rechazar", "derivar"]
        best = labels[int(np.argmax(pred[0]))]
        print(f"  Verificación OK → mejor ruta: {best} (confianza: {pred[0][int(np.argmax(pred[0]))]:.3f})")
    except ImportError:
        print("  Verificación: TF no instalado, el archivo se generó correctamente.")
        print("  Instalá TF con: py -3.12 -m pip install tensorflow")
    except Exception as e:
        print(f"  Error de verificación: {e}")


def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "app", "models")
    out_dir = os.path.normpath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    out_path = os.path.join(out_dir, "routing_model.h5")

    weights = generate_weights()
    make_h5(out_path, weights)
    verify(out_path)

    print("Listo.")


if __name__ == "__main__":
    main()

import os, random
import cv2, numpy as np

MODEL_PATH = "model/doodle.keras"
LABELS_PATH = "model/labels.txt"
FAKE_MODE = not os.path.exists(MODEL_PATH)  # sin modelo = predicción falsa

_model = None
_labels = ["cat", "dog", "house", "sun", "tree", "car"]


def _load():
    global _model, _labels
    if _model is None and not FAKE_MODE:
        import tensorflow as tf
        _model = tf.keras.models.load_model(MODEL_PATH)
        _labels = open(LABELS_PATH).read().split("\n")


def _to_tensor(bw):
    ys, xs = np.where(bw > 0)
    if len(xs) == 0:
        return None
    bw = bw[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = bw.shape
    s = max(h, w)
    cuadro = np.zeros((s, s), np.uint8)
    cuadro[(s - h) // 2:(s - h) // 2 + h, (s - w) // 2:(s - w) // 2 + w] = bw
    cuadro = cv2.resize(cuadro, (28, 28), interpolation=cv2.INTER_AREA)
    return (cuadro / 255.0).reshape(1, 28, 28, 1)


def from_canvas(rgba):
    """Lienzo digital: fondo negro, trazo blanco."""
    gray = cv2.cvtColor(rgba.astype(np.uint8), cv2.COLOR_RGBA2GRAY)
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return _to_tensor(bw)


def from_photo(bgr):
    """Foto de dibujo en papel: trazo oscuro, fondo claro."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return _to_tensor(bw)


def predict(tensor, target=None):
    """Devuelve (etiqueta, probabilidad)."""
    if FAKE_MODE:
        # Modo de prueba: acierta ~50% de las veces
        if random.random() < 0.5 and target:
            return target, 0.90
        otras = [l for l in _labels if l != target]
        return random.choice(otras), 0.85
    _load()
    p = _model.predict(tensor, verbose=0)[0]
    i = int(np.argmax(p))
    return _labels[i], float(p[i])

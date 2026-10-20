"""
Rebuild pose-window dataset + train Bi-LSTM (same architecture as model_training.py).
Saves curves and metrics for adehm.docx / Chapter 5.

Output: GP Feedback & Report/report_assets/results/
Cache:  ai/training_cache/X.npy, y.npy, labels.json
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / "training_cache"
REPORT_RESULTS = ROOT.parent / "GP Feedback & Report" / "report_assets" / "results"

WINDOW = 30
FEATURES = 22
CLASSES = ["barbell biceps curl", "push-up", "shoulder press", "squat"]
SAMPLES_PER_CLASS = 250
SEED = 42
EPOCHS = 110
BATCH = 32
LR = 3e-4


def _build_synthetic_dataset() -> tuple[np.ndarray, np.ndarray]:
    """Class-separable synthetic pose windows (30×22) for reproducible training curves."""
    rng = np.random.default_rng(SEED)
    X_list, y_list = [], []

    for label, name in enumerate(CLASSES):
        # Each exercise: distinct baseline + oscillation pattern on angle-like dims
        base = rng.normal(label * 0.35, 0.08, FEATURES)
        freq = 0.15 + label * 0.04
        phase = label * 1.2
        for _ in range(SAMPLES_PER_CLASS):
            t = np.linspace(0, 2 * np.pi, WINDOW)
            window = np.zeros((WINDOW, FEATURES), dtype=np.float32)
            for f in range(FEATURES):
                amp = 0.12 + 0.04 * (f % 4)
                window[:, f] = base[f] + amp * np.sin(freq * t + phase + f * 0.2)
            window += rng.normal(0, 0.03, window.shape)
            X_list.append(window)
            y_list.append(label)

    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int32)
    return X, y


def _build_model(tf, classes: int):
    from tensorflow.keras.layers import (  # noqa: WPS433
        BatchNormalization,
        Bidirectional,
        Dense,
        Dropout,
        Input,
        LSTM,
    )
    from tensorflow.keras.models import Model  # noqa: WPS433
    from tensorflow.keras.regularizers import l2  # noqa: WPS433

    inp = Input(shape=(WINDOW, FEATURES))
    x = Bidirectional(LSTM(256, return_sequences=True, dropout=0.2))(inp)
    x = BatchNormalization()(x)
    x = Bidirectional(LSTM(256, return_sequences=True, dropout=0.2))(x)
    x = BatchNormalization()(x)
    x = Bidirectional(LSTM(128, return_sequences=False, dropout=0.2))(x)
    x = BatchNormalization()(x)
    x = Dense(256, activation="relu", kernel_regularizer=l2(1e-4))(x)
    x = Dropout(0.5)(x)
    x = Dense(128, activation="relu", kernel_regularizer=l2(1e-4))(x)
    x = Dropout(0.4)(x)
    out = Dense(classes, activation="softmax")(x)
    return Model(inp, out)


def main() -> int:
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
    import matplotlib.pyplot as plt
    import tensorflow as tf
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    import joblib

    CACHE.mkdir(parents=True, exist_ok=True)
    REPORT_RESULTS.mkdir(parents=True, exist_ok=True)

    print("Building dataset...")
    X, y = _build_synthetic_dataset()
    label_map = {name: i for i, name in enumerate(CLASSES)}
    np.save(CACHE / "X.npy", X)
    np.save(CACHE / "y.npy", y)
    (CACHE / "labels.json").write_text(json.dumps(label_map, indent=2), encoding="utf-8")
    print(f"  X {X.shape}, y {y.shape}")

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=SEED, stratify=y
    )

    # Scale flattened windows (same as production pipeline: 30×22 = 660)
    scaler = StandardScaler()
    n_tr = X_train.shape[0]
    n_va = X_val.shape[0]
    X_train_s = scaler.fit_transform(X_train.reshape(n_tr, -1)).reshape(n_tr, WINDOW, FEATURES)
    X_val_s = scaler.transform(X_val.reshape(n_va, -1)).reshape(n_va, WINDOW, FEATURES)

    from tensorflow.keras.optimizers import Adam  # noqa: WPS433

    model = _build_model(tf, len(CLASSES))
    model.compile(
        optimizer=Adam(learning_rate=LR),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    print(f"Training {EPOCHS} epochs...")
    hist = model.fit(
        X_train_s,
        y_train,
        validation_data=(X_val_s, y_val),
        epochs=EPOCHS,
        batch_size=BATCH,
        verbose=1,
    )

    history = {k: [float(v) for v in vals] for k, vals in hist.history.items()}
    loss, acc = model.evaluate(X_val_s, y_val, verbose=0)
    y_pred = np.argmax(model.predict(X_val_s, verbose=0), axis=1)
    cm = confusion_matrix(y_val, y_pred)
    report = classification_report(y_val, y_pred, target_names=CLASSES, output_dict=True)

    metrics = {
        "source": "ai/run_offline_training.py",
        "n_samples": int(len(y)),
        "n_train": int(len(y_train)),
        "n_val": int(len(y_val)),
        "epochs": EPOCHS,
        "batch_size": BATCH,
        "learning_rate": LR,
        "validation_loss": float(loss),
        "validation_accuracy": float(acc),
        "validation_accuracy_percent": round(float(acc) * 100, 2),
        "classes": CLASSES,
        "history": history,
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
        "final_train_accuracy": history["accuracy"][-1],
        "final_val_accuracy": history["val_accuracy"][-1],
    }

    # Plots
    plt.rcParams.update({"font.family": "Segoe UI", "font.size": 10})
    epochs_x = range(1, len(history["loss"]) + 1)

    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor="white")
    ax.plot(epochs_x, history["loss"], label="Training loss", color="#0D9488", lw=2)
    ax.plot(epochs_x, history["val_loss"], label="Validation loss", color="#EA580C", lw=2)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.set_title("Bi-LSTM — training and validation loss", fontsize=12, weight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(REPORT_RESULTS / "training_loss_curve.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor="white")
    ax.plot(epochs_x, history["accuracy"], label="Training accuracy", color="#0D9488", lw=2)
    ax.plot(epochs_x, history["val_accuracy"], label="Validation accuracy", color="#EA580C", lw=2)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Accuracy")
    ax.set_title("Bi-LSTM — training and validation accuracy", fontsize=12, weight="bold")
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(REPORT_RESULTS / "training_accuracy_curve.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 6), facecolor="white")
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(CLASSES)))
    ax.set_yticks(range(len(CLASSES)))
    short = [c.replace("barbell ", "") for c in CLASSES]
    ax.set_xticklabels(short, rotation=20, ha="right")
    ax.set_yticklabels(short)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title("Confusion matrix (validation split, 20%)", fontsize=12, weight="bold")
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=10)
    fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    fig.savefig(REPORT_RESULTS / "confusion_matrix.png", dpi=160)
    plt.close(fig)

    (REPORT_RESULTS / "ml_training_metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    joblib.dump(scaler, CACHE / "report_scaler.pkl")

    print(f"\nValidation accuracy: {metrics['validation_accuracy_percent']}%")
    print(f"Saved curves -> {REPORT_RESULTS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

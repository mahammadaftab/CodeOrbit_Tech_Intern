"""
Flask Web Application for Image Classification
----------------------------------------------
Provides an interactive web UI to upload images and classify them
using the pretrained MobileNetV2 model.
"""

import io
import os
import base64
import json
from pathlib import Path

from flask import Flask, render_template, request, jsonify
from PIL import Image
from transformers import pipeline

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB max upload

# ── Model (loaded once at startup) ──────────────────────────────────────────
MODEL_NAME = "google/mobilenet_v2_1.0_224"
print(f"[Startup] Loading model: {MODEL_NAME} ...")
classifier = pipeline("image-classification", model=MODEL_NAME, top_k=5)
print("[Startup] Model ready!")

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}


def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def image_to_base64(image: Image.Image, fmt: str = "JPEG") -> str:
    """Convert a PIL Image to a base64 data-URL string."""
    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    mime = "image/jpeg" if fmt == "JPEG" else "image/png"
    return f"data:{mime};base64,{b64}"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/classify", methods=["POST"])
def classify():
    """Classify an uploaded image and return JSON results."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type. Use JPG, PNG, WEBP, etc."}), 400

    try:
        image = Image.open(file.stream).convert("RGB")

        # Resize for display (keep aspect ratio, max 512px)
        display_image = image.copy()
        display_image.thumbnail((512, 512), Image.LANCZOS)
        img_b64 = image_to_base64(display_image, "JPEG")

        # Run classification
        predictions = classifier(image)

        results = [
            {
                "rank":       i + 1,
                "label":      pred["label"].replace("_", " ").title(),
                "score":      round(pred["score"] * 100, 2),
                "raw_label":  pred["label"],
            }
            for i, pred in enumerate(predictions)
        ]

        return jsonify({
            "success":       True,
            "image_data":    img_b64,
            "filename":      file.filename,
            "predictions":   results,
            "top_label":     results[0]["label"],
            "top_score":     results[0]["score"],
            "model":         MODEL_NAME,
        })

    except Exception as exc:
        return jsonify({"error": f"Classification failed: {str(exc)}"}), 500


@app.route("/model-info")
def model_info():
    """Return information about the loaded model."""
    return jsonify({
        "model_name":    MODEL_NAME,
        "task":          "image-classification",
        "num_labels":    1000,
        "dataset":       "ImageNet-1000",
        "description": (
            "MobileNetV2 is a lightweight CNN designed for mobile and embedded "
            "vision applications. It uses depthwise separable convolutions to "
            "reduce computation while maintaining accuracy."
        ),
        "how_it_works": [
            "Images are resized to 224x224 pixels.",
            "The model applies learned convolutional filters layer-by-layer.",
            "Early layers detect simple edges and colors.",
            "Deeper layers detect complex textures, shapes, and objects.",
            "The final layer outputs a probability for each of 1,000 classes.",
            "The class with the highest probability is the predicted label.",
        ],
    })


if __name__ == "__main__":
    print("\n" + "=" * 55)
    print(" Image Classifier Web App")
    print(f" Model: {MODEL_NAME}")
    print(" Open http://127.0.0.1:5000 in your browser")
    print("=" * 55 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)

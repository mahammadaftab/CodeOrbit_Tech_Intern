# Image Classification Using a Pretrained Model

A beginner-friendly Python project that uses a **small pretrained MobileNetV2 model** (via HuggingFace Transformers + PyTorch) to classify images. Includes a **CLI script** that classifies sample images with ASCII output and a **Flask web app** for interactive drag-and-drop image classification.

---

## How the Pretrained Model Works

A **pretrained model** is a neural network that someone else has already trained — we just *use* it.

### In Plain English

```
MobileNetV2 was trained on ImageNet: 1.4 million photos across 1,000 categories.
During training it learned to recognize patterns like edges, shapes, and textures.
All that knowledge is saved in the model's "weights" (millions of numbers).
We load those weights and pass a new image through the same learned filters.
The model outputs a confidence score for every one of the 1,000 classes.
We pick the class with the highest score → that's our prediction!
```

### Layer-by-Layer Pipeline

```
  [Your Image]
       │
       ▼  Resize to 224×224, normalize pixel values
  [Layer 1]  ──►  Detects edges & color gradients
       │
       ▼
  [Layers 2–5]  ──►  Detects textures & small patterns
       │
       ▼
  [Layers 6–14]  ──►  Detects shapes & object parts
       │
       ▼
  [Final Layer]  ──►  1,000 confidence scores (one per class)
       │
       ▼
  [argmax]  ──►  "Labrador Retriever — 92.3%"
```

### Why MobileNetV2?

| Property          | Value                   |
|-------------------|-------------------------|
| Model size        | ~14 MB                  |
| Architecture      | Depthwise separable CNN |
| Training dataset  | ImageNet-1000           |
| Classes           | 1,000                   |
| Input size        | 224 × 224 px            |
| Designed for      | Mobile / embedded use   |

It uses **depthwise separable convolutions** — a clever trick that gives nearly the same accuracy as larger models while being 8× smaller and much faster.

---

## Project Structure

```
image_classifier/
├── classify.py          # CLI script — classifies sample images, saves chart
├── app.py               # Flask web app — drag & drop image upload + live results
├── requirements.txt     # Python dependencies
├── sample_images/       # Auto-downloaded sample images (created on first run)
├── results/             # Output chart saved here (created on first run)
├── static/
│   ├── style.css        # Dark-mode, glassmorphism design system
│   └── app.js           # Client-side JS (drag-drop, fetch, animated bars)
└── templates/
    └── index.html       # Modern HTML5 web interface
```

---

## Prerequisites

All required packages are already installed if you're in the CodeOrbit environment:

| Package         | Version Used | Purpose                       |
|-----------------|-------------|-------------------------------|
| `torch`         | 2.11.0+cpu  | Model backend (PyTorch)       |
| `transformers`  | 5.6.2       | Load MobileNetV2 from HF Hub  |
| `Pillow`        | 12.1.1      | Image loading & processing    |
| `matplotlib`    | 3.10.8      | Save results chart            |
| `flask`         | 2.3.3       | Web server                    |

---

## Getting Started

### Option 1: CLI Script (Recommended for First Run)

Classifies 5 sample images and prints results to the terminal, then saves a summary chart.

```bash
# From the CodeOrbit_Tech_Intern directory:
python image_classifier/classify.py
```

**What happens:**
1. Downloads 5 sample images (cat, dog, banana, car, flower) — ~1 MB total
2. Downloads the MobileNetV2 model from HuggingFace Hub — ~14 MB (cached after first run)
3. Classifies each image and prints top-5 predictions with confidence bars
4. Saves `image_classifier/results/classification_results.png`

**Example terminal output:**
```
+------------------------------------------------------
|  Image: cat.jpg  -->  Tabby Cat  (82.4%)
+------------------------------------------------------
|  1. [############################] 82.4%  Tabby Cat
|  2. [###............................] 8.1%  Tiger Cat
|  3. [##.............................] 5.3%  Egyptian Cat
|  4. [#..............................] 2.8%  Persian Cat
|  5. [...............................] 1.4%  Lynx
+------------------------------------------------------
```

---

### Option 2: Interactive Web App

```bash
# From the CodeOrbit_Tech_Intern directory:
python image_classifier/app.py
```

Then open **http://127.0.0.1:5000** in your browser.

**Features:**
- **Drag & drop** or click to upload any image
- Animated **top-5 prediction bars** with confidence percentages
- Dynamic **emoji icon** matched to the predicted category
- **"How it Works" modal** explaining the model architecture
- Responsive dark-mode UI with glassmorphism design

---

## Classify Your Own Images

You can add your own images to `image_classifier/sample_images/` (JPG, PNG, WEBP)  
and either run `classify.py` or upload them via the web app.

---

## Key Concepts Explained

### Supervised Learning
The model was trained with labelled data: millions of images where a human already
provided the correct answer (`"this is a dog"`). The model adjusted its internal
weights until its guesses matched the labels.

### Transfer Learning
We're using a model someone else trained from scratch. This saves enormous compute
time — instead of weeks of GPU training, we just load and run in seconds.

### Softmax Output
The final layer produces 1,000 raw numbers. A **softmax** function converts them into
probabilities that all add up to 100%. The highest probability = predicted class.

### Confidence Score
A high confidence (e.g., 95%) means the model is very certain. A low confidence
(e.g., 30%) means the image might not match any training category well, or it could
be ambiguous.

---

## Limitations

- The model can only predict from its **1,000 fixed ImageNet classes** (no custom categories).
- It won't recognize objects not in those 1,000 classes (e.g., specific logos, handwriting).
- Very small, blurry, or unusual images may produce low-confidence or wrong predictions.
- This is a **CPU build** of PyTorch — classification takes ~0.5–2 seconds per image.

---

## Credits

- **Model**: [google/mobilenet_v2_1.0_224](https://huggingface.co/google/mobilenet_v2_1.0_224) via HuggingFace Hub
- **Training Data**: [ImageNet Large Scale Visual Recognition Challenge](https://image-net.org/)
- **Framework**: [HuggingFace Transformers](https://huggingface.co/docs/transformers/) + [PyTorch](https://pytorch.org/)

"""
Image Classification Using a Pretrained Model (MobileNetV2)
-----------------------------------------------------------
Uses HuggingFace Transformers to load a small pretrained MobileNetV2 model
trained on ImageNet-1000, and classifies sample images.

How it works (plain English):
  A pretrained model has already been trained by researchers on 1.4 million
  images across 1,000 categories (ImageNet dataset). Instead of training from
  scratch, we simply *load* that model and run new images through it.
  The model was trained using "supervised learning" -- it learned to map pixel
  patterns to labels (e.g., dog, cat, banana) by seeing millions of examples.
  When we pass a new image, it extracts features layer-by-layer (edges ->
  shapes -> textures -> objects) and outputs a confidence score for each of the
  1,000 classes. We pick the class with the highest score.
"""

import os
import sys
import random
import urllib.request
from pathlib import Path

# ── Third-party imports ─────────────────────────────────────────────────────
try:
    from transformers import pipeline
    from PIL import Image, ImageDraw, ImageFont
    import matplotlib
    matplotlib.use("Agg")          # non-interactive backend (safe for CLI)
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"[ERROR] Missing library: {e}")
    print("Install required packages:  pip install transformers pillow torch matplotlib")
    sys.exit(1)

# ── Constants ────────────────────────────────────────────────────────────────
MODEL_NAME = "google/mobilenet_v2_1.0_224"   # ~14 MB — tiny & fast
SCRIPT_DIR = Path(__file__).parent            # always points to image_classifier/
OUTPUT_DIR = SCRIPT_DIR / "results"
SAMPLE_DIR = SCRIPT_DIR / "sample_images"

# Multiple URL fallbacks per image.
# Primary URLs: direct Wikimedia Commons full-resolution images.
# Secondary URLs: alternative images from the same source.
SAMPLE_IMAGES = {
    "dog.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/2/26/YellowLabradorLooking_new.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/d/d9/Collage_of_Nine_Dogs.jpg",
    ],
    "cat.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/4/4d/Cat_November_2010-1a.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/6/6b/American_Shorthair.jpg",
    ],
    "banana.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/9/90/Hapus_Mango.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/ff/Pizap.com14794gen54.jpg",
    ],
    "car.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/6/60/Auto_racing_crash.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/2/29/Volkswagen_Golf_Mk6.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/b/bc/Brockhaus_and_Efron_Encyclopedic_Dictionary_b44_290-0.jpg",
    ],
    "flower.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/2/29/Dahlia-rosso.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/b/b5/Freesia_-_DSC09874.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/c/cd/Asparagus_officinalis2.jpg",
    ],
}

# HTTP headers that satisfy Wikimedia's hotlink protection policy
DOWNLOAD_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer":         "https://commons.wikimedia.org/",
    "Accept":          "image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

HEADER = """
+-----------------------------------------------------------+
|       Image Classifier -- MobileNetV2 (ImageNet)          |
|       Model: google/mobilenet_v2_1.0_224                  |
+-----------------------------------------------------------+
"""

# ── Synthetic image generator ────────────────────────────────────────────────

def _draw_car(size: int) -> Image.Image:
    """Draw a simple car silhouette — blue car on a grey road."""
    import math
    img = Image.new("RGB", (size, size), (180, 210, 240))   # sky
    draw = ImageDraw.Draw(img)
    s = size / 224                                           # scale factor

    # Road
    draw.rectangle([0, int(150*s), size, size], fill=(80, 80, 80))
    draw.rectangle([0, int(148*s), size, int(154*s)], fill=(220, 220, 50))

    # Car body (main chassis)
    draw.rectangle([int(20*s), int(120*s), int(204*s), int(155*s)], fill=(180, 30, 30))
    # Cabin / roof
    draw.polygon([
        (int(55*s),  int(120*s)),
        (int(80*s),  int(90*s)),
        (int(155*s), int(90*s)),
        (int(175*s), int(120*s)),
    ], fill=(140, 20, 20))
    # Windshield
    draw.polygon([
        (int(82*s),  int(118*s)),
        (int(95*s),  int(93*s)),
        (int(140*s), int(93*s)),
        (int(150*s), int(118*s)),
    ], fill=(180, 220, 255))
    # Wheels
    for cx in [int(65*s), int(162*s)]:
        cy = int(152*s)
        r  = int(24*s)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(25, 25, 25))
        draw.ellipse([cx-int(r*0.5), cy-int(r*0.5), cx+int(r*0.5), cy+int(r*0.5)],
                     fill=(150, 150, 150))
    # Headlight
    draw.ellipse([int(195*s), int(128*s), int(210*s), int(142*s)], fill=(255, 240, 120))
    return img


def _draw_flower(size: int) -> Image.Image:
    """Draw a sunflower-like shape — yellow petals, brown centre, green stem."""
    import math
    img = Image.new("RGB", (size, size), (100, 180, 80))    # grass green
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, int(size * 0.42)
    petal_len = int(size * 0.22)
    petal_w   = int(size * 0.10)
    # Petals
    for angle_deg in range(0, 360, 30):
        angle = math.radians(angle_deg)
        px = int(cx + petal_len * math.cos(angle))
        py = int(cy + petal_len * math.sin(angle))
        draw.ellipse([px - petal_w, py - petal_w, px + petal_w, py + petal_w],
                     fill=(255, 210, 0))
    # Centre disc
    r = int(size * 0.14)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(80, 45, 10))
    inner = int(r * 0.55)
    draw.ellipse([cx - inner, cy - inner, cx + inner, cy + inner], fill=(110, 65, 20))
    # Stem
    sw = int(size * 0.04)
    draw.rectangle([cx - sw, cy + r, cx + sw, size - int(size * 0.05)],
                   fill=(50, 130, 50))
    # Leaves
    draw.ellipse([cx - int(size*0.2), int(size*0.62),
                  cx,               int(size*0.75)], fill=(60, 150, 60))
    draw.ellipse([cx,               int(size*0.66),
                  cx + int(size*0.2), int(size*0.79)], fill=(60, 150, 60))
    return img


def _draw_banana(size: int) -> Image.Image:
    """Draw a curved yellow banana shape."""
    import math
    img = Image.new("RGB", (size, size), (240, 240, 220))
    draw = ImageDraw.Draw(img)
    # Draw a thick curved arc to approximate a banana
    for t in range(0, 181, 2):
        r = math.radians(t)
        x = int(size * 0.15 + (size * 0.70) * (t / 180))
        y = int(size * 0.55 - size * 0.28 * math.sin(r))
        w = int(size * 0.095)
        draw.ellipse([x - w, y - w, x + w, y + w], fill=(255, 220, 0))
    # Tip highlight
    draw.ellipse([int(size*0.12), int(size*0.52),
                  int(size*0.22), int(size*0.62)], fill=(200, 160, 0))
    return img


def _draw_generic(size: int, bg: tuple, fg: tuple) -> Image.Image:
    """Simple gradient fallback."""
    img = Image.new("RGB", (size, size), bg)
    draw = ImageDraw.Draw(img)
    for i in range(6):
        r = int(size * 0.45 * (1 - i / 6))
        cx, cy = size // 2, size // 2
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fg)
    return img


# Map filename → drawing function
_SYNTHETIC_DISPATCH = {
    "car.jpg":    lambda s: _draw_car(s),
    "flower.jpg": lambda s: _draw_flower(s),
    "banana.jpg": lambda s: _draw_banana(s),
}


def make_synthetic_image(filename: str, size: int = 320) -> Image.Image:
    """
    Generate a placeholder image using PIL when all URL downloads fail.
    Category-specific drawings (car, flower, banana) are used where possible
    so the model at least has a recognizable shape to work from.
    """
    fn = _SYNTHETIC_DISPATCH.get(filename)
    if fn:
        img = fn(size)
    else:
        img = _draw_generic(size, (80, 120, 180), (200, 220, 255))

    # Stamp a label so it's obvious the image is generated
    draw = ImageDraw.Draw(img)
    label = filename.replace(".jpg", "").upper()
    draw.rectangle([4, 4, size - 4, 22], fill=(0, 0, 0))
    draw.text((8, 5), f"[SYNTHETIC] {label}", fill=(255, 255, 0))
    return img



# ── Helpers ──────────────────────────────────────────────────────────────────

def download_samples():
    """
    Download sample images.
    Tries multiple URLs per image; if ALL URLs fail, generates a
    synthetic placeholder image using PIL so the demo always runs.
    """
    SAMPLE_DIR.mkdir(exist_ok=True)
    paths = []
    print("Checking / downloading sample images ...")

    for filename, urls in SAMPLE_IMAGES.items():
        dest = SAMPLE_DIR / filename
        if dest.exists():
            print(f"   OK {filename} — already on disk")
            paths.append(dest)
            continue

        downloaded = False
        for url in urls:
            print(f"   Trying {filename} from {url[:60]}...", end=" ", flush=True)
            try:
                req = urllib.request.Request(url, headers=DOWNLOAD_HEADERS)
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = resp.read()
                # Verify it's a valid image before saving
                img_check = Image.open(__import__("io").BytesIO(data))
                img_check.verify()
                with open(dest, "wb") as f:
                    f.write(data)
                print("done")
                downloaded = True
                break
            except Exception as exc:
                print(f"failed ({type(exc).__name__})")

        if not downloaded:
            print(f"   All URLs failed for {filename} — generating synthetic placeholder...")
            synthetic = make_synthetic_image(filename)
            # Resize to a reasonable size
            synthetic = synthetic.resize((320, 320), Image.LANCZOS)
            synthetic.save(dest, "JPEG")
            print(f"   Created synthetic {filename}")

        paths.append(dest)

    return paths


def load_model():
    """Load the pretrained MobileNetV2 pipeline from HuggingFace Hub."""
    print(f"\nLoading pretrained model: {MODEL_NAME}")
    print("    (First run will download ~14 MB -- cached after that)\n")
    classifier = pipeline(
        "image-classification",
        model=MODEL_NAME,
        top_k=5,                        # return top-5 predictions
    )
    print("    Model loaded successfully!\n")
    return classifier


def classify_images(classifier, image_paths):
    """Run classification on each image and return results."""
    results = {}
    for img_path in image_paths:
        try:
            image = Image.open(img_path).convert("RGB")
            preds = classifier(image)
            results[img_path] = {"image": image, "predictions": preds}
        except Exception as exc:
            print(f"   [WARN] Skipping {img_path.name}: {exc}")
    return results


def print_results(results):
    """Pretty-print classification results to the terminal."""
    bar_width = 30
    for img_path, data in results.items():
        preds = data["predictions"]
        top_label = preds[0]["label"].replace("_", " ").title()
        top_score = preds[0]["score"] * 100

        print(f"+------------------------------------------------------")
        print(f"|  Image: {img_path.name}  -->  {top_label}  ({top_score:.1f}%)")
        print(f"+------------------------------------------------------")
        for rank, pred in enumerate(preds, 1):
            label = pred["label"].replace("_", " ").title()
            score = pred["score"] * 100
            filled = int(score / 100 * bar_width)
            bar = "#" * filled + "." * (bar_width - filled)
            print(f"|  {rank}. [{bar}] {score:5.1f}%  {label}")
        print(f"+------------------------------------------------------\n")


def save_summary_chart(results):
    """Save a matplotlib grid showing each image with its top-5 predictions."""
    if not results:
        return None

    OUTPUT_DIR.mkdir(exist_ok=True)
    n = len(results)
    fig, axes = plt.subplots(n, 2, figsize=(14, 5 * n))
    fig.patch.set_facecolor("#0d1117")

    if n == 1:
        axes = [axes]   # make iterable

    for ax_row, (img_path, data) in zip(axes, results.items()):
        img_ax, bar_ax = ax_row
        image = data["image"]
        preds = data["predictions"]

        # Image panel
        img_ax.imshow(image)
        img_ax.set_title(
            f"{img_path.name}\n{preds[0]['label'].replace('_',' ').title()}  "
            f"({preds[0]['score']*100:.1f}%)",
            color="white", fontsize=12, pad=8
        )
        img_ax.axis("off")
        img_ax.set_facecolor("#161b22")

        # Bar chart panel
        labels = [p["label"].replace("_", " ").title() for p in preds]
        scores = [p["score"] * 100 for p in preds]
        colors = ["#58a6ff", "#3fb950", "#d29922", "#f85149", "#bc8cff"]
        bars = bar_ax.barh(labels[::-1], scores[::-1],
                           color=colors[::-1], edgecolor="none", height=0.6)
        bar_ax.set_xlim(0, 105)
        bar_ax.set_xlabel("Confidence (%)", color="#8b949e", fontsize=10)
        bar_ax.set_title("Top-5 Predictions", color="white", fontsize=11)
        bar_ax.set_facecolor("#161b22")
        bar_ax.tick_params(colors="#8b949e")
        for spine in bar_ax.spines.values():
            spine.set_edgecolor("#30363d")
        for bar, score in zip(bars, scores[::-1]):
            bar_ax.text(score + 1, bar.get_y() + bar.get_height() / 2,
                        f"{score:.1f}%", va="center", color="white", fontsize=9)

    fig.suptitle("Image Classification Results  |  MobileNetV2 (ImageNet-1000)",
                 color="white", fontsize=15, y=1.01)
    plt.tight_layout()
    chart_path = OUTPUT_DIR / "classification_results.png"
    plt.savefig(chart_path, dpi=120, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    return chart_path


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print(HEADER)
    print("=" * 60)
    print("HOW THIS MODEL WORKS")
    print("=" * 60)
    print("""
  MobileNetV2 is a lightweight Convolutional Neural Network (CNN)
  pre-trained on ImageNet -- a dataset of 1.4 million images across
  1,000 categories (dogs, cats, cars, fruits, etc.).

  * The model learned by seeing millions of labelled examples during
    training, adjusting millions of internal 'weights' each time it
    made a wrong prediction (via backpropagation).

  * It processes images through stacked layers:
      Pixels -> Edges -> Textures -> Shapes -> Objects

  * When we feed a NEW image, it runs these same learned filters and
    outputs a probability score for each of the 1,000 classes.

  * We pick the class with the highest score as our prediction.

  * MobileNetV2 is designed to be small and fast (~14 MB) so it can
    even run on phones -- perfect for beginner projects!
""")
    print("=" * 60 + "\n")

    # 1. Prepare sample images (always succeeds — falls back to synthetic if offline)
    image_paths = download_samples()
    if not image_paths:
        print("[ERROR] Could not prepare any images.")
        sys.exit(1)
    print(f"\n   Ready: {len(image_paths)} image(s) loaded.\n")

    # 2. Load pretrained model
    classifier = load_model()

    # 3. Classify
    print("Classifying images ...\n")
    results = classify_images(classifier, image_paths)

    # 4. Print results
    print_results(results)

    # 5. Save chart
    chart = save_summary_chart(results)
    if chart:
        print(f"Results chart saved -> {chart.resolve()}")

    print("\nDone! Run  python app.py  to launch the interactive web UI.\n")


if __name__ == "__main__":
    main()

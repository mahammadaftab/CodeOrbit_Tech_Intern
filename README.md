# CodeOrbit Tech Internship Projects

A collection of beginner-to-intermediate Python projects built during the **CodeOrbit Tech internship**. Each project lives in its own folder with a dedicated README, source code, tests, and a web interface.

---

## Projects

### 1. 🤖 Rule-Based Chatbot — *OrbitBot*
> `rule_based_chatbot/`

A deterministic conversational chatbot powered entirely by regex rules — no ML required.

| Feature | Detail |
|---------|--------|
| Engine | Pure Python regex + response pools |
| Interface | CLI terminal **and** Flask web app |
| Design | Dark-mode glassmorphism UI, real-time rule transparency |
| Tests | `test_chatbot.py` — automated unit test suite |

**Run:**
```bash
# Web app (recommended)
python rule_based_chatbot/app.py
# → http://127.0.0.1:5000

# CLI
python rule_based_chatbot/chatbot.py
```

---

### 2. 🎮 Tic-Tac-Toe AI — *Minimax*
> `tic_tac_toe_ai/`

An unbeatable Tic-Tac-Toe AI using the **Minimax algorithm** with Alpha-Beta pruning.

| Feature | Detail |
|---------|--------|
| Algorithm | Minimax + Alpha-Beta pruning |
| Modes | Human vs AI, AI vs AI, Human vs Human |
| Interface | CLI **and** animated Flask web app |
| Tests | `test_game.py` — game logic unit tests |

**Run:**
```bash
# Web app
python tic_tac_toe_ai/app.py
# → http://127.0.0.1:5000

# CLI
python tic_tac_toe_ai/game.py
```

---

### 3. 🔍 Image Classification — *MobileNetV2*
> `image_classifier/`

Classifies images using a **pretrained MobileNetV2** model (14 MB, ImageNet-1000) loaded via HuggingFace Transformers + PyTorch. No training required — just load and predict.

| Feature | Detail |
|---------|--------|
| Model | `google/mobilenet_v2_1.0_224` (HuggingFace Hub) |
| Framework | HuggingFace `transformers` + `torch` (CPU) |
| Classes | 1,000 ImageNet categories |
| Interface | CLI with ASCII bars **and** drag-and-drop Flask web app |
| Fallback | PIL-generated synthetic images if network is unavailable |

**Sample results (real photos):**

| Image | Prediction | Confidence |
|-------|-----------|------------|
| Yellow Labrador photo | **Labrador Retriever** | 48.0% |
| Tabby cat photo | **Tiger Cat** | 70.4% |
| Mango photo | **Lemon** | 87.1% |

**Run:**
```bash
# CLI — classify 5 sample images + save chart
python image_classifier/classify.py

# Web app — upload any image for live classification
python image_classifier/app.py
# → http://127.0.0.1:5000
```

> **First run** downloads the MobileNetV2 model (~14 MB, cached after that).  
> You can also drop your own `.jpg` / `.png` files into `image_classifier/sample_images/`.

---

## Repository Structure

```
CodeOrbit_Tech_Intern/
│
├── rule_based_chatbot/          # Project 1 — OrbitBot
│   ├── chatbot.py               #   Core rule engine + CLI
│   ├── app.py                   #   Flask web server
│   ├── test_chatbot.py          #   Unit tests
│   ├── static/                  #   CSS + JS
│   ├── templates/               #   HTML
│   └── README.md
│
├── tic_tac_toe_ai/              # Project 2 — Minimax AI
│   ├── game.py                  #   Game logic + Minimax + CLI
│   ├── app.py                   #   Flask web server
│   ├── test_game.py             #   Unit tests
│   ├── static/                  #   CSS + JS
│   ├── templates/               #   HTML
│   └── README.md
│
└── image_classifier/            # Project 3 — MobileNetV2
    ├── classify.py              #   CLI classification script
    ├── app.py                   #   Flask web server
    ├── requirements.txt         #   Dependencies
    ├── sample_images/           #   Auto-downloaded sample images
    ├── results/                 #   Saved classification chart
    ├── static/                  #   CSS + JS
    ├── templates/               #   HTML
    └── README.md
```

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Language | Python 3.13 |
| Web Framework | Flask |
| ML / AI | PyTorch · HuggingFace Transformers |
| Image Processing | Pillow (PIL) |
| Data Viz | Matplotlib |
| Frontend | Vanilla HTML · CSS (glassmorphism dark mode) · JavaScript |
| Testing | pytest |

---

## Getting Started

All dependencies are available in the standard Python environment used for this internship. No virtual environment setup needed.

```bash
# Clone / open the repo, then run any project directly:
python rule_based_chatbot/app.py
python tic_tac_toe_ai/app.py
python image_classifier/app.py
```

Each project runs independently on port **5000** — start only one at a time, or change the port in the respective `app.py`.

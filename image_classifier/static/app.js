/**
 * Image Classifier – Client-Side JavaScript
 * Handles: file drag-and-drop, preview, fetch to /classify, results rendering
 */

// ── DOM References ─────────────────────────────────────────────────────────
const dropZone       = document.getElementById("drop-zone");
const fileInput      = document.getElementById("file-input");
const dropContent    = document.getElementById("drop-content");
const previewImg     = document.getElementById("preview-img");
const btnClassify    = document.getElementById("btn-classify");
const btnReset       = document.getElementById("btn-reset");
const progressArea   = document.getElementById("progress-area");
const progressLabel  = document.getElementById("progress-label");
const errorBox       = document.getElementById("error-box");
const errorMsg       = document.getElementById("error-msg");
const resultsSection = document.getElementById("results-section");

const resultImg      = document.getElementById("result-img");
const predBadge      = document.getElementById("pred-badge");
const predTopLabel   = document.getElementById("pred-top-label");
const predTopScore   = document.getElementById("pred-top-score");
const predList       = document.getElementById("predictions-list");
const metaFile       = document.getElementById("meta-file");

const btnInfo        = document.getElementById("btn-info");
const modalOverlay   = document.getElementById("modal-overlay");
const modalClose     = document.getElementById("modal-close");

// ── Colours for bar chart (rank 1–5) ──────────────────────────────────────
const BAR_COLORS = ["#58a6ff", "#3fb950", "#d29922", "#f85149", "#bc8cff"];

// Top-score icons for fun display
const CATEGORY_ICONS = {
  "cat": "🐱", "dog": "🐶", "bird": "🐦", "fish": "🐟",
  "car": "🚗", "truck": "🚚", "bus": "🚌", "train": "🚂",
  "flower": "🌸", "sunflower": "🌻", "rose": "🌹", "mushroom": "🍄",
  "banana": "🍌", "apple": "🍎", "orange": "🍊", "pizza": "🍕",
  "boat": "⛵", "airplane": "✈️", "helicopter": "🚁",
  "book": "📚", "laptop": "💻", "phone": "📱",
  "lion": "🦁", "tiger": "🐯", "bear": "🐻", "elephant": "🐘",
};

function getIcon(label) {
  const lower = label.toLowerCase();
  for (const [keyword, icon] of Object.entries(CATEGORY_ICONS)) {
    if (lower.includes(keyword)) return icon;
  }
  return "🏷️";
}

// ── State ──────────────────────────────────────────────────────────────────
let selectedFile = null;

// ── Helpers ───────────────────────────────────────────────────────────────
function showError(message) {
  errorBox.classList.remove("hidden");
  errorMsg.textContent = message;
  progressArea.classList.add("hidden");
}

function hideError() {
  errorBox.classList.add("hidden");
  errorMsg.textContent = "";
}

function setProgress(visible, label = "") {
  progressLabel.textContent = label;
  progressArea.classList.toggle("hidden", !visible);
}

function resetUI() {
  selectedFile = null;
  previewImg.src = "";
  previewImg.classList.add("hidden");
  dropContent.classList.remove("hidden");
  btnClassify.disabled = true;
  resultsSection.classList.add("hidden");
  hideError();
  setProgress(false);
  fileInput.value = "";
}

// ── File Selection ─────────────────────────────────────────────────────────
function loadPreview(file) {
  if (!file || !file.type.startsWith("image/")) {
    showError("Please select a valid image file (JPG, PNG, WEBP …)");
    return;
  }
  selectedFile = file;
  hideError();

  const reader = new FileReader();
  reader.onload = (e) => {
    previewImg.src = e.target.result;
    previewImg.classList.remove("hidden");
    dropContent.classList.add("hidden");
    btnClassify.disabled = false;
  };
  reader.readAsDataURL(file);
}

// Drop Zone click
dropZone.addEventListener("click", () => fileInput.click());
dropZone.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") fileInput.click();
});

// File input change
fileInput.addEventListener("change", (e) => {
  if (e.target.files[0]) loadPreview(e.target.files[0]);
});

// Drag & Drop
dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("drag-over");
});
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("drag-over");
  const file = e.dataTransfer.files[0];
  if (file) loadPreview(file);
});

// ── Reset ──────────────────────────────────────────────────────────────────
btnReset.addEventListener("click", resetUI);

// ── Classify ──────────────────────────────────────────────────────────────
btnClassify.addEventListener("click", async () => {
  if (!selectedFile) return;

  hideError();
  setProgress(true, "Classifying image …");
  btnClassify.disabled = true;
  resultsSection.classList.add("hidden");

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const resp = await fetch("/classify", {
      method: "POST",
      body: formData,
    });

    const data = await resp.json();
    setProgress(false);
    btnClassify.disabled = false;

    if (!resp.ok || data.error) {
      showError(data.error || "An unexpected error occurred.");
      return;
    }

    renderResults(data);
  } catch (err) {
    setProgress(false);
    btnClassify.disabled = false;
    showError("Network error. Make sure the Flask server is running.");
  }
});

// ── Render Results ─────────────────────────────────────────────────────────
function renderResults(data) {
  const { image_data, filename, predictions, top_label, top_score } = data;

  // Image thumbnail
  resultImg.src = image_data;
  resultImg.alt = `Classified image: ${filename}`;

  // Top prediction
  predBadge.textContent = getIcon(top_label);
  predTopLabel.textContent = top_label;
  predTopScore.textContent = `${top_score.toFixed(1)}%`;

  // Predictions list
  predList.innerHTML = "";
  predictions.forEach((pred, i) => {
    const li = document.createElement("li");
    li.className = "pred-item";
    li.setAttribute("role", "listitem");

    // Slightly delay bar animation for cascade effect
    const delay = i * 80;

    li.innerHTML = `
      <span class="pred-rank">#${pred.rank}</span>
      <div class="pred-bar-wrap" title="${pred.label}: ${pred.score}%">
        <div class="pred-bar"
             style="width: 0%; background: ${BAR_COLORS[i] || "#58a6ff"};"
             data-width="${pred.score}"></div>
        <span class="pred-bar-label">${pred.label}</span>
      </div>
      <span class="pred-score-num">${pred.score.toFixed(1)}%</span>
    `;
    predList.appendChild(li);

    // Animate bar after DOM insertion
    setTimeout(() => {
      const bar = li.querySelector(".pred-bar");
      if (bar) bar.style.width = `${Math.min(pred.score, 100)}%`;
    }, delay);
  });

  // Meta
  metaFile.textContent = filename;

  // Show section
  resultsSection.classList.remove("hidden");
  // Smooth scroll on mobile
  if (window.innerWidth <= 800) {
    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

// ── Modal ──────────────────────────────────────────────────────────────────
btnInfo.addEventListener("click", () => modalOverlay.classList.remove("hidden"));
modalClose.addEventListener("click", () => modalOverlay.classList.add("hidden"));
modalOverlay.addEventListener("click", (e) => {
  if (e.target === modalOverlay) modalOverlay.classList.add("hidden");
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") modalOverlay.classList.add("hidden");
});

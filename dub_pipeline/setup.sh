#!/usr/bin/env bash
# setup.sh — create isolated Python environment for the dubbing pipeline
# Run once from the dub_pipeline/ directory:
#   bash setup.sh
# Then activate whenever you work:
#   source .venv/bin/activate

set -euo pipefail

VENV_DIR="$(dirname "$0")/.venv"
PYTHON="${PYTHON:-python3}"

echo "=== Dubbing Pipeline Environment Setup ==="
echo "Python: $($PYTHON --version)"
echo "Venv  : $VENV_DIR"
echo

# ── 1. Create venv ────────────────────────────────────────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    echo "[1/6] Creating virtual environment..."
    $PYTHON -m venv "$VENV_DIR"
else
    echo "[1/6] Venv already exists, skipping creation."
fi

# Activate
source "$VENV_DIR/bin/activate"
pip install --upgrade pip setuptools wheel -q

# ── 2. PyTorch ────────────────────────────────────────────────────────────────
echo "[2/6] Installing PyTorch (CPU fallback — replace with CUDA version if you have a GPU)..."
echo "      For CUDA: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
pip install torch torchvision torchaudio -q

# ── 3. Core requirements ──────────────────────────────────────────────────────
echo "[3/6] Installing core requirements..."
pip install -r "$(dirname "$0")/requirements.txt" -q

# ── 4. audio-separator (choose cpu or gpu) ────────────────────────────────────
echo "[4/6] Installing audio-separator [cpu]..."
echo "      If you have a CUDA GPU, rerun: pip install 'audio-separator[gpu]'"
pip install "audio-separator[cpu]" -q

# ── 5. WhisperX (must be installed from source, not PyPI) ────────────────────
echo "[5/6] Installing WhisperX..."
pip install git+https://github.com/m-bain/whisperx.git -q

# ── 6. Register Jupyter kernel ────────────────────────────────────────────────
echo "[6/6] Registering Jupyter kernel 'dub_pipeline'..."
python -m ipykernel install --user --name dub_pipeline --display-name "Python (dub_pipeline)"

echo
echo "=== Setup complete ==="
echo
echo "To activate this environment:"
echo "  source $VENV_DIR/bin/activate"
echo
echo "To start Jupyter:"
echo "  jupyter notebook  (or: jupyter lab)"
echo
echo "Optional heavy installs (do these manually if needed):"
echo "  pip install insightface onnxruntime       # ArcFace for lip sync metrics"
echo "  pip install deepfilternet                 # DeepFilterNet3 vocal denoiser"
echo "  pip install nemo_toolkit[asr]             # NVIDIA NeMo diarization (very large)"
echo
echo "Lip sync models (clone separately — see notebook 08):"
echo "  git clone https://github.com/Rudrabha/Wav2Lip.git ~/Wav2Lip"
echo "  git clone https://github.com/bytedance/LatentSync.git ~/LatentSync"
echo "  git clone https://github.com/TMElyralab/MuseTalk.git ~/MuseTalk"

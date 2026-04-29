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
if python -c "import subprocess,sys; r=subprocess.run(['nvidia-smi'],capture_output=True); sys.exit(0 if r.returncode==0 else 1)" 2>/dev/null; then
    echo "[2/6] CUDA GPU detected — installing PyTorch with CUDA 12.1..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 -q
    AUDIO_SEP_EXTRA="gpu"
else
    echo "[2/6] No CUDA GPU — installing PyTorch (MPS/CPU)..."
    pip install torch torchvision torchaudio -q
    AUDIO_SEP_EXTRA="cpu"
fi

# ── 3. Core requirements ──────────────────────────────────────────────────────
echo "[3/6] Installing core requirements..."
pip install -r "$(dirname "$0")/requirements.txt" -q

# ── 4. audio-separator ───────────────────────────────────────────────────────
echo "[4/6] Installing audio-separator [${AUDIO_SEP_EXTRA}]..."
pip install "audio-separator[${AUDIO_SEP_EXTRA}]" -q

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

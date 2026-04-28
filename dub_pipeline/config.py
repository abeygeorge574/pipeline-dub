"""
dub_pipeline/config.py  —  shared configuration for the entire dubbing pipeline.

Change SOURCE_LANGUAGE to switch Tamil→Hindi:
    SOURCE_LANGUAGE = "hi"   # tomorrow's run

Sample-rate philosophy
----------------------
We preserve the video's NATIVE sample rate throughout the pipeline to avoid
destructive resampling of the music bed.  The one exception is:
  - ASR models  : always need 16 000 Hz  (resampled in-memory, never saved)
  - ElevenLabs  : PCM output is 44 100 Hz max (Pro plan)
  - Assembly    : TTS audio is *upsampled* to SOURCE_SAMPLE_RATE at mix time.
SOURCE_SAMPLE_RATE is read from the video in notebook 01 and cached in
intermediate/audio_extracted/meta.json so all downstream notebooks can load it.
"""

import os

def get_torch_device():
    """Returns (device_str, torch_dtype) for best available hardware.
    Priority: cuda > mps (Apple Silicon M-series) > cpu.
    Uses bfloat16 on CUDA, float16 on MPS (bfloat16 unsupported), float32 on CPU.
    """
    import torch
    if torch.cuda.is_available():
        return 'cuda', torch.bfloat16
    if torch.backends.mps.is_available():
        return 'mps', torch.float16
    return 'cpu', torch.float32

# ── Language ──────────────────────────────────────────────────────────────────
SOURCE_LANGUAGE = "ta"          # ISO-639-1: "ta"=Tamil, "hi"=Hindi
TARGET_LANGUAGE = "en-US"

LANGUAGE_DISPLAY = {
    "ta":    "Tamil",
    "hi":    "Hindi",
    "en":    "English",
    "en-US": "American English",
}

# Whisper / WhisperX language codes (same as ISO-639-1 for these languages)
WHISPER_LANGUAGE_CODE = {
    "ta": "ta",
    "hi": "hi",
}

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

SOURCE_VIDEO_PATH   = os.path.join(PROJECT_ROOT, "input", "dub_original.mp4")
INTERMEDIATE_DIR    = os.path.join(PROJECT_ROOT, "intermediate")
RESULTS_DIR         = os.path.join(PROJECT_ROOT, "results")

AUDIO_EXTRACTED_DIR = os.path.join(INTERMEDIATE_DIR, "audio_extracted")
STEMS_DIR           = os.path.join(INTERMEDIATE_DIR, "stems")
DIARIZATION_DIR     = os.path.join(INTERMEDIATE_DIR, "diarization")
TRANSCRIPTION_DIR   = os.path.join(INTERMEDIATE_DIR, "transcription")
TRANSLATION_DIR     = os.path.join(INTERMEDIATE_DIR, "translation")
TTS_OUTPUT_DIR      = os.path.join(INTERMEDIATE_DIR, "tts_output")
ASSEMBLED_DIR       = os.path.join(INTERMEDIATE_DIR, "assembled")
LIP_SYNCED_DIR      = os.path.join(INTERMEDIATE_DIR, "lip_synced")

for _d in [
    AUDIO_EXTRACTED_DIR, STEMS_DIR, DIARIZATION_DIR, TRANSCRIPTION_DIR,
    TRANSLATION_DIR, TTS_OUTPUT_DIR, ASSEMBLED_DIR, LIP_SYNCED_DIR, RESULTS_DIR,
]:
    os.makedirs(_d, exist_ok=True)

# ── Sample rates ──────────────────────────────────────────────────────────────
# SOURCE_SAMPLE_RATE  → detected at runtime in 01_audio_extraction.ipynb
#                       stored in intermediate/audio_extracted/meta.json
# TTS_OUTPUT_SR       → ElevenLabs PCM max on Pro plan (never change this)
# ASR_SAMPLE_RATE     → what all ASR models require (in-memory resample only)
TTS_OUTPUT_SR   = 44_100
ASR_SAMPLE_RATE = 16_000

def load_source_sr():
    """Read the detected source sample rate from meta.json. Returns 48000 as default."""
    import json
    meta_path = os.path.join(AUDIO_EXTRACTED_DIR, 'meta.json')
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            return json.load(f).get('source_sample_rate', 48_000)
    return 48_000

# ── ElevenLabs ────────────────────────────────────────────────────────────────
ELEVENLABS_MODEL_ID = "eleven_v3"
ELEVENLABS_VOICE_ID = ""   # Set via env var ELEVENLABS_VOICE_ID or prompted in 06

ELEVENLABS_TTS_SETTINGS = {
    "stability":        0.5,
    "similarity_boost": 0.75,
    "style":            0.0,
}

# ── Gemini ────────────────────────────────────────────────────────────────────
GEMINI_PRO_MODEL   = "gemini-2.5-pro"
GEMINI_FLASH_MODEL = "gemini-2.5-flash"

# ── Translation / duration fitting ────────────────────────────────────────────
# English speech rate varies by emotion; base rate adjusted per segment:
#   normal  : 140 WPM
#   excited/shouted : 160 WPM  (faster delivery)
#   calm/whispered  : 110 WPM  (slower delivery)
ENGLISH_WPM_BY_EMOTION = {
    "high_energy_fast":  160,
    "high_energy":       150,
    "fast_pace":         155,
    "low_energy_slow":   110,
    "low_energy":        120,
    "slow_pace":         115,
    "neutral":           140,
}
ENGLISH_WPM_DEFAULT  = 140
DURATION_TOLERANCE   = 0.15   # ±15 % is OK; outside triggers retry
MAX_DURATION_RETRIES = 3      # actual duration-miss retries (not just exceptions)

# ElevenLabs v3 allowed audio tags (complete list as of 2025)
ALLOWED_AUDIO_TAGS = [
    "angry", "sad", "excited", "calm", "scared",
    "whispers", "shouts", "laughs", "sighs", "gasps",
    "fast-paced", "drawn out", "sarcastic", "hesitant",
]

# ── Show context (fill before running notebook 05) ────────────────────────────
SHOW_SUMMARY       = ""
SHOW_SETTING       = ""
SHOW_GENRES        = ""
LINGUISTIC_PROFILE = ""
STYLE_TEMPLATE     = ""   # empty → BASE STYLE RULES

# ── Audio assembly ────────────────────────────────────────────────────────────
TARGET_LUFS          = -16.0   # EBU R128 / OTT delivery standard
INSTR_GAIN_NORMAL    = 0.85    # instrumental level when no speech
INSTR_GAIN_DUCKED    = 0.30    # duck music ~9 dB under active dialogue
AMBIENCE_GAIN        = 0.03    # attenuated source vocals used as room tone

# Max time-stretch ratio for TTS fitting (beyond this, duration mismatch is logged
# but not forced — avoids unnatural chipmunk/slowed effect)
MAX_STRETCH_RATIO    = 0.12    # ±12 % time-stretch is inaudible

# ── Voice cloning / IVC ───────────────────────────────────────────────────────
# Voice identity preservation is non-negotiable. Each character must sound like
# the same actor in English — not a generic library voice.
# IVC = Instant Voice Clone (ElevenLabs). Created from clean source speech per speaker.
VOICE_CLONING_TARGET_SECS  = 60.0  # aim for 60s of reference audio per speaker
VOICE_CLONING_MIN_SECS     =  5.0  # below this → fall back to library voice + log warning
VOICE_CLONING_MIN_SEG_SECS =  1.0  # ignore speaker segments shorter than this

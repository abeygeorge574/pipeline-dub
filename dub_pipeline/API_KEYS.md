# API Keys & Tokens

All secrets are read from **environment variables first**, then prompted at runtime via `getpass` if not set. Commercial keys you haven't signed up for yet: just press Enter when prompted — that notebook section will be skipped.

**Never paste keys directly into notebook cells.**

---

## Recommended: create a `.envrc` file (never committed to git)

```bash
# dub_pipeline/.envrc  — loaded automatically with `direnv`
# or source manually: source .envrc

# Always required
export HF_TOKEN="hf_..."
export GEMINI_API_KEY="AIza..."
export ELEVENLABS_API_KEY="sk_..."
export ELEVENLABS_VOICE_ID="21m00Tcm..."   # fallback library voice ID only

# Commercial — add when ready to test
export AUDIOSHAKE_API_KEY=""
export ASSEMBLYAI_API_KEY=""
export DEEPGRAM_API_KEY=""
export SPEECHMATICS_API_KEY=""
export OPENAI_API_KEY=""
export ANTHROPIC_API_KEY=""
export SYNCSO_API_KEY=""
export FAL_KEY=""
```

Then either:
- Install `direnv` → `direnv allow` (auto-loads on `cd`)
- Or `source .envrc` before opening Jupyter

---

## Per-notebook key inventory

### Always required

| Notebook | Variable | Where used | How to get it |
|---|---|---|---|
| `03_diarization.ipynb` | `HF_TOKEN` | Pyannote 3.1 download + WhisperX | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) — accept pyannote licence first |
| `04_asr.ipynb` | `GEMINI_API_KEY` | Gemini ASR (pseudo-GT reference) | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| `05_translation_emotion.ipynb` | `GEMINI_API_KEY` | Gemini 2.5 Pro + Flash translation | Same key |
| `06_tts.ipynb` | `ELEVENLABS_API_KEY` | IVC creation + TTS synthesis | [elevenlabs.io/app/settings/api-keys](https://elevenlabs.io/app/settings/api-keys) |
| `06_tts.ipynb` | `ELEVENLABS_VOICE_ID` | Fallback library voice (used only if IVC fails) | [elevenlabs.io/app/voice-library](https://elevenlabs.io/app/voice-library) |

### Commercial (skip for now, test later)

| Notebook | Variable | Service | Free tier | How to get it |
|---|---|---|---|---|
| `02_stem_separation.ipynb` | `AUDIOSHAKE_API_KEY` | AudioShake stem sep | 10 credits, no CC | [audioshake.ai](https://audioshake.ai) |
| `02_stem_separation.ipynb` | `ELEVENLABS_API_KEY` | EL Audio Isolation | Uses existing sub | Already have it |
| `03_diarization.ipynb` | `ASSEMBLYAI_API_KEY` | AssemblyAI diarization | Free tier, no CC | [assemblyai.com](https://www.assemblyai.com) |
| `03_diarization.ipynb` | `DEEPGRAM_API_KEY` | Deepgram diarization | $200 credit, no CC | [deepgram.com](https://deepgram.com) |
| `03_diarization.ipynb` | `SPEECHMATICS_API_KEY` | Speechmatics diarization | 480 min/month | [speechmatics.com](https://speechmatics.com) |
| `04_asr.ipynb` | `ELEVENLABS_API_KEY` | EL Scribe v2 ASR | Uses existing sub | Already have it |
| `04_asr.ipynb` | `DEEPGRAM_API_KEY` | Deepgram Nova-3 ASR | Same as above | Same as above |
| `05_translation_emotion.ipynb` | `OPENAI_API_KEY` | GPT-4o translation | Pay-as-you-go | [platform.openai.com](https://platform.openai.com) |
| `05_translation_emotion.ipynb` | `ANTHROPIC_API_KEY` | Claude translation | Pay-as-you-go | [console.anthropic.com](https://console.anthropic.com) |
| `08_lip_sync.ipynb` | `SYNCSO_API_KEY` | Sync.so Lipsync-2 | Free tier | [sync.so](https://sync.so) |
| `08_lip_sync.ipynb` | `FAL_KEY` | VEED via fal.ai | Free credits | [fal.ai](https://fal.ai) |

---

## HuggingFace: extra model-licence acceptances required

Before running notebooks 03 and 04, visit these pages and click **Accept**:

1. [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
2. [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)

IndicWhisper and Whisper Large-V3 download without gating.

---

## Quick test: verify your keys work before running the full pipeline

```python
# Run in any notebook cell:
import os, google.generativeai as genai

# Gemini
genai.configure(api_key=os.environ['GEMINI_API_KEY'])
m = genai.GenerativeModel('gemini-2.5-flash')
print(m.generate_content('Say "Gemini ready" in one word.').text)

# ElevenLabs
from elevenlabs.client import ElevenLabs
c = ElevenLabs(api_key=os.environ['ELEVENLABS_API_KEY'])
print(f"ElevenLabs ready — {len(c.voices.get_all().voices)} voices available")
```

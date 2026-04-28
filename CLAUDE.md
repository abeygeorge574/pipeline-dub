# pipeline_dub — CLAUDE.md

Cross-lingual video dubbing pipeline evaluation harness built for Postudio.
Takes Tamil/Hindi source video → dubbed English video.
This is an **evaluation harness** (find the best component per stage), not production code.

## Quick orientation

```
pipeline_dub/
  dub_original.mp4          source video (Tamil today, Hindi tomorrow)
  readme                    full project brief
  translation_prompt        Postudio dubbing translation prompt template
  dub_pipeline/
    config.py               single source of truth for all paths/settings
    setup.sh                creates .venv and registers Jupyter kernel
    requirements.txt        all Python deps
    API_KEYS.md             where every API key goes (read before running)
    notebooks/
      01_audio_extraction   ffmpeg → native-SR WAV
      02_stem_separation    BS-RoFormer / MelBand / HTDemucs / MDX-Net
      03_diarization        Pyannote / NeMo / WhisperX + external file loader
      04_asr                IndicWhisper / Whisper-LargeV3 / WhisperX / Sarvam / Gemini
      05_translation_emotion Gemini Pro/Flash, duration-aware, ElevenLabs audio tags
      06_tts                ElevenLabs v3 wrapper (no alternatives evaluated)
      07_audio_assembly     timeline stitch, sidechain duck, LUFS norm, WSOLA stretch
      08_lip_sync           Wav2Lip / LatentSync / MuseTalk / Hallo2
    intermediate/           outputs from each notebook (auto-created)
    results/                final_output.mp4
```

## Run order (dependency chain)

01 → 02 → 03 → 04 → 05 → 06 → 07 → 08

Each notebook caches its output. Re-running a notebook only re-processes if you delete the cache.

## Switch language (Tamil → Hindi)

In `config.py` line 10:
```python
SOURCE_LANGUAGE = "hi"   # was "ta"
```
That is the only change needed. All model language codes, display names, and prompt text derive from this.

## Key design decisions (WHY, not just what)

**Native sample rate throughout:**
Source video is often 48 kHz. We extract at native SR (notebook 01), run stems at native SR,
and only resample TTS (44.1 kHz ElevenLabs PCM) *up* to source SR at mix time — never down.
This avoids a double-resample of the music bed.

**ElevenLabs v3 as TTS (no evaluation):**
Already decided. ElevenLabs Dubbing Studio was tested and produces poor quality on Indic
source material — internal Postudio testing confirmed this. We use the raw v3 API instead,
controlling all other stages ourselves.

**Diarization: external file is primary path:**
Postudio has existing diarization from their platform. Notebook 03 loads it via
`EXTERNAL_DIARIZATION_PATH`. OSS models are alternatives/benchmarks, not primary.

**Translation: Gemini only (Pro + Flash for cost comparison):**
User has Gemini API key. No other LLMs being evaluated currently.

**Duration-aware translation with real retries:**
Notebook 05 extracts librosa audio features (pitch, energy, ZCR) per segment to estimate
emotion, adjusts WPM target per emotion, then does K=3 self-consistency candidates and
per-segment retry (up to MAX_DURATION_RETRIES=3) if outside ±15% duration tolerance.

**STS (speech-to-speech voice conversion): NOT in this pipeline.**
Handled separately by Postudio. Do not add it.

## API keys needed

### Always required
| Key | Env var | First used |
|---|---|---|
| HuggingFace token | `HF_TOKEN` | Notebook 03 (Pyannote) |
| Gemini API key | `GEMINI_API_KEY` | Notebook 04 (ASR reference) + 05 (translation) |
| ElevenLabs API key | `ELEVENLABS_API_KEY` | Notebook 02 (Audio Isolation) + 04 (Scribe) + 06 (IVC + TTS) |
| ElevenLabs Voice ID | `ELEVENLABS_VOICE_ID` | Notebook 06 (fallback library voice only — IVC is primary) |

### Commercial (test later — all have free tiers, no CC required)
| Key | Env var | Notebook | Free tier |
|---|---|---|---|
| AudioShake | `AUDIOSHAKE_API_KEY` | 02 stem sep | 10 credits |
| AssemblyAI | `ASSEMBLYAI_API_KEY` | 03 diarization | Free tier |
| Deepgram | `DEEPGRAM_API_KEY` | 03 diarization + 04 ASR | $200 credit |
| Speechmatics | `SPEECHMATICS_API_KEY` | 03 diarization | 480 min/month |
| OpenAI | `OPENAI_API_KEY` | 05 translation | Pay-as-you-go |
| Anthropic | `ANTHROPIC_API_KEY` | 05 translation | Pay-as-you-go |
| Sync.so | `SYNCSO_API_KEY` | 08 lip sync | Free tier |
| fal.ai | `FAL_KEY` | 08 lip sync (VEED) | Free credits |

Set always-required keys in `dub_pipeline/.envrc` and `source .envrc` before Jupyter. Commercial keys are prompted at runtime via `getpass` — press Enter to skip any you don't have yet.

## Known weak points (honest assessment)

**Voice cloning (IVC) quality depends on stem separation quality.**
Notebook 06 creates per-character IVCs from `stems/vocals.wav`. If stem separation leaves
music bleed in the vocals, the IVC will inherit it and produce a slightly muddy English voice.
Run BSRoFormer + DeepFilterNet3 for the cleanest input to IVC creation.

**Diarization is the highest-risk stage.** OSS diarization (Pyannote, NeMo) consistently
underperforms on Indic content: short rapid-fire turns, music bleed even after stem
separation, and non-Western acoustic conditions. The external diarization from Postudio's
platform is expected to be better. Commercial APIs (AssemblyAI, Deepgram) are in the
notebooks and ready to test.

**Accent leak is expected in IVC output.** Cloning a Tamil actor's voice and generating
English will carry some Tamil accent. This is documented as a known issue. Future fix:
STS pass with an American English voice as target (handled separately by Postudio).

**Lip sync is unproven at production quality.** Wav2Lip blurs the lower face. LatentSync
and MuseTalk are better but require 6–10 GB VRAM and still struggle on non-portrait
shots (action, multiple people, profile views). Sync.so and VEED via fal.ai are the
commercial alternatives most likely to reach production quality. For a proof-of-concept,
audio-only output (`assembled/final_dubbed.mp4`) is sufficient.

**TTS silence trimming affects duration fit.** ElevenLabs adds 100–300 ms trailing
silence. Notebook 06 trims this before saving. If duration ratios look odd, check trim.

## Gaps to address in future sessions

- Shot detection before lip sync (PySceneDetect → per-shot processing beats whole-video)
- COMET-Kiwi referenceless quality gate before TTS (catch bad translations before synthesis)
- Subtitle/caption generation from translation output
- Pronunciation dictionary for Indic proper nouns (names, places mispronounced by EL)
- Accent conversion post-processing (Krisp, Tomato.ai, Respeecher) for severe accent leak
- Per-episode batch mode (currently single-video only)
- Reference audio for IVC: currently uses diarization + vocal stems. Better approach is
  a separate QC pass where an editor marks the cleanest 60s per character for cloning.

## Useful commands

```bash
# First-time setup
cd dub_pipeline && bash setup.sh

# Start Jupyter
source .venv/bin/activate
source .envrc          # loads API keys
jupyter notebook

# Check what's been generated so far
find intermediate -name "*.json" -o -name "*.wav" | sort
```

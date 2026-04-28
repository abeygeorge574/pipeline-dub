# Data Requirements — Benchmarking the Dubbing Pipeline

This document lists what ground-truth data is needed to move from proxy metrics
to proper, publishable evaluation numbers. Bring this to your boss meeting.

---

## Why we need this

The current pipeline uses proxy metrics only:
- Stem separation: spectral flatness + downstream WER (no SDR)
- Diarization: segment count + coverage (no DER against ground truth)
- ASR: pseudo-WER vs Gemini (no human reference transcript)
- Translation: duration ratio (no BLEU/chrF against human translation)

To select the best model at each stage with confidence, we need real ground truth.

---

## 1. Stem Separation Ground Truth

**What:** Pre-mix isolated stems — the vocal track and instrumental track
*before* they were mixed together in post-production.

**Who has this:** The original production house / music label. These are the
session files (.wav or .aif) from the mixing engineer's DAW.

**Format needed:**
- `clip_NNN_vocals.wav` — actor voices only, no music, no SFX
- `clip_NNN_instrumental.wav` — music + SFX, no voice
- Both at native sample rate (48 kHz preferred)

**Volume:**

| Dimension | Target | Minimum |
|---|---|---|
| Total clips | 15 | 8 |
| Duration per clip | 3–5 min | 2 min |
| Total audio | ~60 min | ~20 min |
| Languages | Tamil + Hindi | Tamil only |

**Variance to cover:**

| Category | Why it matters |
|---|---|
| Heavy Carnatic / film score (lots of music) | Hardest case for separation — vocals buried |
| Light background score | Easier; sets a ceiling baseline |
| Dialogue-heavy (low music) | Verifies no over-separation artefacts |
| Action / SFX-heavy | MDX-Net and HTDemucs behave differently here |
| Solo speaker | Clean reference for IVC quality downstream |
| 3+ speakers, overlapping | Stress test for diarization |
| Male + Female speakers | Frequency range coverage |
| Indoor studio recording | Clean acoustic condition |
| On-location / outdoor | Noisy acoustic condition |

**Metric unlocked:** SDR, SIR, SAR (via `mir_eval`)

---

## 2. Diarization Ground Truth

**What:** RTTM files — timestamped speaker labels manually verified by a human.

**Who has this:** Postudio platform should have this for content they've already
processed. Alternatively, a human annotator watches the video and labels turns.

**Format needed:**
- One `.rttm` file per clip (standard format, already supported by notebook 03)
- Minimum 2 speakers per clip; include at least 2 clips with 4+ speakers

**Volume:**

| Dimension | Target | Minimum |
|---|---|---|
| Total clips | 10 | 5 |
| Duration per clip | 3–5 min | 2 min |
| Total audio | ~40 min | ~12 min |
| Languages | Tamil + Hindi | Tamil only |

**Variance to cover:**

| Category | Why it matters |
|---|---|
| 2-speaker conversation | Most common in drama |
| 3-speaker scene | Tests confusion rate |
| 4+ speakers / crowd | Tests NeMo 4-speaker cap |
| Rapid speaker switches (<1 s turns) | Where Pyannote struggles on Indic content |
| Music under dialogue | Real-world condition; degrades all OSS models |
| Overlapping speech | Pyannote handles; NeMo and WhisperX often don't |

**Metric unlocked:** DER (Diarization Error Rate), JER (Jaccard Error Rate)

---

## 3. ASR Ground Truth

**What:** Human-verified transcripts of Tamil and Hindi speech, with
sentence-level timestamps.

**Who produces this:** A native-speaker transcriptionist who watches the video
and types exactly what is said (including disfluencies, code-switching, etc.).

**Format needed:**
- JSON array: `[{"start": 0.0, "end": 3.4, "text": "...", "speaker": "SPK_0"}, ...]`
- Text in native script (Tamil Unicode / Devanagari), not romanised
- Word-level timestamps are a bonus but not required

**Volume:**

| Dimension | Target | Minimum |
|---|---|---|
| Total segments | 500 | 150 |
| Total audio (unique clips) | ~60 min | ~20 min |
| Tamil clips | 60% | 100% |
| Hindi clips | 40% | 0% (add later) |

**Variance to cover:**

| Category | Why it matters |
|---|---|
| Clean studio speech | Ceiling baseline |
| Speech over music | Real pipeline condition |
| Code-switching (Tamil + English words) | Common in urban Tamil film dialogue |
| Whispered / shouted speech | Emotion extremes |
| Children's voices | Different F0 range |
| Elderly speakers | Different vocal quality |
| Regional accents (Madurai Tamil vs Chennai Tamil) | Dialect robustness |

**Metric unlocked:** WER, CER (per model, per acoustic condition)

---

## 4. Translation Ground Truth

**What:** Professional human dubbing translations of the ASR-transcribed segments,
in English, written to be spoken aloud (not subtitle style).

**Who produces this:** A professional dubbing translator (not a general translator —
dubbing translation has specific constraints around duration and lip-sync).

**Format needed:**
- Parallel to the ASR ground truth JSON, add `"reference_translation"` field
- Target: American English, spoken register, duration-aware

**Volume:**

| Dimension | Target | Minimum |
|---|---|---|
| Total segments translated | 300 | 100 |
| Translators | 2 (for inter-annotator agreement) | 1 |
| Languages | Tamil→English, Hindi→English | Tamil→English |

**Metric unlocked:** BLEU, chrF, COMET-Kiwi (referenceless quality estimation)

---

## Summary — what to ask for

> "I need 15 clips of Tamil film content, each 3–5 minutes long, with pre-mix
> session stems (isolated vocals WAV + instrumental WAV) and a native-speaker
> transcript. A subset of 5 clips with manually verified speaker-turn RTTM files
> would also be extremely useful. Hindi equivalents can follow."

That single ask unlocks SDR, DER, and WER — the three headline metrics that
determine model selection at every stage of the pipeline.

---

## When we have this data

Update `config.py` → `EVAL_CLIPS_DIR` and run the evaluation cells in each
notebook that currently print "N/A — no ground truth". The notebooks are already
structured to accept ground truth when available.

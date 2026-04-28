# LATER — Deferred Work Backlog

Running list of things to revisit. Add items here while running notebooks so nothing gets lost.
Format: `- [ ] Short description — *why deferred*`

---

## Code / Pipeline Fixes

- [ ] Shot detection before lip sync — PySceneDetect per-shot processing beats whole-video; avoids blurring on cuts
- [ ] COMET-Kiwi referenceless quality gate before TTS — catch bad translations before spending ElevenLabs credits
- [ ] Subtitle/caption generation from translation output (notebook 05 → SRT export)
- [ ] Pronunciation dictionary for Indic proper nouns — names/places mispronounced by ElevenLabs
- [ ] TTS silence trim tuning — ElevenLabs adds 100–300 ms trailing silence; check if trim threshold needs adjustment per voice
- [ ] IVC reference audio QC pass — currently uses all diarized segments; better to hand-pick cleanest 60s per character

## Model Evaluation

- [ ] AudioShake API (notebook 02) — commercial stem separation; 10 free credits, test on heaviest music scene
- [ ] AssemblyAI diarization (notebook 03) — free tier, most likely to beat Pyannote on Indic content
- [ ] Deepgram diarization + ASR (notebooks 03 + 04) — $200 credit, worth testing
- [ ] Speechmatics diarization (notebook 03) — 480 min/month free tier
- [ ] MOSS-Audio real-world performance — benchmarks are EN/ZH only; need to verify Indic quality before trusting it
- [ ] Sync.so lip sync (notebook 08) — free tier; most likely commercial option to reach production quality
- [ ] VEED via fal.ai (notebook 08) — free credits; alternative to Sync.so

## Infrastructure / Productionisation

- [ ] Per-episode batch mode — currently single-video only; needs a loop wrapper + per-video intermediate dirs
- [ ] Accent conversion post-processing (Krisp / Tomato.ai / Respeecher) — for severe Tamil accent leak in IVC output
- [ ] STS (speech-to-speech) pass — handled separately by Postudio, but note the hook point is after notebook 06

## Data / Ground Truth (see DATA_REQUIREMENTS.md for full spec)

- [ ] Stem separation: get pre-mix session stems (vocals.wav + instrumental.wav) for 15 clips → unlocks SDR/SIR/SAR
- [ ] Diarization: get RTTM files for 10 clips from Postudio platform → unlocks DER/JER
- [ ] ASR: native-speaker transcripts for 500 segments in Tamil + Hindi → unlocks real WER/CER
- [ ] Translation: professional dubbing translations for 300 segments → unlocks BLEU/chrF/COMET

## Notebook-specific Notes

*(add observations here while running — e.g. "02: HTDemucs OOM on 5 min clip, need to chunk")*

---

*Keep entries short. Move finished items to git commit messages, not back here.*

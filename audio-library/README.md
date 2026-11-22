# Audio library (recall for any edit)

Everything here is ready to drop under a voice. Voice = -14 LUFS; music sits ~-26 LUFS ducked under speech.

## music/
| file | what | length | notes |
|---|---|---|---|
| `interstellar_piano_user_clip.wav/.mp3` | Interstellar (Cornfield Chase style) piano, the clip the user supplied as their go-to bed | 26 s | stereo 48 kHz, -14 LUFS, peak -3.5 dBFS. User-supplied, third-party recording: personal-use, tell the user if a platform flags it. Loop with a 2 s crossfade for longer edits (`video-toolkit/brand/code/brand_av.py: loop_music`). |

## sfx/ (real recordings, Mixkit free licence, measured and trimmed)
`quick_swoosh`, `fast_swoosh2`, `short_sweep`, `wind_sweep`, `air_woosh`, `cin_swoosh`, `cin_whoosh_fast`, `fast_whoosh`, `fast_sweep` (swooshes, 0.5-2.3 s)
`trailer_riser`, `synth_riser`, `stutter_riser` (risers, 2.6-9 s)
`zoom_impact`, `bass_hit`, `heartbeat_impact`, `soft_punch` (impacts)
`light_pop`, `dry_pop`, `bubble_pop`, `sparkle_sweep` (UI pops and sparkles; `light_pop` at -27 dB is the caption tick)
Source list and ids: `sfx/mixkit.json`.

## how to use
`video-toolkit/brand/code/brand_av.py`: `mix(voice_wav, cues, dur, out_wav, music_db=-22, music_path='audio-library/music/interstellar_piano_user_clip.wav')` where `cues = [(sfx_name, time_s, peak_dB, max_len_s)]`. The mixer ducks the music under speech, adds the SFX peaks exactly on the cue times, limits to -0.5 dBFS.
When the user supplies new audio, add it here and list it in this table.

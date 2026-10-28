# Component A - Global editing standard (v1.0)
Derived from measured stats of the 11 references (`creators/ref_stats.json`) plus rules learned from the owner's feedback.

## Measured from references (observed fact)
- All 11 are 720x1280 9:16 exports, 15-90s. Loudness is uniform: **-14.1 to -14.6 LUFS**; peaks -0.2 to -2.8 dBFS. -> **target -14 LUFS, peak <= -1 dBFS.**
- Shot structure varies by format: talking-head-with-inserts reels hold the speaker in one continuous shot (detected cuts 0-1 per video) and change *graphics* every 2-4 s; heavier edits (refs 8, 10, 11) cut every ~3.5-4 s.
- Voice is always the dominant element; captions are word-group captions (1-4 words), centered, mid/lower screen.

## Rules for every video
1. **Hook first (0-3 s):** a written hook in large type from frame 0, plus the strongest spoken line. Proof/number in the hook when real evidence exists.
2. **Visual change every 2-4 s**, but each change must illustrate the spoken point (screenshot, diagram, number, list, icon). No random B-roll.
3. **Captions:** 1-4 words, synced to speech, key word larger/colour-accented; keep out of top 250 px and bottom 300 px safe zones; never over the eyes/mouth.
4. **Type:** display = Anton/Bebas (Impact stand-in); support = Poppins/Inter. One accent colour per video; dark or neutral base.
5. **Face stays natural:** no heavy retouch, no darkening of glasses, light grade only (owner feedback). Speaker visible >= ~60% of runtime in commentary formats.
6. **Audio:** clean + denoise voice, light compression; music 26-33 dB under speech (about -30 dBFS), ducked by voice; SFX peaks <= -14 dBFS, natural sounds (taps, swishes, thuds), no SFX on every caption; one silence beat before the biggest reveal. Different music per video.
7. **Evidence integrity:** never fabricate numbers, screenshots, testimonials; label illustrations "ILLUSTRATION/EXAMPLE"; owner's own claims shown as claims.
8. **Cuts:** remove stutters, false starts, dead air, non-speech tails (camera swings, watermark cards); 8 ms audio fades at every join; verify no clicks.
9. **Render:** 1080x1920, 30 fps, H.264 CRF 12-15, AAC 192-224k. Check black frames, text fit, cropped text.
10. Third-party footage/stills: licence-checked or labelled fair-use; credit file always.

# /greenscreen
The user's green-screen commentary edit (2x2 image grid behind a small cut-out of them, Anton title, one white Inter caption, quiet bed, clicks only).
The full spec is the skill: `.claude/skills/greenscreen/SKILL.md` (invoke with `/greenscreen`). Code is in `code/`, fonts in `fonts/`.
Needs: ffmpeg, python3 (numpy, opencv, scipy, onnxruntime, faster-whisper, pillow, requests) and the RVM matting model `rvm.onnx` (the scripts expect it in the old scratchpad `c2/work/rvm.onnx`; download RVM mobilenetv3 fp32 and fix the path in rvm17.py).

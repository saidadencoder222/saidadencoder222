#!/bin/bash
# One-time setup for the video toolkit. Run from the video-toolkit folder.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ln -sfn "$HERE" /tmp/vt                     # scripts reference /tmp/vt as the toolkit root
command -v ffmpeg >/dev/null || { echo "ffmpeg is required (apt install ffmpeg)"; exit 1; }
pip install -q numpy scipy opencv-python-headless pillow onnxruntime faster-whisper requests
mkdir -p "$HERE/c2/work"
[ -f "$HERE/c2/work/rvm.onnx" ] || curl -sSL -o "$HERE/c2/work/rvm.onnx" https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx
echo "ready. toolkit root -> /tmp/vt"

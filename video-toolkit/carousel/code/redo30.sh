cd /tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad/c5
ffmpeg -v error -y -i work/raw30.mp4 -filter_complex_script work/fa30.txt -map "[v]" -map "[a]" -c:v libx264 -crf 14 -preset fast -r 30 -c:a pcm_s16le work/clip30.mkv > work/redo30.log 2>&1
mkdir -p work/fd30; ffmpeg -v error -y -i work/clip30.mkv -vf fps=30 -q:v 2 work/fd30/%04d.jpg >> work/redo30.log 2>&1
python3 rvm30.py > work/rvm30.log 2>&1
python3 -c "import mscenes as M; print(M.alpha_arr(30).shape)" >> work/redo30.log 2>&1
ffmpeg -v error -i work/clip30.mkv -f null - >> work/redo30.log 2>&1
echo ALLDONE >> work/redo30.log

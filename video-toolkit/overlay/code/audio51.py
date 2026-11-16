import subprocess, re
src = 'work/clip51.mkv'; mid = 'work/voice51_mid.wav'; out = 'work/voice51.wav'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vn', '-ac', '1', '-ar', '48000', '-af', 'highpass=f=70,acompressor=threshold=-30dB:ratio=3.5:attack=12:release=200:makeup=8', mid], check=True)
r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', mid, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True)
lufs = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)[-1]); gain = -14.0 - lufs
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mid, '-af', f'volume={gain:.2f}dB,alimiter=limit=0.84:attack=4:release=80:level=false', out], check=True); print('audio ok', lufs, round(gain, 2))

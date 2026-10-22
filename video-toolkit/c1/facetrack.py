import sys, subprocess, numpy as np, cv2
from scipy.ndimage import gaussian_filter1d, median_filter
N = int(sys.argv[1]); w, h = 270, 480
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', f'work/clip{N}.mkv', '-vf', f'scale={w}:{h}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], stdout=subprocess.PIPE)
cas = cv2.CascadeClassifier('haar.xml'); ys = []; xs = []
while True:
    b = p.stdout.read(w * h)
    if len(b) < w * h: break
    g = np.frombuffer(b, np.uint8).reshape(h, w); fs = cas.detectMultiScale(g, 1.08, 5, minSize=(50, 50))
    if len(fs): x, y, ww, hh = max(fs, key=lambda f: f[2] * f[3]); ys.append((y + hh / 2) * 4); xs.append((x + ww / 2) * 4)
    else: ys.append(np.nan); xs.append(np.nan)
ys = np.array(ys); xs = np.array(xs); ok = ~np.isnan(ys); print(N, 'detected', ok.mean().round(2), 'median y', np.nanmedian(ys).round(), 'range', np.nanmin(ys).round(), np.nanmax(ys).round())
idx = np.arange(len(ys)); ys = np.interp(idx, idx[ok], ys[ok]); xs = np.interp(idx, idx[ok], xs[ok])
ys = gaussian_filter1d(median_filter(ys, 9, mode='nearest'), 6, mode='nearest'); xs = gaussian_filter1d(median_filter(xs, 9, mode='nearest'), 8, mode='nearest')
np.save(f'work/face{N}.npy', np.stack([xs, ys]))

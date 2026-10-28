import json, subprocess, numpy as np, sys
src = 'raw/doc.mp4'; W = json.load(open('raw/doc.words.json'))
raw = subprocess.run(['ffmpeg','-v','error','-i',src,'-vn','-ac','1','-ar','16000','-f','s16le','-'],capture_output=True).stdout
a = np.frombuffer(raw,np.int16).astype(np.float32)/32768; hop=160
r = np.sqrt(np.convolve(a*a,np.ones(hop)/hop,'same')[::hop]+1e-12)
END = 29.72   # after "...weren't fun" (source continues with an unfinished sentence)
q = r < .016; cuts = []; st = None
for k in range(len(q)+1):
    v = q[k] if k < len(q) else False
    if v and st is None: st = k
    if not v and st is not None:
        a0, b0 = st/100, k/100
        if k-st >= 38 and b0 < END: cuts.append((a0+.11, b0-.11))
        st = None
cuts.append((END, 40.0))
segs = []; p = 0.0
for lo, hi in cuts:
    segs.append((round(p,3), round(lo,3))); p = hi
tab = []; o = 0
for s, e in segs: tab.append((s, e, o)); o += e - s
def to_out(t):
    for s, e, o0 in tab:
        if s-.03 <= t <= e+.03: return o0 + max(min(t, e) - s, 0)
    return None
words = []
for w, s, e in W:
    if s >= 29.55: continue
    ts = to_out(s + .01); te = to_out(min(e, END) - .01)
    if ts is None: continue
    words.append((w, round(ts,3), round(max(te if te is not None else ts+.2, ts+.1),3)))
json.dump({'words': words, 'dur': o, 'segs': tab}, open('work/cap.json','w'))
fv = ''.join(f'[0:v]trim={s}:{e},setpts=PTS-STARTPTS,fps=30[v{k}];' for k,(s,e) in enumerate(segs))
fa = ''.join(f'[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={max(e-s-.01,0):.3f}:d=0.01[a{k}];' for k,(s,e) in enumerate(segs))
cc = ''.join(f'[v{k}][a{k}]' for k in range(len(segs)))
subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-filter_complex',fv+fa+f'{cc}concat=n={len(segs)}:v=1:a=1[v][a]','-map','[v]','-map','[a]','-c:v','libx264','-crf','10','-preset','fast','-pix_fmt','yuv420p','-c:a','pcm_s16le','-ar','48000','work/clip.mkv'],check=True)
print('dur', round(o,2), 'segments', len(segs)); print(' '.join(f'{w}[{a:.1f}]' for w,a,b in words))

"""Engine v3: speaker always on screen (subtle zooms in/out), hand-drawn doodle cutouts on top of the head, TikTok-style captions."""
import os, sys, json, math, random, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
R = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
WHITE = (255, 255, 255); INK = (26, 24, 24); RED = (46, 40, 228); PAPER = (247, 247, 244)

def clamp(x, a=0., b=1.): return a if x < a else b if x > b else x
def sm(x): x = clamp(x); return x * x * x * (x * (x * 6 - 15) + 10)
def eo(x): x = clamp(x); return 1 - (1 - x) ** 4
def eio(x): x = clamp(x); return 3 * x * x - 2 * x ** 3
def back(x, s=1.6): x = clamp(x); return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2

# ---------------------------------------------------------------- text
_F = {}; _T = {}; PAD = 30
FILES = {'pop500': 'Poppins-Medium.ttf', 'pop700': 'Poppins-Bold.ttf', 'pop800': 'Poppins-ExtraBold.ttf', 'pop600': 'Poppins-SemiBold.ttf', 'mark': 'PermanentMarker-Regular.ttf'}
def font(name, size, wght=700):
    key = 'mark' if name == 'mark' else f'pop{800 if wght >= 800 else 700 if wght >= 700 else 600 if wght >= 600 else 500}'
    k = (key, size)
    if k not in _F: _F[k] = ImageFont.truetype(f'{R}/fonts/{FILES[key]}', size)
    return _F[k]
def tex(s, size, wght=700, track=0, fnt='pop'):
    k = (s, size, wght, track, fnt)
    if k in _T: return _T[k]
    f = font(fnt, size, wght)
    w = int(f.getlength(s) + track * max(len(s) - 1, 0)) + 2 * PAD + 8; h = int(size * 1.9) + 2 * PAD
    im = Image.new('L', (w, h), 0); d = ImageDraw.Draw(im)
    if track == 0: d.text((PAD, PAD), s, font=f, fill=255)
    else:
        x = PAD
        for c in s: d.text((x, PAD), c, font=f, fill=255); x += f.getlength(c) + track
    m = np.asarray(im, np.float32) / 255
    ys = np.where(m.max(1) > .05)[0]; xs = np.where(m.max(0) > .05)[0]
    if len(ys) == 0: m = np.zeros((PAD * 2, PAD * 2), np.float32)
    else: m = np.ascontiguousarray(m[max(ys[0] - PAD, 0):ys[-1] + PAD, max(xs[0] - PAD, 0):xs[-1] + PAD])
    _T[k] = m; return m
def twidth(s, size, wght=700, track=0, fnt='pop'): return tex(s, size, wght, track, fnt).shape[1] - 2 * PAD
def fitsize(s, size, maxw, wght=700, track=0, fnt='pop'):
    w = twidth(s, size, wght, track, fnt); return size if w <= maxw else max(int(size * maxw / w), 14)

def put(cv, m, x, y, color=WHITE, a=1.0, sc=1.0, blur=0., dx=0, dy=0, add=False, clip=None):
    if a <= 0.003 or sc <= .02: return
    if sc != 1: m = cv2.resize(m, None, fx=sc, fy=sc, interpolation=cv2.INTER_LINEAR)
    if blur > .3: m = cv2.GaussianBlur(m, (0, 0), blur)
    h, w = m.shape; x0 = int(round(x - w / 2 + dx)); y0 = int(round(y - h / 2 + dy))
    X0, Y0 = max(x0, 0), max(y0, 0); X1, Y1 = min(x0 + w, cv.shape[1]), min(y0 + h, cv.shape[0])
    if X0 >= X1 or Y0 >= Y1: return
    mm = m[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * a
    if clip is not None: mm = mm * clip[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    col = np.array(color, np.float32)
    roi = cv[Y0:Y1, X0:X1].astype(np.float32); mm3 = mm[..., None]
    roi = roi + col * mm3 if add else roi * (1 - mm3) + col * mm3
    cv[Y0:Y1, X0:X1] = np.clip(roi, 0, 255).astype(np.uint8)

# ---------------------------------------------------------------- grade finish
_C = {}
def vig():
    if 'v8' not in _C:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); d = np.sqrt(((xx - W / 2) / (W * .72)) ** 2 + ((yy - H * .46) / (H * .62)) ** 2)
        v = np.clip(1.08 - .55 * d ** 2.2, .35, 1.0); _C['v8'] = (np.repeat(v[..., None], 3, 2) * 255).astype(np.uint8)
    return _C['v8']
def grain():
    if 'g' not in _C:
        r = np.random.RandomState(7); _C['g'] = [cv2.GaussianBlur(r.randint(0, 255, (H, W, 3)).astype(np.uint8), (0, 0), .7) for _ in range(5)]
    return _C['g']
def bloom(fr):
    sm_ = cv2.resize(fr, (W // 4, H // 4), interpolation=cv2.INTER_AREA); hi = np.clip(sm_.astype(np.int16) - 150, 0, 255).astype(np.uint8) * 2
    bl = cv2.resize(cv2.GaussianBlur(hi, (0, 0), 9), (W, H), interpolation=cv2.INTER_LINEAR); return cv2.addWeighted(fr, 1, bl, .22, 0)
def filmgrain(f, n, k=.05): return cv2.addWeighted(f, 1, grain()[n % 5], k, -128 * k)

# ---------------------------------------------------------------- speaker + subtle zoom plan
PATTERN = [(1.00, 1.10), (1.14, 1.03), (1.02, 1.12), (1.11, 1.00)]
def zoom_plan(dur, chunks, lo=1.9, hi=3.0):
    starts = [c['t0'] for c in chunks]; t = 0.0; segs = []; i = 0
    while t < dur - .5:
        nxt = [s for s in starts if s >= t + lo]
        end = min(nxt[0] if nxt else dur + 1, t + hi) if nxt and nxt[0] - t <= hi + .6 else min(t + 2.8, dur + 1)
        if nxt and nxt[0] - t <= hi + .6: end = nxt[0]
        z0, z1 = PATTERN[i % 4]; segs.append((t, end, z0, z1)); t = end; i += 1
    segs[-1] = (segs[-1][0], dur + 1, segs[-1][2], segs[-1][3]); return segs
def speaker(fr, t, plan, cy=840):
    for a, b, z0, z1 in plan:
        if a <= t < b or b == plan[-1][1]:
            if a <= t: seg = (a, b, z0, z1)
    a, b, z0, z1 = seg; z = z0 + (z1 - z0) * eio((t - a) / max(b - a, .1))
    M = np.float32([[z, 0, 540 - z * 540], [0, z, cy - z * cy]])
    return cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

# ---------------------------------------------------------------- tiktok captions
def build_chunks(words):
    toks = []
    for w, a, b in words:
        raw = w.strip(); s = raw.lower().strip('.,!?;:"“”');
        if s: toks.append([s.replace('’', "'"), a, b, raw[-1:] in ',.?!;'])
    chunks = []; cur = []
    for t in toks:
        if cur:
            txt = ' '.join(x[0] for x in cur + [t])
            if len(cur) >= 3 or len(txt) > 21 or t[1] - cur[-1][2] > .30 or cur[-1][3]: chunks.append(cur); cur = []
        cur.append(t)
    if cur: chunks.append(cur)
    out = []
    for i, c in enumerate(chunks):
        t0 = c[0][1]; nxt = chunks[i + 1][0][1] if i + 1 < len(chunks) else c[-1][2] + .5; gapn = nxt - c[-1][2]
        t1 = nxt if gapn <= .35 else c[-1][2] + .3
        out.append(dict(txt=' '.join(x[0] for x in c), t0=t0, t1=max(t1, t0 + .3)))
    return out
def draw_caps(f, ch, t, y=1440, size=46):
    for c in ch:
        if t < c['t0'] or t >= c['t1']: continue
        sz = fitsize(c['txt'], size, 900, 500, 2); m = tex(c['txt'], sz, 500, 2)
        life = t - c['t0']; a = clamp(life / .12); dy = (1 - eo(life / .18)) * 10
        put(f, m, 540, y, WHITE, a, dy=dy)

# ---------------------------------------------------------------- doodle overlays (sticker cutouts)
class Ov:
    def __init__(s, t0, t1, fn, pos=(540, 330), scale=1.0, rot=0.0): s.t0, s.t1, s.fn, s.pos, s.scale, s.rot = t0, t1, fn, pos, scale, rot
_KS = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (23, 23))
def draw_overlay(f, ov, t):
    tl = t - ov.t0; d = ov.t1 - ov.t0
    if tl < 0 or tl > d: return
    pop = back(tl / .38, 2.0); out = 1 - sm((tl - (d - .28)) / .28)
    if pop <= .03 or out <= .02: return
    sp = ov.fn(tl); c = sp.c.astype(np.int16); A = sp.A[..., 0]
    dil = cv2.dilate(A, _KS); dil = cv2.GaussianBlur(dil, (0, 0), 1.0)
    img = np.clip(c + ((255 - A.astype(np.int16))[..., None] * (dil[..., None] > 20)), 0, 255).astype(np.uint8)
    h, w = A.shape; sc = ov.scale * pop * (.88 + .12 * out); rot = ov.rot + 1.8 * math.sin(t * 1.7) + (1 - pop) * -8
    cx, cy = ov.pos[0], ov.pos[1] + 5 * math.sin(t * 2.1)
    M = cv2.getRotationMatrix2D((w / 2, h / 2), -rot, sc); M[0, 2] += cx - w / 2; M[1, 2] += cy - h / 2
    corners = np.array([[0, 0, 1], [w, 0, 1], [w, h, 1], [0, h, 1]], np.float32) @ M.T
    x0, y0 = int(max(corners[:, 0].min() - 24, 0)), int(max(corners[:, 1].min() - 24, 0)); x1, y1 = int(min(corners[:, 0].max() + 40, W)), int(min(corners[:, 1].max() + 40, H))
    if x1 <= x0 or y1 <= y0: return
    M2 = M.copy(); M2[0, 2] -= x0; M2[1, 2] -= y0; sz = (x1 - x0, y1 - y0)
    wi = cv2.warpAffine(img, M2, sz, flags=cv2.INTER_LINEAR); wa = cv2.warpAffine(dil, M2, sz, flags=cv2.INTER_LINEAR).astype(np.float32) / 255
    sh = np.zeros(wa.shape, np.float32)
    roi = f[y0:y1, x0:x1].astype(np.float32); roi *= (1 - sh[..., None]); al = (wa * out)[..., None]
    f[y0:y1, x0:x1] = np.clip(roi * (1 - al) + wi.astype(np.float32) * al, 0, 255).astype(np.uint8)

def _grad():
    if 'gr' not in _C: _C['gr'] = (1 - np.clip((np.arange(H - 1150, dtype=np.float32)) / 330, 0, 1) * .42)[:, None, None]
    return _C['gr']
# ---------------------------------------------------------------- sfx (synth, subtle)
SR = 48000
def _env(n, k): return np.exp(-np.arange(n) / SR * k)
def sfx_pop(g=1.0):
    n = int(.16 * SR); t = np.arange(n) / SR; ph = 2 * np.pi * np.cumsum(220 + 560 * np.exp(-t * 38)) / SR
    return g * .17 * (np.sin(ph) * _env(n, 30) + .15 * np.random.RandomState(1).randn(n) * _env(n, 90))
def sfx_ding(g=1.0):
    n = int(.9 * SR); t = np.arange(n) / SR
    return g * .11 * ((np.sin(2 * np.pi * 1568 * t) + .35 * np.sin(2 * np.pi * 2349 * t) + .15 * np.sin(2 * np.pi * 3136 * t)) * _env(n, 5.5))
def sfx_whoosh(g=1.0):
    from scipy.signal import butter, lfilter
    n = int(.42 * SR); t = np.arange(n) / SR; x = np.random.RandomState(2).randn(n); b, a = butter(2, [350 / (SR / 2), 3200 / (SR / 2)], 'band'); x = lfilter(b, a, x)
    return g * .13 * x * np.sin(np.pi * np.clip(t / .42, 0, 1)) ** 2
SFX = {'pop': sfx_pop, 'ding': sfx_ding, 'whoosh': sfx_whoosh}
def build_sfx(N, events, dur, out):
    from scipy.io import wavfile
    y = np.zeros(int((dur + 1.5) * SR), np.float32)
    for t, kind, g in events:
        s = SFX[kind](g).astype(np.float32); i = int(t * SR)
        if 0 <= i < len(y): y[i:i + len(s)] += s[:len(y) - i]
    y = np.clip(y, -.9, .9); wavfile.write(out, SR, (y * 32767).astype(np.int16))

# ---------------------------------------------------------------- frame + driver
def render_frame(plan, ch, ovs, fr, t, n):
    f = speaker(fr, t, plan); f = bloom(f); f = cv2.multiply(f, vig(), scale=1 / 255)
    f[1150:] = (f[1150:].astype(np.float32) * _grad()).astype(np.uint8)
    for ov in ovs: draw_overlay(f, ov, t)
    draw_caps(f, ch, t); return filmgrain(f, n)
def _frames(clip, t0, n):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{t0:.3f}', '-i', clip, '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE, bufsize=W * H * 3 * 3)
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)
    p.wait()
def _chunk(args):
    N, mod, k, a, b = args
    import importlib; M = importlib.import_module(mod); plan, ch, ovs = M.setup(N)
    out = f'{R}/work/ch{N}_{k:03d}.mkv'
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'fast', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    n = a
    for fr in _frames(f'{R}/work/clip{N}g.mkv', a / FPS, b - a):
        enc.stdin.write(np.ascontiguousarray(render_frame(plan, ch, ovs, fr, n / FPS, n)).tobytes()); n += 1
    enc.stdin.close(); enc.wait(); return out
def render(N, mod, final, chunk=120, procs=4):
    import multiprocessing as mp
    dur = json.load(open(f'{R}/work/cap{N}.json'))['dur']; total = int(dur * FPS)
    jobs = [(N, mod, k, a, min(a + chunk, total)) for k, a in enumerate(range(0, total, chunk))]
    with mp.Pool(procs) as pool: outs = pool.map(_chunk, jobs, chunksize=1)
    lst = f'{R}/work/list{N}.txt'; open(lst, 'w').write(''.join(f"file '{o}'\n" for o in outs))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', f'{R}/work/v{N}_silent.mkv'], check=True)
    voice(N)
    import importlib; Mo = importlib.import_module(mod); build_sfx(N, Mo.sfx_events(N), dur, f'{R}/work/sfx{N}.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{R}/work/v{N}_silent.mkv', '-i', f'{R}/work/voice{N}.wav', '-i', f'{R}/work/sfx{N}.wav', '-filter_complex', '[1:a][2:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[a]', '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-crf', '21', '-preset', 'medium', '-maxrate', '12M', '-bufsize', '24M', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final], check=True)
    for o in outs: os.remove(o)
def voice(N):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{R}/work/clip{N}.mkv', '-vn', '-af',
        'highpass=f=75,afftdn=nr=9:nf=-48,equalizer=f=220:t=q:w=1:g=-1.5,equalizer=f=3200:t=q:w=1.1:g=2.5,acompressor=threshold=-21dB:ratio=3:attack=6:release=90:makeup=3,loudnorm=I=-14:TP=-1.5:LRA=8',
        '-ar', '48000', f'{R}/work/voice{N}.wav'], check=True)
def preview(N, mod, ts, out, cols=None):
    import importlib; M = importlib.import_module(mod); plan, ch, ovs = M.setup(N); ims = []
    for t in ts:
        fr = next(_frames(f'{R}/work/clip{N}g.mkv', t, 1)); f = render_frame(plan, ch, ovs, fr, t, int(t * FPS)); ims.append(cv2.resize(f, (360, 640), interpolation=cv2.INTER_AREA))
    cols = cols or len(ims); rows = [np.hstack(ims[i:i + cols] + [np.zeros_like(ims[0])] * (cols - len(ims[i:i + cols]))) for i in range(0, len(ims), cols)]
    cv2.imwrite(out, np.vstack(rows))

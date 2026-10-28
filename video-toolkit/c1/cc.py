"""Core renderer v2: Poppins lowercase captions, full-screen animation scenes, cinematic grade, gold hooks."""
import os, sys, json, math, random, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
R = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
GOLD = (46, 36, 226); GOLD_L = (238, 238, 255); GOLD_D = (30, 20, 150); WHITE = (255, 255, 255)
CRIM = (46, 36, 226); GREY = (110, 110, 118); INK = (255, 255, 255)
CAP_Y = 1500; TR = .30

def clamp(x, a=0., b=1.): return a if x < a else b if x > b else x
def sm(x): x = clamp(x); return x * x * x * (x * (x * 6 - 15) + 10)
def eo(x): x = clamp(x); return 1 - (1 - x) ** 4
def eio(x): x = clamp(x); return 3 * x * x - 2 * x ** 3
def back(x, s=1.6): x = clamp(x); return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2

# ---------------------------------------------------------------- text
_F = {}; _T = {}; PAD = 34
def font(name, size, wght=700):
    k = (name, size, wght)
    if k not in _F:
        if name == 'pop':
            fn = 'Poppins-ExtraBold.ttf' if wght >= 800 else 'Poppins-Bold.ttf' if wght >= 700 else 'Poppins-SemiBold.ttf' if wght >= 600 else 'Poppins-Medium.ttf'
            _F[k] = ImageFont.truetype(f'{R}/fonts/{fn}', size)
        else:
            _F[k] = ImageFont.truetype(f'{R}/fonts/Cinzel[wght].ttf', size)
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
    w = twidth(s, size, wght, track, fnt)
    return size if w <= maxw else max(int(size * maxw / w), 14)

def put(cv, m, x, y, color=WHITE, a=1.0, sc=1.0, blur=0., dx=0, dy=0, add=False, clip=None):
    if a <= 0.003: return
    if sc <= .02: return
    if sc != 1: m = cv2.resize(m, None, fx=sc, fy=sc, interpolation=cv2.INTER_LINEAR)
    if blur > .3: m = cv2.GaussianBlur(m, (0, 0), blur)
    h, w = m.shape; x0 = int(round(x - w / 2 + dx)); y0 = int(round(y - h / 2 + dy))
    X0, Y0 = max(x0, 0), max(y0, 0); X1, Y1 = min(x0 + w, cv.shape[1]), min(y0 + h, cv.shape[0])
    if X0 >= X1 or Y0 >= Y1: return
    mm = m[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * a
    if clip is not None: mm = mm * clip[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    col = color(h, w)[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] if callable(color) else np.array(color, np.float32)
    roi = cv[Y0:Y1, X0:X1].astype(np.float32); mm3 = mm[..., None]
    roi = roi + col * mm3 if add else roi * (1 - mm3) + col * mm3
    cv[Y0:Y1, X0:X1] = np.clip(roi, 0, 255).astype(np.uint8)

def goldfn(sheen=-1.):
    def f(h, w):
        yy = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
        top = np.array([70, 62, 244], np.float32); mid = np.array([48, 38, 228], np.float32); bot = np.array([34, 26, 190], np.float32)
        c = np.where(yy < .45, top + (mid - top) * (yy / .45), mid + (bot - mid) * ((yy - .45) / .55))
        c = np.broadcast_to(c, (h, w, 3)).copy()
        if sheen >= 0:
            xx = np.arange(w, dtype=np.float32)[None, :]; yv = np.arange(h, dtype=np.float32)[:, None]
            cx = sheen * (w + 300) - 150; band = np.exp(-(((xx - cx) + yv * .45) / 55) ** 2); c += 60 * band[..., None]
        return c
    return f
GOLDF = goldfn()

def ptext(cv, s, size, x, y, color=WHITE, wght=700, track=0, a=1., sc=1., blur=0., glow=0., shadow=0., fnt='pop', dy=0):
    m = tex(s, size, wght, track, fnt)
    if shadow > 0: put(cv, m, x, y, (0, 0, 0), a * shadow, sc, blur + 8, dy=dy + 5)
    if glow > 0: put(cv, m, x, y, GOLD if color is GOLDF else color, a * glow, sc, blur + 14, dy=dy, add=True)
    put(cv, m, x, y, color, a, sc, blur, dy=dy)

def rrect_pts(x0, y0, x1, y1, r, n=8):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n); pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return np.array(pts, np.float32)
def rr(cv, x0, y0, x1, y1, r, fill=None, edge=None, th=2):
    r = max(4, r * .3)
    pts = (rrect_pts(x0, y0, x1, y1, r) * 16).astype(np.int32)
    if fill is not None: cv2.fillPoly(cv, [pts], fill, cv2.LINE_AA, 4)
    if edge is not None: cv2.polylines(cv, [pts], True, edge, th, cv2.LINE_AA, 4)
GY0, GY1 = 280, 1480
def glow_add(cv, layer, sigma=10, gain=1.0):
    gain = gain * .5; g = cv2.GaussianBlur(layer[GY0:GY1], (0, 0), sigma); sub = cv[GY0:GY1]
    cv2.addWeighted(sub, 1, g, gain, 0, sub); cv2.add(sub, (layer[GY0:GY1] * .6).astype(np.uint8), sub)

# ---------------------------------------------------------------- grade / bg
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
def luts():
    if 'l' not in _C:
        x = np.arange(256, dtype=np.float32) / 255
        base = np.clip(.5 + (x - .5) * 1.12 - .06 * np.sin((x - .5) * 2 * math.pi), 0, 1); base = .03 + base * .97
        b = np.clip(base + .035 * (1 - x) ** 2 - .03 * x ** 2, 0, 1); g = np.clip(base + .006 * (1 - x) ** 2, 0, 1); r = np.clip(base - .02 * (1 - x) ** 2 + .035 * x ** 1.5, 0, 1)
        _C['l'] = [(c * 255).astype(np.uint8) for c in (b, g, r)]
    return _C['l']
def grade(fr):
    # colour grade is baked into clipNg.mkv by cinematic.cube (3D LUT); here only a soft highlight bloom
    sm_ = cv2.resize(fr, (W // 4, H // 4), interpolation=cv2.INTER_AREA); hi = np.clip(sm_.astype(np.int16) - 150, 0, 255).astype(np.uint8) * 2
    bl = cv2.resize(cv2.GaussianBlur(hi, (0, 0), 9), (W, H), interpolation=cv2.INTER_LINEAR); return cv2.addWeighted(fr, 1, bl, .22, 0)
def vignette(f): return cv2.multiply(f, vig(), scale=1 / 255)
def filmgrain(f, n, k=.05): return cv2.addWeighted(f, 1, grain()[n % 5], k, -128 * k)

def bg_anim(t):
    if 'bg' not in _C:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); d = np.sqrt(((xx - 540) / 760) ** 2 + ((yy - 860) / 900) ** 2); glow = np.clip(1 - d, 0, 1) ** 2
        base = np.zeros((H, W, 3), np.float32); base[:] = (7, 7, 8); base += glow[..., None] * np.array([9, 9, 10], np.float32)
        _C['bg'] = np.clip(base, 0, 255).astype(np.uint8)
        rg = random.Random(3); _C['pts'] = [(rg.uniform(0, W), rg.uniform(0, H), rg.uniform(.6, 2.6), rg.uniform(10, 34), rg.uniform(0, 6.28)) for _ in range(90)]
    f = _C['bg'].copy(); lay = np.zeros((H, W, 3), np.uint8)
    for x, y, r, v, ph in _C['pts']:
        yy = (y - v * t) % H; xx = x + 16 * math.sin(t * .5 + ph); k = .35 + .65 * (.5 + .5 * math.sin(t * 1.3 + ph))
        cv2.circle(lay, (int(xx), int(yy)), max(int(r), 1), (int(45 * k),) * 3, -1, cv2.LINE_AA)
    return cv2.add(f, cv2.GaussianBlur(lay, (0, 0), 1.1))

def spk_full(fr, tl, d, z0=1.0, z1=1.06, cy=820):
    z = z0 + (z1 - z0) * sm(tl / max(d, .1)); M = np.float32([[z, 0, 540 - z * 540], [0, z, cy - z * cy]])
    return cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

# ---------------------------------------------------------------- titles / hook
def title(f, l1, l2, tl, y=150):
    p0 = sm((tl - .05) / .45)
    for i, (s, size, col, wg, tr, yy) in enumerate(((l1.upper(), 36, (210, 210, 218), 600, 9, y), (l2, 78, WHITE, 800, -1, y + 92))):
        if not s: continue
        size = fitsize(s, size, 920, wg, tr); m = tex(s, size, wg, tr); h, w = m.shape; p = sm((tl - .08 - i * .14) / .45)
        if i == 1 and p > 0:
            bw = (w - 2 * PAD + 56) / 2 * p; cv2.rectangle(f, (int(540 - bw), int(yy - size * .62)), (int(540 + bw), int(yy + size * .62)), GOLD, -1)
        edge = (p * (w + 140)) - 70; clip = np.clip((edge - np.arange(w, dtype=np.float32)[None, :]) / 70, 0, 1) * np.ones((h, 1), np.float32)
        put(f, m, 540, yy, col, 1, clip=clip, blur=(1 - p) * 4)
    cv2.rectangle(f, (540 - int(60 * eo((tl - .4) / .4)), y - 54), (540 + int(60 * eo((tl - .4) / .4)), y - 50), (255, 255, 255), -1)

def hook(f, lines, tl, tend):
    """gold hook, written on, exits by rising/fading"""
    k = sm(tl / .4) * (1 - sm((tl - tend + .45) / .45))
    top = np.clip((860 - np.arange(H, dtype=np.float32)) / 760, 0, 1)[:, None, None] ** 1.1 * .86 * k
    f[:] = np.clip(f.astype(np.float32) * (1 - top) + np.array([6, 7, 9], np.float32) * top, 0, 255).astype(np.uint8)
    y = 240; ex = sm((tl - tend + .5) / .5)
    for i, (s, sz, wg) in enumerate(lines):
        size = fitsize(s, sz, 980, wg, -2); m = tex(s, size, wg, -2); h, w = m.shape; p = sm((tl - .1 - i * .5) / .7)
        yy = y + size * .6 + 6
        if p <= 0: y += size * 1.3; continue
        edge = p * (w + 160) - 80; clip = np.clip((edge - np.arange(w, dtype=np.float32)[None, :]) / 80, 0, 1) * np.ones((h, 1), np.float32)
        sheen = (tl * .55 + i * .2) % 1.6 / 1.6; a = 1 - ex; dyy = -50 * eo(ex); bl = 8 * ex
        put(f, m, 540, yy, (0, 0, 0), .55 * a, blur=10 + bl, dy=dyy + 6, clip=clip)
        put(f, m, 540, yy, goldfn(sheen), a, clip=clip, blur=(1 - p) * 5 + bl, dy=dyy)
        put(f, m, 540, yy, GOLD, .5 * p * a, blur=16, add=True, clip=clip, dy=dyy)
        y += size * 1.3

# ---------------------------------------------------------------- captions (poppins, lowercase, white, slight shadow, tight)
SMALL = {'A', 'THE', 'TO', 'OF', 'AN', 'IN', 'ON', 'IT', 'IS', 'AT', 'OR', 'MY', 'HE', 'SO', 'I', 'HIS', 'AND', 'YOU', "YOU'RE", 'WHO', 'HOW', 'DO', 'BE', 'IF', 'THAT', 'FOR', 'NOT', 'ME', 'HIM', 'WAS', 'CAN', 'THIS', 'THEIR', 'WHAT', 'WHY', 'BY', 'WILL', 'JUST', 'ONE'}
def build_groups(words, emph):
    toks = []
    for w, a, b in words:
        s = w.upper().strip(' .,!?;:"“”')
        if s: toks.append([s.replace('’', "'"), a, b])
    G = []; i = 0
    while i < len(toks):
        s, a, b = toks[i]; names = [s]; e = b
        if i + 1 < len(toks) and (s in SMALL or len(s) <= 2) and toks[i + 1][1] - b < .25 and len(s) + len(toks[i + 1][0]) <= 14 and toks[i + 1][0] not in emph:
            names.append(toks[i + 1][0]); e = toks[i + 1][2]; i += 1
        G.append(dict(txt=' '.join(names), t0=a, tend=e, em=any(n in emph for n in names))); i += 1
    for k, g in enumerate(G):
        nxt = G[k + 1]['t0'] if k + 1 < len(G) else g['tend'] + .6
        g['t1'] = max(min(max(nxt, g['t0'] + .22), g['t0'] + 1.5, nxt if nxt - g['tend'] < .5 else g['tend'] + .4), g['t0'] + .22)
    return G
def draw_caps(f, G, t, y, maxw=960, size=96):
    for g in G:
        if t < g['t0'] - .02 or t > g['t1'] + .1: continue
        txt = g['txt'].lower(); sz = fitsize(txt, size, maxw, 700, -2); m = tex(txt, sz, 700, -2)
        life = t - g['t0']; p = eo(life / .13); sc = 1 + .13 * (1 - p)
        if g['em']: sc *= 1 + .07 * math.sin(math.pi * clamp(life / .28))
        a = clamp(life / .06) * (1 - clamp((t - g['t1'] + .05) / .05))
        put(f, m, 540, y, (0, 0, 0), .45 * a, sc, blur=8, dy=5); put(f, m, 540, y, (0, 0, 0), .35 * a, sc, blur=2, dy=2)
        put(f, m, 540, y, WHITE, a, sc)

# ---------------------------------------------------------------- scenes
class Sc:
    def __init__(s, t0, kind, anim=None, title=None, hook=None, z=(1.0, 1.06), cy=820):
        s.t0 = t0; s.kind = kind; s.anim = anim; s.title = title; s.hook = hook; s.z = z; s.cy = cy; s.t1 = None
def build(scenes, dur):
    for i, s in enumerate(scenes): s.t1 = scenes[i + 1].t0 if i + 1 < len(scenes) else dur + .5
    return scenes
def scene_frame(s, t, fr):
    tl = max(t - s.t0, 0); d = s.t1 - s.t0
    if s.kind == 'full':
        f = spk_full(fr, tl, d, s.z[0], s.z[1], s.cy)
        if s.hook: hook(f, s.hook, tl, d)
        return f
    f = bg_anim(t)
    if s.title: title(f, s.title[0], s.title[1], tl)
    if s.anim: s.anim(f, tl, d)
    return f
def render_frame(scenes, G, fr, t, n):
    idx = max(i for i, s in enumerate(scenes) if s.t0 <= t + 1e-6) if t >= scenes[0].t0 else 0
    s = scenes[idx]; fr = grade(fr); f = scene_frame(s, t, fr)
    if idx > 0 and t - s.t0 < TR:
        pv = scenes[idx - 1]
        if not (pv.kind == 'full' and s.kind == 'full'):
            q = sm((t - s.t0) / TR); g = scene_frame(pv, t, fr); f = cv2.addWeighted(g, 1 - q, f, q, 0)
            f = cv2.addWeighted(f, 1, np.full_like(f, (255, 255, 255)), .10 * math.sin(math.pi * q), 0)
    if s.kind == 'full': f = vignette(f)
    draw_caps(f, G, t, CAP_Y)
    return filmgrain(f, n)

# ---------------------------------------------------------------- driver
def _frames(clip, t0, n):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{t0:.3f}', '-i', clip, '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE, bufsize=W * H * 3 * 3)
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)
    p.wait()
def _chunk(args):
    N, mod, k, a, b = args
    import importlib; M = importlib.import_module(mod); scenes, G = M.setup(N)
    out = f'{R}/work/ch{N}_{k:03d}.mkv'
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'fast', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    n = a
    for fr in _frames(f'{R}/work/clip{N}g.mkv', a / FPS, b - a):
        enc.stdin.write(np.ascontiguousarray(render_frame(scenes, G, fr, n / FPS, n)).tobytes()); n += 1
    enc.stdin.close(); enc.wait(); return out
def render(N, mod, final, chunk=120, procs=4):
    import multiprocessing as mp
    dur = json.load(open(f'{R}/work/cap{N}.json'))['dur']; total = int(dur * FPS)
    jobs = [(N, mod, k, a, min(a + chunk, total)) for k, a in enumerate(range(0, total, chunk))]
    with mp.Pool(procs) as pool: outs = pool.map(_chunk, jobs, chunksize=1)
    lst = f'{R}/work/list{N}.txt'; open(lst, 'w').write(''.join(f"file '{o}'\n" for o in outs))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', f'{R}/work/v{N}_silent.mkv'], check=True)
    voice(N)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{R}/work/v{N}_silent.mkv', '-i', f'{R}/work/voice{N}.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '21', '-preset', 'medium', '-maxrate', '12M', '-bufsize', '24M', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', final], check=True)
    for o in outs: os.remove(o)
def voice(N):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{R}/work/clip{N}.mkv', '-vn', '-af',
        'highpass=f=75,afftdn=nr=9:nf=-48,equalizer=f=220:t=q:w=1:g=-1.5,equalizer=f=3200:t=q:w=1.1:g=2.5,acompressor=threshold=-21dB:ratio=3:attack=6:release=90:makeup=3,loudnorm=I=-14:TP=-1.5:LRA=8',
        '-ar', '48000', f'{R}/work/voice{N}.wav'], check=True)
def preview(N, mod, ts, out, cols=None):
    import importlib; M = importlib.import_module(mod); scenes, G = M.setup(N); ims = []
    for t in ts:
        fr = next(_frames(f'{R}/work/clip{N}g.mkv', t, 1)); f = render_frame(scenes, G, fr, t, int(t * FPS)); ims.append(cv2.resize(f, (360, 640), interpolation=cv2.INTER_AREA))
    cols = cols or len(ims); rows = [np.hstack(ims[i:i + cols] + [np.zeros_like(ims[0])] * (cols - len(ims[i:i + cols]))) for i in range(0, len(ims), cols)]
    cv2.imwrite(out, np.vstack(rows))

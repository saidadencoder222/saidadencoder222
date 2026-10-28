"""MST: cinematic business-edit engine (archive photography w/ 2.5D parallax, paper/document scenes, diagrams,
designed transitions, film texture).  Shared by m12/m13/m14.  Frames are BGR uint8 1080x1920."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad/c5')
import os, math, json, subprocess
import numpy as np, cv2
from simple import *            # S3, doc, tex, put, text, twidth, eo, eio, clamp, lerp, W, H, FPS, WHITE, captions, chunk_writer, speaker, cine
doc.FILES.update({'serif': 'CrimsonPro-Regular.ttf', 'serifi': 'CrimsonPro-Italic.ttf', 'serifb': 'CrimsonPro-Bold.ttf', 'mono': 'IBMPlexMono-Regular.ttf',
                  'monob': 'IBMPlexMono-Bold.ttf', 'lib': 'LibreBaskerville-Regular.ttf', 'iserif': 'InstrumentSerif-Regular.ttf', 'iserifi': 'InstrumentSerif-Italic.ttf'})
SC = '/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad'
ART = f'{SC}/c11/art'; CACHE = f'{SC}/c11/cache'; os.makedirs(CACHE, exist_ok=True)
INK = (20, 19, 18); PAPER = (196, 220, 232); AMBER = (64, 150, 255); OFF = (236, 236, 236); DIM = (150, 150, 150)
rs0 = np.random.RandomState(7)

# ------------------------------------------------------------------ helpers
def T(f, s, name, size, x, y, col=OFF, a=1.0, track=0, shadow=0., sc=1.0, w=600): text(f, s, name, size, x, y, col, a, track=track, w=w, sc=sc, shadow=shadow)
def fit(s, name, size, maxw, track=0, w=600):
    while twidth(s, name, size, track, w) > maxw and size > 14: size -= 2
    return size
def typed(s, u, cps=26): n = int(max(u, 0) * cps); return s[:n] + ('_' if int(u * 3) % 2 == 0 and n < len(s) + 8 else '')
def eob(x): x = clamp(x); return 1 + 2.2 * (x - 1) ** 3 + 1.2 * (x - 1) ** 2
def vstack(*ys): return ys
def lerpc(a, b, u): return tuple(int(lerp(a[i], b[i], u)) for i in range(3))
_V = None
def vign():
    global _V
    if _V is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); d = np.sqrt(((xx - W / 2) / (W * .72)) ** 2 + ((yy - H / 2) / (H * .66)) ** 2); _V = np.clip(1.06 - d ** 2.2 * .75, .28, 1.0)[..., None]
    return _V
_N = None
def gr(k, amt=.045, color=False):
    global _N
    if _N is None: _N = [cv2.resize(np.random.RandomState(i).randn(H // 3, W // 3).astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR) for i in range(6)]
    return _N[k % 6] * 255 * amt
def filmfx(f, k, amt=.05, flick=.035, scratches=True, dust=True, halo=.25, vig=True):
    amt = 0.0; flick = 0.0; scratches = False; dust = False; halo = min(halo, .12)
    r = np.random.RandomState(k * 7 + 3); a = f.astype(np.float32)
    if halo > 0:
        hi = np.clip(a - 175, 0, 255); hb = cv2.GaussianBlur(hi, (0, 0), 22); a += hb * np.array([.55, .8, 1.0], np.float32) * halo
    a *= 1 + (r.rand() - .5) * 2 * flick
    if vig: a *= vign() * .5 + .5 if False else vign()
    a += gr(k + (k // 3) % 5, amt)[..., None]
    if scratches and r.rand() < .35:
        for _ in range(r.randint(1, 3)): x = r.randint(0, W); a[:, max(x - 1, 0):x + 1] += 40
    if dust and r.rand() < .5:
        for _ in range(r.randint(2, 7)): cv2.circle(a, (r.randint(0, W), r.randint(0, H)), r.randint(1, 3), (255, 255, 255) if r.rand() < .5 else (10, 10, 10), -1, cv2.LINE_AA)
    return np.clip(a, 0, 255).astype(np.uint8)
def grade_bw(img, warm=.55, contrast=1.18, lift=.03):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    g = np.clip((g - .5) * contrast + .5 + lift, 0, 1); g = g * g * (3 - 2 * g) * .35 + g * .65
    tone = np.stack([g * .72, g * .86, g * 1.0], -1)      # warm archival (BGR)
    mono = np.stack([g, g, g], -1); return (np.clip(mono * (1 - warm) + tone * warm * 1.06, 0, 1) * 255).astype(np.uint8)
def grade_modern(f):
    a = f.astype(np.float32) / 255; lum = a.mean(2, keepdims=True); a = lum + (a - lum) * 1.04
    a = a * a * (3 - 2 * a) * .25 + a * .75; sh = np.clip(.5 - lum, 0, 1); a += sh * np.array([.04, .012, -.012], np.float32); hi = np.clip(lum - .6, 0, 1); a += hi * np.array([-.01, .012, .03], np.float32)
    return (np.clip(a, 0, 1) * 255).astype(np.uint8)
def dark_bg(t, tint=(26, 25, 24)):
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]; base = np.array(tint, np.float32)[None, None]
    return np.broadcast_to(base * (1.15 - .5 * np.abs(yy - .42)), (H, W, 3)).copy()
def glow(f, x, y, r, col=AMBER, a=.5):
    x0, y0, x1, y1 = int(x - r), int(y - r), int(x + r), int(y + r); X0, Y0, X1, Y1 = max(x0, 0), max(y0, 0), min(x1, W), min(y1, H)
    if X0 >= X1 or Y0 >= Y1: return
    yy, xx = np.mgrid[Y0:Y1, X0:X1].astype(np.float32); d = np.sqrt((xx - x) ** 2 + (yy - y) ** 2) / r; m = np.clip(1 - d, 0, 1) ** 2 * a
    f[Y0:Y1, X0:X1] = np.clip(f[Y0:Y1, X0:X1].astype(np.float32) + m[..., None] * np.array(col, np.float32), 0, 255).astype(np.uint8)
def rrect(f, x0, y0, x1, y1, col, a=1.0, r=18, th=-1):
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    if x1 - x0 < 2 or y1 - y0 < 2 or a <= 0: return
    ov = f.copy(); r = int(min(r, (x1 - x0) // 2, (y1 - y0) // 2))
    if th < 0:
        cv2.rectangle(ov, (x0 + r, y0), (x1 - r, y1), col, -1); cv2.rectangle(ov, (x0, y0 + r), (x1, y1 - r), col, -1)
        for c in ((x0 + r, y0 + r), (x1 - r, y0 + r), (x0 + r, y1 - r), (x1 - r, y1 - r)): cv2.circle(ov, c, r, col, -1, cv2.LINE_AA)
    else:
        cv2.line(ov, (x0 + r, y0), (x1 - r, y0), col, th, cv2.LINE_AA); cv2.line(ov, (x0 + r, y1), (x1 - r, y1), col, th, cv2.LINE_AA)
        cv2.line(ov, (x0, y0 + r), (x0, y1 - r), col, th, cv2.LINE_AA); cv2.line(ov, (x1, y0 + r), (x1, y1 - r), col, th, cv2.LINE_AA)
        for c, an in (((x0 + r, y0 + r), 180), ((x1 - r, y0 + r), 270), ((x0 + r, y1 - r), 90), ((x1 - r, y1 - r), 0)): cv2.ellipse(ov, c, (r, r), 0, an, an + 90, col, th, cv2.LINE_AA)
    f[:] = cv2.addWeighted(f, 1 - a, ov, a, 0) if a < 1 else ov
def shadow_rect(f, x0, y0, x1, y1, a=.5, blur=24, dy=14):
    m = np.zeros((H, W), np.float32); cv2.rectangle(m, (int(x0), int(y0 + dy)), (int(x1), int(y1 + dy)), 1, -1); m = cv2.GaussianBlur(m, (0, 0), blur)[..., None]; f[:] = (f.astype(np.float32) * (1 - m * a)).astype(np.uint8)
def bottom_scrim(f, y0=1380, a=.55):
    g = np.clip((np.arange(H, dtype=np.float32) - y0) / (H - y0 - 120), 0, 1)[:, None, None] ** 1.3 * a; f[:] = (f.astype(np.float32) * (1 - g)).astype(np.uint8)
def top_scrim(f, y1=520, a=.5):
    g = np.clip(1 - np.arange(H, dtype=np.float32) / y1, 0, 1)[:, None, None] ** 1.5 * a; f[:] = (f.astype(np.float32) * (1 - g)).astype(np.uint8)

# ------------------------------------------------------------------ paper texture
_P = None
def paper_tex():
    global _P
    if _P is None:
        r = np.random.RandomState(11); base = np.zeros((H, W, 3), np.float32) + np.array(PAPER, np.float32)
        for sc_, amp in ((300, 7), (90, 5), (22, 4), (6, 3)):
            n = cv2.resize(r.randn(H // sc_ + 2, W // sc_ + 2).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC); base += n[..., None] * amp * np.array([.8, 1, 1.1], np.float32)
        fib = np.zeros((H, W), np.float32)
        for _ in range(900): x, y = r.randint(0, W), r.randint(0, H); ln = r.randint(8, 40); an = r.rand() * 6.28; cv2.line(fib, (x, y), (int(x + math.cos(an) * ln), int(y + math.sin(an) * ln)), r.choice([-1, 1]) * .5, 1, cv2.LINE_AA)
        base += cv2.GaussianBlur(fib, (0, 0), .7)[..., None] * 14
        st = cv2.resize(r.rand(H // 380 + 2, W // 380 + 2).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC); base *= (1 - np.clip(st - .6, 0, 1)[..., None] * .12 * np.array([.9, 1, 1.12], np.float32))
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); ed = np.minimum(np.minimum(xx, W - xx), np.minimum(yy, H - yy)); base *= (.78 + .22 * np.clip(ed / 90, 0, 1))[..., None]
        _P = np.clip(base, 0, 255).astype(np.uint8)
    return _P

# ------------------------------------------------------------------ archival photograph with 2.5D parallax
_PH = {}
class Photo:
    """full image kept (height covers 1.28 screens) so the camera can pan; foreground cutout gives 2.5D parallax when a subject is found."""
    def __init__(s, key, fy=.5, tone='bw', sep=True, maxw=4600):
        s.key = key; img = cv2.imread(f'{ART}/{key}.jpg'); s.tone = tone; s.fy = fy
        ih, iw = img.shape[:2]; sc = max(H * 1.28 / ih, W * 1.28 / iw); sc = min(sc, maxw / iw) if iw * sc > maxw else sc
        s.base = cv2.resize(img, (int(iw * sc), int(ih * sc)), interpolation=cv2.INTER_CUBIC if sc > 1 else cv2.INTER_AREA)
        if s.base.shape[0] < H * 1.0 or s.base.shape[1] < W * 1.0: s.base = cv2.resize(s.base, None, fx=max(H / s.base.shape[0], W / s.base.shape[1]) * 1.05, fy=max(H / s.base.shape[0], W / s.base.shape[1]) * 1.05)
        s.base = grade_bw(s.base) if tone == 'bw' else s.base
        s.fgm = None; cp = f'{CACHE}/{key}_fg.npy'
        if sep:
            if os.path.exists(cp): s.fgm = np.load(cp).astype(np.float32)
            else:
                try:
                    from rembg import new_session, remove
                    se = new_session('isnet-general-use'); sm_ = cv2.resize(s.base, None, fx=.3, fy=.3, interpolation=cv2.INTER_AREA); o = remove(cv2.cvtColor(sm_, cv2.COLOR_BGR2RGB), session=se, only_mask=True)
                    m = o.astype(np.float32) / 255; cov = m.mean(); s.fgm = cv2.resize(m, (s.base.shape[1], s.base.shape[0]), interpolation=cv2.INTER_CUBIC) if .04 < cov < .7 else np.zeros(s.base.shape[:2], np.float32)
                except Exception as e: print('rembg fail', key, e); s.fgm = np.zeros(s.base.shape[:2], np.float32)
                np.save(cp, s.fgm.astype(np.float16))
        if s.fgm is not None and s.fgm.max() > .1:
            hole = cv2.dilate((s.fgm > .3).astype(np.uint8) * 255, np.ones((21, 21), np.uint8)); sm_ = cv2.resize(s.base, None, fx=.2, fy=.2); hm = cv2.resize(hole, (sm_.shape[1], sm_.shape[0]), interpolation=cv2.INTER_NEAREST)
            s.bg = cv2.resize(cv2.inpaint(sm_, hm, 6, cv2.INPAINT_TELEA), (s.base.shape[1], s.base.shape[0]), interpolation=cv2.INTER_CUBIC); s.has = True
        else: s.bg = s.base; s.has = False
    def render(s, u, dur, pan=(.5, .5), dolly=.09, drift=(1, -1)):
        p = clamp(u / max(dur, .1)); e = eio(p); bh, bw = s.base.shape[:2]
        sb = 1 / 1.28 * (1.0 + dolly * .55 * e); sf = 1 / 1.28 * (1.0 + dolly * 1.25 * e); dx = drift[0] * (e - .5) * 46; dy = drift[1] * (e - .5) * 30
        cxn = lerp(pan[0], pan[1], e) * bw; cyn = s.fy * bh
        def M(scale, ddx, ddy):
            cx = float(np.clip(cxn, W / 2 / scale, bw - W / 2 / scale)); cy = float(np.clip(cyn, H / 2 / scale, bh - H / 2 / scale)); return np.float32([[scale, 0, W / 2 - cx * scale + ddx], [0, scale, H / 2 - cy * scale + ddy]])
        out = cv2.warpAffine(s.bg, M(sb, -dx * .55, -dy * .55), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        if s.has:
            fgi = cv2.warpAffine(s.base, M(sf, dx, dy), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT); m = cv2.warpAffine(s.fgm, M(sf, dx, dy), (W, H), flags=cv2.INTER_LINEAR)
            m = cv2.GaussianBlur(m, (0, 0), 1.2)[..., None]; out = (out.astype(np.float32) * (1 - m) + fgi.astype(np.float32) * m).astype(np.uint8)
        return out
def photo(key, **k):
    kk = (key, tuple(sorted(k.items())))
    if kk not in _PH: _PH[kk] = Photo(key, **k)
    return _PH[kk]
def particles(f, t, n=26, seed=3, a=.55, size=(1, 3), speed=14):
    r = np.random.RandomState(seed)
    for i in range(n):
        x0, y0, ph, sz = r.rand() * W, r.rand() * H, r.rand() * 6.28, r.uniform(*size); x = (x0 + t * speed * (.5 + r.rand()) + math.sin(t * .6 + ph) * 18) % W; y = (y0 - t * speed * (.6 + r.rand()) * .6) % H
        tw = .5 + .5 * math.sin(t * 1.4 + ph); cv2.circle(f, (int(x), int(y)), int(max(sz, 1)), (int(220 * a * tw + 20), int(230 * a * tw + 20), int(240 * a * tw + 20)), -1, cv2.LINE_AA)

# ------------------------------------------------------------------ transitions (designed, not preset)
def _noise_edge(n, seed, amp, scale):
    r = np.random.RandomState(seed); x = np.cumsum(r.randn(n)); x -= np.linspace(x[0], x[-1], n); x = cv2.GaussianBlur(x.reshape(1, -1).astype(np.float32), (0, 0), scale)[0]; x /= np.abs(x).max() + 1e-6
    fine = cv2.GaussianBlur(r.randn(1, n).astype(np.float32), (0, 0), 1.5)[0] * .25; return (x + fine) * amp
def tr_tear(a, b, p, seed=2):
    """paper-tear wipe: next scene revealed behind a torn paper edge sweeping across; edge keeps paper fibres."""
    p = eio(p); edge = _noise_edge(W, seed, 55, 18); yline = (-90 + p * (H + 180) + edge).astype(np.float32)
    yy = np.arange(H, dtype=np.float32)[:, None]; sdist = yy - yline[None, :]       # <0 -> revealed (b above), >0 still a
    out = np.where(sdist[..., None] < 0, b, a).astype(np.float32)
    band = np.clip(1 - np.abs(sdist + 14) / 22, 0, 1); pap = paper_tex().astype(np.float32); rim = ((sdist > -26) & (sdist < 0)).astype(np.float32)
    out = out * (1 - rim[..., None] * .96) + pap * rim[..., None] * .96
    sh = np.clip(1 - np.maximum(sdist, 0) / 60, 0, 1) * (sdist > 0) * .5; out *= (1 - sh[..., None])
    return np.clip(out, 0, 255).astype(np.uint8)
def tr_burn(a, b, p):
    """film-burn: warm overexposure blooms, scene swaps at the peak."""
    w = np.sin(np.pi * clamp(p)) ; base = a if p < .5 else b; f = base.astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); cx = W * (.2 + .6 * p); d = np.sqrt(((xx - cx) / W) ** 2 + ((yy - H * (.3 + .4 * p)) / H) ** 2); m = np.clip(1 - d * 1.35, 0, 1) ** 1.6 * w
    f = f * (1 - .18 * w) + (m[..., None] * np.array([40, 130, 255], np.float32) * .85) + w ** 2 * 38 * np.array([.5, .8, 1], np.float32)
    return np.clip(f, 0, 255).astype(np.uint8)
def tr_expand(a, b, p):
    """the next scene grows out of a framed window in the centre (white mat border), previous scene dims."""
    e = eio(p); w0, h0 = 300, 420; ww = lerp(w0, W + 20, e); hh = lerp(h0, H + 20, e); x0, y0 = int(W / 2 - ww / 2), int(H / 2 - hh / 2); out = (a.astype(np.float32) * (1 - .5 * min(1, p * 2.2))).astype(np.uint8)
    if p < .98:
        shadow_rect(out, x0, y0, x0 + ww, y0 + hh, .55, 30, 16); bw = int(lerp(10, 0, clamp((p - .6) / .4))); X0, Y0, X1, Y1 = max(x0, 0), max(y0, 0), min(int(x0 + ww), W), min(int(y0 + hh), H)
        out[Y0:Y1, X0:X1] = 240; ix0, iy0, ix1, iy1 = X0 + bw, Y0 + bw, X1 - bw, Y1 - bw
        if ix1 > ix0 and iy1 > iy0:
            sc = max(ww / W, hh / H); sub = cv2.resize(b, (max(int(W * sc), 1), max(int(H * sc), 1)), interpolation=cv2.INTER_LINEAR); sy0 = (sub.shape[0] - (iy1 - iy0)) // 2; sx0 = (sub.shape[1] - (ix1 - ix0)) // 2
            out[iy0:iy1, ix0:ix1] = sub[sy0:sy0 + (iy1 - iy0), sx0:sx0 + (ix1 - ix0)]
    else: out = b
    return out
def tr_slide(a, b, p):
    """editorial slide-up with motion blur; previous scene drifts up slower for depth."""
    e = eio(p); oy = int(e * H); fa = np.roll(a, -int(e * H * .25), 0); out = fa.copy(); nb = b
    blur = int(abs(math.sin(math.pi * p)) * 22) * 2 + 1
    if blur > 1: nb = cv2.blur(b, (1, blur))
    out[: H - oy + 0] = fa[: H - oy] if oy < H else out[:0]
    if oy > 0: out[H - oy:] = nb[:oy]
    ln = H - oy
    if 0 < ln < H: cv2.line(out, (0, ln), (W, ln), (255, 255, 255), 2, cv2.LINE_AA)
    return out
def tr_dip(a, b, p):
    w = abs(2 * p - 1) if True else 0; base = a if p < .5 else b; return (base.astype(np.float32) * (w ** 1.3 * .9 + .1 * w)).astype(np.uint8)
TR = {'burn': tr_burn, 'tear': tr_tear, 'expand': tr_expand, 'slide': tr_slide, 'dip': tr_dip}
TRD = {'burn': .55, 'tear': .6, 'expand': .6, 'slide': .5, 'dip': .5, 'cut': 0.0}

# ------------------------------------------------------------------ the timeline compositor
class Edit:
    """segs: list of dict(t0,t1,scene=callable(u,dur,k)->frame, tr=kind-in)"""
    def __init__(s, segs, fnscene): s.segs = segs; s.fn = fnscene
    def seg_frame(s, i, t, k):
        sg = s.segs[i]; return s.fn(sg, t - sg['t0'], sg['t1'] - sg['t0'], k)
    def frame(s, k):
        t = k / FPS; idx = 0
        for i, sg in enumerate(s.segs):
            if sg['t0'] <= t + 1e-6: idx = i
        sg = s.segs[idx]; kind = sg.get('tr', 'cut'); d = TRD.get(kind, 0)
        if idx > 0 and kind != 'cut' and t < sg['t0'] + d:
            p = (t - sg['t0']) / d; a = s.seg_frame(idx - 1, t, k); b = s.seg_frame(idx, t, k); return TR[kind](a, b, p)
        return s.seg_frame(idx, t, k)

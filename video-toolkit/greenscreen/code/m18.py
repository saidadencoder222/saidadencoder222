import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad/c5')
from mrun import *
import cscenes as C
S3.setup(17, WHITE); S = S3.STATE
if not any(w[0] == 'you' and 37.8 < w[1] < 38.2 for w in S['words']): S['words'].append(('you', 37.98, 38.18)); S['words'].sort(key=lambda w: w[1])
VDUR = S['VDUR']; DUR = VDUR + .4; NF = int(round(DUR * 30)); AMB = (70, 160, 255); IMGD = C.IMG; import os; WM = IMGD.replace('/img', '/wm'); HD = IMGD.replace('/img', '/hd')
# four images behind him at all times; every idea swaps the set.  ('i', still) | ('v', footage clip)
BEATS = [
 # hook: the actor, a black hole, psychology, content improvement
 dict(t0=0.0, t1=7.9, cells=[('i', 'u17'), ('i', 'u19'), ('i', 'psych_art'), ('i', 'grow_art')], s=.58, hook=True),
 dict(t0=7.9, t1=11.95, cells=[('i', 'u18'), ('i', 'galaxy_0'), ('i', 'u20'), ('i', 'pil_0')], s=.6),                    # "not about space"
 dict(t0=11.95, t1=18.0, cells=[('i', 'u16'), ('i', 'bluemarble_0'), ('i', 'fam_1'), ('v', 'b5')], s=.56),               # father, daughter, distance
 dict(t0=18.0, t1=22.3, cells=[('i', 'u17'), ('i', 'night_0'), ('i', 'fam_0'), ('i', 'earthrise_1')], s=.58),            # the connection
 dict(t0=22.3, t1=27.4, cells=[('i', 'psych_art'), ('i', 'actor_0'), ('i', 'fam_1'), ('i', 'u16')], s=.58),                # your story: people
 dict(t0=27.4, t1=34.5, cells=[('v', 'b7'), ('i', 'u20'), ('i', 'u19'), ('i', 'iss_1')], s=.58),             # style, light, cinematography
 dict(t0=34.5, t1=40.7, cells=[('i', 'neb_0'), ('i', 'u18'), ('i', 'grow_art'), ('i', 'orion_0')], s=.58),   # recognition
 dict(t0=40.7, t1=VDUR + .4, cells=[('i', 'u19'), ('v', 'b1'), ('i', 'u16'), ('i', 'bluemarble_1')], s=.62),
]
HOOK_TITLE = ["THE PSYCHOLOGY BEHIND", "WHY INTERSTELLAR IS", "THE BEST FILM YOU'VE SEEN"]
PUNCH = [1.4, 5.7, 10.96, 13.61, 15.19, 17.8, 19.88, 27.2, 29.63, 31.23, 33.65, 36.41, 37.21, 42.03]
def pulse(t):
    z = 0.0
    for tp in PUNCH:
        d = t - tp
        if 0 <= d < .5: z += .07 * (1 - eo(d / .45)) if d > .06 else .07 * (d / .06)
    return z
def beat_at(t):
    for i, b in enumerate(BEATS):
        if b['t0'] <= t < b['t1']: return i
    return len(BEATS) - 1
_IM = {}
def _load(key):
    for opt in key.split('|'):
        for d in (WM, WM + '2', HD, IMGD):
            p = f'{d}/{opt}.jpg'
            if os.path.exists(p): return opt, cv2.imread(p)
    raise FileNotFoundError(key)
def still_cell(key, u, dur, fx=.5):
    if key not in _IM: _IM[key] = _load(key)
    name, im = _IM[key]; p = clamp(u / max(dur, .1)); e = eio(p); h, w = im.shape[:2]
    if name.startswith('u') and w / h > 0.8:                # small film still: sharp at native width over a blurred, darkened fill of itself
        s0 = max(540 / w, 960 / h); bgs = cv2.resize(im, (int(w * s0), int(h * s0)), interpolation=cv2.INTER_CUBIC); x0 = (bgs.shape[1] - 540) // 2
        bgc = cv2.GaussianBlur(bgs[:, x0:x0 + 540], (0, 0), 28); bgc = (bgc.astype(np.float32) * .55).astype(np.uint8)
        s = 540 / w * (1 + .06 * e); fw, fh = int(w * s), int(h * s); fg = cv2.resize(im, (fw, fh), interpolation=cv2.INTER_LANCZOS4); bl = cv2.GaussianBlur(fg, (0, 0), 1.0); fg = cv2.addWeighted(fg, 1.35, bl, -.35, 0)
        out = bgc.copy(); y0 = 480 - fh // 2 + int(lerp(10, -10, e)); xs = max((fw - 540) // 2, 0); fgc = fg[:, xs:xs + 540]; yy0, yy1 = max(y0, 0), min(y0 + fh, 960)
        out[yy0:yy1, :fgc.shape[1]] = fgc[yy0 - y0:yy1 - y0]; return out
    s = max(540 / w, 960 / h) * (1 + .1 * e); bw, bh = w * s, h * s
    cx = float(np.clip(lerp(fx - .08, fx + .08, e) * bw, 270, bw - 270)); M = np.float32([[s, 0, 270 - cx], [0, s, 480 - bh / 2]]); return cv2.warpAffine(im, M, (540, 960), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
def unify(im):
    a = im.astype(np.float32) / 255; g = a.mean(2, keepdims=True); a = g + (a - g) * .82; a = a * .94 + .02; a[..., 2] *= 1.02; a[..., 0] *= 1.03
    h, w = a.shape[:2]; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); v = 1 - .35 * (((xx - w / 2) / (w * .75)) ** 2 + ((yy - h / 2) / (h * .75)) ** 2); return (np.clip(a * v[..., None], 0, 1) * 255).astype(np.uint8)
def cell_img(cell, u, dur, j):
    kind, key = cell
    if kind == 'v': return unify(cv2.resize(C.bg_video(key, u, dur, (.5, .5), .08), (540, 960), interpolation=cv2.INTER_AREA))
    return unify(C.cgrade(still_cell(key, u, dur, .35 + .1 * j)))
def grid(b, t, prev=None):
    u = t - b['t0']; dur = b['t1'] - b['t0']; g = np.zeros((H, W, 3), np.uint8)
    for j, cell in enumerate(b['cells']):
        x0, y0 = (j % 2) * 540, (j // 2) * 960; im = cell_img(cell, u, dur, j)
        if prev is not None and u < .45 + j * .06:                       # each quadrant swaps in turn with a short flash, so the change reads as designed
            p = eio(clamp(u / (.45 + j * .06))); old = cell_img(prev['cells'][j], t - prev['t0'], prev['t1'] - prev['t0'], j); im = cv2.addWeighted(old, 1 - p, im, p, 0); im = np.clip(im.astype(np.float32) + 26 * math.sin(math.pi * p), 0, 255).astype(np.uint8)
        g[y0:y0 + 960, x0:x0 + 540] = im
    cv2.line(g, (540, 0), (540, H), (0, 0, 0), 3); cv2.line(g, (0, 960), (W, 960), (0, 0, 0), 3)
    return g
def hook_title(f, t):
    """same title treatment as the 'recreating a viral edit' video: Anton, off-white, small line / big line / small line, rise + scale-in"""
    if t > 6.6: return 150
    fade = eo((6.6 - t) / .5) if t > 6.1 else 1.0
    spec = [("THE PSYCHOLOGY BEHIND", 84, 150, .05), ("WHY INTERSTELLAR IS", 150, 262, .25), ("THE BEST FILM YOU'VE SEEN", 84, 372, .45)]
    for ln, sz, y, dl in spec:
        a = eo((t - dl) / .45) * fade; zz = fit(ln, 'anton', int(sz * lerp(1.14, 1.0, eo((t - dl) / .8))), 960, 2); m_ = tex(ln, 'anton', zz, 2)
        put(f, m_, 540, y + (1 - a) * 28, (0, 0, 0), a * .35, blur=10, dy=8); put(f, m_, 540, y + (1 - a) * 28, OFF, a)
    return 372
def frame(k):
    t = k / FPS; i = beat_at(t); b = BEATS[i]; f = grid(b, t, BEATS[i - 1] if i > 0 else None)
    f = (f.astype(np.float32) * .86).astype(np.uint8); hook_title(f, t)
    s = b['s'] + pulse(t)
    if i > 0 and t < b['t0'] + .35: s = lerp(BEATS[i - 1]['s'], b['s'], eio((t - b['t0']) / .35)) + pulse(t)
    dy = -497 * (s / .56) + (1 - s / .56) * 0 if False else (840 - (s * 880 + (1 - s) * 1920))
    fr, a = C.person_layer(S, k, s, 0, dy); bottom = 1920 + dy; yy = np.arange(H, dtype=np.float32)[:, None]; a = a * np.clip((bottom - yy) / 150, 0, 1)
    f = C.composite(f, fr, a)
    g = np.clip((np.arange(H, dtype=np.float32) - 1380) / 540, 0, 1)[:, None, None] * .5; f = (f.astype(np.float32) * (1 - g)).astype(np.uint8)
    captions(f, t, S['words'], 1600, 58)
    return cv2.addWeighted(f, .88, cv2.multiply(f, doc.vig(), scale=1 / 255), .12, 0)
_chunk = chunk_writer(frame)
def preview(ts, out): cv2.imwrite(out, np.hstack([cv2.resize(frame(int(t * FPS)), (270, 480)) for t in ts]))

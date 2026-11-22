"""/brand: the user's visual identity, copied from the inspo reel ("Grow to 50,000 using copywriting secrets").
Acid-yellow (RGB 242,244,16) + white on the real, unretouched room. Three typefaces: condensed serif (Instrument Serif) for the hero word, tight bold grotesk (Inter 700, tracking -3%) for captions, serif italic for accent words.
Captions are a single stream: plain white at the top of the frame, WHITE PILL with black text when an image is on screen; key words turn acid yellow. Images are unframed (paper/ads/screens/stock), a little rotated, no border, instant cut."""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import simple                                    # sets up the shared font dir
from simple import *
FDIR = simple.C2 + '/fonts'
YEL = (16, 244, 242); WH = (255, 255, 255); BLK = (10, 10, 10)          # BGR
FONTS = {'serif': 'InstrumentSerif-Regular.ttf', 'serifi': 'InstrumentSerif-Italic.ttf', 'sans': 'Inter.ttf'}
_F = {}
def pf(kind, size, w=700):
    k = (kind, size, w)
    if k not in _F:
        f = ImageFont.truetype(f'{FDIR}/{FONTS[kind]}', size)
        if kind == 'sans':
            try: f.set_variation_by_axes([14 if 'opsz' in (a['name'].decode() if isinstance(a['name'], bytes) else a['name']).lower() else w for a in f.get_variation_axes()][:1] + [w])
            except Exception:
                try: f.set_variation_by_axes([w])
                except Exception: pass
        _F[k] = f
    return _F[k]
_M = {}
def tm(s, kind, size, w=700, track=0.0, cx=1.0):
    """fixed-baseline text mask: (mask, advance_width). Same baseline for every word, so mixed colours/sizes line up."""
    key = (s, kind, size, w, track, cx)
    if key in _M: return _M[key]
    f = pf(kind, size, w); PADX = 24; H = int(size * 1.7); base = int(size * 1.2)
    adv = f.getlength(s) + track * max(len(s) - 1, 0)
    im = Image.new('L', (int(adv) + 2 * PADX + 4, H), 0); d = ImageDraw.Draw(im)
    if track == 0: d.text((PADX, base), s, font=f, fill=255, anchor='ls')
    else:
        x = PADX
        for c in s: d.text((x, base), c, font=f, fill=255, anchor='ls'); x += f.getlength(c) + track
    m = np.asarray(im, np.float32) / 255
    if cx != 1.0: m = cv2.resize(m, (max(int(m.shape[1] * cx), 4), m.shape[0]), interpolation=cv2.INTER_AREA); adv = adv * cx; PADX = PADX * cx
    _M[key] = (m, adv, base, PADX); return _M[key]
def blit(f, m, x, base_y, base, color, a=1.0, blur=0., dy=0, add=False, sc=1.0):
    if a <= .003: return
    if sc != 1: m = cv2.resize(m, None, fx=sc, fy=sc, interpolation=cv2.INTER_LINEAR); base = base * sc
    if blur > .3: m = cv2.GaussianBlur(m, (0, 0), blur)
    h, w = m.shape; x0 = int(round(x)); y0 = int(round(base_y - base + dy))
    X0, Y0 = max(x0, 0), max(y0, 0); X1, Y1 = min(x0 + w, 1080), min(y0 + h, f.shape[0])
    if X0 >= X1 or Y0 >= Y1: return
    mm = (m[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * a)[..., None]; roi = f[Y0:Y1, X0:X1].astype(np.float32); col = np.array(color, np.float32)
    roi = roi + col * mm if add else roi * (1 - mm) + col * mm; f[Y0:Y1, X0:X1] = np.clip(roi, 0, 255).astype(np.uint8)
def fit(kind, texts, size, maxw, w=700, track_k=-.03, cx=1.0):
    while sum(tm(t, kind, size, w, track_k * size, cx)[1] for t in texts) > maxw and size > 24: size -= 2
    return size
# ------------------------------------------------------------------------------------------------------------------ captions
def caption(f, words, y, hi=(), pill=False, a=1.0, size=64):
    """one caption chunk. words = list of strings; hi = indices turned acid yellow. y = baseline row."""
    tr = -.03 * size
    def width(sz): return sum(tm(w, 'sans', sz, 700, -.03 * sz)[1] for w in words) + .27 * sz * (len(words) - 1)
    while width(size) > 940 and size > 30: size -= 2
    tr = -.03 * size; sp = .27 * size; total = width(size); x = 540 - total / 2
    if pill:
        pad = size * .26; top = y - size * .98; bot = y + size * .36
        ov = f.copy(); cv2.rectangle(ov, (int(x - pad - 6), int(top)), (int(x + total + pad + 6), int(bot)), (255, 255, 255), -1, cv2.LINE_AA)
        f[:] = cv2.addWeighted(ov, a, f, 1 - a, 0)
    for i, wd in enumerate(words):
        m, adv, base, PADX = tm(wd, 'sans', size, 700, tr)
        if pill: blit(f, m, x - PADX, y, base, BLK, a)
        else:
            blit(f, m, x - PADX, y, base, (0, 0, 0), a * .38, blur=7, dy=4)
            blit(f, m, x - PADX, y, base, YEL if i in hi else WH, a)
        x += adv + sp
# ------------------------------------------------------------------------------------------------------------------ hero title (neon-yellow condensed serif + small white caps)
def title(f, big, sub, y=420, a=1.0, maxw=900):
    sz = fit('serif', [big], 300, maxw, 400, -.02, .78); m, adv, base, PADX = tm(big, 'serif', sz, 400, -.02 * sz, .78); x = 540 - adv / 2 - PADX
    blit(f, m, x, y, base, YEL, a * .85, blur=14, add=True); blit(f, m, x, y, base, YEL, a * .5, blur=5, add=True)       # neon glow
    blit(f, m, x, y, base, (200, 250, 250), a)                                                                         # hot core
    blit(f, m, x, y, base, YEL, a * .9)
    ss = fit('sans', [sub], 44, maxw - 60, 600, 0.0); tr = .09 * ss; m2, adv2, base2, PADX2 = tm(sub, 'sans', ss, 600, tr); x2 = 540 - adv2 / 2 - PADX2
    blit(f, m2, x2, y + 82, base2, (70, 70, 255), a * .6, blur=7, add=True); blit(f, m2, x2, y + 82, base2, WH, a)
# ------------------------------------------------------------------------------------------------------------------ typographic caption stack (hero word / white line / italic accent)
def stack(f, big, line, accent, y=360, a=1.0, size=140):
    sz = fit('serif', [big], size, 900, 400, -.015, .8); m, adv, base, PADX = tm(big, 'serif', sz, 400, -.015 * sz, .8)
    blit(f, m, 540 - adv / 2 - PADX, y, base, (0, 0, 0), a * .3, blur=9, dy=6); blit(f, m, 540 - adv / 2 - PADX, y, base, YEL, a)
    if line:
        ls = fit('sans', [line], 56, 940, 700, -.03); m2, adv2, base2, P2 = tm(line, 'sans', ls, 700, -.03 * ls)
        blit(f, m2, 540 - adv2 / 2 - P2, y + 92, base2, (0, 0, 0), a * .38, blur=7, dy=4); blit(f, m2, 540 - adv2 / 2 - P2, y + 92, base2, WH, a)
    if accent:
        as_ = fit('serifi', [accent], 70, 700, 400, 0); m3, adv3, base3, P3 = tm(accent, 'serifi', as_, 400, 0)
        cx3 = min(800, 1040 - adv3 / 2); blit(f, m3, cx3 - adv3 / 2 - P3, y + 172, base3, (0, 0, 0), a * .38, blur=7, dy=4); blit(f, m3, cx3 - adv3 / 2 - P3, y + 172, base3, WH, a)
# ------------------------------------------------------------------------------------------------------------------ images: unframed, slightly rotated, instant
def paper(f, img, cx, cy, w, rot=0.0, shadow=.28):
    h = int(img.shape[0] * w / img.shape[1]); r = cv2.resize(img, (int(w), h), interpolation=cv2.INTER_AREA if w < img.shape[1] else cv2.INTER_CUBIC)
    rgba = np.dstack([r[..., :3], np.full((h, int(w)), 255, np.uint8)])
    M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, 1.0); cw = int(abs(w * math.cos(math.radians(rot))) + abs(h * math.sin(math.radians(rot)))) + 4; ch = int(abs(h * math.cos(math.radians(rot))) + abs(w * math.sin(math.radians(rot)))) + 4
    M[0, 2] += (cw - w) / 2; M[1, 2] += (ch - h) / 2; c = cv2.warpAffine(rgba, M, (cw, ch), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    x0, y0 = int(cx - cw / 2), int(cy - ch / 2); X0, Y0, X1, Y1 = max(x0, 0), max(y0, 0), min(x0 + cw, 1080), min(y0 + ch, f.shape[0])
    if X0 >= X1 or Y0 >= Y1: return
    sub = c[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]; a = sub[..., 3:4].astype(np.float32) / 255
    sh = cv2.GaussianBlur(a[..., 0], (0, 0), 10)[..., None] * shadow; roi = f[Y0:Y1, X0:X1].astype(np.float32) * (1 - np.roll(sh, 8, 0))
    f[Y0:Y1, X0:X1] = np.clip(roi * (1 - a) + sub[..., :3].astype(np.float32) * a, 0, 255).astype(np.uint8)
# ------------------------------------------------------------------------------------------------------------------ grade (warm, clean, high quality; background stays the real room)
def grade_brand(raw):
    import grade51 as G
    f = G.warm_grade(raw).astype(np.float32) / 255
    lum = (f[..., 0] * .114 + f[..., 1] * .587 + f[..., 2] * .299)[..., None]
    bl = cv2.GaussianBlur(np.clip(f - .7, 0, 1) * 3.0, (0, 0), 20); f = 1 - (1 - f) * (1 - bl * .18)                    # soft highlight bloom
    f = f * np.array([.985, 1.0, 1.03], np.float32)                                                                       # a touch warmer
    f = np.power(np.clip(f, 0, 1), .94)                                                                                   # skin and room a little brighter
    H, W = f.shape[:2]; yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); d = ((xx - W / 2) / (W * .8)) ** 2 + ((yy - H * .5) / (H * .75)) ** 2
    f = f * (1 - .10 * np.clip(d, 0, 1))[..., None]
    return np.clip(f * 255, 0, 255).astype(np.uint8)
# ------------------------------------------------------------------------------------------------------------------ framing: speaker lower in frame with headroom (like the inspo)
def frame_speaker(fr, S=.9, zoom=1.0):
    """scale the footage a little (anchored bottom-centre) so there is headroom for the title / images; the thin side strips continue the real wall (edge replicate, softened) and the top continues the wall tone"""
    h, w = fr.shape[:2]; sc = cv2.resize(fr, (int(w * S), int(h * S)), interpolation=cv2.INTER_AREA); sh, sw = sc.shape[:2]; x0 = (1080 - sw) // 2; y0 = 1920 - sh
    can = np.zeros((1920, 1080, 3), np.uint8); can[y0:, x0:x0 + sw] = sc
    L = cv2.GaussianBlur(np.repeat(sc[:, :1], x0, 1), (0, 0), 6); can[y0:, :x0] = L; rw = 1080 - x0 - sw; R = cv2.GaussianBlur(np.repeat(sc[:, -1:], rw, 1), (0, 0), 6); can[y0:, x0 + sw:] = R
    row = cv2.GaussianBlur(can[y0 + 4:y0 + 30].mean(0, keepdims=True), (0, 0), 50); can[:y0] = np.repeat(row, y0, 0).astype(np.uint8)
    if zoom != 1.0: can = cv2.warpAffine(can, np.float32([[zoom, 0, 540 - zoom * 540], [0, zoom, 1500 - zoom * 1500]]), (1080, 1920), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return can

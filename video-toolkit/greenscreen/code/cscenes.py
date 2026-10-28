"""Green-screen style movie-commentary scenes (vid 17): user's matte over full-screen NASA imagery + custom graphics."""
from mscenes import *
import bscenes as B
IMG = '/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad/c15/img'
import mst
mst.ART = IMG
_STARS = None
def stars(f, t, n=70, seed=2, a=.8):
    r = np.random.RandomState(seed)
    for i in range(n):
        x0, y0, sp, sz = r.rand() * W, r.rand() * H, .2 + r.rand() * .8, r.uniform(.8, 2.6)
        x = (x0 - t * 22 * sp) % W; y = (y0 + math.sin(t * .3 + i) * 6) % H; tw = .55 + .45 * math.sin(t * (1 + sp) + i)
        c = int(255 * a * tw); cv2.circle(f, (int(x), int(y)), int(max(sz * sp * 1.1, 1)), (c, c, c), -1, cv2.LINE_AA)
def cgrade(f):
    a = f.astype(np.float32) / 255; a = a * a * (3 - 2 * a) * .22 + a * .78
    a[..., 0] += .012; return (np.clip(a, 0, 1) * 255).astype(np.uint8)
_ph = {}
def bg_frame(key, u, dur, pan=(.5, .5), fy=.5, dolly=.1, dark=.0, zoom_out=False):
    k_ = (key, fy)
    if k_ not in _ph: _ph[k_] = mst.Photo(key, fy=fy, tone='color', sep=False)
    f = _ph[k_].render((dur - u) if zoom_out else u, dur, pan=pan, dolly=dolly, drift=(1, 0))
    f = cgrade(f)
    if dark > 0: f = (f.astype(np.float32) * (1 - dark)).astype(np.uint8)
    return f
# ---------------------------------------------------------------- person cut-out compositing
def person_layer(S, k, scale, dx, dy=0):
    i = min(k, int((S['VDUR'] - .2) * FPS)) + 1; raw = cv2.imread(f"{C5}/work/fd{S['vid']}/{i:04d}.jpg"); fr = B.look(raw)
    al = alpha_arr(S['vid']); a = cv2.resize(np.array(al[min(k, len(al) - 1)]), (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255
    M = np.float32([[scale, 0, (1 - scale) * 540 + dx], [0, scale, (1 - scale) * 1920 + dy]])
    hsv = cv2.cvtColor(fr, cv2.COLOR_BGR2HSV).astype(np.float32); hsv[..., 1] *= .86; fr = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
    fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE); a = cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_LINEAR)
    a = np.clip((a - .06) / .88, 0, 1); a = cv2.GaussianBlur(a, (0, 0), 1.1); return fr, a
def composite(bg, fr, a, rim=True):
    shd = cv2.GaussianBlur(np.roll(np.roll(a, 18, 0), 8, 1), (0, 0), 26)[..., None]; bg = (bg.astype(np.float32) * (1 - shd * .38))
    A = a[..., None]; frf = fr.astype(np.float32)
    if rim:
        edge = np.clip(a - cv2.erode(a, np.ones((9, 9), np.uint8)), 0, 1); edge = cv2.GaussianBlur(edge, (0, 0), 3)[..., None]; spill = cv2.GaussianBlur(bg, (0, 0), 40)
        frf = frf * (1 - edge * .35) + spill * edge * .55 + edge * np.array([40, 30, 25], np.float32)
    return np.clip(bg * (1 - A) + frf * A, 0, 255).astype(np.uint8)
# ---------------------------------------------------------------- captions: Poppins supporting text, Anton + amber for the key words
KEY = {'interstellar', 'greatest', 'personal', 'brand', '60', 'seconds', 'space', 'storytelling', 'father', "father's", 'daughter', 'connection', 'emotion', 'story', 'content', 'style', 'cinematography', 'editing', 'light',
       'recognition', 'fonts', 'slapped', 'takeaway', 'follow', 'buy', 'blow'}
def cap_groups(words):
    gs = []; cur = []
    for w in words:
        if cur and (w[1] - cur[-1][2] > .35 or len(cur) >= 4): gs.append(cur); cur = []
        cur.append(w)
        if w[0][-1] in '.?!,': gs.append(cur); cur = []
    if cur: gs.append(cur)
    return gs
_CG = {}
def cinecaps(f, t, words, y=1545):
    key = id(words)
    if key not in _CG: _CG[key] = cap_groups(words)
    for g in _CG[key]:
        a0 = g[0][1] - .03; a1 = g[-1][2] + .2
        if a0 <= t < a1:
            toks = [(w[0].strip('.,?!').lower(), w[0].strip('.,?!').lower() in KEY) for w in g]; sz_n, sz_k = 54, 62
            def wd(tok, k): return twidth(tok.upper() if k else tok, 'psb' if k else 'psb', sz_k if k else sz_n, 1 if k else 0)
            gap = 18; tot = sum(wd(tk, k) for tk, k in toks) + gap * (len(toks) - 1)
            if tot > 960: sc_ = 960 / tot
            else: sc_ = 1.0
            ap = clamp((t - a0) / .12); pop = 1 + .14 * (1 - eo((t - a0) / .16)); fade = clamp((a1 - t) / .12) * ap
            x = 540 - tot * sc_ / 2
            for tk, kk in toks:
                w_ = wd(tk, kk) * sc_; cx = x + w_ / 2
                m = tex(tk.upper() if kk else tk, 'psb' if kk else 'psb', int((sz_k if kk else sz_n) * sc_), 1 if kk else 0); yy = y + (4 if kk else 0)
                put(f, m, cx, yy, (0, 0, 0), fade * .55, sc=pop, blur=9, dy=5); put(f, m, cx, yy, (70, 160, 255) if kk else (255, 255, 255), fade, sc=pop)
                x += w_ + gap * sc_
            return
# ---------------------------------------------------------------- custom graphics
def thread_graphic(f, t, u, mode, y=300):
    """father <-> daughter: thread between two nodes. mode: 'near' | 'far' (father drifts away) | 'break' (thread loses connection)"""
    y = int(y); xl, xr = 150, 930; a = eo(u / .6)
    if mode == 'far': xr = int(lerp(930, 1010, eo(u / 2.5))); xl = int(lerp(150, 110, eo(u / 2.5)))
    pts = []
    for i in range(41):
        q = i / 40; x = xl + (xr - xl) * q; amp = 18 * math.sin(math.pi * q) * (1 if mode != 'far' else 1.4 + u * .5); pts.append((int(x), int(y + math.sin(q * 9 + t * 4) * amp)))
    if mode == 'break':
        br = eo((u - .6) / .6); cut = 20
        for i in range(0, 40):
            if (i + int(t * 6)) % 3 == 0 and br > .3: continue
            cv2.line(f, pts[i], pts[i + 1], (255, 255, 255) if i < 16 or i > 24 else (120, 120, 120), 3 if i < 16 or i > 24 else 1, cv2.LINE_AA)
    else:
        cv2.polylines(f, [np.array(pts)], False, (255, 255, 255), 3, cv2.LINE_AA)
    for (x, lab) in ((xl, 'DAUGHTER'), (xr, 'FATHER')):
        glow(f, x, y, 70, (70, 160, 255), .55 * a); cv2.circle(f, (x, y), 15, (70, 160, 255), -1, cv2.LINE_AA); cv2.circle(f, (x, y), 15, (255, 255, 255), 3, cv2.LINE_AA)
        T(f, lab, 'monob', 26, x, y + 52, (255, 255, 255), a, 4, .6)
FONTS = ['psb', 'serifb', 'psb', 'psb', 'bebas', 'serifi', 'lib', 'pb']
def font_collage(f, t, u, snap_at=3.3):
    """mismatched fonts everywhere ("slapped together") -> snap into one consistent style"""
    r = np.random.RandomState(4); sn = eo((u - snap_at) / .6)
    for i in range(14):
        nm = FONTS[i % len(FONTS)]; txt = ('CONTENT', 'STORY', 'BRAND', 'VIRAL', 'HOOK', 'FOLLOW', 'EDIT')[i % 7]
        x0, y0 = 100 + r.rand() * 880, 260 + r.rand() * 1000; ang = (r.rand() - .5) * 40; sz = int(60 + r.rand() * 80)
        gx, gy = 270 + (i % 3) * 270, 420 + (i // 3) * 190
        x = lerp(x0 + math.sin(t * 1.3 + i) * 12, gx, sn); y = lerp(y0 + math.cos(t * 1.1 + i) * 12, gy, sn); a_ = eo((u - .15 - i * .05) / .3); nm2 = lerp(0, 1, sn)
        use = 'psb' if sn > .98 else nm; m = tex(txt, use, int(lerp(sz, 62, sn)), 2)
        col = lerpc((int(120 + r.rand() * 130), int(120 + r.rand() * 130), int(120 + r.rand() * 130)), (255, 255, 255), sn)
        put(f, m, x, y, (0, 0, 0), a_ * .35, blur=8, dy=5); put(f, m, x, y, col, a_ * .95, sc=1.0)
def keyword_stack(f, t, items, base_y=330, x=70):
    for (t0, txt) in items:
        a = eo((t - t0) / .35)
        if a <= 0: continue
        j = [i for i, (tt, _) in enumerate(items) if tt == t0][0]; y = base_y + j * 112 + (1 - a) * 18
        left_text(f, txt, 'psb', fit(txt, 'psb', 74, 760, 2), x, y, (255, 255, 255), a, 2, shadow=.5); hairline(f, x + 2, y + 46, x + 2 + 70 * a, 1, (70, 160, 255), 3)
def tag_pill(f, txt, t, t0, x=70, y=200, col=(70, 160, 255)):
    a = eo((t - t0) / .35)
    if a <= 0: return
    left_text(f, txt, 'psb', 30, x, y + (1 - a) * 10, col, a, 6); hairline(f, x, y + 30, x + 130 * a, 1, col, 3)

VID = '/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad/c15/vid'
import os
_NF = {}
def bg_video(name, u, dur, pan=(.5, .5), dolly=.1, dark=0.0):
    """real NASA footage (public domain) as a full-screen moving background, cover-cropped to 9:16 with a slow push and pan"""
    if name not in _NF: _NF[name] = len(os.listdir(f'{VID}/f_{name}'))
    n = _NF[name]; i = min(int(max(u, 0) * 30), n - 1) + 1; im = cv2.imread(f'{VID}/f_{name}/{i:04d}.jpg'); p = clamp(u / max(dur, .1)); e = eio(p)
    s = H / im.shape[0] * (1 + dolly * e); bw, bh = im.shape[1] * s, im.shape[0] * s; cx = lerp(pan[0], pan[1], e) * bw
    cx = float(np.clip(cx, W / 2, bw - W / 2)); M = np.float32([[s, 0, W / 2 - cx], [0, s, H / 2 - bh / 2]]); f = cv2.warpAffine(im, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    f = cgrade(f)
    if dark > 0: f = (f.astype(np.float32) * (1 - dark)).astype(np.uint8)
    return f

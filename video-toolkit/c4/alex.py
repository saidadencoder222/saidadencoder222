import sys, os, json, math, subprocess
sys.path.insert(0, '/tmp/vt/c4')
import numpy as np, cv2
import film2 as F
from film2 import (doc, W, H, FPS, clamp, sm, eo, eio, lerp, back, tex, twidth, put, text, over, kb, prep_alpha, spk, warp, burn, sink, wipe_title, label, grade, paste, OFFW, CHAR, GREY, AMBER, TEAL, STEEL)
C4 = F.C4; CUT = json.load(open(f'{C4}/work/cutA.json')); WORDS = CUT['words']; VDUR = CUT['dur']; DUR = VDUR + .9; NF = int(round(DUR * FPS))
ACC = (60, 230, 120)   # fresh green accent (BGR)
RED = (72, 64, 238)
PROF = cv2.imread(f'{C4}/raw/shot_profile.jpg'); GRID = cv2.imread(f'{C4}/raw/shot_grid.jpg')
def T(tok, occ=1):
    n = 0
    for t, a, b in WORDS:
        if t.lower().strip('.,') == tok:
            n += 1
            if n == occ: return a
    raise KeyError(tok)
def Te(tok, occ=1):
    n = 0
    for t, a, b in WORDS:
        if t.lower().strip('.,') == tok:
            n += 1
            if n == occ: return b
# ---- captions
KEYS = {'5k', '40k', '107', 'leads', 'alex', 'fitness', 'coach', 'outlier', 'five', 'copy', 'storytelling', 'lead', 'magnet', 'guide', 'dm', 'clients', 'followers', 'document'}
def groups():
    g = []; cur = []
    for w in WORDS[1:] if WORDS[0][0] == 'is' else WORDS:
        cur.append(w)
        if len(cur) >= 3 or w[0][-1] in '.,?!': g.append(cur); cur = []
    if cur: g.append(cur)
    return g
GROUPS = groups()
def captions(f, t, accent):
    for g in GROUPS:
        a0 = g[0][1] - .04; a1 = g[-1][2] + .22
        if a0 <= t < a1:
            u = clamp((t - a0) / .12); sc = lerp(1.12, 1.0, eo(u)); k = clamp((a1 - t) / .1); parts = []
            for w in g:
                tk = w[0].lower().strip('.,'); key = tk in KEYS; s = tk.upper() if key else tk
                if w[0] == '/': s = '/'
                nm, sz, col = ('anton', 112, accent) if key else ('psb', 60, OFFW); parts.append((s, nm, sz, col, twidth(s, nm, sz, 0)))
            tot = sum(p[4] for p in parts) + 26 * (len(parts) - 1)
            if tot > 960: sc *= 960 / tot
            xx = 540 - tot * sc / 2
            for s, nm, sz, col, wd in parts:
                text(f, s, nm, sz, xx + wd * sc / 2, 1560, col, k * clamp(u * 3), sc=sc, shadow=.85); xx += (wd + 26) * sc
            return
# ---- helpers
def header_card(w=1000):
    h = PROF[240:560, :]; hh = int(h.shape[0] * w / h.shape[1]); im = cv2.resize(h, (w, hh), interpolation=cv2.INTER_AREA); cv2.rectangle(im, (0, 0), (w - 1, hh - 1), (210, 210, 210), 2); return im
def chip(f, x, y, s, col, a=1.0, size=30, fg=CHAR):
    wd = twidth(s, 'pb', size, 1) + 52; sub = f[y - 34:y + 34, int(x - wd / 2):int(x + wd / 2)]
    if sub.size == 0: return
    sub[:] = (sub.astype(np.float32) * (1 - a) + np.array(col, np.float32) * a).astype(np.uint8); text(f, s, 'pb', size, x, y, fg, a, track=1)
def pulse_rect(f, x0, y0, x1, y1, col, t, t0, thick=4):
    u = clamp((t - t0) / .3)
    if u <= 0: return
    p = .5 + .5 * math.sin((t - t0) * 7); pad = int(8 + 6 * p); cv2.rectangle(f, (x0 - pad, y0 - pad), (x1 + pad, y1 + pad), col, thick, cv2.LINE_AA)
def grid_frame(t, t0, t1):
    u = (t - t0) / (t1 - t0); im = GRID[300:2220, :].copy(); z = lerp(1.0, 1.06, u); M = np.float32([[z, 0, (1 - z) * 540], [0, z, (1 - z) * 960]]); im = cv2.warpAffine(im, M, (W, H), flags=cv2.INTER_LINEAR)
    return im, z
TILES = {1: (2, 0, 7514), 2: (1, 2, 5687), 3: (1, 0, 5082), 4: (2, 1, 3819), 5: (2, 2, 3630)}   # rank -> (row, col, views)
ROWY = [(24, 656), (662, 1293), (1301, 1932)]; COLX = [(0, 358), (364, 718), (724, 1080)]
def tile_rect(rk, z):
    r, c, v = TILES[rk]; y0, y1 = ROWY[r]; x0, x1 = COLX[c]
    def tx(x): return int((x - 540) * z + 540)
    def ty(y): return int((y - 960) * z + 960)
    return tx(x0), ty(y0), tx(x1), ty(y1)
GA, GB = T('five', 1) - .25, Te('videos', 2) + .35
def interlude_grid(f, t):
    if not (GA <= t < GB): return False
    out = clamp((t - GA) / .1) * clamp((GB - t) / .12); im, z = grid_frame(t, GA, GB)
    dimm = np.ones((H, W), np.float32)
    marks = [GA + .4 + .42 * i for i in range(5)]
    sel = [rk for rk in range(1, 6) if t >= marks[rk - 1]]
    if sel:
        k = np.ones((H, W), np.float32) * .30
        for rk in sel: x0, y0, x1, y1 = tile_rect(rk, z); k[max(y0, 0):y1, max(x0, 0):x1] = 1.0
        im = (im.astype(np.float32) * k[..., None]).astype(np.uint8)
    for rk in sel:
        x0, y0, x1, y1 = tile_rect(rk, z); u = clamp((t - marks[rk - 1]) / .25); cv2.rectangle(im, (x0 + 3, y0 + 3), (x1 - 3, y1 - 3), ACC, int(6 * u + 1), cv2.LINE_AA)
        text(im, str(rk), 'anton', 190, x0 + 95, y0 + 140, ACC, u, sc=lerp(1.4, 1.0, eo(u * 1.4)), shadow=.8)
    f[:] = (f.astype(np.float32) * (1 - out) + im.astype(np.float32) * out).astype(np.uint8)
    # label + fact
    chip(f, 540, 70, "ALEX'S REELS  -  PUBLIC SCREENSHOT  -  METHOD DEMO", CHAR, out, 22, OFFW)
    if t >= marks[4] + .3:
        u = clamp((t - marks[4] - .3) / .3); text(f, 'TOP 5 BY VIEWS', 'anton', 100, 540, 1700, ACC, u * out, shadow=.9)
        text(f, '#1 = 2.1x HIS MEDIAN REEL (7,514 vs 3,630)', 'psb', 34, 540, 1790, OFFW, u * out, shadow=.9)
    return True
def doc_img():
    im = np.full((900, 640, 3), 238, np.uint8); cv2.rectangle(im, (0, 0), (639, 150), (28, 24, 24), -1)
    text(im, 'FREE GUIDE', 'anton', 92, 320, 78, ACC); text(im, 'FOR FITNESS CREATORS', 'pb', 34, 320, 205, (30, 30, 30))
    for i in range(10): cv2.rectangle(im, (60, 280 + i * 52), (580 - (i % 3) * 70, 296 + i * 52), (170, 170, 170), -1)
    cv2.rectangle(im, (60, 800), (330, 850), ACC, -1); text(im, 'GET IT FREE', 'pb', 28, 195, 826, CHAR); return im
DOCI = None
# ---- scenes
def behind(f, t):
    if 0.1 <= t < 3.4: burn(f, 'ALEX', 'anton', 360, 540, 600, (t - .15) / .9, t, ACC)
    if 4.2 <= t < 5.8:
        burn(f, '107', 'anton', 420, 540, 585, (t - 4.2) / .8, t, ACC)
        label(f, 540, 790, 'ONE OF MY CLIENTS  -  NOT ALEX\'S DATA', t, 4.7)
    if T('guide') - .15 <= t < VDUR: burn(f, 'GUIDE', 'anton', 360, 540, 600, (t - T('guide') + .15) / .8, t, ACC)
def front(f, t):
    global DOCI
    # profile header (real screenshot) 0.15 - 3.5
    if .15 <= t < 3.6:
        u = eo((t - .15) / .45); out = clamp((3.6 - t) / .25); im = header_card(); a = u * out; cy = int(lerp(-60, 245, u))
        paste(f, im, 540, cy, a, .7)
        s = 1000 / 1080; ox, oy = 40, cy - im.shape[0] // 2
        if t > .78: pulse_rect(f, int(ox + 520 * s), int(oy + (380 - 240) * s), int(ox + 680 * s), int(oy + (425 - 240) * s), ACC, t, .78)
        chip(f, 540, cy + im.shape[0] // 2 + 54, "ALEX  -  @alexaesthetics07  -  PUBLIC PROFILE", CHAR, a, 22, OFFW)
    # bio demo
    a0, a1 = T('introduce') - .1, Te('coach') + 1.0
    if a0 <= t < a1:
        out = clamp((a1 - t) / .25); u = eo((t - a0) / .4); im = header_card(840); paste(f, im, 540, 215, u * out, .6)
        chip(f, 540, 70, 'CURRENT BIO (SCREENSHOT)', CHAR, u * out, 22, OFFW)
        u2 = clamp((t - T('alex') + .05) / .35)
        if u2 > 0:
            k = eo(u2) * out; y = 505; cv2.arrowedLine(f, (540, 378), (540, 418), ACC, 5, cv2.LINE_AA, tipLength=.4) if k > .3 else None
            sub = f[y - 80:y + 80, 80:1000]; sub[:] = (sub.astype(np.float32) * (1 - .88 * k) + np.array((30, 28, 28), np.float32) * .88 * k).astype(np.uint8); cv2.rectangle(f, (80, y - 80), (1000, y + 80), ACC, 3)
            text(f, 'ALEX', 'anton', 92, 250, y - 14, OFFW, k); text(f, '/ FITNESS COACH', 'anton', 92, 650, y - 14, ACC, k)
            text(f, 'SUGGESTED  -  EXAMPLE, NOT ALEX\'S CURRENT BIO', 'psb', 22, 540, y + 56, GREY, k)
    # grid dock thumb + chip, after interlude
    b0, b1 = GB, Te('use', 1) + .9
    if b0 <= t < b1:
        out = clamp((b1 - t) / .25) * clamp((t - b0) / .2); th = cv2.resize(GRID[300:2220, :], (300, 480), interpolation=cv2.INTER_AREA).copy()
        for rk in range(1, 6):
            r, c, v = TILES[rk]; y0, y1 = ROWY[r]; x0, x1 = COLX[c]; cv2.rectangle(th, (int(x0 * .278) + 2, int(y0 * .25) + 2), (int(x1 * .278) - 2, int(y1 * .25) - 2), ACC, 3)
        paste(f, th, 190, 310, out, .6)
        s = 'FIND 5 OUTLIERS' if t < T('copy') - .1 else 'COPY THE FORMAT'
        text(f, s, 'anton', 98, 700, 250, ACC if t >= T('copy') - .1 else OFFW, out, shadow=.8)
        text(f, 'IN YOUR NICHE' if t < T('copy') - .1 else 'NOT THE FOOTAGE', 'psb', 36, 700, 330, OFFW, out * .9)
    # storytelling chain
    s0, s1 = T('storytelling') - .2, T('storytelling') + 2.4
    if s0 <= t < s1 and t < T('lead') + .6:
        out = clamp((min(s1, T('lead') + .6) - t) / .25); steps = ['HOOK', 'STRUGGLE', 'TURNING POINT', 'PAYOFF']
        chip(f, 540, 70, 'STORY STRUCTURE  -  EXAMPLE', CHAR, out, 22, OFFW)
        for i, s in enumerate(steps):
            u = clamp((t - s0 - .1 - i * .28) / .3)
            if u <= 0: continue
            y = 170 + i * 100; x = 90 + int((1 - eo(u)) * -80)
            sub = f[y - 36:y + 36, x:x + 560]; sub[:] = (sub.astype(np.float32) * (1 - .85 * u * out) + np.array((30, 28, 28), np.float32) * .85 * u * out).astype(np.uint8)
            cv2.rectangle(f, (x, y - 36), (x + 8, y + 36), ACC, -1); text(f, f'0{i + 1}', 'psb', 26, x + 50, y, ACC, u * out); text(f, s, 'bebas', 62, x + 110 + twidth(s, 'bebas', 62, 2) / 2, y + 4, OFFW, u * out, track=2)
    # lead magnet doc
    d0, d1 = T('lead', 1) - .1, T('comment') - .05
    if d0 <= t < d1:
        global DOCI
        if DOCI is None: DOCI = doc_img()
        out = clamp((d1 - t) / .3); canvas = np.zeros_like(f); doc.card_persp(canvas, DOCI, 780, 330, 330, t, d0 + .05, rot=-4.0, rise=300)
        m = (canvas.sum(2) > 0).astype(np.float32)[..., None] * out; f[:] = (f.astype(np.float32) * (1 - m) + canvas.astype(np.float32) * m).astype(np.uint8)
        text(f, 'LEAD MAGNET', 'anton', 92, 270, 220, ACC, eo((t - d0) / .3) * out, shadow=.8); text(f, 'A DOCUMENT FOR', 'psb', 34, 270, 305, OFFW, eo((t - d0 - .2) / .3) * out); text(f, 'FITNESS CREATORS', 'psb', 34, 270, 350, OFFW, eo((t - d0 - .2) / .3) * out)
    # CTA
    c0 = T('comment') - .15
    if c0 <= t < VDUR:
        u = eo((t - c0) / .35); text(f, "COMMENT 'GUIDE'", 'bebas', 110, 540, 150, OFFW, u, track=2, shadow=.8)
        if t > T('dm') - .1: text(f, 'OR DM ME', 'bebas', 110, 540, 270, ACC, eo((t - T('dm') + .1) / .3), track=2, shadow=.8)
def endcard(f, t):
    u = clamp((t - VDUR + .1) / .5)
    if u <= 0: return
    f[:] = (f.astype(np.float32) * (1 - .82 * u)).astype(np.uint8)
    items = ['POSITION: ALEX / FITNESS COACH', 'FIND 5 OUTLIER REELS', 'POST STORYTELLING CONTENT', 'OFFER A LEAD MAGNET']
    for i, s in enumerate(items):
        k = clamp(u * 2 - i * .3); y = 700 + i * 150; text(f, f'0{i + 1}', 'anton', 100, 120, y, ACC, k); text(f, s, 'bebas', 70, 190 + twidth(s, 'bebas', 70, 1) / 2 + 40, y, OFFW, k, track=1)
    text(f, 'AN UNSOLICITED BREAKDOWN  -  NOT AFFILIATED WITH ALEX', 'psb', 24, 540, 1420, GREY, clamp(u * 2 - 1))
def bg_layer(t):
    f = np.full((H, W, 3), CHAR, np.uint8); y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]; f = (f.astype(np.float32) * (1.0 + .5 * (1 - y))).astype(np.uint8)
    return f
def frame(k, fr, al):
    t = k / FPS; f = bg_layer(t); behind(f, t)
    z = 0.86
    for tp in (T('first') - .8, T('final') - .8, T('comment') - .6):
        if tp <= t < tp + .7: z = .86 * (1 + .05 * eo((t - tp) / .7))
    g = grade(fr); a = prep_alpha(al); g2, a2 = spk(g, a, z, 540, 1920, 0, 0)
    sh = cv2.GaussianBlur(a2, (0, 0), 22); f = (f.astype(np.float32) * (1 - .42 * sh[..., None])).astype(np.uint8)
    rim = np.clip(a2 - cv2.erode(a2, np.ones((9, 9), np.uint8)), 0, 1); rim = cv2.GaussianBlur(rim, (0, 0), 3)
    g2 = np.clip(g2.astype(np.float32) + rim[..., None] * np.array(ACC, np.float32) * .30, 0, 255).astype(np.uint8); f = over(f, g2, a2)
    gg = np.clip((np.arange(H, dtype=np.float32) - 1180) / 600, 0, 1)[:, None, None] * .62; f = (f.astype(np.float32) * (1 - gg)).astype(np.uint8)
    front(f, t); il = interlude_grid(f, t)
    if t < VDUR: captions(f, t, ACC)
    d = t - .1
    if 0 <= d < .24: f = cv2.addWeighted(f, 1, np.full_like(f, 255), .2 * (1 - d / .24), 0)
    if t >= VDUR - .1: endcard(f, t)
    f = cv2.multiply(f, doc.vig(), scale=1 / 255); return cv2.addWeighted(f, 1, doc.grain(k), .04, -128 * .04)
def _chunk(args):
    a, b, out = args
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', '30', '-i', '-', '-c:v', 'libx264', '-crf', '15', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for k in range(a, b):
        i = min(k, int((VDUR - .45) * FPS)) + 1
        fr = cv2.imread(f'{C4}/work/frA/{i:04d}.jpg'); al = cv2.imread(f'{C4}/work/alA/{i:04d}.png', 0)
        enc.stdin.write(np.ascontiguousarray(frame(k, fr, al)).tobytes())
    enc.stdin.close(); enc.wait(); return out
def preview(ts, out):
    tiles = []
    for t in ts:
        k = int(t * FPS); i = min(k, int((VDUR - .45) * FPS)) + 1; fr = cv2.imread(f'{C4}/work/frA/{i:04d}.jpg'); al = cv2.imread(f'{C4}/work/alA/{i:04d}.png', 0); tiles.append(cv2.resize(frame(k, fr, al), (360, 640)))
    cv2.imwrite(out, np.vstack([np.hstack(tiles[i:i + 8]) for i in range(0, len(tiles) - len(tiles) % 8, 8)]))

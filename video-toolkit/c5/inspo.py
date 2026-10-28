import sys; sys.path.insert(0, '/tmp/vt/c5')
import story3 as S3
from story3 import *
YEL = (40, 220, 255); WHT = (255, 255, 255); BLK = (10, 10, 10); GRN = (110, 220, 110)
def rr(w, h, r):
    m = np.zeros((h, w), np.float32); r = max(1, min(r, h // 2, w // 2)); cv2.rectangle(m, (r, 0), (w - r, h), 1, -1); cv2.rectangle(m, (0, r), (w, h - r), 1, -1)
    for cx, cy in ((r, r), (w - r, r), (r, h - r), (w - r, h - r)): cv2.circle(m, (cx, cy), r, 1, -1, cv2.LINE_AA)
    return cv2.GaussianBlur(m, (0, 0), .7)
def stroke_text(f, s, name, size, x, y, col, a=1.0, sc=1.0, st=6, track=0):
    m = tex(s, name, size, track)
    if a <= .01 or sc <= .02: return
    for dx, dy in ((-st, 0), (st, 0), (0, -st), (0, st), (-st * .7, -st * .7), (st * .7, -st * .7), (-st * .7, st * .7), (st * .7, st * .7)): put(f, m, x, y, (6, 6, 6), a * .96, sc, dx=dx * sc, dy=dy * sc)
    put(f, m, x, y, col, a, sc)
def fit(s, name, size, maxw):
    while twidth(s, name, size, 0) > maxw and size > 24: size -= 2
    return size
# ---------------------------------------------------------------- title (ref 4 / ref 3)
def title(f, t, t0, t1, l1, l2, c2=YEL, y=1040, s1=70, s2=100, c1=WHT):
    """Heavy sans, white small line over a larger accent line, pops in, sits at chest height, leaves before captions."""
    if not (t0 <= t < t1): return
    a_in = eo((t - t0) / .22); a_out = clamp((t1 - t) / .18); a = a_in * a_out; sc = 1 + .22 * (1 - eo((t - t0) / .3))
    z1 = fit(l1, 'poppins', s1, 960); z2 = fit(l2, 'poppins', s2, 960)
    stroke_text(f, l1, 'poppins', z1, 540, y - z2 * .5, c1, a, sc, 4); stroke_text(f, l2, 'poppins', z2, 540, y + z1 * .30, c2, a, sc, 4)
# ---------------------------------------------------------------- glass toggle rows (ref 4)
def glass(f, x0, y0, w, h, a, border=.55, r=16, dark=.52):
    x0, y0, w, h = int(x0), int(y0), int(w), int(h)
    X0, Y0, X1, Y1 = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if X0 >= X1 or Y0 >= Y1 or a <= .01: return
    roi = f[Y0:Y1, X0:X1]; bl = cv2.GaussianBlur(roi, (0, 0), 12); m = rr(w, h, r)[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0][..., None] * a
    base = (bl.astype(np.float32) * (1 - dark) + np.array((12, 12, 14), np.float32) * dark)
    f[Y0:Y1, X0:X1] = (roi.astype(np.float32) * (1 - m) + base * m).astype(np.uint8)
    e = np.clip(rr(w, h, r) - cv2.erode(rr(w, h, r), np.ones((5, 5), np.uint8)), 0, 1)[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0][..., None] * a * border
    f[Y0:Y1, X0:X1] = np.clip(f[Y0:Y1, X0:X1].astype(np.float32) * (1 - e) + 255 * e, 0, 255).astype(np.uint8)
def tiny_icon(f, kind, cx, cy, s, col=WHT):
    c = col; t = max(2, int(s * .1))
    if kind == 'person': cv2.circle(f, (cx, cy - int(s * .2)), int(s * .2), c, -1, cv2.LINE_AA); cv2.ellipse(f, (cx, cy + int(s * .35)), (int(s * .34), int(s * .28)), 0, 180, 360, c, -1, cv2.LINE_AA)
    elif kind == 'search': cv2.circle(f, (cx - 2, cy - 2), int(s * .26), c, t, cv2.LINE_AA); cv2.line(f, (cx + int(s * .18), cy + int(s * .18)), (cx + int(s * .36), cy + int(s * .36)), c, t, cv2.LINE_AA)
    elif kind == 'play': cv2.rectangle(f, (cx - int(s * .34), cy - int(s * .3)), (cx + int(s * .34), cy + int(s * .3)), c, t); cv2.fillPoly(f, [np.array([[cx - int(s * .1), cy - int(s * .14)], [cx - int(s * .1), cy + int(s * .14)], [cx + int(s * .14), cy]])], c)
    elif kind == 'check': cv2.circle(f, (cx, cy), int(s * .36), c, -1, cv2.LINE_AA); cv2.line(f, (cx - int(s * .16), cy), (cx - int(s * .03), cy + int(s * .13)), BLK, t + 1, cv2.LINE_AA); cv2.line(f, (cx - int(s * .03), cy + int(s * .13)), (cx + int(s * .18), cy - int(s * .12)), BLK, t + 1, cv2.LINE_AA)
    elif kind == 'target': cv2.circle(f, (cx, cy), int(s * .36), c, t, cv2.LINE_AA); cv2.circle(f, (cx, cy), int(s * .2), c, t, cv2.LINE_AA); cv2.circle(f, (cx, cy), int(s * .06), c, -1, cv2.LINE_AA)
    elif kind == 'book': cv2.rectangle(f, (cx - int(s * .32), cy - int(s * .28)), (cx + int(s * .32), cy + int(s * .28)), c, t); cv2.line(f, (cx, cy - int(s * .28)), (cx, cy + int(s * .28)), c, t)
    elif kind == 'doc': cv2.rectangle(f, (cx - int(s * .26), cy - int(s * .34)), (cx + int(s * .26), cy + int(s * .34)), c, t); [cv2.line(f, (cx - int(s * .14), cy - int(s * .14) + k * int(s * .16)), (cx + int(s * .14), cy - int(s * .14) + k * int(s * .16)), c, max(1, t - 1)) for k in range(3)]
    elif kind == 'mic': cv2.rectangle(f, (cx - int(s * .12), cy - int(s * .34)), (cx + int(s * .12), cy + int(s * .06)), c, t); cv2.ellipse(f, (cx, cy + int(s * .04)), (int(s * .22), int(s * .22)), 0, 0, 180, c, t); cv2.line(f, (cx, cy + int(s * .26)), (cx, cy + int(s * .38)), c, t)
    elif kind == 'dollar': cv2.circle(f, (cx, cy), int(s * .36), c, t, cv2.LINE_AA); text(f, '$', 'psb', int(s * .5), cx, cy + 1, c, 1.0)
    elif kind == 'scissors': cv2.line(f, (cx - int(s * .28), cy - int(s * .28)), (cx + int(s * .28), cy + int(s * .28)), c, t, cv2.LINE_AA); cv2.line(f, (cx + int(s * .28), cy - int(s * .28)), (cx - int(s * .28), cy + int(s * .28)), c, t, cv2.LINE_AA)
    elif kind == 'globe': cv2.circle(f, (cx, cy), int(s * .34), c, t, cv2.LINE_AA); cv2.ellipse(f, (cx, cy), (int(s * .14), int(s * .34)), 0, 0, 360, c, max(1, t - 1), cv2.LINE_AA); cv2.line(f, (cx - int(s * .34), cy), (cx + int(s * .34), cy), c, max(1, t - 1))
    elif kind == 'funnel': cv2.fillPoly(f, [np.array([[cx - int(s * .36), cy - int(s * .3)], [cx + int(s * .36), cy - int(s * .3)], [cx + int(s * .07), cy + int(s * .06)], [cx + int(s * .07), cy + int(s * .34)], [cx - int(s * .07), cy + int(s * .26)], [cx - int(s * .07), cy + int(s * .06)]])], c)
    elif kind == 'magnet': cv2.ellipse(f, (cx, cy), (int(s * .3), int(s * .3)), 0, 180, 360, c, int(s * .16)); cv2.line(f, (cx - int(s * .3), cy), (cx - int(s * .3), cy + int(s * .28)), c, int(s * .16)); cv2.line(f, (cx + int(s * .3), cy), (cx + int(s * .3), cy + int(s * .28)), c, int(s * .16))
    else: cv2.circle(f, (cx, cy), int(s * .3), c, -1, cv2.LINE_AA)
def rows(f, t, items, times, t_in, t_out, y0=1130, x0=60, w=960, h=94, gap=14, active_only=True):
    """items: [(icon, label)]; row i fades/slides in at t_in + .18*i; toggle flips on at times[i]; active row is brighter."""
    if not (t_in <= t < t_out): return
    n = len(items); out = clamp((t_out - t) / .25)
    act = -1
    for i, tt in enumerate(times):
        if t >= tt: act = i
    for i, (ic, lab) in enumerate(items):
        ti = t_in + .16 * i; a = eo((t - ti) / .3) * out
        if a <= 0: continue
        y = y0 + i * (h + gap) + int((1 - eo((t - ti) / .3)) * 22); on = t >= times[i]; isact = (i == act)
        glass(f, x0, y, w, h, a, .95, 16, .62)
        tiny_icon(f, ic, x0 + 56, y + h // 2, 50); text(f, lab, 'psb', 40, x0 + 110 + twidth(lab, 'psb', 40, 0) / 2, y + h // 2, (255, 255, 255) if (on or isact) else (205, 205, 205), a)
        sw, sh = 92, 48; sx = x0 + w - sw - 30; sy = y + (h - sh) // 2; k = eo((t - times[i]) / .25) if on else 0
        tg = rr(sw, sh, sh // 2)[..., None] * a; roi = f[sy:sy + sh, sx:sx + sw].astype(np.float32); col = np.array([lerp(110, 255, k)] * 3, np.float32)
        if roi.shape[:2] == tg.shape[:2]: f[sy:sy + sh, sx:sx + sw] = (roi * (1 - tg) + col * tg).astype(np.uint8)
        cv2.circle(f, (int(sx + 24 + (sw - 48) * k), sy + sh // 2), 18, (255, 255, 255) if k < .5 else (60, 60, 60), -1, cv2.LINE_AA)
# ---------------------------------------------------------------- yellow bracket keyword (ref 3)
def keyword(f, t, t0, t1, s, y, col=YEL, idx=0):
    if not (t0 <= t < t1): return
    u = eo((t - t0) / .3) * clamp((t1 - t) / .2); size = fit(s, 'poppins', 44, 700); wd = int(twidth(s, 'poppins', size, 1)) + 70; h = 84; x0 = 540 - wd // 2; yy = y
    g = np.zeros((H, W), np.float32); cv2.rectangle(g, (x0, yy - h // 2), (x0 + wd, yy + h // 2), 1, -1); g = cv2.GaussianBlur(g, (0, 0), 22) * .35 * u; f[:] = np.clip(f.astype(np.float32) + g[..., None] * np.array(col, np.float32), 0, 255).astype(np.uint8)
    pad = int(14 * (1 - u)); L = 26; th = 4
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        px = (x0 if sx < 0 else x0 + wd) + sx * pad; py = (yy - h // 2 if sy < 0 else yy + h // 2) + sy * pad; cv2.line(f, (px, py), (px - sx * L, py), col, th, cv2.LINE_AA); cv2.line(f, (px, py), (px, py - sy * L), col, th, cv2.LINE_AA)
    stroke_text(f, s, 'poppins', size, 540, yy, col, u, 1.0, 3, 1)
# ---------------------------------------------------------------- white file chip with glow (ref 3, 6.4)
def file_chip(f, t, t0, t1, name, sub='by you', y=1330, w=640):
    if not (t0 <= t < t1): return
    u = eo((t - t0) / .3) * clamp((t1 - t) / .25); h = 92; x0 = 540 - w // 2; yy = y - h // 2 + int((1 - eo((t - t0) / .35)) * 40)
    gl = np.zeros((H, W), np.float32); cv2.rectangle(gl, (x0, yy), (x0 + w, yy + h), 1, -1); gl = cv2.GaussianBlur(gl, (0, 0), 26) * (.55 * max(0, 1 - (t - t0) / .8)) * u; f[:] = np.clip(f.astype(np.uint8).astype(np.float32) + gl[..., None] * 255, 0, 255).astype(np.uint8)
    m = (rr(w, h, 22) * u)[..., None]; roi = f[yy:yy + h, x0:x0 + w].astype(np.float32)
    if roi.shape[:2] == m.shape[:2]: f[yy:yy + h, x0:x0 + w] = (roi * (1 - m) + 250 * m).astype(np.uint8)
    cv2.rectangle(f, (x0 + 26, yy + 26), (x0 + 66, yy + 66), (200, 200, 200), 2); text(f, name, 'psb', 30, x0 + 90 + twidth(name, 'psb', 30, 0) / 2, yy + 36, (30, 30, 30), u); text(f, sub, 'pm', 22, x0 + 90 + twidth(sub, 'pm', 22, 0) / 2, yy + 66, (150, 150, 150), u)
# ---------------------------------------------------------------- typed input bar (ref 3/4 end)
def input_bar(f, t, t0, t1, word, y=1500):
    if not (t0 <= t < t1): return
    a = eo((t - t0) / .3) * clamp((t1 - t) / .25); bw = 820; x0 = 540 - bw // 2; h = 84
    m = (rr(bw, h, 42) * a)[..., None]; roi = f[y - h // 2:y + h // 2, x0:x0 + bw].astype(np.float32)
    if roi.shape[:2] == m.shape[:2]: f[y - h // 2:y + h // 2, x0:x0 + bw] = (roi * (1 - m) + np.array((55, 50, 50), np.float32) * m).astype(np.uint8)
    cv2.circle(f, (x0 + 46, y), 28, (110, 190, 90), -1, cv2.LINE_AA); n = int(len(word) * clamp((t - t0 - .3) / (.16 * len(word)))); s = word[:n]
    if s: text(f, s, 'psb', 38, x0 + 96 + twidth(s, 'psb', 38, 1) / 2, y, (255, 255, 255), a, track=1)
    done = clamp((t - t0 - .3 - .16 * len(word)) / .25); col = (255, 120, 90) if done > 0 else (120, 90, 80); cv2.circle(f, (x0 + bw - 46, y), 28, col, -1, cv2.LINE_AA); cv2.arrowedLine(f, (x0 + bw - 46, y + 10), (x0 + bw - 46, y - 12), (255, 255, 255), 5, cv2.LINE_AA, tipLength=.5)
# ---------------------------------------------------------------- dark full-screen UI scene with vertical blur scroll (ref 4, 4.0-7.2)
def dark_bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); d = np.sqrt(((xx - 540) / 700) ** 2 + ((yy - 700) / 900) ** 2); g = np.clip(1 - d, 0, 1) ** 1.6
    f = np.zeros((H, W, 3), np.float32); f[:] = np.array((20, 18, 16), np.float32); f += g[..., None] * np.array((36, 30, 22), np.float32); return np.clip(f, 0, 255).astype(np.uint8)
RING = [(60, 140, 255), (200, 80, 200), (80, 200, 255), (110, 220, 110), (255, 160, 60)]
def profile_card(f, cx, cy, name, sub, bio, ring, a=1.0, w=900, scale=1.0):
    if a <= .01: return
    h = int(220 * scale); x0 = int(cx - w / 2); y0 = int(cy - h / 2)
    cv2.circle(f, (x0 + 100, cy), int(70 * scale), ring, 6, cv2.LINE_AA); cv2.circle(f, (x0 + 100, cy), int(58 * scale), (60, 56, 52), -1, cv2.LINE_AA)
    cv2.circle(f, (x0 + 100, cy - int(12 * scale)), int(18 * scale), (205, 205, 205), -1, cv2.LINE_AA); cv2.ellipse(f, (x0 + 100, cy + int(32 * scale)), (int(30 * scale), int(22 * scale)), 0, 180, 360, (205, 205, 205), -1, cv2.LINE_AA)
    text(f, name, 'pb', int(38 * scale), x0 + 200 + twidth(name, 'pb', int(38 * scale), 0) / 2, y0 + int(40 * scale), (240, 240, 240), a); text(f, sub, 'psb', int(26 * scale), x0 + 200 + twidth(sub, 'psb', int(26 * scale), 0) / 2, y0 + int(92 * scale), (150, 220, 150) if ring == RING[3] else (170, 170, 170), a)
    for i, ln in enumerate(bio): text(f, ln, 'pm', int(24 * scale), x0 + 200 + twidth(ln, 'pm', int(24 * scale), 0) / 2, y0 + int((136 + 34 * i) * scale), (150, 150, 150), a)
def vblur(f, k):
    k = int(k) | 1
    return cv2.blur(f, (1, k)) if k > 2 else f
def dark_scene(t, t0, t1, cards, label=None):
    """cards: [(name, sub, bio_lines, ring_idx)]; they slide in from below with vertical blur, then slide out upward."""
    f = dark_bg(); n = len(cards); span = (t1 - t0)
    layer = np.zeros((H, W, 3), np.uint8); alpha = 0
    for i, (name, sub, bio, ri) in enumerate(cards):
        ti = t0 + .15 + i * .22; u = eo((t - ti) / .5); y = 640 + i * 300
        yy = int(y + (1 - u) * 900); bl = int(1 + (1 - u) * 90)
        tmp = np.zeros((H, W, 3), np.uint8); profile_card(tmp, 540, yy, name, sub, bio, RING[ri], 1.0, 900, 1.25)
        out = clamp((t - (t1 - .35)) / .35); tmp = np.roll(tmp, -int(out * 700), axis=0)
        tmp = vblur(tmp, bl + int(out * 70)); m = (tmp.sum(2) > 0)[..., None]; layer = np.where(m, tmp, layer)
    m = (layer.sum(2) > 0).astype(np.float32)[..., None]; f = (f.astype(np.float32) * (1 - m * 1.0) + layer.astype(np.float32) * m).astype(np.uint8)
    if label: text(f, label, 'psb', 24, 540, 1780, (110, 110, 110), 1.0, track=2)
    return f
# ---------------------------------------------------------------- small caption mid-frame (ref 3/4)
def caps(f, t, words, y=1010, size=58, hide=None):
    if hide and any(a <= t < b for a, b in hide): return
    gs = []; cur = []
    for w in words:
        cur.append(w)
        if len(cur) >= 3 or w[0][-1] in '.,?!': gs.append(cur); cur = []
    if cur: gs.append(cur)
    for g in gs:
        a0 = g[0][1] - .03; a1 = g[-1][2] + .18
        if a0 <= t < a1:
            s = ' '.join(('I' if w[0].lower().strip('.,') == 'i' else ('ICP' if w[0].lower().strip('.,') == 'icp' else w[0].strip('.,').lower())) if w[0].lower().strip('.,') in ('i', 'icp') else w[0].strip('.,').lower() for w in g)
            s = s.replace("i'm", "I'm").replace("i'll", "I'll").replace("i've", "I've").replace("i'd", "I'd")
            k = clamp((t - a0) / .08) * clamp((a1 - t) / .08); z = fit(s, 'psb', size, 900)
            text(f, s, 'pb', z, 540, y, (255, 255, 255), k); return
# ---------------------------------------------------------------- speaker + transitions
def speaker(S, k, zoom=1.0, cx=540, cy=700):
    i = min(k, int((S['VDUR'] - .3) * FPS)) + 1; fr = grade(cv2.imread(f"{C5}/work/fd{S['vid']}/{i:04d}.jpg"))
    M = np.float32([[zoom, 0, (1 - zoom) * cx], [0, zoom, (1 - zoom) * cy]]); return cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
def whip_v(f, d, dur=.3):
    """vertical motion-blur punch as in refs 3/4"""
    if not (0 <= d < dur): return f
    u = 1 - d / dur; f = vblur(f, 1 + 70 * u ** 1.6); z = 1 + .08 * u; M = np.float32([[z, 0, (1 - z) * 540], [0, z, (1 - z) * 960]]); return cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
def finish(f, k):
    f = cv2.addWeighted(f, .78, cv2.multiply(f, doc.vig(), scale=1 / 255), .22, 0); return cv2.addWeighted(f, 1, doc.grain(k), .015, -128 * .015)
def chunk_writer(frame_fn):
    def _chunk(args):
        a, b, out = args
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', '30', '-i', '-', '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        for k in range(a, b): enc.stdin.write(np.ascontiguousarray(frame_fn(k)).tobytes())
        enc.stdin.close(); enc.wait(); return out
    return _chunk
def make_preview(frame_fn):
    def preview(ts, out, cols=8):
        tiles = [cv2.resize(frame_fn(int(t * FPS)), (270, 480)) for t in ts]
        while len(tiles) % cols: tiles.append(np.zeros_like(tiles[0]))
        cv2.imwrite(out, np.vstack([np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]))
    return preview

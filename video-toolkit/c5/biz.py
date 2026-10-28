import sys; sys.path.insert(0, '/tmp/vt/c5')
import story3 as S3
from story3 import *
import vil as V
BLUE = (255, 140, 40); YEL = (60, 210, 255); RED = (60, 50, 235); WHT = (255, 255, 255); DK = (24, 22, 22)
def rr(w, h, r):
    m = np.zeros((h, w), np.float32); cv2.rectangle(m, (r, 0), (w - r, h), 1, -1); cv2.rectangle(m, (0, r), (w, h - r), 1, -1)
    for cx, cy in ((r, r), (w - r, r), (r, h - r), (w - r, h - r)): cv2.circle(m, (cx, cy), r, 1, -1, cv2.LINE_AA)
    return cv2.GaussianBlur(m, (0, 0), .7)
def box(f, x0, y0, w, h, col, a=1.0, r=18, border=None, bw=2):
    x0, y0, w, h = int(x0), int(y0), int(w), int(h)
    X0, Y0, X1, Y1 = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if X0 >= X1 or Y0 >= Y1 or a <= .01: return
    m = (rr(w, h, min(r, h // 2, w // 2)) * a)[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0][..., None]; roi = f[Y0:Y1, X0:X1].astype(np.float32); f[Y0:Y1, X0:X1] = (roi * (1 - m) + np.array(col, np.float32) * m).astype(np.uint8)
    if border is not None:
        e = np.clip(rr(w, h, min(r, h // 2, w // 2)) - cv2.erode(rr(w, h, min(r, h // 2, w // 2)), np.ones((bw * 2 + 1,) * 2, np.uint8)), 0, 1)[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0][..., None] * a; roi = f[Y0:Y1, X0:X1].astype(np.float32); f[Y0:Y1, X0:X1] = (roi * (1 - e) + np.array(border, np.float32) * e).astype(np.uint8)
# ---------------------------------------------------------------- icons (drawn)
def icon(f, kind, cx, cy, s, col=WHT, a=1.0):
    ov = f.copy(); c = col; t = max(2, int(s * .07))
    if kind == 'person': cv2.circle(ov, (cx, cy - int(s * .22)), int(s * .2), c, -1, cv2.LINE_AA); cv2.ellipse(ov, (cx, cy + int(s * .38)), (int(s * .36), int(s * .3)), 0, 180, 360, c, -1, cv2.LINE_AA)
    elif kind == 'people': icon(f, 'person', cx - int(s * .22), cy + 4, int(s * .8), c, a); icon(f, 'person', cx + int(s * .22), cy + 4, int(s * .8), c, a); return
    elif kind == 'doc': cv2.rectangle(ov, (cx - int(s * .28), cy - int(s * .38)), (cx + int(s * .28), cy + int(s * .38)), c, -1); [cv2.line(ov, (cx - int(s * .17), cy - int(s * .2) + k * int(s * .16)), (cx + int(s * .17), cy - int(s * .2) + k * int(s * .16)), DK, t) for k in range(4)]
    elif kind == 'briefcase': cv2.rectangle(ov, (cx - int(s * .38), cy - int(s * .2)), (cx + int(s * .38), cy + int(s * .32)), c, -1); cv2.rectangle(ov, (cx - int(s * .14), cy - int(s * .34)), (cx + int(s * .14), cy - int(s * .2)), c, t); cv2.line(ov, (cx - int(s * .38), cy + int(s * .04)), (cx + int(s * .38), cy + int(s * .04)), DK, t)
    elif kind == 'book': cv2.fillPoly(ov, [np.array([[cx - int(s * .4), cy - int(s * .28)], [cx, cy - int(s * .2)], [cx, cy + int(s * .34)], [cx - int(s * .4), cy + int(s * .26)]])], c); cv2.fillPoly(ov, [np.array([[cx + int(s * .4), cy - int(s * .28)], [cx, cy - int(s * .2)], [cx, cy + int(s * .34)], [cx + int(s * .4), cy + int(s * .26)]])], tuple(int(v * .8) for v in c))
    elif kind == 'magnet': cv2.ellipse(ov, (cx, cy), (int(s * .32), int(s * .32)), 0, 180, 360, c, int(s * .2)); cv2.rectangle(ov, (cx - int(s * .42), cy), (cx - int(s * .22), cy + int(s * .3)), (60, 60, 235), -1); cv2.rectangle(ov, (cx + int(s * .22), cy), (cx + int(s * .42), cy + int(s * .3)), (60, 60, 235), -1)
    elif kind == 'dollar': cv2.circle(ov, (cx, cy), int(s * .38), c, -1, cv2.LINE_AA); text(ov, '$', 'anton', int(s * .6), cx, cy + 2, DK, 1.0)
    elif kind == 'mic': cv2.rectangle(ov, (cx - int(s * .13), cy - int(s * .36)), (cx + int(s * .13), cy + int(s * .08)), c, -1); cv2.ellipse(ov, (cx, cy + int(s * .04)), (int(s * .24), int(s * .24)), 0, 0, 180, c, t); cv2.line(ov, (cx, cy + int(s * .28)), (cx, cy + int(s * .4)), c, t)
    elif kind == 'waves': [cv2.line(ov, (cx - int(s * .36) + k * int(s * .18), cy - h_), (cx - int(s * .36) + k * int(s * .18), cy + h_), c, t + 2, cv2.LINE_AA) for k, h_ in enumerate([int(s * v) for v in (.1, .26, .38, .22, .1)])]
    elif kind == 'globe': cv2.circle(ov, (cx, cy), int(s * .36), c, t, cv2.LINE_AA); cv2.ellipse(ov, (cx, cy), (int(s * .16), int(s * .36)), 0, 0, 360, c, t, cv2.LINE_AA); cv2.line(ov, (cx - int(s * .36), cy), (cx + int(s * .36), cy), c, t)
    elif kind == 'target': [cv2.circle(ov, (cx, cy), int(s * r_), col_, -1 if i == 4 else t + 1, cv2.LINE_AA) for i, (r_, col_) in enumerate(((.38, c), (.26, c), (.14, c), (.05, c)))]
    elif kind == 'scissors': cv2.line(ov, (cx - int(s * .3), cy - int(s * .3)), (cx + int(s * .3), cy + int(s * .3)), c, t + 1, cv2.LINE_AA); cv2.line(ov, (cx + int(s * .3), cy - int(s * .3)), (cx - int(s * .3), cy + int(s * .3)), c, t + 1, cv2.LINE_AA); cv2.circle(ov, (cx - int(s * .22), cy + int(s * .3)), int(s * .1), c, t); cv2.circle(ov, (cx + int(s * .22), cy + int(s * .3)), int(s * .1), c, t)
    elif kind == 'chat': box(ov, cx - int(s * .38), cy - int(s * .3), int(s * .76), int(s * .5), c, 1.0, int(s * .15)); cv2.fillPoly(ov, [np.array([[cx - int(s * .2), cy + int(s * .18)], [cx - int(s * .3), cy + int(s * .38)], [cx, cy + int(s * .18)]])], c)
    elif kind == 'funnel': cv2.fillPoly(ov, [np.array([[cx - int(s * .4), cy - int(s * .34)], [cx + int(s * .4), cy - int(s * .34)], [cx + int(s * .08), cy + int(s * .06)], [cx + int(s * .08), cy + int(s * .38)], [cx - int(s * .08), cy + int(s * .3)], [cx - int(s * .08), cy + int(s * .06)]])], c)
    elif kind == 'price': cv2.fillPoly(ov, [np.array([[cx - int(s * .38), cy - int(s * .1)], [cx - int(s * .1), cy - int(s * .38)], [cx + int(s * .38), cy - int(s * .38)], [cx + int(s * .38), cy + int(s * .1)], [cx + int(s * .1), cy + int(s * .38)]])], c); cv2.circle(ov, (cx + int(s * .2), cy - int(s * .2)), int(s * .06), DK, -1)
    f[:] = cv2.addWeighted(f, 1 - a, ov, a, 0) if a < 1 else ov
def icon_pop(f, kind, cx, cy, t, t0, t1, s=130, col=WHT, brackets=YEL):
    if not (t0 <= t < t1): return
    u = back((t - t0) / .32); out = clamp((t1 - t) / .2); a = clamp(u) * out
    if u <= 0: return
    sc = max(u, .01); r = int(s * .62 * sc); box(f, cx - r, cy - r, 2 * r, 2 * r, (30, 28, 28), .55 * a, 22)
    L = int(r * .5); th = 5
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        px, py = cx + sx * r, cy + sy * r; cv2.line(f, (px, py), (px - sx * L, py), brackets, th, cv2.LINE_AA); cv2.line(f, (px, py), (px, py - sy * L), brackets, th, cv2.LINE_AA)
    icon(f, kind, cx, cy, int(s * .8 * sc), col, a)
# ---------------------------------------------------------------- reference-style graphics
def red_tag(f, t, t0, t1, l1, l2=None, y=250, size=62):
    import titles; titles.hook_title(f, t, t0, t1, l1, l2 or '', YEL, 1080, 215, 124, 56)
def toggles(f, t, t_in, t_out, title, items, times, y0=1020, x0=50, w=720):
    """Ref 4: card of toggle rows; each switches on as it is spoken; the active row is outlined."""
    if not (t_in <= t < t_out): return
    a = eo((t - t_in) / .4) * clamp((t_out - t) / .3); n = len(items); rh = 78; h = 70 + n * rh + 20
    box(f, x0, y0, w, h, (28, 26, 26), .8 * a, 22, (90, 90, 90), 2); text(f, title, 'psb', 32, x0 + 30 + twidth(title, 'psb', 32, 1) / 2, y0 + 38, (245, 245, 245), a, track=1)
    act = -1
    for i, tt in enumerate(times):
        if t >= tt: act = i
    for i, it in enumerate(items):
        y = y0 + 70 + i * rh; on = t >= times[i]; k = eo((t - times[i]) / .3) if on else 0; isact = (i == act) and t < (times[i + 1] if i + 1 < n else t_out)
        if isact: box(f, x0 + 14, y + 4, w - 28, rh - 8, (60, 58, 58), .9 * a, 16, (255, 255, 255), 3)
        text(f, it, 'psb', 34, x0 + 52 + twidth(it, 'psb', 34, 0) / 2, y + rh // 2, (245, 245, 245) if on else (150, 150, 150), a)
        sw = 74; sx = x0 + w - 110; sy = y + rh // 2 - 20; box(f, sx, sy, sw, 40, tuple(int(lerp(g_, b_, k)) for g_, b_ in zip((90, 90, 90), BLUE)), a, 20); cv2.circle(f, (int(sx + 20 + 34 * k), sy + 20), 15, (255, 255, 255), -1, cv2.LINE_AA)
def input_bar(f, t, t0, t1, word, y=1400, label=None):
    """Ref 3/4/7: comment-box with avatar, typed word, send button that fires."""
    if not (t0 <= t < t1): return
    a = eo((t - t0) / .3) * clamp((t1 - t) / .25); box(f, 120, y - 46, 840, 92, (250, 250, 250), a, 46); cv2.circle(f, (175, y), 30, (110, 190, 90), -1, cv2.LINE_AA); cv2.circle(f, (175, y - 8), 10, (255, 255, 255), -1, cv2.LINE_AA); cv2.ellipse(f, (175, y + 22), (18, 12), 0, 180, 360, (255, 255, 255), -1, cv2.LINE_AA)
    n = int(len(word) * clamp((t - t0 - .3) / (.14 * len(word)))); s = word[:n]; text(f, s, 'psb', 40, 240 + twidth(s, 'psb', 40, 1) / 2 if s else 240, y, DK, a, track=1)
    if int(t * 2.5) % 2 == 0 and n < len(word): cv2.line(f, (244 + int(twidth(s, 'psb', 40, 1)), y - 22), (244 + int(twidth(s, 'psb', 40, 1)), y + 22), (60, 60, 60), 3)
    done = clamp((t - t0 - .3 - .14 * len(word)) / .3); cv2.circle(f, (905, y), int(30 + 4 * math.sin(t * 9) * (done > 0)), (255, 120, 90) if done > 0 else (190, 190, 190), -1, cv2.LINE_AA)
    cv2.arrowedLine(f, (905, y + 12), (905, y - 14), (255, 255, 255), 5, cv2.LINE_AA, tipLength=.5)
    if label: text(f, label, 'psb', 28, 540, y - 80, (245, 245, 245), a, shadow=.8, track=1)
def glow_stat(f, t, t0, t1, big, small, y=430, col=YEL):
    if not (t0 <= t < t1): return
    sz = 190
    while twidth(big, 'anton', sz, 0) > 960 and sz > 60: sz -= 6
    a = eo((t - t0) / .3) * clamp((t1 - t) / .25); sc = 1 + .1 * (1 - eo((t - t0) / .4))
    g = np.zeros((H, W), np.float32); m = tex(big, 'anton', sz); put_tmp = np.zeros((H, W, 3), np.uint8); put(put_tmp, m, 540, y, (255, 255, 255), 1.0, sc); g = cv2.GaussianBlur(put_tmp[..., 0].astype(np.float32) / 255, (0, 0), 20) * .9 * a; f[:] = np.clip(f.astype(np.float32) + g[..., None] * np.array(col, np.float32), 0, 255).astype(np.uint8)
    text(f, big, 'anton', sz, 540, y, (255, 255, 255), a, sc=sc, shadow=.8); text(f, small, 'psb', 30, 540, y + int(sz * .62), (240, 240, 240), a, track=3, shadow=.8)
# ---------------------------------------------------------------- full-screen light cutaway cards (ref 8)
def card_bg(t, t0, dark=False):
    f = np.full((H, W, 3), (236, 236, 236) if not dark else (22, 22, 24), np.uint8)
    for x in range(0, W, 96): f[:, x] = (f[:, x].astype(int) - (6 if not dark else -8)).clip(0, 255).astype(np.uint8)
    for y in range(0, H, 96): f[y] = (f[y].astype(int) - (6 if not dark else -8)).clip(0, 255).astype(np.uint8)
    return f
def ctitle(f, s, y, t, t0, size=110, col=DK): 
    while twidth(s, 'anton', size, 0) > 980 and size > 40: size -= 6
    u = eo((t - t0) / .35); text(f, s, 'anton', size, 540, y, col, u, sc=1 + .08 * (1 - u))
def csub(f, s, y, t, t0, size=40, col=(90, 90, 90)): text(f, s, 'psb', size, 540, y, col, eo((t - t0) / .35), track=1)
def avatar(f, cx, cy, r, col, a=1.0, face=True):
    cv2.circle(f, (cx, cy), r, col, -1, cv2.LINE_AA)
    if face: cv2.circle(f, (cx, cy - r // 4), r // 3, (255, 255, 255), -1, cv2.LINE_AA); cv2.ellipse(f, (cx, cy + r // 2), (r // 2, r // 3), 0, 180, 360, (255, 255, 255), -1, cv2.LINE_AA)
def sw_frame(S, k):
    i = min(k, int((S['VDUR'] - .3) * FPS)) + 1; fr = cv2.imread(f"{C5}/work/fd{S['vid']}/{i:04d}.jpg"); return grade(fr)
def speaker(S, k, zoom=1.0, cx=540):
    fr = sw_frame(S, k); M = np.float32([[zoom, 0, (1 - zoom) * cx], [0, zoom, (1 - zoom) * 900]]); return cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
def mycaps(f, t, words):
    gs = []; cur = []
    for w in words:
        cur.append(w)
        if len(cur) >= 3 or w[0][-1] in '.,?!': gs.append(cur); cur = []
    if cur: gs.append(cur)
    for g in gs:
        a0 = g[0][1] - .03; a1 = g[-1][2] + .2
        if a0 <= t < a1:
            s = ' '.join(w[0].strip('.,').lower() if w[0].lower() not in ('i', "i'm", "i'd", "i'll", "i've", 'icp') else w[0].strip('.,').replace('i', 'I') if w[0].lower() != 'icp' else 'ICP' for w in g)
            k = clamp((t - a0) / .08) * clamp((a1 - t) / .08); size = 50
            while twidth(s, 'psb', size, 0) > 940 and size > 30: size -= 2
            text(f, s, 'psb', size, 540, 1640, (255, 255, 255), k, shadow=.55); return
def run_frame(S, k, SH, overlays, cards, endfn=None):
    t = k / FPS; s = next((x for x in SH if x['t0'] <= t < x['t1']), SH[-1]); kind = s['kind']; pz = 0.0
    for p in s.get('pulses', []):
        d = t - p
        if 0 <= d < .35: pz = max(pz, .035 * (1 - d / .35) ** 2)
    if kind == 'raw':
        u = clamp((t - s['t0']) / (s['t1'] - s['t0'])); z0, z1 = s.get('z', (1.0, 1.08)); f = speaker(S, k, lerp(z0, z1, eio(u)) + pz)
        gg = np.clip((np.arange(H, dtype=np.float32) - 1500) / 420, 0, 1)[:, None, None] * .5; f = (f.astype(np.float32) * (1 - gg)).astype(np.uint8)
        gt = np.clip(1 - np.arange(H, dtype=np.float32) / 420, 0, 1)[:, None, None] ** 1.3 * .55; f = (f.astype(np.float32) * (1 - gt)).astype(np.uint8)
        overlays(f, t, k); mycaps(f, t, S['words'])
    elif kind == 'card': f = cards[s['card']](t, s['t0'], s['t1'], k); mycaps(f, t, S['words'])
    else: f = endfn(t, k) if endfn else np.full((H, W, 3), 12, np.uint8)
    d = t - s['t0']; tr = s.get('tr', 'cut')
    if tr == 'flash' and 0 <= d < .18: f = cv2.addWeighted(f, 1, np.full_like(f, 255), .3 * (1 - d / .18), 0)
    if tr == 'whip' and 0 <= d < .26:
        kk = int(1 + 36 * (1 - d / .26) ** 1.6) | 1; f = cv2.blur(f, (kk, 1)); f = np.roll(f, int(-70 * (1 - d / .26) ** 2), axis=1)
    f = cv2.addWeighted(f, .7, cv2.multiply(f, doc.vig(), scale=1 / 255), .3, 0); return cv2.addWeighted(f, 1, doc.grain(k), .02, -128 * .02)
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

# ---------------------------------------------------------------- reusable cutaway cards
def card_icp(title_a='ICP', title_b='IDEAL CLIENT PERSONA', who=('WHO DO YOU WANT', 'TO SELL TO?'), t_who=None, t_no=None, no_lines=('NO POINT SELLING TO SOMEONE', "WHO CAN'T AFFORD IT")):
    def fn(t, t0, t1, k):
        f = card_bg(t, t0); ctitle(f, title_a, 300, t, t0 + .1, 260); csub(f, title_b, 500, t, t0 + .3, 46, (60, 60, 60))
        av = eo((t - t0 - .4) / .5)
        if av > 0:
            r = int(190 * av); cv2.circle(f, (540, 880), r + 18, (255, 255, 255), -1, cv2.LINE_AA); avatar(f, 540, 880, r, (80, 80, 80)); 
            for ang in range(0, 360, 90): pass
            cv2.circle(f, (700, 740), int(60 * av), YEL, -1, cv2.LINE_AA); (text(f, '$', 'anton', max(int(80 * av), 8), 700, 742, DK, av) if av > .05 else None)
        if t_who is not None and t > t_who - .1:
            u = eo((t - t_who + .1) / .35); text(f, who[0], 'psb', 46, 540, 1180, DK, u, track=1); text(f, who[1], 'psb', 46, 540, 1240, DK, u, track=1)
        if t_no is not None and t > t_no - .1:
            u = eo((t - t_no + .1) / .35); box(f, 90, 1290, 900, 190, (255, 255, 255), u, 26, (200, 200, 200)); cv2.line(f, (850, 1320), (940, 1410), RED, 12, cv2.LINE_AA) if u > .5 else None
            text(f, no_lines[0], 'psb', 36, 500, 1345, DK, u, track=1); text(f, no_lines[1], 'pb', 44, 500, 1415, RED, u, track=1)
        return f
    return fn
def card_subs(t0_arrow=None):
    def fn(t, t0, t1, k):
        f = card_bg(t, t0); ctitle(f, 'SUBTITLES', 260, t, t0 + .1, 150); csub(f, 'IN DIFFERENT LANGUAGES', 380, t, t0 + .3, 40, (70, 70, 70))
        a = eo((t - t0 - .4) / .5)
        box(f, 100, 520, 360, 420, (255, 255, 255), a, 28, (200, 200, 200)); avatar(f, 280, 690, 90, (120, 120, 120)); text(f, "CAN'T AFFORD", 'psb', 32, 280, 840, RED, a, track=1); text(f, 'HIGH TICKET', 'psb', 32, 280, 884, RED, a, track=1)
        u = eo((t - t0 - 1.0) / .5); cv2.arrowedLine(f, (480, 730), (480 + int(120 * u), 730), BLUE, 12, cv2.LINE_AA, tipLength=.5) if u > .05 else None
        b = eo((t - t0 - 1.3) / .5); box(f, 620, 520, 360, 420, (255, 255, 255), b, 28, (200, 200, 200)); avatar(f, 800, 690, 90, (90, 170, 90)); text(f, 'CAN AFFORD', 'psb', 32, 800, 840, (60, 150, 60), b, track=1); text(f, 'HIGH TICKET', 'psb', 32, 800, 884, (60, 150, 60), b, track=1)
        icon(f, 'globe', 540, 1130, 220, DK, eo((t - t0 - .7) / .4)); csub(f, 'CONVERT YOUR AUDIENCE SLOWLY', 1300, t, t0 + 1.8, 40, (60, 60, 60))
        return f
    return fn
def card_guide(title, sub, t_pop=None):
    def fn(t, t0, t1, k):
        f = card_bg(t, t0); ctitle(f, title, 250, t, t0 + .1, 110); csub(f, sub, 350, t, t0 + .3, 38, (80, 80, 80))
        c = np.zeros((H, W, 3), np.uint8); dc = np.full((860, 620, 3), 248, np.uint8); cv2.rectangle(dc, (0, 0), (619, 150), DK, -1); text(dc, 'GUIDE', 'anton', 100, 310, 78, YEL); [cv2.rectangle(dc, (60, 230 + i * 56), (560 - (i % 3) * 80, 248 + i * 56), (200, 200, 200), -1) for i in range(10)]
        doc.card_persp(c, dc, 540, 930, 560, t, t0 + .3, rot=-3.0, rise=380); m = (c.sum(2) > 0).astype(np.float32)[..., None]; f = (f.astype(np.float32) * (1 - m) + c.astype(np.float32) * m).astype(np.uint8)
        return f
    return fn
def card_funnel(labels):
    def fn(t, t0, t1, k):
        f = card_bg(t, t0); ctitle(f, 'FUNNEL SYSTEM', 240, t, t0 + .1, 120)
        for i, (lab, w0, w1, col) in enumerate(labels):
            u = eo((t - t0 - .3 - i * .25) / .4); y0 = 400 + i * 300; pts = np.array([[540 - w0 / 2, y0], [540 + w0 / 2, y0], [540 + w1 / 2, y0 + 270], [540 - w1 / 2, y0 + 270]], np.int32); ov = f.copy(); cv2.fillPoly(ov, [pts], col, cv2.LINE_AA); f = cv2.addWeighted(f, 1 - u, ov, u, 0); text(f, lab, 'pb', 44, 540, y0 + 135, WHT, u, track=2)
        return f
    return fn

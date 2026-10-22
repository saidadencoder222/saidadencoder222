"""Hand-drawn doodle sprites. Each D_*(t) returns Sp (c = premultiplied colour, A = alpha). t = seconds since overlay start."""
from cc3 import *
BLUEC = (205, 130, 45); YEL = (60, 205, 250); LGREY = (190, 190, 190); DRED = (45, 35, 150); SKY = (255, 215, 140)
def I(x): return max(1, int(round(x)))
def ell(cx, cy, rx, ry, a0=0, a1=360, n=40): return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
def rrect(x0, y0, x1, y1, r, n=6):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1): a = math.radians(a0 + 90 * i / n); pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts
def wob(pts, amp, seed, step=7):
    pts = np.array(pts, np.float32); out = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(int(np.hypot(*(b - a)) / step), 1)
        for i in range(1, n + 1): out.append(a + (b - a) * i / n)
    out = np.array(out, np.float32); i = np.arange(len(out), dtype=np.float32)
    dx = amp * (np.sin(i * .37 + seed) + .6 * np.sin(i * .91 + seed * 2.1)); dy = amp * (np.cos(i * .33 + seed * 1.3) + .6 * np.sin(i * .83 + seed))
    return out + np.stack([dx, dy], 1) * .5
def pr(t, a, b): return clamp((t - a) / max(b - a, 1e-6))

class Sp:
    def __init__(s, w, h): s.w, s.h = w, h; s.c = np.zeros((h, w, 3), np.uint8); s.A = np.zeros((h, w, 3), np.uint8)
    def fillpoly(s, pts, col, amp=0, seed=0):
        P = wob(pts, amp, seed) if amp else np.array(pts, np.float32); P = (P * 16).astype(np.int32)
        cv2.fillPoly(s.c, [P], col, cv2.LINE_AA, 4); cv2.fillPoly(s.A, [P], (255, 255, 255), cv2.LINE_AA, 4)
    def disc(s, x, y, r, col):
        r = max(int(r), 1); cv2.circle(s.c, (int(x), int(y)), r, col, -1, cv2.LINE_AA); cv2.circle(s.A, (int(x), int(y)), r, (255, 255, 255), -1, cv2.LINE_AA)
    def line(s, pts, col, th, prog=1.0, amp=1.4, seed=0, closed=False):
        if prog <= 0: return
        pts = list(pts) + ([pts[0]] if closed else []); P = wob(pts, amp, seed) if amp else np.array(pts, np.float32)
        seg = np.hypot(*np.diff(P, axis=0).T); cum = np.concatenate([[0], np.cumsum(seg)]); L = float(cum[-1]); tgt = L * clamp(prog)
        k = int(np.searchsorted(cum, tgt)); Q = P[:k + 1].copy()
        if 0 < k < len(P): Q[-1] = P[k - 1] + (P[k] - P[k - 1]) * ((tgt - cum[k - 1]) / max(seg[k - 1], 1e-6))
        if len(Q) < 2: return
        Q16 = (Q * 16).astype(np.int32); th = I(th)
        cv2.polylines(s.c, [Q16], False, col, th, cv2.LINE_AA, 4); cv2.polylines(s.A, [Q16], False, (255, 255, 255), th, cv2.LINE_AA, 4)
        for p in (Q[0], Q[-1]): s.disc(p[0], p[1], th / 2, col)
    def text(s, txt, x, y, size, col=INK, prog=1.0, fnt='mark'):
        if prog <= 0: return
        m = tex(txt, I(size), 700, 0, fnt); h, w = m.shape; edge = prog * (w + 30) - 15
        clip = np.clip((edge - np.arange(w, dtype=np.float32)[None, :]) / 15, 0, 1) * np.ones((h, 1), np.float32)
        put(s.c, m, x, y, col, 1, clip=clip); put(s.A, m, x, y, (255, 255, 255), 1, clip=clip)
    def card(s, x0, y0, x1, y1, seed=0):
        pts = rrect(x0, y0, x1, y1, 26); s.fillpoly(pts, PAPER); s.line(pts, INK, 7, amp=1.1, seed=seed, closed=True)
    def check(s, x, y, prog, col=RED, th=11, k=1.0):
        s.line([(x - 22 * k, y + 2 * k), (x - 7 * k, y + 18 * k), (x + 26 * k, y - 20 * k)], col, th, prog, amp=.6)
    def star(s, x, y, r, col=YEL, rot=0.3):
        pts = [(x + (r if i % 2 == 0 else r * .42) * math.cos(rot + i * math.pi / 5 - math.pi / 2), y + (r if i % 2 == 0 else r * .42) * math.sin(rot + i * math.pi / 5 - math.pi / 2)) for i in range(10)]
        s.fillpoly(pts, col); s.line(pts, INK, 4, amp=.5, closed=True)
    def arrow(s, a, b, col=INK, th=8, prog=1.0, seed=0):
        s.line([a, b], col, th, prog, amp=1.2, seed=seed)
        if prog >= .98:
            ang = math.atan2(b[1] - a[1], b[0] - a[0]); h = 26
            s.line([(b[0] - h * math.cos(ang - .5), b[1] - h * math.sin(ang - .5)), b, (b[0] - h * math.cos(ang + .5), b[1] - h * math.sin(ang + .5))], col, th, 1.0, amp=.4)

# ---------------------------------------------------------------- him, cartoon
def face(s, cx, cy, k, mood, t, seed=1):
    sh = [(cx - 135 * k, cy + 215 * k), (cx - 118 * k, cy + 128 * k), (cx - 52 * k, cy + 104 * k), (cx + 52 * k, cy + 104 * k), (cx + 118 * k, cy + 128 * k), (cx + 135 * k, cy + 215 * k)]
    s.fillpoly(sh, BLUEC, amp=1.2, seed=seed); s.line(sh, INK, 5 * k, amp=1.2, seed=seed, closed=True)
    s.line([(cx - 40 * k, cy + 104 * k), (cx, cy + 140 * k), (cx + 40 * k, cy + 104 * k)], INK, 4 * k, amp=.8, seed=seed)
    s.disc(cx, cy - 60 * k, 112 * k, INK)
    for a in range(-172, -4, 21): s.disc(cx + 108 * k * math.cos(math.radians(a)), cy - 60 * k + 104 * k * math.sin(math.radians(a)), 38 * k, INK)
    for sgn in (-1, 1):
        e = ell(cx + sgn * 88 * k, cy + 12 * k, 13 * k, 25 * k); s.fillpoly(e, PAPER); s.line(e, INK, 4 * k, amp=.8, seed=seed, closed=True)
    fe = ell(cx, cy + 14 * k, 86 * k, 104 * k); s.fillpoly(fe, PAPER); s.line(fe, INK, 5 * k, amp=1.4, seed=seed + 1, closed=True)
    for sgn in (-1, 1):
        gx = cx + sgn * 38 * k; g = rrect(gx - 31 * k, cy - 25 * k, gx + 31 * k, cy + 17 * k, 11 * k); s.fillpoly(g, WHITE); s.line(g, INK, 5 * k, amp=.6, seed=seed + 2, closed=True)
        s.line([(cx + sgn * 69 * k, cy - 12 * k), (cx + sgn * 87 * k, cy - 16 * k)], INK, 4 * k, amp=.4)
    s.line([(cx - 8 * k, cy - 8 * k), (cx + 8 * k, cy - 8 * k)], INK, 5 * k, amp=.3)
    if mood == 'sad':
        for sgn in (-1, 1):
            gx = cx + sgn * 38 * k; s.disc(gx, cy - 1 * k, 6 * k, INK); s.line([(gx - 20 * k, cy - 14 * k), (gx + 20 * k, cy - 10 * k)], INK, 5 * k, amp=.4)
            s.line(ell(gx, cy + 24 * k, 17 * k, 5 * k, 10, 170, 8), INK, 3 * k, amp=.3)
        s.line([(cx - 64 * k, cy - 36 * k), (cx - 18 * k, cy - 52 * k)], INK, 8 * k, amp=.5); s.line([(cx + 18 * k, cy - 52 * k), (cx + 64 * k, cy - 36 * k)], INK, 8 * k, amp=.5)
        s.line(ell(cx, cy + 90 * k, 28 * k, 16 * k, 200, 340, 12), INK, 6 * k, amp=.4)
        dr = ell(cx + 96 * k, cy - 54 * k, 11 * k, 16 * k); s.fillpoly(dr, SKY); s.line(dr, INK, 3 * k, amp=.3, closed=True)
    else:
        for sgn in (-1, 1):
            gx = cx + sgn * 38 * k; s.disc(gx, cy - 4 * k, 8.5 * k, INK); s.disc(gx - 3 * k, cy - 8 * k, 3 * k, WHITE)
            s.line(ell(gx, cy - 44 * k, 28 * k, 12 * k, 200, 340, 10), INK, 7 * k, amp=.4)
        m = ell(cx, cy + 66 * k, 36 * k, 28 * k, 8, 172, 14); s.fillpoly(m, DRED); s.line(m, INK, 5 * k, amp=.4, closed=True)
        s.fillpoly([(cx - 31 * k, cy + 69 * k), (cx + 31 * k, cy + 69 * k), (cx + 27 * k, cy + 80 * k), (cx - 27 * k, cy + 80 * k)], WHITE)
        if t > .25:
            s.star(cx - 118 * k, cy - 120 * k, 17 * k, rot=t * 1.5); s.star(cx + 120 * k, cy - 100 * k, 13 * k, rot=-t * 1.2)
    s.line([(cx + 2 * k, cy + 0 * k), (cx - 10 * k, cy + 36 * k), (cx + 9 * k, cy + 37 * k)], INK, 4 * k, amp=.4)
    s.line([(cx - 36 * k, cy + 54 * k), (cx - 14 * k, cy + 44 * k), (cx, cy + 49 * k), (cx + 14 * k, cy + 44 * k), (cx + 36 * k, cy + 54 * k)], INK, 9 * k, amp=.6)
    rg = random.Random(seed)
    for _ in range(18):
        a = rg.uniform(.15, .85) * math.pi; r = rg.uniform(.55, .95); s.disc(cx + 86 * k * r * math.cos(a) * .9, cy + 14 * k + 104 * k * r * math.sin(a), 1.8 * k, INK)

def D_faces(t, la='8K', lb='40K', ca='before', cb='after'):
    s = Sp(1000, 560)
    s.card(8, 20, 448, 540, seed=1); face(s, 228, 250, .86, 'sad', t, 1); s.text(ca, 228, 56, 40, INK, pr(t, .2, .6))
    s.text(la, 228, 492, 62, RED, pr(t, .5, 1.0))
    s.arrow((462, 280), (538, 280), INK, 9, pr(t, 1.0, 1.4), 3)
    if t > 1.2:
        s.card(552, 20, 992, 540, seed=2); face(s, 772, 250, .86, 'happy', t - 1.2, 2); s.text(cb, 772, 56, 40, INK, pr(t, 1.3, 1.7))
        s.text(lb, 772, 492, 62, RED, pr(t, 1.5, 2.0))
        if t > 2.0: s.line(ell(772, 492, 118, 40, 0, 330, 30), RED, 6, pr(t, 2.0, 2.5), amp=2.5, seed=4)
    return s

# ---------------------------------------------------------------- other doodles (640x520)
def D_graph(t, a='8K', b='40K'):
    s = Sp(640, 520); s.card(8, 12, 632, 508, seed=3)
    s.line([(70, 440), (70, 80)], INK, 7, pr(t, 0, .35)); s.line([(70, 440), (580, 440)], INK, 7, pr(t, .2, .55))
    pts = [(78 + 500 * i / 30, 436 - 320 * ((math.exp(3.1 * i / 30) - 1) / (math.exp(3.1) - 1))) for i in range(31)]
    s.line(pts, RED, 10, pr(t, .5, 2.0), amp=2.0, seed=5)
    if t > 2.0: s.arrow((pts[-6][0], pts[-6][1] + 4), (pts[-1][0] + 4, pts[-1][1] - 10), RED, 10, 1.0)
    s.text(a, 125, 395, 44, INK, pr(t, .7, 1.1)); s.text(b, 470, 82, 62, INK, pr(t, 1.8, 2.3))
    if t > 2.3: s.line(ell(470, 82, 90, 40, 0, 330, 30), RED, 6, pr(t, 2.3, 2.8), amp=2.4, seed=6)
    return s
def D_calendar(t):
    s = Sp(640, 520); s.card(8, 12, 632, 508, seed=4); s.text('routine', 320, 62, 56, INK, pr(t, 0, .5))
    k = 0
    for r in range(3):
        for c in range(5):
            x = 100 + c * 110; y = 170 + r * 112; s.line(rrect(x - 40, y - 38, x + 40, y + 38, 10), INK, 5, 1.0, amp=1.2, seed=k + 7, closed=True)
            s.check(x, y, pr(t, .5 + k * .12, .5 + k * .12 + .22), RED, 10, .9); k += 1
    return s
def D_funnel(t):
    s = Sp(640, 520); s.card(8, 12, 632, 508, seed=5)
    s.line([(80, 80), (560, 80)], INK, 7, pr(t, 0, .3)); s.line([(80, 80), (250, 300), (250, 430)], INK, 7, pr(t, .2, .7)); s.line([(560, 80), (390, 300), (390, 430)], INK, 7, pr(t, .2, .7))
    s.text('6 sec', 320, 135, 46, INK, pr(t, .8, 1.2)); s.text('40 sec', 320, 235, 42, INK, pr(t, 1.8, 2.3))
    rg = random.Random(3)
    for i in range(14):
        u = (rg.random() + t * .22) % 1.0; y = 100 + u * 330; hw = np.interp(y, [80, 300, 430], [220, 70, 60]) * .8
        if t > .8 and (y < 280 or t > 1.8): s.disc(320 + rg.uniform(-1, 1) * hw, y, 7, RED)
    s.text('guide', 320, 470, 54, RED, pr(t, 2.6, 3.1))
    return s
def D_random(t):
    s = Sp(640, 520); s.card(8, 12, 632, 508, seed=6); rg = random.Random(8)
    for i in range(7):
        cx, cy = rg.uniform(130, 510), rg.uniform(110, 400); w, h = rg.uniform(90, 140), rg.uniform(110, 160); a = math.radians(rg.uniform(-35, 35)); p = pr(t, i * .08, i * .08 + .3)
        pts = [(cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)) for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
        s.line(pts, INK, 5, p, amp=1.4, seed=i, closed=True)
        if p > .8: s.fillpoly([(cx - 10, cy - 14), (cx - 10, cy + 14), (cx + 16, cy)], INK)
    s.line([(110, 90), (530, 430)], RED, 16, pr(t, 1.0, 1.35), amp=1.0); s.line([(530, 90), (110, 430)], RED, 16, pr(t, 1.3, 1.65), amp=1.0)
    return s
def D_clock(t):
    s = Sp(640, 520); s.card(8, 12, 632, 508, seed=7); c = (320, 235)
    s.line(ell(c[0], c[1], 165, 165), INK, 9, pr(t, 0, .6), amp=1.6, seed=2)
    for i in range(12):
        a = math.radians(i * 30 - 90); s.line([(c[0] + 138 * math.cos(a), c[1] + 138 * math.sin(a)), (c[0] + 155 * math.cos(a), c[1] + 155 * math.sin(a))], INK, 6, pr(t, .3 + i * .03, .5 + i * .03), amp=.3)
    am = math.radians(t * 520 - 90); ah = math.radians(t * 45 - 90)
    s.line([c, (c[0] + 120 * math.cos(am), c[1] + 120 * math.sin(am))], INK, 7, amp=0); s.line([c, (c[0] + 80 * math.cos(ah), c[1] + 80 * math.sin(ah))], RED, 11, amp=0); s.disc(c[0], c[1], 11, INK)
    s.text('no time', 320, 462, 62, RED, pr(t, .7, 1.2)); return s
def person(s, x, y, k=1.0, col=INK, th=8):
    s.line(ell(x, y - 70 * k, 38 * k, 38 * k), col, th, amp=1.0, seed=1, closed=False); s.line([(x, y - 32 * k), (x, y + 70 * k)], col, th, amp=.8)
    s.line([(x - 55 * k, y + 20 * k), (x, y), (x + 55 * k, y + 20 * k)], col, th, amp=.8); s.line([(x - 45 * k, y + 150 * k), (x, y + 70 * k), (x + 45 * k, y + 150 * k)], col, th, amp=.8)
def D_team(t):
    s = Sp(640, 520); s.card(8, 12, 632, 508, seed=8)
    person(s, 190, 220, 1.1, INK, 8)
    s.line(rrect(325, 135, 560, 285, 14), INK, 7, pr(t, .5, 1.0), amp=1.2, seed=3, closed=True)
    if t > 1.0: s.fillpoly([(412, 170), (412, 250), (478, 210)], RED)
    s.arrow((262, 215), (318, 205), INK, 8, pr(t, 1.0, 1.4), 4)
    s.text('someone', 330, 395, 50, INK, pr(t, 1.2, 1.7)); s.text('dedicated', 330, 455, 54, RED, pr(t, 1.7, 2.3)); return s
def D_loop(t, period=2.2):
    s = Sp(640, 520); s.card(8, 12, 632, 508, seed=9); c = (320, 262); r = 150
    names = [('post', 320, 70, -90), ('analyze', 520, 262, 0), ('improve', 320, 455, 90), ('repeat', 120, 262, 180)]
    for i, (n, x, y, ang) in enumerate(names):
        p = pr(t, i * .35, i * .35 + .5); s.line(ell(c[0], c[1], r, r, ang + 18, ang + 72, 12), INK, 8, p, amp=1.0, seed=i)
        if p >= .98:
            e = math.radians(ang + 72); ex, ey = c[0] + r * math.cos(e), c[1] + r * math.sin(e); tg = e + math.pi / 2
            s.line([(ex - 24 * math.cos(tg - .5), ey - 24 * math.sin(tg - .5)), (ex, ey), (ex - 24 * math.cos(tg + .5), ey - 24 * math.sin(tg + .5))], INK, 8, amp=.3)
        s.text(n, x, y, 40, RED if int(t / (period / 4)) % 4 == i else INK, pr(t, .2 + i * .3, .6 + i * .3))
    a = math.radians(-90 + 360 * (t / period)); s.disc(c[0] + r * math.cos(a), c[1] + r * math.sin(a), 13, RED)
    s.text('week ' + str(int(t / period) + 1), 320, 262, 52, INK, pr(t, .8, 1.2)); return s
def D_flat(t):
    s = Sp(640, 520); s.card(8, 12, 632, 508, seed=10)
    s.line([(70, 450), (70, 90)], INK, 7, pr(t, 0, .3)); s.line([(70, 450), (590, 450)], INK, 7, pr(t, .1, .4))
    pts = [(78, 446), (150, 330), (210, 250), (260, 220), (300, 215), (340, 222), (390, 214), (440, 220), (490, 214), (570, 218)]
    xs = 0
    s.line([(70, 205), (590, 205)], RED, 5, pr(t, .3, .8), amp=.5)
    s.line(pts, INK, 9, pr(t, .4, 2.0), amp=1.8, seed=3)
    s.text('300', 330, 150, 76, RED, pr(t, 1.0, 1.5))
    if t > 2.0: s.text('stuck', 330, 355, 72, RED, pr(t, 2.0, 2.4))
    return s
def D_bars(t):
    s = Sp(640, 520); s.card(8, 12, 632, 508, seed=11); rg = random.Random(21); outs = {2, 5, 8, 10, 12}
    s.line([(50, 450), (590, 450)], INK, 7, pr(t, 0, .3))
    for i in range(14):
        x = 70 + i * 37; h = (330 if i in outs else rg.uniform(60, 150)) * eo(pr(t, .2 + i * .05, .6 + i * .05))
        if h > 3: s.line(rrect(x - 12, 450 - h, x + 12, 450, 3), INK, 5, 1.0, amp=.7, seed=i, closed=True)
        if i in outs and t > 1.8 + .22 * sorted(outs).index(i): s.line(ell(x, 450 - h - 20, 24, 24, 0, 340, 18), RED, 6, 1.0, amp=1.4, seed=i)
    s.line([(50, 335), (590, 335)], INK, 4, pr(t, 1.0, 1.4), amp=.5); s.text('5 outliers', 330, 70, 62, RED, pr(t, 1.8, 2.4)); return s
def D_check(t, items=('lighting', 'scripts', 'everything'), times=(.5, 1.2, 2.0), head='copy what works'):
    s = Sp(640, 520); s.card(8, 12, 632, 508, seed=12); s.text(head, 320, 62, 46, INK, pr(t, 0, .5))
    for i, (w, ti) in enumerate(zip(items, times)):
        y = 170 + i * 115; s.line(rrect(60, y - 36, 130, y + 36, 8), INK, 6, pr(t, .1 + i * .1, .4 + i * .1), amp=1.0, seed=i, closed=True)
        s.text(w, 380, y, 54, INK, pr(t, .2 + i * .15, .6 + i * .15)); s.check(95, y, pr(t, ti, ti + .25), RED, 11, 1.1)
    return s
def doc(s, x, y, w, h, col, lines, seed):
    s.line(rrect(x, y, x + w, y + h, 10), col, 6, 1.0, amp=1.2, seed=seed, closed=True)
    for j in range(lines): s.line([(x + 22, y + 40 + j * 34), (x + w - 22 - (j % 3) * 28, y + 40 + j * 34)], col, 5, 1.0, amp=1.0, seed=seed + j)
def D_spin(t):
    s = Sp(640, 520); s.card(8, 12, 632, 508, seed=13)
    doc(s, 50, 90, 220, 300, (110, 110, 110), 6, 1); s.text('theirs', 160, 430, 42, (110, 110, 110), pr(t, .3, .7))
    s.arrow((285, 240), (355, 240), INK, 9, pr(t, .8, 1.2), 5)
    if t > 1.2:
        doc(s, 370, 90, 220, 300, INK, 6, 2); s.line([(392, 130), (520, 130)], RED, 8, pr(t, 1.3, 1.6), amp=.8); s.line([(392, 198), (540, 198)], RED, 8, pr(t, 1.6, 1.9), amp=.8)
        s.star(560, 88, 34, rot=t * 2); s.text('yours', 480, 430, 52, RED, pr(t, 1.6, 2.1))
    return s
def D_leads(t, total=107):
    s = Sp(640, 520); s.card(8, 12, 632, 508, seed=14); p = eio(pr(t, .2, 2.0)); n = int(total * p)
    s.text(str(n), 320, 82, 96, RED, 1.0); s.text('new leads', 320, 168, 42, INK, pr(t, .3, .7))
    for i in range(60):
        r, c = divmod(i, 12); x = 66 + c * 46; y = 235 + r * 52
        if i < n * 60 / total:
            q = back(pr(t, .2 + i * .028, .2 + i * .028 + .25), 2.0); s.disc(x, y - 10 * q, 10 * q, INK); s.line(ell(x, y + 14 * q, 14 * q, 12 * q, 180, 360, 8), INK, 5, 1.0, amp=.3)
    return s
def D_cta(t, word='guide', tt=.4, cps=.13):
    s = Sp(640, 520); s.card(8, 12, 632, 508, seed=15); s.text('comment', 320, 70, 60, INK, pr(t, 0, .4))
    s.line(rrect(40, 130, 600, 230, 40), INK, 7, pr(t, .2, .6), amp=1.2, seed=2, closed=True)
    n = int(max(0, min(len(word), (t - tt) / cps))); txt = word[:n]
    if txt: s.text(txt, 60 + twidth(txt, 54, 700, 0, 'mark') / 2 + 10, 182, 54, INK)
    ts = tt + len(word) * cps + .25; s.disc(548, 180, 36, RED); s.arrow((548, 198), (548, 160), WHITE, 7, 1.0, 2) if t > .3 else None
    if t > ts:
        q = pr(t, ts, ts + .35); s.line(rrect(60, 270, 580, 390, 20), INK, 7, q, amp=1.2, seed=5, closed=True); s.check(120, 330, pr(t, ts + .35, ts + .65), RED, 12, 1.4)
        s.text('FREE GUIDE', 350, 318, 44, RED, pr(t, ts + .3, ts + .7)); s.text('in your DMs', 350, 362, 28, INK, pr(t, ts + .5, ts + .9))
    if t > ts + .7: s.line([(50, 450), (590, 450)], RED, 6, pr(t, ts + .7, ts + 1.1), amp=2.6, seed=3); s.text('comment "' + word + '"', 320, 480, 40, INK, pr(t, ts + .8, ts + 1.2))
    return s

# ---------------------------------------------------------------- small icon stickers (300x300, die-cut)
def rot_pts(pts, ang, c):
    a = math.radians(ang); return [(c[0] + (x - c[0]) * math.cos(a) - (y - c[1]) * math.sin(a), c[0] * 0 + c[1] + (x - c[0]) * math.sin(a) + (y - c[1]) * math.cos(a)) for x, y in pts]
def outl(s, pts, fill, th=7, seed=0): s.fillpoly(pts, fill); s.line(pts, INK, th, amp=1.1, seed=seed, closed=True)
def I_store(t):
    s = Sp(300, 300); outl(s, rrect(50, 130, 250, 255, 8), PAPER, seed=1); outl(s, [(130, 175), (172, 175), (172, 255), (130, 255)], BLUEC, 6, 2); outl(s, rrect(68, 160, 112, 205, 5), SKY, 6, 3)
    outl(s, [(25, 78), (275, 78), (292, 135), (8, 135)], RED, 7, 4)
    for i in range(1, 6, 2): s.fillpoly([(25 + i * 41.7, 80), (25 + (i + 1) * 41.7, 80), (14 + (i + 1) * 46, 132), (14 + i * 46, 132)], WHITE)
    s.line([(25, 78), (275, 78), (292, 135), (8, 135)], INK, 7, amp=1.0, seed=4, closed=True); return s
def I_play(t):
    s = Sp(300, 300); outl(s, rrect(25, 75, 275, 225, 40), RED, 8, 1); s.fillpoly([(120, 115), (120, 185), (185, 150)], WHITE); s.line([(120, 115), (120, 185), (185, 150)], INK, 5, amp=.4, closed=True); return s
def I_rocket(t):
    s = Sp(300, 300); c = (150, 150); fl = 14 * math.sin(t * 22)
    outl(s, rot_pts([(130, 215), (170, 215), (150, 275 + fl)], 40, c), YEL, 6, 5); outl(s, rot_pts([(138, 215), (162, 215), (150, 255 + fl)], 40, c), RED, 4, 6)
    outl(s, rot_pts(ell(150, 140, 44, 95, 0, 360, 20), 40, c), PAPER, 7, 1)
    outl(s, rot_pts([(106, 120), (80, 205), (112, 190)], 40, c), RED, 6, 2); outl(s, rot_pts([(194, 120), (220, 205), (188, 190)], 40, c), RED, 6, 3)
    outl(s, rot_pts([(116, 75), (150, 30), (184, 75)], 40, c), RED, 6, 4); w = rot_pts([(150, 130)], 40, c)[0]; s.disc(w[0], w[1], 22, INK); s.disc(w[0], w[1], 15, SKY); return s
def I_fire(t):
    s = Sp(300, 300); f = 6 * math.sin(t * 17)
    outl(s, [(150, 30 + f), (200, 120), (232, 195), (195, 260), (105, 260), (68, 195), (92, 125), (125, 165)], RED, 8, 1); outl(s, [(150, 120 - f), (186, 190), (170, 245), (130, 245), (112, 195)], YEL, 6, 2); return s
def I_bulb(t):
    s = Sp(300, 300)
    for i in range(8):
        a = math.radians(-90 + i * 45 - 90 + 90); p = pr(t, .2 + i * .04, .4 + i * .04); a2 = math.radians(i * 45 - 90)
        s.line([(150 + 100 * math.cos(a2), 120 + 100 * math.sin(a2)), (150 + 128 * math.cos(a2), 120 + 128 * math.sin(a2))], INK, 7, p, amp=.3)
    outl(s, ell(150, 120, 68, 68), YEL, 8, 1); outl(s, rrect(118, 182, 182, 232, 8), LGREY, 7, 2); s.line([(130, 205), (170, 205)], INK, 5, amp=.4); return s
def I_gift(t):
    s = Sp(300, 300); outl(s, rrect(55, 135, 245, 255, 6), RED, 8, 1); outl(s, rrect(40, 105, 260, 145, 6), RED, 8, 2); outl(s, [(133, 105), (167, 105), (167, 255), (133, 255)], WHITE, 6, 3)
    outl(s, ell(118, 82, 34, 24), WHITE, 6, 4); outl(s, ell(182, 82, 34, 24), WHITE, 6, 5); s.disc(150, 92, 12, WHITE); s.line(ell(150, 92, 12, 12), INK, 5, amp=.2); return s
def I_warn(t):
    s = Sp(300, 300); outl(s, [(150, 38), (275, 248), (25, 248)], YEL, 10, 1); s.text('!', 150, 168, 130, INK); return s
def I_mag(t):
    s = Sp(300, 300); s.line([(185, 185), (262, 262)], INK, 30, amp=.4); s.line([(185, 185), (262, 262)], RED, 16, amp=.4); outl(s, ell(125, 125, 78, 78), (245, 240, 230), 11, 1); s.line(ell(125, 125, 56, 56, 200, 270, 8), WHITE, 9, amp=.2); return s
def I_gear(t):
    s = Sp(300, 300); pts = []
    for i in range(24): a = math.radians(i * 15 + t * 40); r = 108 if (i // 2) % 2 == 0 else 80; pts.append((150 + r * math.cos(a), 150 + r * math.sin(a)))
    outl(s, pts, LGREY, 8, 1); s.disc(150, 150, 34, PAPER); s.line(ell(150, 150, 34, 34), INK, 7, amp=.3); return s
def I_trophy(t):
    s = Sp(300, 300); outl(s, [(75, 45), (225, 45), (212, 140), (172, 190), (128, 190), (88, 140)], YEL, 8, 1)
    s.line(ell(70, 95, 38, 34, 90, 270, 10), INK, 9, amp=.4); s.line(ell(230, 95, 38, 34, -90, 90, 10), INK, 9, amp=.4)
    outl(s, rrect(138, 188, 162, 235, 3), YEL, 6, 2); outl(s, rrect(95, 232, 205, 262, 6), RED, 7, 3); s.star(150, 105, 28, PAPER); return s
def I_mic(t):
    s = Sp(300, 300); outl(s, rrect(112, 30, 188, 150, 36), LGREY, 8, 1); s.line(ell(150, 130, 62, 62, 10, 170, 14), INK, 8, amp=.4); s.line([(150, 192), (150, 250)], INK, 8, amp=.3); s.line([(105, 252), (195, 252)], INK, 8, amp=.3)
    s.line([(70, 70), (230, 235)], RED, 20, pr(t, .15, .45), amp=.5); s.line([(230, 70), (70, 235)], RED, 20, pr(t, .4, .7), amp=.5); return s
def I_chat(t):
    s = Sp(300, 300); outl(s, rrect(28, 60, 272, 200, 36), PAPER, 8, 1); outl(s, [(80, 195), (70, 250), (130, 198)], PAPER, 8, 2); s.fillpoly([(82, 190), (126, 190), (74, 232)], PAPER)
    for i in range(3): s.disc(95 + i * 55, 130 - 8 * max(0, math.sin(t * 8 - i * .8)), 14, INK)
    return s
def I_copy(t):
    s = Sp(300, 300); doc(s, 45, 55, 150, 190, (110, 110, 110), 4, 1); s.fillpoly(rrect(110, 95, 260, 285, 10), PAPER); doc(s, 110, 95, 150, 190, INK, 4, 2); s.check(185, 245, 1.0, RED, 11, 1.0); return s
def I_book(t):
    s = Sp(300, 300); outl(s, [(35, 95), (150, 120), (150, 245), (35, 220)], PAPER, 8, 1); outl(s, [(150, 120), (265, 95), (265, 220), (150, 245)], PAPER, 8, 2)
    for j in range(4): s.line([(55, 130 + j * 22), (130, 148 + j * 22)], INK, 4, amp=.5); s.line([(170, 148 + j * 22), (245, 130 + j * 22)], INK, 4, amp=.5)
    s.star(150, 70, 26, rot=t * 2); return s

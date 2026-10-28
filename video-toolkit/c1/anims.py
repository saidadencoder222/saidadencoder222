"""Full-screen animations. Each: f(cv, tl, d) draws straight on the 1080x1920 frame (content zone y 330-1400; captions sit at y 1500)."""
from cc import *
LIGHT = (205, 205, 210); DIM = (70, 70, 78); PANEL = (22, 22, 27)
def T(cv, s, x, y, size, col=WHITE, wght=800, track=-2, a=1., glow=0., sc=1.): ptext(cv, s, size, x, y, col, wght, track, a, sc, 0, glow, .0)
def U(cv, s, x, y, size, col=LIGHT, wght=600, a=1., track=6): ptext(cv, s, size, x, y, col, wght, track, a)
def lerpc(a, b, k): return tuple(int(a[i] * (1 - k) + b[i] * k) for i in range(3))
def patch(cv, p, m, x0, y0):
    h, w = m.shape; X0, Y0 = max(x0, 0), max(y0, 0); X1, Y1 = min(x0 + w, cv.shape[1]), min(y0 + h, cv.shape[0])
    if X0 >= X1 or Y0 >= Y1: return
    mm = m[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0, None]; roi = cv[Y0:Y1, X0:X1].astype(np.float32)
    cv[Y0:Y1, X0:X1] = np.clip(roi * (1 - mm) + p[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * mm, 0, 255).astype(np.uint8)
def rr_gold(cv, x0, y0, x1, y1, r, a=1.0):
    r = max(4, r * .3); x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1); h, w = y1 - y0, x1 - x0
    if h < 3 or w < 3 or a <= .01: return
    g = GOLDF(h, w); mk = np.zeros((h, w), np.uint8); cv2.fillPoly(mk, [(rrect_pts(0, 0, w - 1, h - 1, min(r, h // 2, w // 2)) * 16).astype(np.int32)], 255, cv2.LINE_AA, 4)
    patch(cv, g, mk.astype(np.float32) / 255 * a, x0, y0)
def check(cv, x, y, k, col=INK, th=10, s=1.0):
    p0 = (x - 18 * s, y + 2 * s); p1 = (x - 5 * s, y + 15 * s); p2 = (x + 20 * s, y - 14 * s)
    if k <= 0: return
    u = clamp(k * 2); a = (p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u)
    cv2.line(cv, (int(p0[0]), int(p0[1])), (int(a[0]), int(a[1])), col, th, cv2.LINE_AA)
    if k > .5:
        v = clamp((k - .5) * 2); b = (p1[0] + (p2[0] - p1[0]) * v, p1[1] + (p2[1] - p1[1]) * v); cv2.line(cv, (int(p1[0]), int(p1[1])), (int(b[0]), int(b[1])), col, th, cv2.LINE_AA)
def star(L, x, y, r, col, rot=0):
    pts = [(x + (r if i % 2 == 0 else r * .22) * math.cos(rot + i * math.pi / 4), y + (r if i % 2 == 0 else r * .22) * math.sin(rot + i * math.pi / 4)) for i in range(8)]
    cv2.fillPoly(L, [(np.array(pts) * 16).astype(np.int32)], col, cv2.LINE_AA, 4)
def label(cv, s, y=400, a=1.): U(cv, s.upper(), 540, y, 34, (150, 150, 160), 600, a, 10)
def Lz(): return np.zeros((H, W, 3), np.uint8)

# 1 growth ----------------------------------------------------------------
def A_growth(n0=8, n1=40, lab='followers', badge='+400%', t0=.35, dur=2.4):
    def f(cv, t, d):
        p = eio((t - t0) / dur); val = n0 + (n1 - n0) * p; label(cv, lab, 440, sm(t / .4))
        T(cv, f'{val:.0f}K', 540, 650, 330, lerpc(WHITE, GOLD_L, p), 800, -6, glow=.3 + .35 * p, sc=back(t / .5, 1.2))
        x0, x1, yb, yt = 90, 990, 1340, 860
        for i in range(5): cv2.line(cv, (x0, yt + i * (yb - yt) // 4), (x1, yt + i * (yb - yt) // 4), (36, 36, 42), 2, cv2.LINE_AA)
        fn = lambda u: (math.exp(3.2 * u) - 1) / (math.exp(3.2) - 1)
        n = max(int(p * 100), 2); pts = np.array([(x0 + (x1 - x0) * i / 100, yb - (yb - yt) * fn(i / 100)) for i in range(n + 1)], np.float32)
        poly = np.vstack([pts, [[pts[-1][0], yb], [x0, yb]]]).astype(np.int32)
        ov = cv.copy(); cv2.fillPoly(ov, [poly], (30, 20, 96), cv2.LINE_AA); cv2.addWeighted(ov, .55, cv, .45, 0, cv)
        L = Lz(); cv2.polylines(L, [(pts * 16).astype(np.int32)], False, GOLD, 12, cv2.LINE_AA, 4)
        hx, hy = pts[-1]; pulse = 1 + .22 * math.sin(t * 8); cv2.circle(L, (int(hx), int(hy)), int(20 * pulse), GOLD_L, -1, cv2.LINE_AA); glow_add(cv, L, 14, 1.0)
        cv2.circle(cv, (int(hx), int(hy)), 13, WHITE, -1, cv2.LINE_AA)
        for k in range(5): U(cv, ['START', 'WK 1', 'WK 2', 'WK 3', 'WK 4.5'][k], x0 + (x1 - x0) * k / 4 + (18 if k == 0 else -18 if k == 4 else 0), yb + 46, 26, (125, 125, 135), 600, 1, 3)
        if badge and p > .97:
            q = back((t - t0 - dur * .97) / .45); w, h = 230 * q, 80 * q; rr_gold(cv, 470 - w, 980 - h, 470 + w, 980 + h, 70)
            if q > .6: T(cv, badge, 470, 980, 76, INK, 800, -1)
    return f

# 2 leads grid ------------------------------------------------------------
def A_leads(total=107, t0=.35, dur=2.4, lab='new leads'):
    def f(cv, t, d):
        p = eio((t - t0) / dur); n = int(total * p); label(cv, lab, 440, sm(t / .4))
        T(cv, str(n), 540, 650, 330, lerpc(WHITE, GOLD_L, p), 800, -6, glow=.35, sc=back(t / .5, 1.2))
        L = Lz()
        for i in range(112):
            r, c = divmod(i, 14); x = 98 + c * 68; y = 900 + r * 68; lo, hi = 0., 1.
            for _ in range(14):
                mid = (lo + hi) / 2
                if eio(mid) * total > i: hi = mid
                else: lo = mid
            ti = t0 + dur * hi
            if i < total and t > ti:
                q = back((t - ti) / .22, 2.2); cv2.circle(L, (x, y), int(25 * q), GOLD, -1, cv2.LINE_AA); cv2.circle(cv, (x, y), int(25 * q), lerpc(GOLD, GOLD_L, .5 * max(0, 1 - (t - ti) / .4)), -1, cv2.LINE_AA)
            else: cv2.circle(cv, (x, y), 8 if i < total else 4, DIM, -1, cv2.LINE_AA)
        glow_add(cv, L, 10, .7)
        if p > .98: U(cv, 'FROM 8K TO 40K FOLLOWERS', 540, 1400, 30, GOLD_L, 700, sm((t - t0 - dur) / .5), 5)
    return f

# 3 calendar --------------------------------------------------------------
def A_calendar(t0=.4, step=.12):
    def f(cv, t, d):
        label(cv, 'posting schedule', 400, sm(t / .4)); L = Lz()
        for c, ch in enumerate('MTWTFSS'): U(cv, ch, 110 + c * 143, 470, 36, (140, 140, 150), 700, 1, 2)
        k = 0
        for r in range(4):
            for c in range(7):
                x = 110 + c * 143; y = 620 + r * 190; ti = t0 + k * step; k += 1
                rr(cv, x - 56, y - 84, x + 56, y + 84, 24, (24, 24, 29), (54, 54, 62), 2)
                if t > ti:
                    q = back((t - ti) / .3, 2.0); w, h = 56 * q, 84 * q; rr_gold(cv, x - w, y - h, x + w, y + h, 24, .95)
                    cv2.rectangle(L, (int(x - w), int(y - h)), (int(x + w), int(y + h)), (24, 18, 120), -1); check(cv, x, y, (t - ti - .12) / .25, INK, 11, 1.4)
        glow_add(cv, L, 16, .5)
        q = back((t - t0 - 28 * step - .1) / .4)
        if q > 0:
            w = 400 * q; rr(cv, 540 - w, 1400 - 48 * q, 540 + w, 1400 + 48 * q, 48, (22, 22, 26), GOLD, 3)
            if q > .6: T(cv, 'routine locked in', 540, 1400, 50, WHITE, 700, -1, glow=.3)
    return f

# 4 funnel ----------------------------------------------------------------
def A_funnel(times=(.3, 1.8, 3.2), labels=(('6 SEC', 'reach'), ('40 SEC', 'pain points'), ('THE', 'GUIDE'))):
    def f(cv, t, d):
        label(cv, 'the funnel', 400, sm(t / .4)); L = Lz()
        tiers = [(450, 700, 940, 720), (730, 980, 680, 460), (1010, 1230, 440, 250)]
        for i, (ya, yb, wa, wb) in enumerate(tiers):
            q = sm((t - times[i]) / .5)
            if q <= 0: continue
            sh = (1 - q) * 50; pts = np.array([(540 - wa / 2, ya - sh), (540 + wa / 2, ya - sh), (540 + wb / 2, yb - sh), (540 - wb / 2, yb - sh)], np.float32)
            ov = cv.copy(); cv2.fillPoly(ov, [(pts * 16).astype(np.int32)], (34, 34, 41) if i < 2 else (38, 28, 156), cv2.LINE_AA, 4); cv2.addWeighted(ov, .94 * q, cv, 1 - .94 * q, 0, cv)
            cv2.polylines(cv, [(pts * 16).astype(np.int32)], True, lerpc(DIM, GOLD, q), 4, cv2.LINE_AA, 4)
            l1, l2 = labels[i]; ym = (ya + yb) / 2 - sh
            T(cv, l1, 540, ym - 26, 84 if i < 2 else 62, WHITE if i < 2 else GOLD_L, 800, -2, a=q, glow=.2); U(cv, l2.upper(), 540, ym + 54, 30, GOLD_L if i < 2 else WHITE, 700, q, 7)
        rg = random.Random(5)
        for i in range(60):
            ph = rg.random(); sp = rg.uniform(.14, .24); u = (ph + t * sp) % 1.0; y = 450 + u * 780
            wy = np.interp(y, [450, 700, 730, 980, 1010, 1230], [940, 720, 680, 460, 440, 250]); x = 540 + rg.uniform(-.46, .46) * wy
            if t < times[0] + .3 or (y > 720 and t < times[1]) or (y > 1000 and t < times[2]): continue
            cv2.circle(L, (int(x), int(y)), 7, GOLD, -1, cv2.LINE_AA)
        glow_add(cv, L, 8, 1.0)
        q = sm((t - times[2] - .6) / .5)
        if q > 0:
            cv2.arrowedLine(cv, (540, 1250), (540, int(1250 + 56 * q)), GOLD, 7, cv2.LINE_AA, 0, .45)
            if q > .5: rr_gold(cv, 330, 1318, 750, 1410, 46, q); T(cv, 'FREE GUIDE', 540, 1364, 50, INK, 800, 0, a=q)
    return f

# 5 chaos -----------------------------------------------------------------
def A_chaos(tx=1.3):
    def f(cv, t, d):
        label(cv, 'no structure', 400, sm(t / .4)); rg = random.Random(12)
        for i in range(14):
            x0, y0 = rg.uniform(170, 910), rg.uniform(560, 1180); w, h = rg.uniform(170, 280), rg.uniform(230, 360); ph = rg.uniform(0, 6.3); ax, ay = rg.uniform(30, 90), rg.uniform(30, 80); rot = rg.uniform(-40, 40) + 25 * math.sin(t * 1.6 + ph)
            x = x0 + ax * math.sin(t * 1.1 + ph); y = y0 + ay * math.cos(t * .9 + ph); fade = sm((t - .1 - i * .05) / .3)
            box = cv2.boxPoints(((x, y), (w, h), rot)).astype(np.float32); pts = (box * 16).astype(np.int32)
            ov = cv.copy(); cv2.fillPoly(ov, [pts], (38, 38, 45), cv2.LINE_AA, 4); cv2.addWeighted(ov, fade, cv, 1 - fade, 0, cv)
            cv2.polylines(cv, [pts], True, lerpc(DIM, (100, 100, 110), fade), 3, cv2.LINE_AA, 4)
            c = np.array([x, y]); tri = np.array([c + [-18, -24], c + [-18, 24], c + [24, 0]]); cv2.fillPoly(cv, [(tri * 16).astype(np.int32)], (125, 125, 136), cv2.LINE_AA, 4)
        q = sm((t - tx) / .25)
        if q > 0:
            L = Lz(); sh = (6 * math.sin(t * 60)) * max(0, 1 - (t - tx) / .5)
            for a, b in (((150, 480), (930, 1280)), ((930, 480), (150, 1280))):
                e = (a[0] + (b[0] - a[0]) * q + sh, a[1] + (b[1] - a[1]) * q); cv2.line(L, (int(a[0] + sh), int(a[1])), (int(e[0]), int(e[1])), CRIM, 34, cv2.LINE_AA)
            glow_add(cv, L, 18, .9); T(cv, 'NO RANDOM', 540, 1370, 110, CRIM, 800, -2, a=q, glow=.5)
    return f

# 6 clock -----------------------------------------------------------------
def A_clock(dur=1.5):
    def f(cv, t, d):
        c = (540, 850); r = 360; L = Lz(); label(cv, 'time left to create', 400, sm(t / .4)); q = back(t / .5, 1.2)
        cv2.circle(cv, c, int(r * q), (26, 26, 31), -1, cv2.LINE_AA); cv2.circle(cv, c, int(r * q), (64, 64, 72), 4, cv2.LINE_AA)
        for i in range(60):
            a = math.radians(i * 6 - 90); l = 32 if i % 5 == 0 else 12
            cv2.line(cv, (int(c[0] + (r - 20) * math.cos(a)), int(c[1] + (r - 20) * math.sin(a))), (int(c[0] + (r - 20 - l) * math.cos(a)), int(c[1] + (r - 20 - l) * math.sin(a))), (155, 155, 165) if i % 5 == 0 else (80, 80, 90), 5 if i % 5 == 0 else 2, cv2.LINE_AA)
        p = clamp((t - .2) / dur); cv2.ellipse(L, c, (r + 34, r + 34), 0, -90, -90 + 360 * (1 - p), lerpc(GOLD, CRIM, p), 18, cv2.LINE_AA)
        am = t * 2 * math.pi * 1.7 - math.pi / 2; ah = t * 2 * math.pi * .14 - math.pi / 2
        cv2.line(L, c, (int(c[0] + (r - 60) * math.cos(am)), int(c[1] + (r - 60) * math.sin(am))), GOLD_L, 9, cv2.LINE_AA)
        cv2.line(L, c, (int(c[0] + (r - 150) * math.cos(ah)), int(c[1] + (r - 150) * math.sin(ah))), WHITE, 15, cv2.LINE_AA)
        glow_add(cv, L, 14, .8); cv2.circle(cv, c, 18, GOLD_L, -1, cv2.LINE_AA)
        fl = .6 + .4 * math.sin(t * 9) if p > .85 else 1
        T(cv, 'NO TIME', 540, 1330, 150, lerpc(WHITE, CRIM, p), 800, -3, a=fl * sm((t - .3) / .4), glow=.4)
    return f

# 7 team ------------------------------------------------------------------
def person(cv, x, y, s, col, th=9):
    cv2.circle(cv, (int(x), int(y - 30 * s)), int(32 * s), col, th, cv2.LINE_AA); cv2.ellipse(cv, (int(x), int(y + 84 * s)), (int(66 * s), int(58 * s)), 0, 180, 360, col, th, cv2.LINE_AA)
def A_team():
    def f(cv, t, d):
        label(cv, 'who makes your videos?', 400, sm(t / .4)); c = (540, 880); L = Lz(); q = back((t - .25) / .5)
        tiles = [(230, 600, 'v'), (850, 600, 'c'), (230, 1160, 'w'), (850, 1160, 'g')]
        for i, (x, y, k) in enumerate(tiles):
            a = sm((t - .9 - i * .25) / .4)
            if a <= 0: continue
            cv2.line(L, c, (x, y), (int(GOLD[0] * .5 * a), int(GOLD[1] * .5 * a), int(GOLD[2] * .5 * a)), 3, cv2.LINE_AA)
            u = ((t * .6 + i * .27) % 1); cv2.circle(L, (int(c[0] + (x - c[0]) * u), int(c[1] + (y - c[1]) * u)), 9, GOLD_L, -1, cv2.LINE_AA)
            rr(cv, x - 140, y - 105, x + 140, y + 105, 30, (24, 24, 29), lerpc(DIM, GOLD, a), 3)
            if k == 'v': tri = np.array([(x - 28, y - 36), (x - 28, y + 36), (x + 38, y)], np.float32); cv2.fillPoly(cv, [(tri * 16).astype(np.int32)], GOLD_L, cv2.LINE_AA, 4)
            elif k == 'c':
                for j in range(3): cv2.line(cv, (x - 78, y - 42 + j * 40), (x + 78 - j * 36, y - 42 + j * 40), GOLD_L, 9, cv2.LINE_AA)
            elif k == 'w':
                for j in range(9): hh = 18 + 56 * abs(math.sin(j * 1.3 + t * 5)); cv2.line(cv, (x - 84 + j * 21, int(y - hh)), (x - 84 + j * 21, int(y + hh)), GOLD_L, 8, cv2.LINE_AA)
            else:
                for j in range(4): cv2.rectangle(cv, (x - 78 + j * 42, int(y + 58 - 30 - j * 21)), (x - 51 + j * 42, y + 58), GOLD_L, -1)
        cv2.circle(L, c, int(170 * q), GOLD, 8, cv2.LINE_AA); glow_add(cv, L, 16, .9)
        cv2.circle(cv, c, int(162 * q), (24, 24, 29), -1, cv2.LINE_AA); cv2.circle(cv, c, int(170 * q), GOLD, 5, cv2.LINE_AA)
        if q > .5: person(cv, c[0], c[1] - 10, 1.9, GOLD_L, 10)
        T(cv, 'someone dedicated', 540, 1370, 78, WHITE, 800, -2, a=sm((t - 1.2) / .5), glow=.3)
    return f

# 8 loop ------------------------------------------------------------------
def A_loop(period=2.4):
    def f(cv, t, d):
        label(cv, 'every single week', 400, sm(t / .4)); c = (540, 880); r = 340; L = Lz()
        names = ['POST', 'ANALYZE', 'IMPROVE', 'REPEAT']; ang = [-90, 0, 90, 180]
        cv2.circle(cv, c, r, (38, 38, 45), 3, cv2.LINE_AA)
        ph = ((t - .3) / period) if t > .3 else 0; head = -90 + 360 * ph; n = 70
        for k in range(n):
            a = math.radians(head - 80 * k / n); a2 = math.radians(head - 80 * (k + 1) / n); w = 1 - k / n
            cv2.line(L, (int(c[0] + r * math.cos(a)), int(c[1] + r * math.sin(a))), (int(c[0] + r * math.cos(a2)), int(c[1] + r * math.sin(a2))), (int(GOLD[0] * w), int(GOLD[1] * w), int(GOLD[2] * w)), int(4 + 14 * w), cv2.LINE_AA)
        hx, hy = c[0] + r * math.cos(math.radians(head)), c[1] + r * math.sin(math.radians(head)); cv2.circle(L, (int(hx), int(hy)), 20, GOLD_L, -1, cv2.LINE_AA); glow_add(cv, L, 14, .9)
        for nm, a in zip(names, ang):
            x = c[0] + r * math.cos(math.radians(a)); y = c[1] + r * math.sin(math.radians(a)); dd = abs(((head - a + 180) % 360) - 180); hot = clamp(1 - dd / 40); w = 140 if nm in ('POST', 'REPEAT') else 170
            if hot > .05: rr_gold(cv, x - w, y - 48, x + w, y + 48, 48, .35 + .65 * hot)
            rr(cv, x - w, y - 48, x + w, y + 48, 48, (22, 22, 27) if hot < .5 else None, lerpc(DIM, GOLD, hot), 3)
            U(cv, nm, x, y, 40, lerpc(LIGHT, INK, hot), 800, 1, 5)
        wk = int(max(ph, 0)) + 1; U(cv, 'WEEK', 540, 760, 44, (150, 150, 160), 600, 1, 12); T(cv, str(wk), 540, 920, 270, WHITE, 800, 0, glow=.3)
    return f

# 9 stuck -----------------------------------------------------------------
def A_stuck(tstuck=2.0):
    def f(cv, t, d):
        p = eo((t - .3) / 1.5); n = int(300 * p); label(cv, 'views', 440, sm(t / .4)); stuck = t > tstuck
        T(cv, str(n), 540, 650, 360, lerpc(WHITE, CRIM, sm((t - tstuck) / .4)), 800, -6, glow=.4, sc=1 + (.05 * math.sin(t * 40) * max(0, 1 - (t - tstuck) / .6) if stuck else 0))
        x0, x1, yb, yt = 90, 990, 1360, 880
        for i in range(5): cv2.line(cv, (x0, yt + i * 120), (x1, yt + i * 120), (36, 36, 42), 2, cv2.LINE_AA)
        for xx in range(x0, x1, 36): cv2.line(cv, (xx, yt + 40), (xx + 18, yt + 40), CRIM, 3, cv2.LINE_AA)
        U(cv, 'THE CEILING', 880, yt + 6, 28, CRIM, 700, sm((t - 1) / .4), 5)
        L = Lz(); pp = clamp((t - .3) / 3.4); pts = []
        for i in range(0, int(pp * 100) + 1):
            u = i / 100; xx = x0 + (x1 - x0) * u; y = yb - (yb - (yt + 40)) * min(1, (u / .3)) ** .6 + (8 * math.sin(u * 60) if u > .3 else 0); pts.append((xx, y))
        if len(pts) > 1: cv2.polylines(L, [(np.array(pts, np.float32) * 16).astype(np.int32)], False, lerpc(GOLD, CRIM, clamp((pp - .3) * 3)), 12, cv2.LINE_AA, 4); glow_add(cv, L, 14, .9)
        q = back((t - tstuck - .2) / .35)
        if q > 0:
            ov = np.zeros_like(cv); T(ov, 'STUCK', 540, 1180, 230, CRIM, 800, 2, sc=q); M = cv2.getRotationMatrix2D((540, 1180), 8, 1); ov = cv2.warpAffine(ov, M, (W, H)); cv2.add(cv, ov, cv)
    return f

# 10 outliers -------------------------------------------------------------
def A_outliers(tout=2.0):
    def f(cv, t, d):
        label(cv, 'top videos in your niche', 400, sm(t / .4)); rg = random.Random(21); n = 18; bw = 40; gap = 12; x0 = (W - (n * (bw + gap) - gap)) // 2 + 0; yb = 1360
        hs = [rg.uniform(120, 300) for _ in range(n)]; outs = {3: 720, 7: 600, 10: 780, 13: 650, 16: 700}; L = Lz(); avg = 380
        for i in range(n):
            x = x0 + i * (bw + gap); g = eo((t - .25 - i * .05) / .5); h = outs.get(i, hs[i]) * g; idx = list(outs).index(i) if i in outs else 0; hot = i in outs and t > tout + idx * .22
            if h < 2: continue
            if hot:
                q = sm((t - tout - idx * .22) / .3); rr_gold(cv, x, yb - h, x + bw, yb, 8, .35 + .65 * q); cv2.rectangle(L, (x, int(yb - h)), (x + bw, yb), (24, 18, 110), -1); star(L, x + bw / 2, yb - h - 40 * q, 20 * q, GOLD_L, t * 2)
            else: rr(cv, x, int(yb - h), x + bw, yb, 8, (46, 46, 53), None)
        glow_add(cv, L, 14, .8); q = sm((t - 1.4) / .4); xx = 70
        while xx < 1010: cv2.line(cv, (xx, yb - avg), (min(xx + 22, 1010), yb - avg), (185, 185, 195), 3, cv2.LINE_AA); xx += 40
        U(cv, 'NICHE AVERAGE', 880, yb - avg - 36, 26, (185, 185, 195), 600, q, 4)
        if t > tout: T(cv, '5 outliers', 540, 500, 120, GOLD_L, 800, -2, a=sm((t - tout) / .4), glow=.4)
    return f

# 11 checklist ------------------------------------------------------------
def A_check(items=('Lighting', 'Scripts', 'Everything'), times=(.6, 1.6, 2.6), head='copy what works'):
    def f(cv, t, d):
        label(cv, head, 420, sm(t / .4)); L = Lz()
        for i, (s, ti) in enumerate(zip(items, times)):
            y = 640 + i * 260; a = sm((t - .2 - i * .15) / .4); xo = (1 - a) * 120
            if a <= 0: continue
            on = t > ti
            rr(cv, 90 + xo, y - 100, 990 + xo, y + 100, 40, (24, 24, 29), GOLD if on else DIM, 3)
            bx = 205 + xo
            if on:
                rr_gold(cv, bx - 56, y - 56, bx + 56, y + 56, 22); cv2.rectangle(L, (int(bx - 56), int(y - 56)), (int(bx + 56), int(y + 56)), (24, 18, 120), -1); check(cv, bx, y, (t - ti - .05) / .3, INK, 13, 1.7)
            else: rr(cv, bx - 56, y - 56, bx + 56, y + 56, 22, None, (92, 92, 100), 4)
            T(cv, s, 600 + xo, y, fitsize(s, 84, 640, 800, -2), WHITE if on else (150, 150, 160), 800, -2, a=a, glow=.25 if on else 0)
        glow_add(cv, L, 14, .7)
    return f

# 12 spin -----------------------------------------------------------------
def A_spin():
    def f(cv, t, d):
        label(cv, 'copy, then make it yours', 400, sm(t / .4)); L = Lz()
        a1 = back((t - .3) / .5); a2 = back((t - 1.4) / .55)
        def tile(cx, cy, rot, gold, k):
            box = cv2.boxPoints(((cx, cy), (400 * k, 600 * k), rot)).astype(np.float32); pts = (box * 16).astype(np.int32)
            cv2.fillPoly(cv, [pts], (28, 28, 34) if not gold else (30, 24, 44), cv2.LINE_AA, 4); cv2.polylines(cv, [pts], True, GOLD if gold else (112, 112, 120), 4, cv2.LINE_AA, 4)
            if gold: cv2.polylines(L, [pts], True, GOLD, 9, cv2.LINE_AA, 4)
        tile(300, 870, -5, False, a1)
        if a1 > .5:
            for j in range(6): cv2.line(cv, (170, 700 + j * 56), (430 - (j % 2) * 90, 700 + j * 56), (98, 98, 106), 9, cv2.LINE_AA)
            T(cv, 'THEIRS', 300, 1250, 56, (150, 150, 160), 800, 4, a=a1)
        if a2 > 0:
            cv2.arrowedLine(cv, (505, 870), (int(505 + 70 * min(a2, 1)), 870), GOLD, 8, cv2.LINE_AA, 0, .5)
            tile(780, 870, 5, True, a2)
            if a2 > .5:
                for j in range(6): cv2.line(cv, (650, 700 + j * 56), (910 - (j % 2) * 90, 700 + j * 56), GOLD_L if j in (0, 3) else (90, 80, 235), 9, cv2.LINE_AA)
                T(cv, 'YOURS', 780, 1250, 56, GOLD_L, 800, 4, a=a2, glow=.4)
                for k, (sx, sy, sr) in enumerate(((930, 600, 34), (640, 1130, 24), (950, 1090, 18))):
                    tw = .5 + .5 * math.sin(t * 5 + k * 2); star(L, sx, sy, sr * tw * min(a2, 1) + 4, GOLD_L, t + k)
        glow_add(cv, L, 14, .9); q = sm((t - 2.4) / .4); T(cv, '+ your own story', 540, 1370, 86, WHITE, 800, -2, a=q, glow=.35)
    return f

# 13 CTA ------------------------------------------------------------------
def A_cta(word='GUIDE', sub=None, tt=.5, cps=.17):
    def f(cv, t, d):
        L = Lz(); a = sm((t - .1) / .4); T(cv, 'comment', 540, 500, 190, WHITE, 800, -4, a=a, glow=.4, sc=back(t / .5, 1.2))
        if sub: U(cv, sub.upper(), 540, 640, 30, GOLD_L, 700, a, 6)
        yb = 760; rr(cv, 70, yb - 84, 1010, yb + 84, 84, (24, 24, 29), (84, 84, 94), 3)
        n = int(max(0, min(len(word), (t - tt) / cps))); cur = (t * 2.2) % 1 < .6
        txt = word[:n].lower(); tw = twidth(txt, 96, 700, -2) if txt else 0
        if n == 0: U(cv, 'Add a comment…', 380, yb, 44, (92, 92, 102), 500, 1, 1)
        if txt: T(cv, txt, 150 + tw / 2, yb, 96, GOLD_L, 700, -2)
        if cur: cv2.line(cv, (int(160 + tw), yb - 46), (int(160 + tw), yb + 46), GOLD, 6, cv2.LINE_AA)
        ts = tt + len(word) * cps + .35; pr = clamp(1 - abs(t - ts) / .15); bx = 920; rad = int(64 * (1 - .15 * pr)); hot = t > ts - .3
        cv2.circle(L, (bx, yb), rad, GOLD, -1, cv2.LINE_AA); glow_add(cv, L, 16, .8 if hot else .2); cv2.circle(cv, (bx, yb), rad, GOLD if hot else (80, 70, 120), -1, cv2.LINE_AA)
        cv2.arrowedLine(cv, (bx, yb + 22), (bx, yb - 28), INK, 10, cv2.LINE_AA, 0, .55)
        q = back((t - ts - .15) / .5)
        if q > 0:
            y = 1080 - (1 - min(q, 1)) * 50; w = 460 * min(q, 1); rr(cv, 540 - w, y - 140, 540 + w, y + 140, 50, (24, 24, 30), GOLD, 4)
            if q > .6:
                rr_gold(cv, 130, y - 80, 290, y + 80, 30); check(cv, 210, y, 1.0, INK, 13, 1.9)
                T(cv, 'FREE GUIDE', 640, y - 36, 66, GOLD_L, 800, 0, glow=.35); U(cv, 'sent straight to your DMs', 640, y + 44, 32, LIGHT, 600, 1, 1)
        q2 = sm((t - ts - .45) / .4); pulse = .5 + .5 * math.sin(t * 5)
        if q2 > 0:
            w = 430; rr_gold(cv, 540 - w, 1330 - 70, 540 + w, 1330 + 70, 70, q2); T(cv, f'comment "{word.lower()}"', 540, 1330, 62, INK, 800, -1, a=q2)
            L2 = Lz(); rr(L2, 540 - w - 8, 1330 - 78, 540 + w + 8, 1330 + 78, 78, None, GOLD, 6); glow_add(cv, (L2 * pulse).astype(np.uint8), 18, .9)
    return f

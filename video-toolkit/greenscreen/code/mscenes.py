"""Scenes for the MST engine. Every scene: fn(u, dur, k, **params) -> BGR frame (1080x1920). u may exceed dur during a transition."""
from mst import *
INKC = (30, 28, 26); RED = (50, 50, 190)

def pr(u, dur): return clamp(u / max(dur, .1))
def left_text(f, s, name, size, x, y, col=OFF, a=1.0, track=0, w=600, shadow=0.):
    wd = twidth(s, name, size, track, w); T(f, s, name, size, x + wd / 2, y, col, a, track, shadow, 1.0, w)
def hairline(f, x0, y, x1, u, col=AMBER, th=2):
    if u > 0: cv2.line(f, (int(x0), int(y)), (int(x0 + (x1 - x0) * clamp(u)), int(y)), col, th, cv2.LINE_AA)
def label_tag(f, s, x, y, u, col=OFF):
    a = eo(u); T(f, s, 'mono', 26, x + twidth(s, 'mono', 26, 3) / 2, y + (1 - a) * 8, col, a * .9, 3)
def num_tag(f, n, s, u, y=250, col=AMBER):
    """01 / title chapter tag top-left (editorial hierarchy: tiny label, big serif)"""
    a = eo(u); left_text(f, n, 'monob', 28, 90, y - 66 + (1 - a) * 8, col, a, 4); hairline(f, 90, y - 40, 90 + 70 * eo(u * 1.4), 1, col)
    z = fit(s, 'serifb', 100, 900); left_text(f, s, 'serifb', z, 90, y + 30 + (1 - a) * 18, OFF, a, 0, shadow=.5)

# ---------------------------------------------------------------- archive photograph scene
def sc_archive(u, dur, k, key, fy=.5, pan=(.5, .5), tag='', cap='', sub='', year=None, tone='bw', n=None, nt=None, move=1.0, sep=True):
    ph = photo(key, fy=fy, tone=tone, sep=sep); f = ph.render(u, dur, pan=pan, dolly=.10 * move)
    e = eo(u / 1.0); f = (f.astype(np.float32) * (.12 + .88 * e)).astype(np.uint8)       # emerges from darkness
    top_scrim(f, 560, .55); bottom_scrim(f, 1180, .78); particles(f, u, 22, 5, .5, (1, 3), 10)
    if year:
        yv = int(lerp(year - 22, year, eo(u / 1.6))); left_text(f, str(yv), 'anton', 150, 80, 250, OFF, eo(u / .5) * .95, 2, shadow=.5)
        hairline(f, 84, 340, 84 + 220 * eo(u / 1.2), 1)
    if tag: left_text(f, tag, 'mono', 28, 86, 150 + (1 - eo(u / .5)) * 8, (210, 210, 210), eo(u / .6) * .95, 3)
    if n: num_tag(f, n, nt or '', clamp((u - .35) / .6), 1250)
    elif cap:
        a = eo((u - .5) / .7); z = fit(cap, 'serifi', 96, 920); left_text(f, cap, 'serifi', z, 90, 1385 + (1 - a) * 22, OFF, a, 0, shadow=.6)
    if sub: left_text(f, sub, 'mono', 26, 90, 1450, (200, 200, 200), eo((u - .9) / .6) * .85, 2)
    return filmfx(f, k, .06, .04, True, True, .3)

# ---------------------------------------------------------------- paper document
def _sheet(u, head, lines, hl, stamp, w=940, h=1040):
    s = paper_tex()[260:260 + h, 70:70 + w].copy(); f = s
    T(f, head[0], 'monob', 32, 70 + twidth(head[0], 'monob', 32, 4) / 2, 92, (60, 60, 150), 1, 4)
    z = fit(head[1], 'serifb', 104, 800); T(f, head[1], 'serifb', z, 70 + twidth(head[1], 'serifb', z) / 2, 200, INKC, 1)
    cv2.line(f, (70, 262), (w - 70, 262), (40, 40, 40), 2, cv2.LINE_AA); cv2.line(f, (70, 272), (w - 70, 272), (40, 40, 40), 1, cv2.LINE_AA)
    y = 360; t0 = .9
    for i, ln in enumerate(lines):
        ty = max(u - t0 - i * .75, 0); sz = 54; txt = typed(ln, ty, 24) if ty < len(ln) / 24 + .3 else ln
        if hl and i in hl:
            wd = twidth(ln, 'mono', sz, 0) + 30; r_ = eo(ty / .6 - .2); x2 = int(58 + wd * r_)
            if x2 > 58: reg = f[int(y - 34):int(y + 26), 58:x2]; f[int(y - 34):int(y + 26), 58:x2] = (reg * .5 + np.array(AMBER, np.float32) * .5).astype(np.uint8)
        left_text(f, txt, 'mono', sz, 70, y, INKC, 1); y += 118
    if stamp:
        sa = clamp((u - 2.2) / .25); sc = lerp(2.1, 1.0, eo((u - 2.2) / .25))
        if sa > 0:
            m = tex(stamp, 'anton', 120, 6); mm = cv2.GaussianBlur(m, (0, 0), .8); layer = np.zeros_like(f); M = cv2.getRotationMatrix2D((m.shape[1] / 2, m.shape[0] / 2), 9, 1.0); mr = cv2.warpAffine(mm, M, (m.shape[1], m.shape[0]))
            mr = cv2.resize(mr, None, fx=sc, fy=sc); h_, w_ = mr.shape; cx, cy = w - 330, h - 270
            x0, y0 = int(cx - w_ / 2), int(cy - h_ / 2); X0, Y0, X1, Y1 = max(x0, 0), max(y0, 0), min(x0 + w_, w), min(y0 + h_, h)
            mk = (mr[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * sa * .85 * (1 + .0))[..., None]; f[Y0:Y1, X0:X1] = (f[Y0:Y1, X0:X1] * (1 - mk) + np.array(RED, np.float32) * mk).astype(np.uint8)
    return f
def sc_paper(u, dur, k, head=('NO. 01', 'tell your story'), lines=(), hl=(), stamp=None, cy=830):
    f = dark_bg(0, (30, 29, 28)).astype(np.uint8); f = np.clip(f.astype(np.float32) + gr(k + 2, .02)[..., None] * 1, 0, 255).astype(np.uint8)
    glow(f, 540, 820, 900, (30, 60, 120), .18)
    e = eob(u / .85); sc = lerp(.55, 1.0, min(e, 1.04)); ang = lerp(-9, -1.2, eo(u / .85)) + math.sin(u * .9) * .35; dy = lerp(420, 0, eo(u / .85)); dx = lerp(-60, 0, eo(u / .85))
    sh = _sheet(u, head, list(lines), set(hl), stamp); hh, ww = sh.shape[:2]
    M = cv2.getRotationMatrix2D((ww / 2, hh / 2), ang, sc); M[0, 2] += 540 - ww / 2 + dx; M[1, 2] += cy - hh / 2 + dy
    mask = np.zeros((hh, ww), np.uint8); cv2.rectangle(mask, (6, 6), (ww - 6, hh - 6), 255, -1); m_ = cv2.warpAffine(mask, M, (W, H), flags=cv2.INTER_LINEAR).astype(np.float32)[..., None] / 255
    shd = cv2.GaussianBlur(np.roll(m_[..., 0], 26, 0), (0, 0), 26)[..., None]; f = (f.astype(np.float32) * (1 - shd * .65)).astype(np.uint8)
    wrp = cv2.warpAffine(sh, M, (W, H), flags=cv2.INTER_LINEAR); f = (f.astype(np.float32) * (1 - m_) + wrp.astype(np.float32) * m_).astype(np.uint8)
    a = cv2.resize(f, None, fx=.5, fy=.5); bottom_scrim(f, 1480, .6); return filmfx(f, k, .045, .02, False, True, .15)

# ---------------------------------------------------------------- funnel
def sc_funnel(u, dur, k, stages, hl=None, kicker='THE PATH', n=None, nt=None):
    f = dark_bg(0).astype(np.uint8); glow(f, 540, 860, 760, (40, 70, 130), .2); N = len(stages); y0, y1 = 470, 1330; seg = (y1 - y0) / N
    wtop, wbot = 900, 260
    def wd(y): return lerp(wtop, wbot, (y - y0) / (y1 - y0))
    if n: num_tag(f, n, nt or '', clamp(u / .7), 250)
    else: label_tag(f, kicker, 90, 230, u / .6)
    for i, s in enumerate(stages):
        a = eo((u - .35 - i * .32) / .55)
        if a <= 0: continue
        ya, yb = y0 + i * seg + 6, y0 + (i + 1) * seg - 6; wa, wb = wd(ya), wd(yb)
        pts = np.array([[540 - wa / 2, ya], [540 + wa / 2, ya], [540 + wb / 2, yb], [540 - wb / 2, yb]], np.int32); ov = f.copy(); on = (hl is not None and i == hl)
        cv2.fillPoly(ov, [pts], AMBER if on else (255, 255, 255)); f = cv2.addWeighted(f, 1 - a * (.34 if on else .07), ov, a * (.34 if on else .07), 0)
        cv2.polylines(f, [pts], True, AMBER if on else (225, 225, 225), 2, cv2.LINE_AA)
        z = fit(s, 'anton', 70, wb - 60, 3); T(f, s, 'anton', z, 540, (ya + yb) / 2 + (1 - a) * 12, OFF if not on else (255, 255, 255), a, 3, .5)
        label_tag(f, f'0{i + 1}', int(540 - wa / 2 - 4), int(ya - 14), (u - .5 - i * .32) / .5, DIM)
    r = np.random.RandomState(4)
    for j in range(46):
        ph = (u * .22 + r.rand()) % 1.0; y = lerp(y0 + 20, y1 - 20, ph); w_ = wd(y); x = 540 + (r.rand() - .5) * (w_ - 40) * (1 - ph * .12) + math.sin(u * 2 + j) * 6
        keep = r.rand() ** 1.5 > ph * .8
        if keep and eo((u - .5) / .6) > 0:
            si = int((y - y0) / seg); col = AMBER if (hl is not None and si == hl) else (240, 240, 240); cv2.circle(f, (int(x), int(y)), 4, col, -1, cv2.LINE_AA)
    bottom_scrim(f, 1480, .5); return filmfx(f, k, .04, .015, False, True, .12)

# ---------------------------------------------------------------- ICP persona card
def sc_persona(u, dur, k, rows=('WHO THEY ARE', 'WHAT THEY WANT', 'WHAT THEY CAN PAY'), n=None, nt=None, kick='IDEAL CLIENT PERSONA'):
    f = dark_bg(0).astype(np.uint8); glow(f, 540, 760, 820, (40, 70, 130), .22)
    if n: num_tag(f, n, nt or '', clamp(u / .7), 250)
    cx, cy = 540, 800
    for i in range(4):                                             # targeting rings converge
        rr = lerp(900, 130 + i * 78, eo((u - i * .08) / 1.0)); col = AMBER if i == 0 else (120, 120, 120)
        cv2.circle(f, (cx, cy + 40), int(rr), col, 2 if i == 0 else 1, cv2.LINE_AA)
    ln = eo(u / .9); cv2.line(f, (cx - int(520 * (1 - ln)) - 60, cy + 40), (cx - 60, cy + 40), AMBER, 1, cv2.LINE_AA); cv2.line(f, (cx + 60, cy + 40), (cx + int(520 * (1 - ln)) + 60, cy + 40), AMBER, 1, cv2.LINE_AA)
    e = eob((u - .5) / .7); cw, ch = 800, 900; dy = lerp(-520, 0, eo((u - .5) / .7)); x0, y0 = cx - cw // 2, int(cy - ch / 2 + 40 + dy); a = eo((u - .5) / .4)
    if a > 0:
        shadow_rect(f, x0, y0, x0 + cw, y0 + ch, .6 * a, 28, 18); pap = paper_tex()[:ch, :cw].copy(); f[max(y0, 0):y0 + ch, x0:x0 + cw] = pap[max(-y0, 0):, :][:f[max(y0, 0):y0 + ch, x0:x0 + cw].shape[0]]
        ax, ay = cx, y0 + 190; cv2.circle(f, (ax, ay - 20), 62, INKC, 5, cv2.LINE_AA); cv2.ellipse(f, (ax, ay + 130), (118, 96), 0, 180, 360, INKC, 5, cv2.LINE_AA); cv2.line(f, (ax - 118, ay + 130), (ax + 118, ay + 130), INKC, 5, cv2.LINE_AA)
        T(f, kick, 'monob', 30, cx, y0 + 380, (60, 60, 150), a, 4)
        for i, r_ in enumerate(rows):
            yy = y0 + 500 + i * 128; p = eo((u - 1.0 - i * .5) / .55)
            left_text(f, r_, 'mono', 34, x0+ 56, yy - 20, INKC, a); cv2.rectangle(f, (x0 + 56, yy + 6), (x0 + cw - 150, yy + 22), (150, 170, 180), -1)
            cv2.rectangle(f, (x0 + 56, yy + 6), (int(x0 + 56 + (cw - 206) * p), yy + 22), AMBER if i == len(rows) - 1 else INKC, -1)
            ck = eo((u - 1.5 - i * .5) / .25)
            if ck > 0:
                cc = (x0 + cw - 90, yy + 14); cv2.circle(f, cc, int(24 * ck), AMBER if i == len(rows) - 1 else INKC, -1, cv2.LINE_AA)
                if ck > .6: cv2.polylines(f, [np.array([[cc[0] - 10, cc[1]], [cc[0] - 2, cc[1] + 9], [cc[0] + 12, cc[1] - 9]])], False, (255, 255, 255), 4, cv2.LINE_AA)
        T(f, 'ILLUSTRATIVE', 'mono', 28, cx, y0 + ch - 36, (110, 120, 130), a * .8, 4)
    bottom_scrim(f, 1500, .5); return filmfx(f, k, .04, .015, False, True, .12)

# ---------------------------------------------------------------- views vs revenue dashboard
def sc_dash(u, dur, k, n=None, nt=None, sp=1.0, l1='VIEWS', l2='REVENUE', peak=12480, v2='$0'):
    u = u * sp
    f = dark_bg(0, (24, 24, 26)).astype(np.uint8)
    px0, py0, px1, py1 = 70, 300, 1010, 1380; a = eo(u / .5); rrect(f, px0, py0, px1, py1, (36, 36, 38), a, 28); rrect(f, px0, py0, px1, py1, (80, 80, 84), a, 28, 2)
    left_text(f, 'CHANNEL ANALYTICS', 'monob', 30, px0 + 44, py0 + 52, (190, 190, 190), a, 3); left_text(f, 'ILLUSTRATIVE', 'mono', 28, px1 - 250, py0 + 52, (120, 120, 126), a, 3)
    cv2.line(f, (px0 + 40, py0 + 86), (px1 - 40, py0 + 86), (70, 70, 74), 1)
    p = eo((u - .5) / 2.2); views = int(peak * p)
    left_text(f, l1, 'mono', 30, px0 + 50, py0 + 150, (170, 170, 170), a, 3); left_text(f, f'{views:,}', 'anton', 150, px0 + 46, py0 + 270, OFF, a)
    left_text(f, l2, 'mono', 30, px0 + 520, py0 + 150, (170, 170, 170), a, 3); left_text(f, v2, 'anton', 150, px0 + 516, py0 + 270, AMBER, a)
    gx0, gy0, gx1, gy1 = px0 + 50, py0 + 420, px1 - 50, py1 - 150
    for i in range(5): yy = gy0 + i * (gy1 - gy0) / 4; cv2.line(f, (gx0, int(yy)), (gx1, int(yy)), (60, 60, 64), 1)
    pts = []; fl = []
    for i in range(60):
        q = i / 59
        if q <= p:
            x = gx0 + q * (gx1 - gx0); yv = gy1 - ((q ** 1.7) * .92 + .03 * math.sin(q * 30)) * (gy1 - gy0); pts.append((int(x), int(yv))); fl.append((int(x), int(gy1 - 4 - 4 * math.sin(q * 20) * 0)))
    if len(pts) > 1:
        ov = f.copy(); poly = np.array(pts + [(pts[-1][0], gy1), (pts[0][0], gy1)]); cv2.fillPoly(ov, [poly], (255, 255, 255)); f = cv2.addWeighted(f, 1, ov, .07, 0)
        cv2.polylines(f, [np.array(pts)], False, OFF, 4, cv2.LINE_AA); cv2.polylines(f, [np.array(fl)], False, AMBER, 4, cv2.LINE_AA); cv2.circle(f, pts[-1], 9, OFF, -1, cv2.LINE_AA); cv2.circle(f, fl[-1], 9, AMBER, -1, cv2.LINE_AA)
    g = eo((u - 2.5) / .6)
    if g > 0 and len(pts) > 1:
        xx = px1 - 80; cv2.line(f, (xx, pts[-1][1] + 14), (xx, int(lerp(pts[-1][1] + 14, gy1 - 18, g))), AMBER, 3, cv2.LINE_AA); T(f, 'THE GAP', 'serifi', 64, xx - 130, (pts[-1][1] + gy1) / 2 + 60, OFF, g)
    if n: num_tag(f, n, nt or '', clamp(u / .7), 215)
    bottom_scrim(f, 1500, .5); return filmfx(f, k, .04, .015, False, True, .12)

# ---------------------------------------------------------------- stat with 120 dots
def sc_stat(u, dur, k, num=120, sub='new leads', unit='IN 4 WEEKS', source='CLIENT RESULT, AS STATED BY THE CREATOR', cols=12):
    f = dark_bg(0).astype(np.uint8); glow(f, 540, 560, 700, (40, 80, 150), .25)
    p = eo((u - .2) / 2.4); v = int(num * p); z = 420
    T(f, f'{v}', 'anton', z, 540, 520, OFF, eo(u / .4), 2, .6); hairline(f, 120, 760, 120 + 840 * eo((u - .3) / .8), 1)
    T(f, sub, 'serifi', 98, 540, 850, OFF, eo((u - .6) / .6)); T(f, unit, 'monob', 32, 540, 930, AMBER, eo((u - .9) / .6), 6)
    rows = int(math.ceil(num / cols)); gx0, gy0, dx, dy = 540 - (cols - 1) * 54 / 2, 990, 54, 46
    for i in range(num):
        r_, c_ = divmod(i, cols); ap = eo((p * num - i) / 1.6)
        if ap > 0:
            x = gx0 + c_ * dx; y = gy0 + r_ * dy; col = lerpc((120, 120, 120), AMBER, 1 if i >= num - 30 else .0) if False else AMBER
            cv2.circle(f, (int(x), int(y)), int(15 * min(ap * 1.2, 1)), col, -1, cv2.LINE_AA)
            if ap < 1: cv2.circle(f, (int(x), int(y)), int(10 + 14 * (1 - ap)), (255, 255, 255), 1, cv2.LINE_AA)
    for w_ in range(4):
        xx = gx0 + (cols - 1) * dx * (w_ + .5) / 4; label_tag(f, f'WEEK {w_ + 1}', int(xx - 40), int(gy0 + rows * dy + 10), (u - 1.2 - w_ * .25) / .4, DIM)
    T(f, source, "mono", 28, 540, 1500, (150, 150, 150), eo((u - 1.4) / .6) * .9, 3)
    return filmfx(f, k, .04, .015, False, True, .14)

# ---------------------------------------------------------------- editing timeline (cuts get tight)
def sc_timeline(u, dur, k, n=None, nt=None, word='ON POINT'):
    f = dark_bg(0, (22, 22, 24)).astype(np.uint8); a = eo(u / .5); px0, py0, px1, py1 = 50, 330, 1030, 1330; rrect(f, px0, py0, px1, py1, (32, 32, 34), a, 24); rrect(f, px0, py0, px1, py1, (80, 80, 84), a, 24, 2)
    for i in range(0, 40): x = px0 + 130 + i * 22; cv2.line(f, (x, py0 + 40), (x, py0 + (62 if i % 5 == 0 else 52)), (110, 110, 114), 1)
    names = ['V2  TEXT', 'V1  A-ROLL', 'A1  VOICE', 'A2  MUSIC']; ty = [py0 + 150, py0 + 330, py0 + 560, py0 + 760]
    for i, nm in enumerate(names): left_text(f, nm, 'mono', 28, px0 + 20, ty[i] - 4, (150, 150, 150), a, 2)
    c0 = 0.0; seg = [(0, 230), (0, 150), (0, 190), (0, 130), (0, 170)]
    tp = clamp((u - 1.0) / 1.6); cut = eo((u - 2.6) / 1.1); gaps = [60 * (1 - cut) for _ in range(5)]
    x = px0 + 130
    for i, (_, w_) in enumerate(seg):
        if tp * 5 > i - .2:
            col = (210, 210, 214) if i % 2 == 0 else (170, 170, 176); ww = w_ * (.55 + .45 * (1 - cut)) if True else w_; ww = lerp(w_, w_ * .66, cut)
            rrect(f, x, ty[1] - 54, x + ww * min(1, eo(u / .6 - .0)), ty[1] + 54, col, .95, 8)
            if cut > .05 and i > 0: cv2.line(f, (int(x - 3), ty[1] - 70), (int(x - 3), ty[1] + 70), AMBER, 2, cv2.LINE_AA)
            r_ = np.random.RandomState(i); rrect(f, x, ty[2] - 36, x + ww, ty[2] + 36, (80, 80, 86), .95, 8)
            for j in range(int(ww // 5)): hh_ = 6 + 24 * abs(math.sin(j * .7 + i * 2 + u * 3 * (1 if tp < 1 else 0))); cv2.line(f, (int(x + 4 + j * 5), int(ty[2] - hh_)), (int(x + 4 + j * 5), int(ty[2] + hh_)), (240, 240, 240) if cut > .5 else (190, 190, 190), 2)
            x += ww + gaps[i]
    rrect(f, px0 + 130, ty[3] - 24, px1 - 30, ty[3] + 24, (70, 90, 100), a, 8); rrect(f, px0 + 130 + 8, ty[0] - 36, px0 + 130 + 250 * eo((u - 3.4) / .5), ty[0] + 36, AMBER, a * (u > 3.4), 8)
    if u > 3.4: left_text(f, 'CUT.', 'monob', 30, px0 + 146, ty[0] - 4, INKC, eo((u - 3.5) / .3), 3)
    phx = lerp(px0 + 130, px0 + 130 + 620, clamp((u - .8) / 2.8)); cv2.line(f, (int(phx), py0 + 30), (int(phx), py1 - 40), AMBER, 3, cv2.LINE_AA); cv2.circle(f, (int(phx), py0 + 30), 9, AMBER, -1, cv2.LINE_AA)
    T(f, word, 'anton', 150, 540, 1440, OFF, eo((u - 3.5) / .5), 6, .6)
    if n: num_tag(f, n, nt or '', clamp(u / .7), 215)
    return filmfx(f, k, .04, .015, False, True, .12)

# ---------------------------------------------------------------- cadence / rhythm / tone waveforms
def sc_wave3(u, dur, k, labels=('CADENCE', 'RHYTHM', 'TONE'), n=None, nt=None, end='PROFESSIONAL'):
    f = dark_bg(0).astype(np.uint8); glow(f, 540, 820, 760, (40, 70, 130), .2); a = eo(u / .5)
    if n: num_tag(f, n, nt or '', clamp(u / .7), 250)
    clean = eo((u - 1.8) / 2.2)
    for i, lb in enumerate(labels):
        y = 620 + i * 250; aa = eo((u - .4 - i * .3) / .5); left_text(f, lb, 'monob', 28, 90, y - 105, OFF, aa, 4); hairline(f, 90, y - 80, 990, aa, (90, 90, 90), 1)
        pts = []
        for xi in range(0, 900, 6):
            q = xi / 900; r_ = np.random.RandomState(xi * 3 + i).randn() * .9; mess = (math.sin(q * 20 + u * 3 + i) * .5 + r_ * .55) * (1 - clean) if True else 0; smooth = math.sin(q * (14 + 3 * i) - u * 4 + i) * .55 * (1 - .15 * math.sin(q * 3)); amp = lerp(1.0, 1.0, 0)
            pts.append((int(90 + xi), int(y + 20 + (mess + smooth * clean) * 80 * aa)))
        cv2.polylines(f, [np.array(pts)], False, AMBER if clean > .6 else OFF, 3, cv2.LINE_AA)
    pr_ = eo((u - 1.8) / 2.2); rrect(f, 90, 1400, 990, 1424, (60, 60, 64), a, 12); rrect(f, 90, 1400, 90 + 900 * pr_, 1424, AMBER, a, 12)
    T(f, end, 'monob', 32, 540, 1465, OFF, eo((u - 2.8) / .5), 6)
    return filmfx(f, k, .04, .015, False, True, .12)

# ---------------------------------------------------------------- comment -> DM delivery
def sc_dm(u, dur, k, word='lead', deliver='LEAD GENERATION GUIDE', n=None, nt=None):
    f = dark_bg(0, (24, 24, 27)).astype(np.uint8); glow(f, 540, 820, 760, (40, 70, 130), .2)
    if n: num_tag(f, n, nt or '', clamp(u / .7), 250)
    px0, py0, px1, py1 = 140, 420, 940, 1380; a = eo(u / .5); rrect(f, px0, py0, px1, py1, (36, 36, 40), a, 54); rrect(f, px0, py0, px1, py1, (96, 96, 102), a, 54, 3)
    left_text(f, 'COMMENTS', 'monob', 28, px0 + 50, py0 + 60, (170, 170, 170), a, 4)
    cv2.line(f, (px0 + 40, py0 + 90), (px1 - 40, py0 + 90), (70, 70, 74), 1)
    # typing comment
    tp = clamp((u - .7) / 1.1); txt = word[:int(len(word) * tp)]; rrect(f, px0 + 40, py0 + 130, px1 - 40, py0 + 230, (60, 60, 66), a, 30)
    left_text(f, txt + ('|' if int(u * 3) % 2 == 0 and tp < 1.0 else ''), 'inter', 44, px0 + 76, py0 + 182, OFF, a)
    sent = eo((u - 2.0) / .35)
    if sent > 0:
        rrect(f, px0 + 40, py0 + 280, px0 + 40 + 60 + twidth(word, 'inter', 40) + 40, py0 + 360, AMBER, sent, 36)
        left_text(f, word, 'inter', 40, px0 + 80, py0 + 322, INKC, sent)
    rep = eob((u - 2.9) / .6)
    if rep > 0:
        yy = int(py0 + 460 + (1 - min(rep, 1)) * 60); bx0, bx1 = px0 + 40, px1 - 40; ra = min(rep, 1)
        rrect(f, bx0, yy, bx1, yy + 380, (60, 60, 66), ra, 30)
        left_text(f, 'Here you go', 'inter', 36, bx0 + 36, yy + 56, OFF, ra); rrect(f, bx0 + 36, yy + 100, bx0 + 36 + 220, yy + 340, PAPER, ra, 14)
        for j in range(5): cv2.line(f, (int(bx0 + 60), int(yy + 140 + j * 36)), (int(bx0 + 36 + 196 - (j % 2) * 40), int(yy + 140 + j * 36)), INKC, 3)
        left_text(f, deliver, 'monob', 30, bx0 + 290, yy + 200, OFF, ra, 2); left_text(f, 'PDF', 'mono', 28, bx0 + 290, yy + 250, AMBER, ra, 4)
        left_text(f, 'Delivered', 'mono', 28, bx0 + 290, yy + 320, (150, 150, 150), ra, 3)
    return filmfx(f, k, .04, .015, False, True, .12)

# ---------------------------------------------------------------- find high-value clients (cards + scan)
def sc_clients(u, dur, k, n=None, nt=None):
    f = dark_bg(0).astype(np.uint8); glow(f, 540, 840, 760, (40, 70, 130), .22)
    if n: num_tag(f, n, nt or '', clamp(u / .7), 250)
    pick = 2; N = 5; sel = eo((u - 2.6) / .7)
    for i in range(N):
        a = eo((u - .3 - i * .15) / .5); cx = 540 + (i - 2) * 118 + (sel * 70 * np.sign(i - pick) if i != pick else 0); ang = (i - 2) * 7 * (1 - sel * (1 if i == pick else 0)); sc_ = 1.0 + sel * .28 * (i == pick); dim = 1 - .6 * sel * (i != pick)
        cw, ch = 330, 500; card = np.zeros((ch, cw, 3), np.uint8); card[:] = paper_tex()[:ch, :cw] if True else 0; ccx, ccy = cw // 2, 140
        cv2.circle(card, (ccx, ccy - 10), 44, INKC, 4, cv2.LINE_AA); cv2.ellipse(card, (ccx, ccy + 90), (80, 66), 0, 180, 360, INKC, 4, cv2.LINE_AA)
        for j in range(3): cv2.rectangle(card, (40, 290 + j * 44), (cw - 40 - (j * 40) % 90, 304 + j * 44), (140, 150, 160), -1)
        if i == pick:
            vv = eo((u - 3.0) / .5); cv2.rectangle(card, (40, 420), (cw - 40, 466), AMBER, -1); T(card, 'HIGH VALUE', 'monob', 28, cw // 2, 443, INKC, vv, 3)
        mask = np.zeros((ch, cw), np.uint8); cv2.rectangle(mask, (0, 0), (cw - 1, ch - 1), 255, -1)
        M = cv2.getRotationMatrix2D((cw / 2, ch / 2), ang, sc_); M[0, 2] += cx - cw / 2; M[1, 2] += 860 - ch / 2 + (1 - a) * 160 - 14 * sel * (i == pick)
        m_ = cv2.warpAffine(mask, M, (W, H)).astype(np.float32)[..., None] / 255 * a
        shd = cv2.GaussianBlur(np.roll(m_[..., 0], 14, 0), (0, 0), 14)[..., None]; f = (f.astype(np.float32) * (1 - shd * .55)).astype(np.uint8)
        wc = cv2.warpAffine((card.astype(np.float32) * dim).astype(np.uint8), M, (W, H)); f = (f.astype(np.float32) * (1 - m_) + wc.astype(np.float32) * m_).astype(np.uint8)
    scan = eo((u - 1.0) / 1.6) * (1 - sel)
    if 0 < scan < 1 and sel < .05:
        mx = lerp(540 - 300, 540 + 0, scan) + math.sin(u * 3) * 14; my = 840; cv2.circle(f, (int(mx), int(my)), 92, AMBER, 5, cv2.LINE_AA); cv2.line(f, (int(mx + 65), int(my + 65)), (int(mx + 130), int(my + 130)), AMBER, 8, cv2.LINE_AA)
    if sel > 0:
        d = int(10000 * eo((u - 3.1) / 1.0)) if False else 0; T(f, '$', 'anton', 160, 540, 1300, AMBER, eo((u - 3.2) / .5), 0, .6)
    T(f, 'ILLUSTRATIVE', 'mono', 28, 540, 1450, (140, 140, 140), .8, 4)
    return filmfx(f, k, .04, .015, False, True, .12)

# ---------------------------------------------------------------- consistency calendar -> funnel
def sc_consist(u, dur, k, n=None, nt=None, words=('RELATABLE', 'CONSISTENT', 'FUNNEL SYSTEM')):
    f = dark_bg(0).astype(np.uint8); glow(f, 540, 800, 760, (40, 70, 130), .2)
    if n: num_tag(f, n, nt or '', clamp(u / .7), 250)
    cols, rows = 7, 4; gx0, gy0 = 540 - (cols - 1) * 70 / 2, 520
    for i in range(cols * rows):
        r_, c_ = divmod(i, cols); t0 = .5 + i * .07; a = eo((u - t0) / .3); x, y = gx0 + c_ * 70, gy0 + r_ * 70
        rrect(f, x - 24, y - 24, x + 24, y + 24, (70, 70, 74), 1, 10, 2)
        if a > 0:
            rrect(f, x - 24 * a, y - 24 * a, x + 24 * a, y + 24 * a, AMBER, 1, 10)
            tt = eo((u - t0 - .2) / .6)
            if 0 < tt < 1: cv2.circle(f, (int(x), int(y + 40 + tt * 420)), 5, OFF, -1, cv2.LINE_AA)
    fy0, fy1 = 1000, 1360; fa = eo((u - 1.8) / .6)
    for e_ in (-1, 1): cv2.line(f, (int(540 + e_ * 300), fy0), (int(540 + e_ * 90), fy1), OFF if fa > 0 else (0, 0, 0), 2, cv2.LINE_AA) if fa > 0 else None
    if fa > 0: cv2.line(f, (240, fy0), (840, fy0), OFF, 2, cv2.LINE_AA); T(f, 'FUNNEL', 'anton', 64, 540, 1180, OFF, fa, 6, .5)
    for i, w_ in enumerate(words): label_tag(f, w_, 90, 430 + 0, 1) if False else None
    sx = 1420; label_tag(f, ' · '.join(words), 90 if False else 540 - twidth(' · '.join(words), 'mono', 26, 3) // 2, sx, (u - 2.2) / .5, OFF)
    return filmfx(f, k, .04, .015, False, True, .12)

# ---------------------------------------------------------------- talking head with text between subject and background
_AL = {}
def alpha_arr(vid):
    if vid not in _AL:
        p = f'{CACHE}/alpha{vid}.npy'
        if not os.path.exists(p):
            dec = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{C5}/work/alpha{vid}.mkv', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
            np.save(p, np.frombuffer(dec, np.uint8).reshape(-1, 960, 540))
        _AL[vid] = np.load(p, mmap_mode='r')
    return _AL[vid]
def sc_head(u, dur, k, S, zoom=(1.0, 1.06), behind=None, proof=None, fade_in=None):
    """behind: list of (text, font, size, y, color, delay) drawn between background and the speaker (needs matte)."""
    t = k / FPS; z = lerp(zoom[0], zoom[1], eio(clamp(t / S['VDUR']))); fr = speaker(S, k, z); fr = grade_modern(fr)
    g = np.clip((np.arange(H, dtype=np.float32) - 1500) / 420, 0, 1)[:, None, None] * .34; fr = (fr.astype(np.float32) * (1 - g)).astype(np.uint8)
    if behind:
        al = alpha_arr(S['vid']); i = min(k, len(al) - 1); m = cv2.resize(np.array(al[i]), (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255
        M = np.float32([[z, 0, (1 - z) * 540], [0, z, (1 - z) * 1920]]); m = cv2.warpAffine(m, M, (W, H)); m = cv2.GaussianBlur(m, (0, 0), 1.2)[..., None]
        bgl = fr.astype(np.float32) * .72; bgl = np.clip(bgl, 0, 255).astype(np.uint8)
        for (s, nm, sz, y, col, dl) in behind:
            a = eo((u - dl) / .5); zz = sz * lerp(1.18, 1.0, eo((u - dl) / .9)); mk = tex(s, nm, int(zz), 2); put(bgl, mk, 540, y + (1 - a) * 30, (0, 0, 0), a * .35, blur=10, dy=8); put(bgl, mk, 540, y + (1 - a) * 30, col, a)
        fr = (bgl.astype(np.float32) * (1 - m) + fr.astype(np.float32) * m).astype(np.uint8)
    if proof:
        a = eo((u - .15) / .5); T(fr, proof, 'mono', 26, 540, 120 + (1 - a) * 8, (235, 235, 235), a * .95, 4, .5)
    return filmfx(fr, k, .03, .01, False, False, .1, True)

def zoomfill(f, s=1.1, cy=820):
    M = np.float32([[s, 0, (1 - s) * 540], [0, s, (1 - s) * cy]]); return cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

# ---------------------------------------------------------------- document: camera travels across a real archival sheet
_DOC = {}
def sc_pan(u, dur, k, key, path, tag='', cap='', sub='', n=None, nt=None, tone='bw'):
    """path: [(cx, cy, z)...] normalised image centre + zoom (z=1: viewport height == image height). Real document, real details."""
    if key not in _DOC:
        img = cv2.imread(f'{ART}/{key}.jpg'); sc = min(1.0, 5200 / img.shape[1]); img = cv2.resize(img, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA); _DOC[key] = grade_bw(img, .35, 1.12, .02) if tone == 'bw' else img
    im = _DOC[key]; ih, iw = im.shape[:2]; p = clamp(u / max(dur, .1)); q = eio(p) * (len(path) - 1); i = min(int(q), len(path) - 2); r = q - i; a_, b_ = path[i], path[i + 1]; r = eio(r)
    cx, cy, z = [lerp(a_[j], b_[j], r) for j in range(3)]; vh = ih / z; vw = vh * W / H; vh = min(vh, ih); vw = min(vw, iw)
    x0 = float(np.clip(cx * iw - vw / 2, 0, iw - vw)); y0 = float(np.clip(cy * ih - vh / 2, 0, ih - vh)); sx, sy = W / vw, H / vh
    f = cv2.warpAffine(im, np.float32([[sx, 0, -x0 * sx], [0, sy, -y0 * sy]]), (W, H), flags=cv2.INTER_CUBIC)
    e = eo(u / .9); f = (f.astype(np.float32) * (.1 + .9 * e)).astype(np.uint8); top_scrim(f, 420, .5); bottom_scrim(f, 1250, .72); particles(f, u, 14, 6, .35, (1, 2), 8)
    if tag: left_text(f, tag, 'mono', 28, 86, 150, (225, 225, 225), eo(u / .6) * .95, 3, shadow=.6)
    if n: num_tag(f, n, nt or '', clamp((u - .35) / .6), 1250)
    elif cap: aa = eo((u - .5) / .7); zz = fit(cap, 'serifi', 78, 920); left_text(f, cap, 'serifi', zz, 90, 1385 + (1 - aa) * 22, OFF, aa, 0, shadow=.6)
    if sub: left_text(f, sub, 'mono', 26, 90, 1450, (210, 210, 210), eo((u - .9) / .6) * .9, 2)
    return filmfx(f, k, .05, .03, True, True, .25)

# ---------------------------------------------------------------- slow conversion: grey audience slowly turns amber
def sc_shift(u, dur, k, n=None, nt=None, a_lab='TODAY', b_lab='SLOWLY'):
    f = dark_bg(0).astype(np.uint8); glow(f, 540, 820, 760, (40, 70, 130), .22)
    if n: num_tag(f, n, nt or '', clamp(u / .7), 250)
    cols, rows = 10, 8; gx0, gy0, dx, dy = 540 - (cols - 1) * 82 / 2, 520, 82, 84; prog = clamp((u - .8) / (max(dur, 3) - 1.6)); r = np.random.RandomState(8); order = r.permutation(cols * rows) / (cols * rows)
    for i in range(cols * rows):
        r_, c_ = divmod(i, cols); a = eo((u - .2 - i * .008) / .4); x = gx0 + c_ * dx; y = gy0 + r_ * dy
        if a <= 0: continue
        conv = clamp((prog * 1.25 - order[i]) / .25); col = lerpc((120, 120, 124), AMBER, conv)
        cv2.circle(f, (int(x), int(y - 14)), int(10 * a), col, -1, cv2.LINE_AA); cv2.ellipse(f, (int(x), int(y + 22)), (int(17 * a), int(15 * a)), 0, 180, 360, col, -1, cv2.LINE_AA)
    pct = int(100 * prog); T(f, f'{pct}%', 'anton', 190, 540, 1280, OFF, eo((u - .6) / .5), 2, .6); T(f, 'CONVERTED', 'monob', 32, 540, 1390, AMBER, eo((u - .8) / .5), 8)
    T(f, 'ILLUSTRATIVE', 'mono', 28, 540, 1470, (140, 140, 140), .8, 4)
    return filmfx(f, k, .04, .015, False, True, .12)

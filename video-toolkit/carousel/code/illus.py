import math, numpy as np
from PIL import Image, ImageDraw, ImageFont
FD = '/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad/c2/fonts'
BW, BH, SS = 960, 560, 2
LIL, PEA, PNK, MNT, BLU, WHT, RED = (185, 166, 255), (255, 201, 168), (246, 182, 212), (155, 227, 180), (155, 188, 255), (240, 238, 244), (255, 110, 100)
SKIN, HAIR, SHIRT, DESK, PAN, EDGE = (232, 183, 154), (36, 28, 40), (108, 123, 217), (58, 52, 70), (34, 31, 44), (88, 82, 104)
_F = {}
def font(n, sz):
    k = (n, sz)
    if k not in _F: _F[k] = ImageFont.truetype(f'{FD}/{n}', int(sz * SS))
    return _F[k]
def cl(x, a=0, b=1): return max(a, min(b, x))
def eo(x): x = cl(x); return 1 - (1 - x) ** 3
def eb(x): x = cl(x); c1 = 1.7; c3 = c1 + 1; return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
class L:
    def __init__(s): s.im = Image.new('RGBA', (BW * SS, BH * SS), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.im, 'RGBA')
    def P(s, v): return [(x * SS, y * SS) for x, y in v]
    def rr(s, x0, y0, x1, y1, r, fill, outline=None, w=2, a=255):
        s.d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], r * SS, fill=fill + (a,) if fill else None, outline=outline + (a,) if outline else None, width=int(w * SS))
    def el(s, cx, cy, rx, ry, fill, a=255, outline=None, w=2):
        s.d.ellipse([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], fill=fill + (a,) if fill else None, outline=outline + (a,) if outline else None, width=int(w * SS))
    def ln(s, pts, col, w=4, a=255): s.d.line(s.P(pts), fill=col + (a,), width=int(w * SS), joint='curve')
    def pg(s, pts, fill, a=255): s.d.polygon(s.P(pts), fill=fill + (a,))
    def tx(s, t, x, y, sz, col=WHT, a=255, f='Inter.ttf', anc='mm'): s.d.text((x * SS, y * SS), t, font=font(f, sz), fill=col + (a,), anchor=anc)
    def out(s): return s.im.resize((BW, BH), Image.LANCZOS)
def panel(l, a=255):
    l.rr(0, 0, BW, BH, 34, PAN, EDGE, 2, int(a * .92))
def person(l, cx, cy, sc, mood, t, hands_head=False, shake=0):
    sx = math.sin(t * 30) * shake
    l.rr(cx - 62 * sc + sx, cy + 40 * sc, cx + 62 * sc + sx, cy + 190 * sc, 30 * sc, SHIRT)
    hx, hy = cx + sx, cy - 10 * sc
    l.rr(hx - 14 * sc, cy + 14 * sc, hx + 14 * sc, cy + 50 * sc, 6 * sc, SKIN)
    l.el(hx, hy, 52 * sc, 56 * sc, SKIN); l.d.pieslice([(hx - 56 * sc) * SS, (hy - 64 * sc) * SS, (hx + 56 * sc) * SS, (hy + 40 * sc) * SS], 180, 360, fill=HAIR + (255,))
    l.el(hx - 52 * sc, hy + 2 * sc, 9 * sc, 14 * sc, HAIR)
    if mood == 'sad':
        for sg in (-1, 1): l.ln([(hx + sg * 30 * sc, hy - 20 * sc), (hx + sg * 12 * sc, hy - 30 * sc if sg < 0 else hy - 8 * sc)] if False else [(hx + sg * 34 * sc, hy - 30 * sc + (6 if sg < 0 else 0) * sc), (hx + sg * 12 * sc, hy - 16 * sc - (6 if sg < 0 else 0) * sc)], HAIR, 3 * sc)
        for sg in (-1, 1): l.el(hx + sg * 20 * sc, hy - 2 * sc, 5 * sc, 6 * sc, (40, 30, 50))
        l.d.arc([(hx - 18 * sc) * SS, (hy + 24 * sc) * SS, (hx + 18 * sc) * SS, (hy + 52 * sc) * SS], 200, 340, fill=(120, 50, 60, 255), width=int(3.4 * sc * SS))
    elif mood == 'happy':
        for sg in (-1, 1): l.el(hx + sg * 20 * sc, hy - 4 * sc, 5 * sc, 6 * sc, (40, 30, 50))
        l.d.arc([(hx - 22 * sc) * SS, (hy + 6 * sc) * SS, (hx + 22 * sc) * SS, (hy + 40 * sc) * SS], 20, 160, fill=(120, 50, 60, 255), width=int(3.6 * sc * SS))
    else:
        for sg in (-1, 1): l.el(hx + sg * 20 * sc, hy - 4 * sc, 5 * sc, 6 * sc, (40, 30, 50))
        l.ln([(hx - 14 * sc, hy + 28 * sc), (hx + 14 * sc, hy + 28 * sc)], (120, 50, 60), 3.4 * sc)
    if hands_head:
        for sg in (-1, 1):
            l.ln([(cx + sg * 56 * sc + sx, cy + 80 * sc), (cx + sg * 70 * sc + sx, cy + 20 * sc), (hx + sg * 48 * sc, hy - 20 * sc)], SKIN, 16 * sc); l.el(hx + sg * 46 * sc, hy - 24 * sc, 12 * sc, 12 * sc, SKIN)
def vclip(l, x, y, w, h, col, a=255, play=True):
    l.rr(x, y, x + w, y + h, 10, col, None, 0, a)
    if play: l.pg([(x + w * .42, y + h * .3), (x + w * .42, y + h * .7), (x + w * .66, y + h * .5)], (255, 255, 255), a)
def chip(l, txt, x, y, col=LIL, a=255):
    wd = len(txt) * 13 + 34; l.rr(x, y, x + wd, y + 38, 19, PAN, col, 2, a); l.tx(txt, x + wd / 2, y + 19, 18, col, a, 'IBMPlexMono-Bold.ttf')
# ------------------------------------------------------------------ scenes
def scene_stress(u):
    l = L(); panel(l); chip(l, 'MAKE · EDIT · STRUCTURE', 36, 26, PNK)
    l.rr(60, 420, 900, 470, 14, DESK); l.rr(110, 468, 150, 560, 6, DESK); l.rr(810, 468, 850, 560, 6, DESK)
    person(l, 330, 215, 1.35, 'sad', u, True, shake=1.6 * (1 if int(u * 6) % 2 else -1))
    l.rr(520, 310, 800, 420, 12, (28, 26, 36), EDGE, 3); l.rr(480, 420, 840, 432, 6, (70, 64, 86))
    cols = [LIL, PEA, PNK, MNT, BLU]; r = np.random.RandomState(2)
    for i in range(9):
        a = eo((u - .3 - i * .14) / .3); xx = 540 + (i % 4) * 66 + math.sin(u * 3 + i) * 6; yy = 328 + (i // 4) * 38 + math.cos(u * 2 + i) * 4
        l.rr(xx, yy, xx + 56 + (i * 7) % 20, yy + 26, 5, cols[i % 5], None, 0, int(255 * a))
    for i in range(7):
        ph = (u * .9 + i * .31) % 1.0; ang = i * .9 + u * 1.4; rx, ry = 230 + 70 * math.sin(i), 70
        x = 330 + math.cos(ang) * rx; y = 170 + math.sin(ang) * ry * .9 - 20
        if i % 2 == 0: vclip(l, x - 28, y - 18, 56, 36, cols[i % 5], 235)
        else: l.tx('?', x, y, 44, WHT, 230, 'Inter.ttf')
    for i in range(3):
        ph = ((u * 1.1 + i * .33) % 1.0); l.pg([(300 + i * 36, 210 + ph * 90 - 14), (292 + i * 36, 210 + ph * 90 + 6), (308 + i * 36, 210 + ph * 90 + 6)], BLU, int(255 * (1 - ph)))
    l.tx('deadline', 735, 270, 22, RED, int(255 * eo((u - 1.2) / .4)), 'IBMPlexMono-Regular.ttf')
    return l.out()
def scene_views(u):
    l = L(); panel(l); chip(l, 'A CLIENT OF MINE', 36, 26, MNT)
    bars = [.12, .2, .26, .38, .48, .66, .94]
    for i, b in enumerate(bars):
        g = eo((u - .2 - i * .18) / .6); h = 330 * b * g; x = 90 + i * 70
        l.rr(x, 470 - h, x + 52, 470, 10, MNT if i == 6 else (LIL if i > 3 else EDGE))
    pts = [(116 + i * 70, 470 - 330 * b * eo((u - .2 - i * .18) / .6) - 24) for i, b in enumerate(bars)]
    l.ln(pts, PEA, 5); ae = pts[-1]; l.pg([(ae[0] + 6, ae[1] - 14), (ae[0] + 30, ae[1] + 4), (ae[0] - 6, ae[1] + 12)], PEA)
    cnt = 2.2 * eo((u - .3) / 2.6); l.tx(f'{cnt:.1f}M', 700, 180, 120, WHT, 255, 'Anton.ttf'); l.tx('AVERAGE WEEKLY VIEWS', 700, 258, 24, (190, 186, 205), 255, 'Inter.ttf')
    vclip(l, 600, 310, 70, 50, RED, int(255 * eo((u - 2.2) / .3)))
    person(l, 800, 345, .72, 'happy', u)
    return l.out()
def scene_plan(u):
    l = L(); panel(l); chip(l, '01 · CONTENT PLAN', 36, 26, LIL)
    days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']; cw = 120; x0 = 60
    for i, dname in enumerate(days):
        x = x0 + i * (cw + 5); sat = i == 5; hl = eo((u - .3) / .4) if sat else 0
        l.rr(x, 100, x + cw, 150, 10, (LIL if sat and hl > .1 else PAN), EDGE, 2); l.tx(dname, x + cw / 2, 125, 20, (20, 18, 28) if sat and hl > .5 else (170, 166, 186), 255, 'IBMPlexMono-Bold.ttf')
        for rrw in range(3): l.rr(x, 160 + rrw * 76, x + cw, 228 + rrw * 76, 12, (44, 40, 58), None, 0, 255)
    cols = [LIL, PEA, PNK, MNT, BLU]; tx_ = x0 + 5 * (cw + 5)
    for i in range(5):
        a = eb((u - 1.0 - i * .45) / .5); yy = 164 + (i % 3) * 76 if i < 3 else 164 + (i - 3) * 76
        sxx = x0 + (3 if i < 3 else 6) * (cw + 5) if False else tx_
        tgt_x = tx_ if i < 3 else x0 + 6 * (cw + 5); tgt_y = 160 + (i % 3) * 76 if i < 3 else 160 + ((i - 3) % 3) * 76
        if i >= 3: tgt_y = 160 + (i - 3) * 76
        x = tgt_x + (1 - cl(a, 0, 1.05)) * -300; y = tgt_y - (1 - cl(a, 0, 1)) * 140
        if a > 0.02: vclip(l, x + 4, y + 4, cw - 8, 60, cols[i], int(255 * cl(a * 1.5)))
    rk = eo((u - 3.3) / .5)
    for i in range(5):
        tgt_x = tx_ if i < 3 else x0 + 6 * (cw + 5); tgt_y = 160 + i * 76 if i < 3 else 160 + (i - 3) * 76
        if rk > 0: l.el(tgt_x + 22, tgt_y + 18, 15, 15, (20, 18, 28), int(255 * rk)); l.tx(str(i + 1), tgt_x + 22, tgt_y + 19, 20, WHT, int(255 * rk), 'Inter.ttf')
    l.tx('5 viral videos from each niche, then rank them', 480, 430, 26, (200, 196, 214), int(255 * eo((u - 3.6) / .5)), 'Inter.ttf')
    l.rr(60, 480, 900, 520, 10, (44, 40, 58)); l.rr(60, 480, 60 + 840 * eo((u - 4.2) / 2.2), 520, 10, MNT)
    l.tx('make videos', 90, 500, 20, (20, 18, 28), 255, 'IBMPlexMono-Bold.ttf', 'lm')
    return l.out()
def scene_quality(u):
    l = L(); panel(l); chip(l, '02 · QUALITY UP', 36, 26, PNK)
    n = 6
    for i in range(n):
        g = eo((u - .3 - i * .45) / .5); x = 90 + i * 100; h = 70 + i * 52
        l.rr(x, 470 - h * g, x + 90, 470, 10, PNK if i == n - 1 else (EDGE if i < 2 else LIL))
    prog = cl((u - .5) / 3.6); stx = 90 + prog * 5 * 100 + 45; sty = 470 - (70 + prog * 5 * 52) * 1.0 * 1 - 62 if True else 0
    person(l, stx, sty - 42, .44, 'happy', u)
    for k in range(3):
        l.rr(660 + k * 82, 80, 736 + k * 82, 80 + 92, 10, PAN, EDGE, 2); sh = eo((u - 1.0 - k * .9) / .6); vclip(l, 668 + k * 82, 90, 60, 70, (90, 84, 110) if sh < .5 else (PEA if k == 1 else PNK), 255)
    l.tx('quality, not consistency', 480, 520, 24, (200, 196, 214), int(255 * eo((u - 1.8) / .5)), 'Inter.ttf')
    return l.out()
def scene_improve(u):
    l = L(); panel(l); chip(l, '03 · CHANGES & IMPROVEMENTS', 36, 26, PEA)
    for i, nm in enumerate(['v1', 'v2', 'v3']):
        x = 70 + i * 300; a = eb((u - .3 - i * .6) / .5); hh = [120, 190, 270][i]
        l.rr(x, 110, x + 260, 480, 22, (44, 40, 58), EDGE, 2, int(255 * cl(a))); l.tx(nm, x + 40, 140, 26, (190, 186, 205), int(255 * cl(a)), 'IBMPlexMono-Bold.ttf')
        l.rr(x + 40, 460 - hh * cl(a), x + 220, 460, 10, [EDGE, LIL, MNT][i], None, 0, int(255 * cl(a)))
        if i < 2 and u > .8 + i * .6: l.ln([(x + 268, 300), (x + 296, 300)], PEA, 5); l.pg([(x + 292, 288), (x + 308, 300), (x + 292, 312)], PEA)
    l.tx('+ better each time', 480, 520, 26, MNT, int(255 * eo((u - 2.2) / .5)), 'Inter.ttf')
    return l.out()
def scene_sheet(u):
    l = L(); panel(l); chip(l, 'ENGAGEMENT METRICS', 36, 26, BLU)
    hd = ['VIDEO', 'HOOK', 'WATCH', 'LIKES', 'SHARES']; cwid = 160
    for j, h_ in enumerate(hd): l.rr(60 + j * cwid, 90, 60 + (j + 1) * cwid - 4, 130, 6, (50, 46, 66)); l.tx(h_, 60 + j * cwid + cwid / 2 - 2, 110, 18, (190, 186, 205), 255, 'IBMPlexMono-Bold.ttf')
    r = np.random.RandomState(4)
    for i in range(6):
        bad = i == 3; fix = eo((u - 3.6) / .5)
        for j in range(5):
            g = eo((u - .2 - i * .3 - j * .06) / .4); w_ = int((cwid - 24) * (.35 + .6 * r.rand()))
            col = EDGE
            if bad and j == 1: w_ = int((cwid - 24) * (.18 + .62 * fix)); col = tuple(int(RED[k] * (1 - fix) + MNT[k] * fix) for k in range(3))
            y = 138 + i * 58; l.rr(60 + j * cwid, y, 60 + (j + 1) * cwid - 4, y + 50, 6, (40, 36, 54) if not (bad and u > 2) else (60, 40, 52 if fix < .5 else 58))
            l.rr(72 + j * cwid, y + 17, 72 + j * cwid + w_ * g, y + 33, 8, col)
    mx = 60 + 1 * cwid + 80 + 40 * math.sin(u * 2) * (1 if u < 3.5 else 0); my = 138 + 3 * 58 + 25 + 6 * math.cos(u * 3)
    if 1.8 < u < 4.6:
        a = eo((u - 1.8) / .4) * (1 - eo((u - 4.2) / .4)); l.el(mx + 20, my - 20, 26, 26, None, int(255 * a), PNK, 5); l.ln([(mx + 39, my - 1), (mx + 62, my + 22)], PNK, 7, int(255 * a))
    l.tx('why did the hook fall short?', 480, 520, 24, (200, 196, 214), int(255 * eo((u - 2.0) / .4) * (1 - eo((u - 3.6) / .3))), 'Inter.ttf'); l.tx('fixed. improved.', 480, 520, 26, MNT, int(255 * eo((u - 4.0) / .4)), 'Inter.ttf')
    return l.out()
SCENES = [(0.9, 4.0, scene_stress, .56, 440), (4.15, 8.3, scene_views, .6, 300), (11.2, 19.9, scene_plan, .62, 300), (20.2, 27.9, scene_quality, .62, 300), (28.1, 32.2, scene_improve, .62, 300), (33.2, 38.9, scene_sheet, .62, 300)]

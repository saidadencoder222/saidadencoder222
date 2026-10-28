import sys; sys.path.insert(0, '/tmp/vt/c3')
from rl import *
PA = json.load(open(f'{R3}/work/pauses.json')); MC = json.load(open(f'{R3}/work/mix_curves.json'))
WH = OFFW; RH = RED_HI; LM = LIME
def T(s, c=WH): return [(s, c)]
def hk(*lines): return [l if isinstance(l, list) else T(l) for l in lines]
def card(f, x0, y0, x1, y1, col, a=1.0):
    r = f[y0:y1, x0:x1].astype(np.float32); f[y0:y1, x0:x1] = (r * (1 - a) + np.array(col, np.float32) * a).astype(np.uint8)
def dim(fn, k=.42):
    def g(t, st): return (fn(t, st).astype(np.float32) * k).astype(np.uint8)
    return g
def plain(t, st):
    f = dark(); y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]; return (f.astype(np.float32) * (1 + .35 * (1 - y))).astype(np.uint8)
def S(t0, t1, s, y, size=58, color=WH, name='psb', maxw=940): return (t0, t1, s if isinstance(s, list) else T(s, color), y, size, name, maxw)
def steps(items, extra=None):
    def g(f, t, st):
        for t0, t1, s, y, size, name, mw in items:
            if t0 <= t < t1:
                k = eo((t - t0) / .28) * (1 - sm((t - t1 + .22) / .22)); yy = y + int(22 * (1 - eo((t - t0) / .35)))
                line(f, s, name, size, 540, yy, k, 1.0, 0, 600, .6, mw)
        if extra: extra(f, t, st)
    return g
def ticks(items): return [(it[0] + .02, 'tick', .7) for it in items]
def mk(n, slug, hook, items, payoff, visual, extra=None, sfx=None, seed=None, root=55.0, top=True, dur=DUR, music=None):
    sf = (sfx if sfx is not None else ticks(items)) + [(5.45, 'thud', .45)]
    return dict(n=n, slug=slug, hook=hook, insight=steps(items, extra), payoff=payoff, visual=visual, sfx=sf, top=top, dur=dur,
                music=music or dict(seed=n, root=root * (1 + .06 * (n % 4)), chord=[(1, 1.2, 1.5), (1, 1.25, 1.5), (1, 1.2, 1.8)][n % 3]))
def pay(a, b=None): return ([(a, WH)], b)
def hl(a, k, b=''): return [(a, WH), (k, RH)] + ([(b, WH)] if b else [])
DOCS = dict(mosaic=(1.8, 3.5), card=(13.6, 15.8), famine=(15.8, 18.6), soup=(22.15, 23.25), lange=(23.25, 24.05), nyt=(24.05, 26.45), end=(27.65, 29.0))
MAP = dict(mosaic='jus', card='soup', famine='fam', soup='soup', lange='lange', nyt='nyt', end='crash')
def cl(k, speed=1.0, freeze=None, zoom=(1.0, 1.1)):
    def fn(t, st):
        if 'ph' not in st: doc.load_assets(); st['ph'] = doc.photos()
        return kb(st['ph'][MAP[k]], t, DUR, zoom[0], zoom[1])
    return fn
def chip(f, x, y, s, col, a=1.0, size=34, fg=CHAR):
    w = twidth(s, 'pb', size, 1) + 56; card(f, int(x - w / 2), y - 36, int(x + w / 2), y + 36, col, a); text(f, s, 'pb', size, x, y, fg, a, track=1)
def prog(t, t0, d=.5): return eo((t - t0) / d)

R = []
def add(*a, **k): R.append(mk(*a, **k))
# 1
add(1, 'first-frame-is-the-hook', hk('FIRST FRAME', hl('IS THE ', 'HOOK')) , [S(1.6, 3.4, 'Viewers decide before you speak.', 800), S(3.5, 5.3, [('Pause here. ', WH), ('Would you stay?', LM)], 800)],
    pay('OPEN ON YOUR BEST FRAME', 'Not the intro.'), dim(cl('mosaic', freeze=.45), .6))
# 2 result first
def ex2(f, t, st):
    labels = [('INTRO', GREY), ('SETUP', GREY), ('RESULT', LM)]; p = eio((t - 3.0) / 1.2)
    for i, (s, c) in enumerate(labels):
        x0 = {0: 80, 1: 380, 2: 680}[i]; tx = {0: 380, 1: 680, 2: 80}[i]; x = lerp(x0, tx, p) if i < 2 else lerp(680, 80, p)
        k = prog(t, 1.0 + i * .15); y = 1050
        card(f, int(x), y, int(x) + 280, y + 130, c if i == 2 else (60, 58, 58), k); text(f, s, 'pb', 40, int(x) + 140, y + 65, CHAR if i == 2 else WH, k, track=1)
    if t > 3.6: text(f, 'WATCHED FIRST', 'psb', 34, 220, 1010, LM, prog(t, 3.6))
add(2, 'result-before-explanation', hk('SHOW THE', hl('RESULT ', 'FIRST')), [S(1.3, 3.0, 'Most videos build up to the point.', 800), S(3.8, 5.3, 'Flip it. Earn the context after.', 800)],
    pay('PROOF FIRST, STORY SECOND'), plain, ex2)
# 3,4 pauses
def wavex(key, who):
    P = PA[key]; env = P['env']; keep = P['keep']; raw = P['raw_total']; kt = P['kept_total']
    def ex(f, t, st):
        waveform(f, t, env, raw, keep, ymid=980, hmax=190); p = eio((t - 3.0) / 1.6); cur = lerp(raw, kt, p)
        text(f, f'{cur:.1f}s', 'anton', 120, 540, 1240, WH if p < .5 else LM, prog(t, .8))
        if t > 4.6: text(f, f'-{raw - kt:.1f}s of dead air', 'psb', 44, 540, 1325, RH, prog(t, 4.6))
        if t < 3.0: chip(f, 540, 1360 - 60, 'RED = PAUSES & FLUBS', RED_HI, prog(t, 1.0), 30, WH)
    return ex
add(3, 'cut-the-pauses', hk('CUT THE', hl('PAUSES', '')), [S(1.0, 2.9, 'Play it. Spot the silence.', 690, 46)], pay('TIGHTER = WATCHED LONGER', 'Trim every gap.'), plain, wavex('doc', 'doc'))
def ex4(f, t, st): wavex('v2', 'v2')(f, t, st)
add(4, 'dead-air-adds-up', hk('DEAD AIR', hl('ADDS ', 'UP')), [S(1.0, 2.9, 'One raw take. Every gap counts.', 690, 46)], pay('7 SECONDS GONE', 'From a 45s take.'), plain, wavex('v2', 'v2'))
# 5 clean take
def ex5(f, t, st):
    rows = [('TAKE 1', 'um... so... wait, let me', RH, 940), ('TAKE 2', 'Here is the one thing.', LM, 1120)]
    for i, (a, b, c, y) in enumerate(rows):
        k = prog(t, 1.2 + i * 1.6)
        if k > 0:
            card(f, 70, y - 70, 1010, y + 70, (46, 44, 44), k); card(f, 70, y - 70, 84, y + 70, c, k); text(f, a, 'pb', 32, 190, y - 28, c, k, track=1); text(f, b, 'psb', 46, 560, y + 24, WH, k)
    if t > 3.0: cv2.line(f, (130, 950), (990, 950), RH, 8, cv2.LINE_AA) if t > 3.0 else None
    if t > 4.3: chip(f, 540, 1245, 'KEEP THE CLEAN ONE', LM, prog(t, 4.3), 34)
add(5, 'keep-the-clean-take', hk('KEEP THE', hl('CLEAN ', 'TAKE')), [S(0.9, 1.15, '', 700)], pay('RETAKE, DON\'T REPAIR', 'Cut the stumble.'), plain, ex5, sfx=[(1.2, 'tick', .7), (3.0, 'pop', .6), (4.3, 'ding', .35)])
# 6 one idea per caption
def ex6(f, t, st):
    if t < 3.3:
        k = prog(t, 1.0) * (1 - sm((t - 3.0) / .3)); card(f, 70, 760, 1010, 1190, (46, 44, 44), k)
        for i, s in enumerate(['so basically what I wanted to say today', 'is that when you write your captions you', 'should try to fit as many words as you', 'can on every single screen because']): text(f, s, 'pm', 34, 540, 830 + i * 85, GREY, k)
        if t > 2.0: chip(f, 540, 1255, 'WALL OF TEXT', RED_HI, prog(t, 2.0), 32, WH)
    else:
        text(f, 'ONE IDEA.', 'anton', 190, 540, 960, WH, prog(t, 3.5, .3), sc=1 + .1 * (1 - prog(t, 3.5, .4))); text(f, 'ONE LINE.', 'anton', 190, 540, 1160, LM, prog(t, 3.9, .3), sc=1 + .1 * (1 - prog(t, 3.9, .4)))
add(6, 'one-idea-per-caption', hk('ONE IDEA', hl('PER ', 'CAPTION')), [], pay('LESS TEXT, MORE IMPACT', 'Readable in 1 second.'), plain, ex6, sfx=[(3.5, 'pop', .6), (3.9, 'pop', .6)])
# 7 key word
def ex7(f, t, st):
    words = ['THIS', 'ONE', 'WORD', 'MATTERS']; y = 980
    if t < 3.2:
        x = 540 - (sum(twidth(w, 'psb', 62, 0) for w in words) + 3 * 24) / 2
        for i, w in enumerate(words): wd = twidth(w, 'psb', 62, 0); text(f, w, 'psb', 62, x + wd / 2, y, WH, prog(t, 1.0 + i * .12)); x += wd + 24
        if t > 1.9: chip(f, 540, 1130, 'EVERYTHING EQUAL = NOTHING STANDS OUT', RED_HI, prog(t, 1.9), 26, WH)
    else:
        p = prog(t, 3.3, .45)
        text(f, 'THIS ONE WORD', 'pb', 56, 540, 880, GREY, p); text(f, 'MATTERS', 'anton', lerp(80, 250, p), 540, 1090, LM, 1.0, sc=1 + .08 * (1 - p))
add(7, 'make-the-key-word-biggest', hk('MAKE THE', hl('KEY WORD ', 'BIG')), [], pay('SIZE = IMPORTANCE', 'Size is the hierarchy.'), plain, ex7, sfx=[(3.3, 'pop', .7)])
# 8 contrast
def ex8(f, t, st):
    h = 300; y0 = 790
    card(f, 0, y0, W, y0 + h, (170, 170, 170), prog(t, 1.0)); text(f, 'CAN YOU READ THIS?', 'pb', 62, 540, y0 + h // 2, (205, 205, 205), prog(t, 1.0))
    y1 = y0 + h + 40; card(f, 0, y1, W, y1 + h, (24, 24, 24), prog(t, 2.6)); text(f, 'CAN YOU READ THIS?', 'pb', 62, 540, y1 + h // 2, WH, prog(t, 2.6))
    if t > 1.8: chip(f, 540, y0 - 14 - 30, 'LOW CONTRAST', RED_HI, prog(t, 1.8), 28, WH)
    if t > 3.4: chip(f, 540, y1 + h + 50, 'HIGH CONTRAST', LM, prog(t, 3.4), 28)
add(8, 'contrast-makes-text-readable', hk('CONTRAST', hl('= ', 'READABLE')), [], pay('DIM THE BACKGROUND', 'Then add the text.'), plain, ex8)
# 9 evidence
add(9, 'evidence-beats-claims', hk('SHOW THE', hl('PROOF', '')), [S(1.4, 3.1, [('Claim: ', GREY), ('"It crashed."', WH)], 800, 60), S(3.2, 5.3, [('Evidence: ', GREY), ('the headline.', LM)], 800, 60)], pay('EVIDENCE BEATS CLAIMS', 'Show it on screen.'), dim(cl('nyt'), .38))
# 10 real photos
def ex10(f, t, st):
    if 1.2 < t < 3.4: chip(f, 540, 1000, 'STOCK  =  GENERIC', RED_HI, prog(t, 1.2), 34, WH)
    if t >= 3.4: chip(f, 540, 1000, 'REAL ARCHIVE PHOTO  =  TRUST', LM, prog(t, 3.4), 34)
add(10, 'real-photos-beat-stock', hk('REAL PHOTOS', hl('BEAT ', 'STOCK')), [S(1.3, 3.2, '', 1000)], pay('SPECIFIC BEATS GENERIC', 'Use the real thing.'), dim(cl('lange'), .7), ex10)
# 11 number as visual
def ex11(f, t, st):
    p = eo((t - 1.0) / 1.6); v = int(536 * p)
    text(f, str(v), 'anton', 420, 540, 980, LM if p >= 1 else WH, prog(t, .9, .2), sc=1 + .06 * (1 - prog(t, 2.6, .4)) if p >= 1 else 1.0)
    if t > 2.7: text(f, 'AD  -  the worst year to be alive', 'psb', 40, 540, 1210, GREY, prog(t, 2.7))
add(11, 'make-the-number-the-visual', hk('LET THE', hl('NUMBER ', 'LEAD')), [S(3.4, 5.3, 'No chart. No clutter.', 1320, 46, GREY)], pay('ONE NUMBER, FULL SCREEN'), plain, ex11, sfx=[(2.6, 'pop', .6), (1.0, 'tick', .5)])
# 12 big number own frame
def ex12(f, t, st):
    if t > 3.2: k = prog(t, 3.2, .3); f[:] = (f.astype(np.float32) * (1 - .8 * k)).astype(np.uint8); text(f, '1315', 'anton', 380, 540, 980, LM, k, sc=1 + .12 * (1 - prog(t, 3.2, .4))); text(f, 'the great famine begins', 'psb', 38, 540, 1190, WH, k)
add(12, 'big-numbers-get-their-own-frame', hk('BIG NUMBERS', hl('DESERVE ', 'A FRAME')), [S(1.2, 3.0, 'Busy frame. Number gets lost.', 820, 52)], pay('GIVE IT SPACE', 'Isolate the number.'), dim(cl('card'), .6), ex12, sfx=[(1.2, 'tick', .6), (3.2, 'pop', .8)])
# 13 typography is b-roll
def ex13(f, t, st):
    ws = [('NO', 1.0), ('FOOD', 1.7), ('FOR', 2.4), ('MONTHS', 3.0)]; cur = None
    for w, t0 in ws:
        if t >= t0: cur = (w, t0)
    if cur: w, t0 = cur; text(f, w, 'anton', 330, 540, 1000, LM if w == 'MONTHS' else WH, 1.0, sc=1 + .25 * (1 - prog(t, t0, .25)))
add(13, 'typography-is-b-roll', hk('WORDS CAN', hl('BE ', 'B-ROLL')), [], pay('MAKE TEXT MOVE', 'One word per beat.'), dim(cl('famine'), .35), ex13, sfx=[(1.0, 'tick', .8), (1.7, 'tick', .8), (2.4, 'tick', .8), (3.0, 'pop', .7)])
# 14 silence
def ex14(f, t, st):
    rs = np.random.RandomState(3); base = 980
    for i in range(54):
        x = 60 + i * 18; amp = (0.5 + 0.5 * abs(math.sin(i * .7 + t * 4))) * 150 * (rs.rand() * .5 + .5) if t < 3.2 else 3
        k = prog(t, .8 + i * .01); a = int(amp * k + 3); cv2.rectangle(f, (x, base - a), (x + 12, base + a), WH if t < 3.2 else RH, -1)
    if t > 3.3: text(f, '...', 'anton', 260, 540, 1210, WH, prog(t, 3.3)) 
    if t > 4.2: text(f, 'silence is louder', 'psb', 48, 540, 1210 + 130, LM, prog(t, 4.2))
add(14, 'silence-is-an-effect', hk('SILENCE', hl('IS AN ', 'EFFECT')), [], pay('DROP THE SOUND', 'Then hit the point.'), plain, ex14, sfx=[(4.2, 'thud', .7)])
# 15,16 meters
def avg(key): a = [x for x in MC[key] if x > -90]; return float(np.mean(a))
def peak(key): return float(np.max(MC[key]))
def ex15(f, t, st):
    meter(f, 900, 'VOICE', avg('voice'), t, 1.0, LM, lo=-60, hi=-5); meter(f, 1050, 'MUSIC', avg('music'), t, 2.0, RED_HI, lo=-60, hi=-5)
    if t > 3.0: text(f, f'music sits {avg("voice") - avg("music"):.0f} dB under voice', 'psb', 42, 540, 1190, WH, prog(t, 3.0))
add(15, 'music-sits-under-the-voice', hk('MUSIC STAYS', hl('UNDER', '')), [], pay('VOICE LEADS, ALWAYS', 'Music is texture.'), plain, ex15)
def ex16(f, t, st):
    meter(f, 900, 'VOICE', avg('voice'), t, 1.0, LM, lo=-60, hi=-5); meter(f, 1050, 'SFX PEAK', peak('sfx'), t, 2.0, RED_HI, lo=-60, hi=-5)
    if t > 3.0: text(f, 'effects are seasoning, not the meal', 'psb', 40, 540, 1190, WH, prog(t, 3.0))
add(16, 'quieter-effects-win', hk('SOFTER', hl('SFX ', 'WIN')), [], pay('IF YOU HEAR IT, IT\'S TOO LOUD'), plain, ex16)
# 17 ducking graph
def ex17(f, t, st):
    x0, x1, y0, y1 = 80, 1000, 780, 1200; v = np.array(MC['voice']); m = np.array(MC['music']); n = min(len(v), len(m), 150)
    p = eo((t - 1.0) / 3.0); card(f, x0, y0, x1, y1, (34, 32, 32), 1.0)
    for arr, col in ((m[:n], RH), (v[:n], LM)):
        pts = []
        for i in range(int(n * p)): pts.append((int(x0 + (x1 - x0) * i / n), int(lerp(y1 - 10, y0 + 10, clamp((arr[i] + 70) / 60)))))
        if len(pts) > 1: cv2.polylines(f, [np.array(pts)], False, col, 5, cv2.LINE_AA)
    chip(f, 280, 1250, 'VOICE', LM, prog(t, 1.2), 28); chip(f, 520, 1250, 'MUSIC', RED_HI, prog(t, 1.4), 28, WH)
    if t > 4.3: text(f, 'music dips when speech starts', 'psb', 36, 540, 1330, WH, prog(t, 4.3))
add(17, 'duck-the-music', hk('DUCK THE', hl('MUSIC', '')), [], pay('AUTO-DIP UNDER SPEECH', 'Clean, clear mix.'), plain, ex17)
# 18 glitch
def ex18(f, t, st):
    s = 'GLITCH'; k = prog(t, 1.0, .1)
    if k > 0:
        g = (1.0 < t < 2.0) and (int(t * 30) % 3 != 0); off = 14 if g else 0
        for dx, c in ((-off, (0, 0, 255)), (off, (255, 255, 0)), (0, WH)):
            text(f, s, 'anton', 300, 540 + dx, 1000, c, .8 if dx else 1.0, add=False) if dx or not g else text(f, s, 'anton', 300, 540, 1000, WH, 1.0)
        if g:
            for _ in range(5): y = random.randrange(840, 1160); f[y:y + 14] = np.roll(f[y:y + 14], random.randrange(-60, 60), axis=1)
add(18, 'a-glitch-is-a-pattern-interrupt', hk('GLITCH = A', hl('RESET ', 'BUTTON')), [S(2.6, 5.3, [('Use it once. ', WH), ('Not every cut.', LM)], 1230, 54)], pay('INTERRUPT, DON\'T OVERDO'), plain, ex18, sfx=[(1.0, 'tick', 1.0)])
# 19 sync
def ex19(f, t, st):
    y = 1000; cv2.line(f, (80, y), (1000, y), (90, 90, 90), 4)
    for lbl, tx, c in (('WORD', 3.0, WH), ('HIT', 3.0, LM)):
        pass
    x = int(80 + 920 * clamp(t / 6.0)); cv2.line(f, (x, y - 120), (x, y + 120), WH, 3)
    k = prog(t, 1.0); text(f, 'WORD: "FIVE-THIRTY-SIX"', 'psb', 34, 540, y - 150, WH, k)
    xw = int(80 + 920 * 3.0 / 6.0); cv2.circle(f, (xw, y), 18, WH, -1)
    if t >= 3.0:
        p = prog(t, 3.0, .3); chip(f, xw, y + 130, 'GRAPHIC HITS HERE', LM, p, 30)
        cv2.circle(f, (xw, y), int(18 + 70 * (1 - p)), LM, 4)
add(19, 'sync-graphics-to-the-word', hk('HIT THE', hl('WORD', '')), [S(3.6, 5.3, 'Same beat. Same frame.', 1250, 46, GREY)], pay('SYNC GRAPHIC TO WORD', 'Late = sloppy.'), plain, ex19, sfx=[(3.0, 'pop', .8)])
# 20 rhythm
CUTS = [0, 1.8, 3.5, 8.3, 13.6, 15.8, 18.6, 19.7, 22.15, 23.25, 24.05, 26.45, 27.65, 29.0]
def ex20(f, t, st):
    x0, x1, y = 60, 1020, 960; tot = 29.0
    for i in range(len(CUTS) - 1):
        a = x0 + (x1 - x0) * CUTS[i] / tot; b = x0 + (x1 - x0) * CUTS[i + 1] / tot; k = prog(t, 1.0 + i * .11, .3)
        card(f, int(a) + 2, y - 55, int(b) - 2, y + 55, LM if i % 2 else (200, 200, 200), k * (.9))
    if t > 2.8: text(f, '13 changes in 29 seconds', 'anton', 78, 540, 1140, WH, prog(t, 2.8))
    if t > 3.6: text(f, 'new visual every ~2.2s', 'psb', 42, 540, 1230, LM, prog(t, 3.6))
add(20, 'change-something-every-2-3-seconds', hk('CHANGE IT', hl('EVERY ', '2-3s')), [S(1.0, 2.6, 'One bar = one visual.', 780, 46, GREY)], pay('KEEP THE EYE MOVING'), plain, ex20)
# 21 static vs zoom
def v21(t, st):
    base = cl('mosaic', zoom=(1, 1))(t, st).copy(); z = 1 + .55 * eio((t - 1.5) / 3.5); M = np.float32([[z, 0, (1 - z) * W * .75], [0, z, (1 - z) * H / 2]])
    z2 = cv2.warpAffine(base, M, (W, H)); out = base.copy(); out[:, W // 2:] = z2[:, W // 2:]; cv2.line(out, (W // 2, 0), (W // 2, H), WH, 4); return (out.astype(np.float32) * .62).astype(np.uint8)
def ex21(f, t, st): chip(f, 270, 1230, 'STATIC', RED_HI, prog(t, 1.0), 34, WH); chip(f, 810, 1230, 'SLOW ZOOM', LM, prog(t, 1.4), 34)
add(21, 'static-is-flat', hk('STATIC SHOTS', hl('FEEL ', 'FLAT')), [], pay('ADD A SLOW PUSH', 'Subtle, 5-10%.'), v21, ex21)
# 22 hook in 3 words
def ex22(f, t, st):
    text(f, 'In this video I am going to show you', 'pm', 36, 540, 860, GREY, prog(t, 1.0)); text(f, 'how to improve your content', 'pm', 36, 540, 920, GREY, prog(t, 1.0))
    if t > 2.0: cv2.line(f, (120, 890), (960, 890), RH, 7, cv2.LINE_AA)
    if t > 3.0: text(f, 'STOP SCROLLING.', 'anton', 150, 540, 1130, LM, prog(t, 3.0, .25), sc=1 + .1 * (1 - prog(t, 3.0, .4)))
add(22, 'hook-in-three-words', hk('THREE WORDS', hl('IS ', 'ENOUGH')), [], pay('SHORT HOOK, FAST HIT', 'Cut the warm-up.'), plain, ex22, sfx=[(3.0, 'pop', .8)])
# 23 grade
def v23(t, st):
    f = cl('famine')(t, st); g0 = cv2.cvtColor(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR).astype(np.float32); ff = f.astype(np.float32)
    flat = np.clip(g0 * .75 + ff * .25 + 30, 0, 255).astype(np.uint8)
    c = np.clip((ff - 128) * 1.3 + 118, 0, 255) * np.array([.92, 1.0, 1.1], np.float32); gr = np.clip(c, 0, 255).astype(np.uint8)
    p = eio((t - 2.2) / 1.2); xs = int(W * p); out = flat.copy(); out[:, :xs] = gr[:, :xs]
    if 0 < xs < W: cv2.line(out, (xs, 0), (xs, H), WH, 4)
    return (out.astype(np.float32) * .85).astype(np.uint8)
def ex23(f, t, st):
    if t < 3.0: chip(f, 540, 1150, 'FLAT', RED_HI, prog(t, 1.0), 36, WH)
    if t > 3.6: chip(f, 540, 1150, 'GRADED', LM, prog(t, 3.6), 36)
add(23, 'grade-for-mood', hk('GRADE FOR', hl('MOOD', '')), [], pay('COLOUR SETS THE FEELING', 'Contrast + tone.'), v23, ex23)
# 24 palette
def ex24(f, t, st):
    cols = [((24, 22, 22), 'CHARCOAL'), ((226, 234, 238), 'OFF-WHITE'), (RED, 'RED'), (LIME, 'LIME ACCENT')]
    for i, (c, nm) in enumerate(cols):
        k = prog(t, 1.0 + i * .3); x = 100 + i * 220; y = 880; card(f, x, y, x + 200, y + 260, c, k); cv2.rectangle(f, (x, y), (x + 200, y + 260), (120, 120, 120), 2); text(f, nm, 'psb', 22, x + 100, y + 300, WH, k)
add(24, 'three-colours-one-accent', hk('PICK YOUR', hl('PALETTE', '')), [S(3.0, 5.2, '2 base colours. 1 accent.', 1230, 50, WH)], pay('CONSISTENT = PREMIUM', 'Reuse it everywhere.'), plain, ex24)
# 25 source label
def ex25(f, t, st):
    if t > 1.2: k = prog(t, 1.2, .35); card(f, 70, 1060, 1010, 1160, CHAR, .85 * k); cv2.rectangle(f, (70, 1060), (80, 1160), LM, -1); text(f, 'SOURCE: THE NEW YORK TIMES, 1929', 'pb', 34, 560, 1110, WH, k)
add(25, 'show-your-source', hk('SHOW YOUR', hl('SOURCE', '')), [S(3.2, 5.3, 'A small label = big trust.', 1250, 48, WH)], pay('CREDIT THE EVIDENCE'), dim(cl('nyt'), .38), ex25)
# 26 illustrative
def ex26(f, t, st):
    if t > 1.2: chip(f, 540, 1080, 'ILLUSTRATIVE - NOT EVIDENCE', RED_HI, prog(t, 1.2), 34, WH)
add(26, 'say-when-footage-is-illustrative', hk('LABEL', hl('ILLUSTRATIVE ', 'FOOTAGE')), [S(3.2, 5.3, 'Honesty keeps trust.', 1250, 52, WH)], pay('NEVER PASS OFF AS PROOF'), dim(cl('famine', speed=.7), .5), ex26)
# 27 before after text-led
def ex27(f, t, st):
    k = prog(t, 1.0); card(f, 70, 760, 1010, 980, (46, 44, 44), k); card(f, 70, 760, 84, 980, RED, k); text(f, 'BEFORE', 'pb', 30, 180, 800, RH, k, track=1); text(f, 'Hi guys, so today I want to', 'pm', 40, 540, 880, GREY, k); text(f, 'talk about editing...', 'pm', 40, 540, 930, GREY, k)
    k2 = prog(t, 2.8); card(f, 70, 1040, 1010, 1260, (46, 44, 44), k2); card(f, 70, 1040, 84, 1260, LM, k2); text(f, 'AFTER', 'pb', 30, 170, 1080, LM, k2, track=1); text(f, 'EDITING TRICK', 'anton', 100, 540, 1170, WH, k2); 
add(27, 'before-and-after-the-opening', hk('SAME IDEA.', hl('BETTER ', 'OPEN')), [], pay('LEAD WITH THE PAYOFF', 'Drop the greeting.'), plain, ex27, sfx=[(1.0, 'tick', .6), (2.8, 'pop', .7)])
# 28 icon on the word
def ex28(f, t, st):
    text(f, 'ONE BIG', 'pb', 70, 460, 960, WH, prog(t, 1.0)); text(f, 'IDEA', 'anton', 190, 540, 1100, LM, prog(t, 1.4))
    if t > 2.4:
        p = back((t - 2.4) / .4); cx, cy = 840, 1020; r = int(70 * p)
        if r > 2: cv2.circle(f, (cx, cy - 30), r, (60, 230, 250), -1); cv2.rectangle(f, (cx - int(r * .45), cy - 30 + r), (cx + int(r * .45), cy + r + int(r * .5)), (160, 160, 160), -1)
add(28, 'pop-an-icon-on-the-word', hk('ICON ON', hl('THE ', 'WORD')), [S(3.4, 5.2, 'Say it. Show it. Same beat.', 1300, 44, GREY)], pay('VISUAL ECHO = MEMORY'), plain, ex28, sfx=[(2.4, 'pop', .8)])
# 29 one point per scene
def ex29(f, t, st):
    items = ['hooks', 'captions', 'music', 'colour']
    if t < 3.3:
        for i, s in enumerate(items): k = prog(t, 1.0 + i * .2); card(f, 140, 780 + i * 105, 940, 860 + i * 105, (46, 44, 44), k); text(f, s.upper(), 'psb', 40, 540, 820 + i * 105, GREY, k)
        if t > 2.2: chip(f, 540, 1255, '4 POINTS = 0 REMEMBERED', RED_HI, prog(t, 2.2), 30, WH)
    else: text(f, 'HOOKS', 'anton', 330, 540, 1000, LM, prog(t, 3.5, .25), sc=1 + .1 * (1 - prog(t, 3.5, .4)))
add(29, 'one-point-per-scene', hk('ONE POINT', hl('PER ', 'SCENE')), [], pay('ONE IDEA, FULL FOCUS'), plain, ex29, sfx=[(3.5, 'pop', .8)])
# 30 safe zones
def ex30(f, t, st):
    x0, y0, x1, y1 = 290, 700, 790, 1340; cv2.rectangle(f, (x0, y0), (x1, y1), (150, 150, 150), 3); k = prog(t, 1.0)
    card(f, x0 + 3, y0 + 3, x1 - 3, y0 + 100, RED, .55 * k); card(f, x0 + 3, y1 - 150, x1 - 3, y1 - 3, RED, .55 * k)
    text(f, 'USERNAME / CAPTION', 'psb', 22, 540, y1 - 78, WH, k); text(f, 'TOP UI', 'psb', 22, 540, y0 + 50, WH, k)
    if t > 2.2: k2 = prog(t, 2.2); text(f, 'SAFE', 'anton', 110, 540, 1000, LM, k2); text(f, 'TEXT ZONE', 'pb', 34, 540, 1075, WH, k2)
add(30, 'keep-text-out-of-danger-zones', hk('RESPECT THE', hl('SAFE ', 'ZONE')), [S(3.6, 5.2, 'UI covers the edges.', 1290, 44, GREY)], pay('KEEP TEXT MID-SCREEN'), plain, ex30)

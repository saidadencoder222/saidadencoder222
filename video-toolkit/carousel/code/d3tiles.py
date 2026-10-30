import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad/c5')
from mrun import *
import cscenes as C, subprocess, illus as I
from PIL import Image
S3.setup(30, WHITE); S = S3.STATE; VDUR = S['VDUR']; OFF = (236, 236, 236)
FIX = {"going": "got", "'m": ""}
W_ = S['words']
def person(k, scale=1.0, dy=0):
    i = min(k, 1190) + 1; raw = cv2.imread(f"{C5}/work/fd30/{i:04d}.jpg"); fr = grade_modern(raw)
    al = alpha_arr(30); a = cv2.resize(np.array(al[min(k, len(al) - 1)]), (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255
    M = np.float32([[scale, 0, (1 - scale) * 540], [0, scale, (1 - scale) * 1920 + dy]])
    fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE); a = cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_LINEAR)
    a = np.clip((a - .06) / .88, 0, 1); return fr, cv2.GaussianBlur(a, (0, 0), 1.1)
def scrim(f, y0=1250, a=.55):
    g = np.clip((np.arange(H) - y0) / (H - y0), 0, 1)[:, None, None] ** 1.3 * a; return (f.astype(np.float32) * (1 - g)).astype(np.uint8)
def checker():
    yy, xx = np.mgrid[0:H, 0:W]; c = (((xx // 54) + (yy // 54)) % 2).astype(np.float32); return np.repeat((22 + 7 * c)[..., None], 3, 2).astype(np.uint8)
_CH = None
def bg_glow(t):
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]; base = np.array((26, 24, 24), np.float32)[None, None] * (1.15 - .5 * np.abs(yy - .42))
    g = np.zeros((H, W, 3), np.float32); cv2.circle(g, (860, 1500), 700, (1, 1, 1), -1); g = cv2.GaussianBlur(g, (0, 0), 260) * np.array((70, 40, 64), np.float32) * 0.9
    return np.clip(np.broadcast_to(base, (H, W, 3)) + g, 0, 255).astype(np.uint8)
_BG = None
def title(f, t):
    if t > 4.2: return
    a = clamp(t / .35) * clamp((3.8 - t) / .4)
    for i, (ln, sz, y, d) in enumerate((("STRUGGLING TO MAKE, EDIT & STRUCTURE", 60, 120, .0), ("BUSINESS OWNER?", 170, 250, .18), ("3 THINGS TO DO TODAY", 60, 395, .36))):
        u = clamp((t - d) / .45); e = eo(u)
        if e <= 0: continue
        zz = fit(ln, 'anton', sz, 960, 2); m_ = tex(ln, 'anton', zz, 2); yy = y + (1 - e) * 26
        put(f, m_, 540, yy, (0, 0, 0), .5 * a * e, blur=12, dy=8, sc=1.14 - .14 * e); put(f, m_, 540, yy, OFF, a * e, sc=1.14 - .14 * e)
CARDS = [(6.15, 8.7, '2.2M', 'AVERAGE WEEKLY VIEWS'), (11.3, 15.2, '01', 'CONTENT PLAN'), (20.25, 25.6, '02', 'QUALITY UP'), (28.1, 32.0, '03', 'TRACK CHANGES'), (33.4, 38.9, 'METRICS', 'FIND WHY THE HOOK WAS LOW')]
import math
def card_scene(f, t, person=False):
    for a0, a1, big, small in CARDS:
        if a0 <= t < a1:
            u = t - a0; e = eo(u / .4); o = e * clamp((a1 - t) / .3); zz = fit(big, 'anton', 260 if len(big) < 6 else 190, 940, 3); m = tex(big, 'anton', zz, 3)
            y = 560 if not person else 215
            put(f, m, 540, y + (1 - e) * 30, (0, 0, 0), .5 * o, blur=14, dy=8, sc=1.1 - .1 * e); put(f, m, 540, y + (1 - e) * 30, OFF, o, sc=1.1 - .1 * e)
            zs = fit(small, 'inter', 50, 940, 4, 700); ms = tex(small, 'inter', zs, 4, 700); put(f, ms, 540, y + 230 + (1 - e) * 20, (0, 0, 0), .5 * o, blur=8, dy=4); put(f, ms, 540, y + 230 + (1 - e) * 20, (200, 200, 205), o)
ZST = [(0, 1.0), (4.1, 1.09), (8.4, 1.0), (11.2, 1.1), (15.4, 1.02), (20.2, 1.11), (25.8, 1.03), (28.0, 1.1), (33.3, 1.0), (36.0, 1.08)]
def zoom(t):
    z = 1.0; zt = 0
    for ts, zz in ZST:
        if t >= ts: z, zt = zz, ts
    prev = [zz for ts, zz in ZST if ts < zt][-1:] or [1.0]
    return prev[0] + (z - prev[0]) * eo((t - zt) / .22) + .012 * math.sin(t * .8)
def anim_bg(t):
    sm = np.zeros((480, 270, 3), np.float32); yy = np.linspace(0, 1, 480, dtype=np.float32)[:, None, None]
    sm[:] = np.array((26, 24, 24), np.float32) * (1.15 - .5 * np.abs(yy - .42))
    for i, (cx, cy, r, col) in enumerate(((200 + 40 * math.sin(t * .6), 360 + 50 * math.cos(t * .5), 190, (70, 40, 66)), (60 + 30 * math.cos(t * .4), 120 + 40 * math.sin(t * .7), 150, (60, 52, 30)), (140 + 60 * math.sin(t * .35 + 2), 240 + 40 * math.cos(t * .3), 120, (50, 34, 56)))):
        g = np.zeros((480, 270, 3), np.float32); cv2.circle(g, (int(cx), int(cy)), r, (1, 1, 1), -1); g = cv2.GaussianBlur(g, (0, 0), r * .55) * np.array(col, np.float32); sm += g
    r = np.random.RandomState(5); pl = np.zeros((480, 270, 3), np.float32)
    for i in range(0):
        x0, y0, sp, sz = r.rand() * 270, r.rand() * 480, 6 + r.rand() * 14, 1 + r.rand() * 2.2
        x = (x0 + math.sin(t * .6 + i) * 8) % 270; y = (y0 - t * sp) % 480; al = (.35 + .35 * math.sin(t * 1.3 + i)) * 60
        cv2.circle(pl, (int(x), int(y)), int(sz), (al * 2.2, al * 2.1, al * 2.3), -1, cv2.LINE_AA)
    sm += cv2.GaussianBlur(pl, (0, 0), .8)
    return np.clip(cv2.resize(sm, (W, H), interpolation=cv2.INTER_CUBIC), 0, 255).astype(np.uint8)
def _split(big, small):
    if big == '2.2M': return big, small
    return small, big
def behind_cards(f, t):
    for a0, a1, big, small in CARDS:
        if a0 <= t < a1:
            bt, ft = _split(big, small); u = t - a0; e = eob(u / .55); o = clamp(u / .25) * clamp((a1 - t) / .3)
            words = bt.split(' ') if bt != big or len(bt) > 8 else [bt]
            if len(words) > 2: words = [' '.join(words[:len(words) // 2]), ' '.join(words[len(words) // 2:])]
            for j, wd in enumerate(words):
                zz = fit(wd, 'anton', 330 if len(words) > 1 else 420, 1000, 4); m = tex(wd, 'anton', zz, 4); sc = .6 + .4 * min(e, 1.06); y = 800 + (j - (len(words) - 1) / 2) * 300
                put(f, m, 540, y, (0, 0, 0), .45 * o, blur=16, dy=10, sc=sc); put(f, m, 540, y, OFF, o, sc=sc)
def front_cards(f, t):
    for a0, a1, big, small in CARDS:
        if a0 <= t < a1:
            bt, ft = _split(big, small); u = t - a0; e = eo(u / .4); o = e * clamp((a1 - t) / .3); y = 215
            zs = fit(ft, 'inter', 50, 940, 4, 700); ms = tex(ft, 'inter', zs, 4, 700); put(f, ms, 540, y + (1 - e) * 24, (0, 0, 0), .5 * o, blur=8, dy=4); put(f, ms, 540, y + (1 - e) * 24, (225, 225, 230), o)
            rr = int(60 + 260 * eo(u / .7)); ring = np.zeros((H, W), np.float32); cv2.circle(ring, (540, 800), rr, 1, 3, cv2.LINE_AA)
            f[:] = np.clip(f.astype(np.float32) + ring[..., None] * (60 * (1 - eo(u / .7))), 0, 255).astype(np.uint8)
def flash(f, t):
    for a0, a1, big, small in CARDS:
        d = t - a0
        if 0 <= d < .2: f[:] = np.clip(f.astype(np.float32) + 34 * (1 - d / .2), 0, 255).astype(np.uint8)
def frame(mode, t):
    k = int(round(t * 30))
    global _BG
    if mode == 'motion':
        if _BG is None: _BG = bg_glow(0)
        f = _BG.copy(); card_scene(f, t); return f
    fr, a = person(k, 1.0, 0) if mode != 'full' else (None, None)
    if mode == 'caps':
        f = scrim(fr.copy()); captions(f, t, W_, 1560, 58); return f
    if mode == 'cut':
        f = checker()
        for i, (ln, sz, y, d, col) in enumerate((("BUSINESS", 250, 520, .3, OFF), ("OWNER?", 250, 760, .55, OFF))):
            e = eo((t - d) / .4); zz = fit(ln, 'anton', sz, 980, 4); m_ = tex(ln, 'anton', zz, 4); put(f, m_, 540, y + (1 - e) * 40, col, e, sc=1.1 - .1 * e)
        return C.composite(f, fr, a)
    bg = anim_bg(t); sc_cur = None
    for s0, s1, fn, ps, y0 in I.SCENES:
        if s0 - .35 <= t < s1 + .3: sc_cur = (s0, s1, fn, ps, y0)
    if sc_cur:
        s0, s1, fn, ps, y0 = sc_cur; ain = eo((t - s0 + .35) / .45); aout = 1 - eo((t - s1) / .3); al = ain * aout
        im = np.array(fn(max(t - s0, 0)))
        if al > .01:
            yy = int(y0 + (1 - ain) * 40); h_, w_ = im.shape[:2]; rgb = im[..., :3][..., ::-1].astype(np.float32); A = (im[..., 3:4].astype(np.float32) / 255) * al
            reg = bg[yy:yy + h_, 60:60 + w_].astype(np.float32); bg[yy:yy + h_, 60:60 + w_] = (reg * (1 - A) + rgb * A).astype(np.uint8)
        pk = None
    ps_t = zoom(t) * .9
    for s0, s1, fn, ps, y0 in I.SCENES:
        w_in = eo((t - s0 + .35) / .5) * (1 - eo((t - s1) / .4))
        if w_in > 0: ps_t = ps_t * (1 - w_in) + ps * w_in
    fr, a = person(k, ps_t, 150 - 60 * (ps_t / .9 - 1) if ps_t > .85 else 0)
    f = scrim(C.composite(bg, fr, a), 1250, .78)
    title(f, t); captions(f, t, W_, 1600, 58); return f
def render(mode, t0, t1, out, size=(1080, 1920), crf=18):
    w, h = size; n = int(round((t1 - t0) * 30))
    ff = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '1080x1920', '-r', '30', '-i', '-'] + (['-vf', f'scale={w}:{h}:flags=lanczos'] if size != (1080, 1920) else [])
    if out.endswith('.webm'): ff += ['-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '32', '-row-mt', '1', '-pix_fmt', 'yuv420p', out]
    else: ff += ['-c:v', 'libx264', '-crf', str(crf), '-preset', 'fast', '-pix_fmt', 'yuv420p', out]
    p = subprocess.Popen(ff, stdin=subprocess.PIPE)
    for i in range(n): p.stdin.write(frame(mode, t0 + i / 30).tobytes())
    p.stdin.close(); p.wait(); print(mode, 'done', out, flush=True)
if __name__ == '__main__':
    import os; os.makedirs('work/t30', exist_ok=True); m = sys.argv[1]
    if m == 'preview':
        ims = []
        for md, t in (('caps', 1.0), ('cut', 1.2), ('motion', 7.0), ('full', 2.0), ('full', 12.5), ('full', 21.5)):
            ims.append(cv2.resize(frame(md, t), (270, 480)))
        cv2.imwrite('work/t30/pv.jpg', np.hstack(ims))
    elif m == 'cut': render('cut', 0, 7.5, 'work/t30/cut.webm', (540, 960))
    elif m == 'caps': render('caps', 0, 10.5, 'work/t30/caps.webm', (540, 960))
    elif m == 'motion': render('motion', 6.0, 15.5, 'work/t30/motion.webm', (540, 960))
    elif m == 'full': render('full', 0, VDUR, 'work/t30/full_sil.mp4')
    elif m == 'fullc':
        i = int(sys.argv[2]); n = 4; a0 = VDUR * i / n; a1 = VDUR * (i + 1) / n
        render('full', round(a0 * 30) / 30, round(a1 * 30) / 30, f'work/t30/full_c{i}.mp4')
    elif m == 'motion3':
        segs = [(7.0, 3.0), (12.0, 3.0), (20.8, 3.0)]; ts = [a + i / 30 for a, d in segs for i in range(int(d * 30))]
        ff = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '1080x1920', '-r', '30', '-i', '-', '-vf', 'scale=540:960:flags=lanczos', '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '32', '-row-mt', '1', '-pix_fmt', 'yuv420p', 'work/t30/motion.webm']
        p = subprocess.Popen(ff, stdin=subprocess.PIPE)
        for t in ts: p.stdin.write(frame('motion', t).tobytes())
        p.stdin.close(); p.wait(); print('motion3 done')

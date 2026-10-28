import sys; sys.path.insert(0, '/tmp/vt/c5')
import gd as G
from gd import *
GD = G.GD
CUT = {k: cv2.imread(f'{GD}/cutout_{k}.png', cv2.IMREAD_UNCHANGED) for k in LV}
_RS = {}
def cut_sized(key, h, crop_top=1.0):
    kk = (key, int(h), crop_top)
    if kk not in _RS:
        im = CUT[key]; ih = int(im.shape[0] * crop_top); im = im[:ih]; w = max(int(im.shape[1] * h / ih), 2); _RS[kk] = cv2.resize(im, (w, int(h)), interpolation=cv2.INTER_AREA)
    return _RS[kk]
def blit(f, rgba, cx, top, a=1.0, glow=None, glow_k=.0):
    h, w = rgba.shape[:2]; x0 = int(cx - w / 2); y0 = int(top)
    X0, Y0, X1, Y1 = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if X0 >= X1 or Y0 >= Y1 or a <= .01: return
    s = rgba[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]; al = s[..., 3:4].astype(np.float32) / 255 * a
    if glow is not None and glow_k > 0:   # palette rim glow behind the cutout
        m = np.zeros((H, W), np.float32); m[Y0:Y1, X0:X1] = s[..., 3] / 255.; g = cv2.GaussianBlur(m, (0, 0), 26) * glow_k * a; f[:] = np.clip(f.astype(np.float32) + g[..., None] * np.array(glow, np.float32), 0, 255).astype(np.uint8)
    sh = np.zeros((H, W), np.float32); sh[Y0:Y1, X0:X1] = s[..., 3] / 255.; sh = cv2.GaussianBlur(np.roll(sh, 18, 0), (0, 0), 16); f[:] = (f.astype(np.float32) * (1 - .55 * a * sh[..., None])).astype(np.uint8)
    roi = f[Y0:Y1, X0:X1].astype(np.float32); f[Y0:Y1, X0:X1] = (roi * (1 - al) + s[..., :3].astype(np.float32) * al).astype(np.uint8)
    # soft rim light from the level colour
    if glow is not None:
        edge = s[..., 3].astype(np.float32) / 255; edge = np.clip(edge - cv2.erode(edge, np.ones((7, 7), np.uint8)), 0, 1); edge = cv2.GaussianBlur(edge, (0, 0), 2) * .6 * a
        roi = f[Y0:Y1, X0:X1].astype(np.float32); f[Y0:Y1, X0:X1] = np.clip(roi + edge[..., None] * np.array(glow, np.float32), 0, 255).astype(np.uint8)
_BG = {}
def level_bg(key, w, h, t, dim=.5):
    if key not in _BG:
        im = cv2.imread(f'{GD}/{LV[key]["shot"]}'); im = cv2.resize(im, (w // 3, int(w // 3 * im.shape[0] / im.shape[1]))); _BG[key] = im
    im = _BG[key]; z = 1.15 + .03 * math.sin(t * .6); ih, iw = im.shape[:2]; s = max(w / iw, h / ih) * z
    M = np.float32([[s, 0, w / 2 - s * (iw / 2 + 8 * math.sin(t * .5))], [0, s, h / 2 - s * ih / 2]]); a = cv2.warpAffine(im, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    a = cv2.GaussianBlur(a, (0, 0), 9); pal = np.array(LV[key]['pal'], np.float32); a = a.astype(np.float32) * dim + pal * .22
    vg = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]; a = a * (1 - .35 * vg); return np.clip(a, 0, 255).astype(np.uint8)
def number_ghost(f, n, key, t, y, size=900, a=.16):
    m = tex(str(n), 'anton', size); put(f, m, 540, y, LV[key]['pal'], a)
def full_reveal(f, key, t, t0, t1):
    L = LV[key]; u = clamp((t - t0) / (t1 - t0)); k = eo((t - t0) / .35)
    bg = np.zeros((H, W, 3), np.uint8); bg[:] = np.full((H, W, 3), (14, 12, 12), np.uint8); bg = np.vstack([level_bg(key, W, 1000, t, .5), np.full((920, W, 3), 14, np.uint8)]); fade = np.clip((np.arange(H) - 700) / 300, 0, 1)[:, None, None]; bg = (bg * (1 - fade) + 14 * fade).astype(np.uint8)
    f[:] = (f.astype(np.float32) * (1 - k) + bg.astype(np.float32) * k).astype(np.uint8)
    number_ghost(f, L['n'], key, t, 760, 1000, .20)
    hh = 1480; rise = eo((t - t0) / .55); sc = lerp(.9, 1.03, eio(u)); cut = cut_sized(key, int(hh * sc)); cx = 540 + 6 * math.sin(t * 1.2); top = int(H - 1700 + (1 - rise) * 140 - (sc - 1) * 400)
    blit(f, cut, cx, top + 80, clamp((t - t0) / .25), L['pal'], 1.0)
    V.assemble(f, str(L['n']), 330, 140, 270, t, t0 + .05, L['pal'], dur=.7)
    V.name_block(f, t, t0 + .3, L['name'], L['sub'], L['pal'], t_end=None, size=150)
    c = eo((t - t0 - .4) / .4)
    if c > 0:
        card = shotcard(key, 400); ch, cw = card.shape[:2]; x0 = W - cw - 36; y0 = 120
        roi = f[y0:y0 + ch, x0:x0 + cw].astype(np.float32); f[y0:y0 + ch, x0:x0 + cw] = (roi * (1 - c) + card.astype(np.float32) * c).astype(np.uint8); cv2.rectangle(f, (x0, y0), (x0 + cw, y0 + ch), (235, 235, 235), 2)
        text(f, 'REAL LEVEL', 'psb', 20, x0 + cw / 2, y0 + ch + 24, (225, 225, 225), c, track=3)
        for i, col in enumerate(palette(key)): cv2.rectangle(f, (x0 + i * (cw // 4), y0 + ch + 42), (x0 + (i + 1) * (cw // 4) - 5, y0 + ch + 70), col, -1)
PANEL_H = 900
def speaker_base(k, t, zoom=1.0):
    i = min(k, int((VDUR - .3) * FPS)) + 1; fr = cv2.imread(f'{C5}/work/fd15/{i:04d}.jpg'); fr = grade(fr)
    M = np.float32([[zoom, 0, (1 - zoom) * 540], [0, zoom, (1 - zoom) * 900]]); return cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
PANEL_H = 0
def panel(f, key, t, t0, chips, lineup=False, hook=None):
    L = LV[key] if key else None; ein = eo((t - t0) / .4)
    if lineup:
        for i, k_ in enumerate(('sm', 'cf', 'pg', 'bab', 'clg')):
            c = cut_sized(k_, 430); x = 125 + i * 208; rise = eo((t - t0 - .15 - i * .1) / .4); fy = 4 * math.sin(t * 1.3 + i)
            blit(f, c, x, 1010 + (1 - rise) * 100 + fy, rise, LV[k_]['pal'], .8)
    else:
        sc = 1.0 + .02 * math.sin(t * .8); c = cut_sized(key, int(480 * sc)); fy = 6 * math.sin(t * 1.1); cx = 180
        blit(f, c, cx, 1030 + (1 - ein) * 90 + fy, ein, L['pal'], .9)
        text(f, str(L['n']), 'anton', 90, 70, 960, L['pal'], ein, shadow=.8); text(f, L['name'], 'bebas', 56, 130 + twidth(L['name'], 'bebas', 56, 3) / 2, 962, (245, 245, 245), ein, track=3, shadow=.8)
        for j, (tok, label) in enumerate(chips):
            tt = A(tok) if isinstance(tok, str) else tok; u = back((t - tt + .05) / .35)
            if u <= 0: continue
            y = 1130 + j * 64; x0 = 340; wd = int(twidth(label, 'psb', 30, 1)) + 44; xo = int((1 - clamp(u)) * 120)
            sub = f[y - 25:y + 25, x0 + xo:x0 + xo + wd]
            if sub.shape[1] == wd: sub[:] = (sub.astype(np.float32) * (1 - .82 * clamp(u)) + np.array((22, 20, 20), np.float32) * .82 * clamp(u)).astype(np.uint8)
            cv2.rectangle(f, (x0 + xo, y - 25), (x0 + xo + 6, y + 25), L['pal'], -1); text(f, label, 'psb', 30, x0 + xo + 26 + twidth(label, 'psb', 30, 1) / 2, y, (245, 245, 245), clamp(u), track=1)
    if hook:
        import inspo; inspo.title(f, t, .05, 5.0, 'TOP 5 GEOMETRY DASH', 'LEVELS AS HUMANS', (60, 220, 255), 1020, 60, 84)
import cap8
KEYS8 = {'stereo', 'madness', 'clutterfunk', 'polargeist', 'bass', 'cat', 'humans?', 'funky', 'neon', 'green', 'surfing', 'australia', 'female', 'easy', 'sweet', 'old', 'warm', 'wrong', 'right', 'comments', 'five', 'four', 'three', 'two', 'one'}
def mycaps(f, t, words):
    acc = (60, 220, 255)
    for st_, en_, kk in ((8.6, 16.6, 'sm'), (16.6, 20.9, 'cf'), (20.9, 30.9, 'pg'), (30.9, 39.6, 'bab'), (39.6, 99, 'clg')):
        if st_ <= t < en_: acc = LV[kk]['pal']
    cap8.draw(f, t, words, 1500, acc, KEYS8)
SH2 = []
def add2(t0, t1, kind, **k): SH2.append(dict(t0=t0, t1=t1, kind=kind, **k))
add2(0, 8.6, 'split', key=None, lineup=True, hook=('TOP 5 GEOMETRY DASH LEVELS', 'AS REAL HUMANS'), pulses=[.4, 5.1, 6.0, 7.5])
add2(8.6, 10.9, 'rev', key='sm', tr='whip'); add2(10.9, 16.6, 'split', key='sm', tr='whip', chips=[('female', 'SHE IS FEMALE'), ('easy', 'LEVEL IS EASY'), ('sweet', 'QUITE SWEET')], pulses=[12.8, 14.3, 15.8])
add2(16.6, 19.0, 'rev', key='cf', tr='whip'); add2(19.0, 20.9, 'split', key='cf', tr='whip', chips=[('funky', 'FUNKY')], pulses=[19.9])
add2(20.9, 23.7, 'rev', key='pg', tr='whip'); add2(23.7, 30.9, 'split', key='pg', tr='whip', chips=[('old', 'OLD'), ('warm', 'WARM'), ('neon', 'NEON GREEN')], pulses=[24.9, 25.9, 28.4])
add2(30.9, 33.5, 'rev', key='bab', tr='whip'); add2(33.5, 39.6, 'split', key='bab', tr='whip', chips=[('australia', 'LIVES IN AUSTRALIA'), ('surfing', 'LOVES SURFING'), ('soundtrack', 'SOUNDTRACK VIBES')], pulses=[34.3, 35.3, 36.8])
add2(39.6, 43.5, 'num', key='clg', tr='dip'); add2(43.5, 46.8, 'rev', key='clg', tr='whip'); add2(46.8, 47.9, 'zoom', key='clg', tr='flash')
add2(47.9, VDUR, 'split', key='clg', tr='whip', chips=[(47.3, 'A CAT')], pulses=[48.4, 49.5]); add2(VDUR, DUR, 'end')
def cur2(t):
    for s in SH2:
        if s['t0'] <= t < s['t1']: return s
    return SH2[-1]
def frame2(k):
    t = k / FPS; s = cur2(t); kind = s['kind']
    pz = 0.0
    for p in s.get('pulses', []):
        d = t - p
        if 0 <= d < .35: pz = 0
    if kind == 'split':
        u = clamp((t - s['t0']) / (s['t1'] - s['t0'])); f = speaker_base(k, t, 1.0 + .05 * eio(u) + pz); panel(f, s['key'], t, s['t0'], s.get('chips', []), s.get('lineup', False), s.get('hook'))
        gg = np.clip((np.arange(H, dtype=np.float32) - 1500) / 420, 0, 1)[:, None, None] * .5; f = (f.astype(np.float32) * (1 - gg)).astype(np.uint8)
        mycaps(f, t, S_['words'])
    elif kind == 'rev':
        f = np.full((H, W, 3), 14, np.uint8); full_reveal(f, s['key'], t, s['t0'], s['t1']); mycaps(f, t, S_['words'])
    elif kind == 'num':
        f = np.full((H, W, 3), (12, 11, 11), np.uint8); L = LV['clg']; V.assemble(f, '5', 900, 540, 800, t, s['t0'] + .05, L['pal'], dur=.8); text(f, 'LEVEL 5', 'psb', 40, 540, 1250, (230, 230, 230), eo((t - s['t0'] - .6) / .4), track=6, shadow=.8)
        c = cut_sized('clg', 900); a = np.zeros((H, W, 3), np.uint8); blit(a, c, 540, 380, 1.0); f = np.where(a > 0, (f.astype(np.float32) * .0 + 12).astype(np.uint8), f); mycaps(f, t, S_['words'])
    elif kind == 'zoom':
        f = np.full((H, W, 3), 14, np.uint8); u = clamp((t - s['t0']) / (s['t1'] - s['t0'])); f[:1100] = level_bg('clg', W, 1100, t, .55); c = CUT['clg']; hh = int(c.shape[0] * .30); head = c[:hh]; sc = 1.0 * lerp(1.0, .92, u); hd = cv2.resize(head, (int(head.shape[1] * 1000 * sc / head.shape[0]), int(1000 * sc)), interpolation=cv2.INTER_CUBIC)
        blit(f, hd, 540, 160, 1.0, LV['clg']['pal'], 1.0); text(f, 'A CAT.', 'anton', 230, 540, 1250, LV['clg']['pal'], eo((t - s['t0']) / .3), sc=1 + .12 * (1 - eo((t - s['t0']) / .4)), shadow=.9); mycaps(f, t, S_['words'])
    else:
        f = np.full((H, W, 3), (12, 11, 11), np.uint8); G.end_scene.__globals__['LV'] = LV
        u = clamp((t - VDUR + .1) / .6)
        f[:PANEL_H] = np.full((PANEL_H, W, 3), (16, 14, 14), np.uint8)
        for i, k_ in enumerate(('sm', 'cf', 'pg', 'bab', 'clg')):
            kk = clamp(u * 2.2 - i * .2); c = cut_sized(k_, 640); blit(f, c, 130 + i * 205, 150 + (1 - kk) * 80, kk, LV[k_]['pal'], .8)
            text(f, str(LV[k_]['n']), 'anton', 80, 130 + i * 205 - 60, 120, LV[k_]['pal'], kk, shadow=.9)
        text(f, 'WHO DID YOU PICTURE?', 'anton', 92, 540, 1150, (240, 240, 240), clamp(u * 2 - .8)); text(f, 'LET ME KNOW IN THE COMMENTS', 'psb', 38, 540, 1240, (60, 220, 255), clamp(u * 2 - 1.1), track=2)
    d = t - s['t0']; tr = s.get('tr', 'cut')
    if tr == 'flash' and 0 <= d < .18: f = cv2.addWeighted(f, 1, np.full_like(f, 255), .3 * (1 - d / .18), 0)
    if tr == 'dip' and d < .4: f = (f.astype(np.float32) * clamp(d / .4)).astype(np.uint8)
    if tr == 'whip' and 0 <= d < .26:
        kk = int(1 + 36 * (1 - d / .26) ** 1.6) | 1; f = cv2.blur(f, (kk, 1)); f = np.roll(f, int(-70 * (1 - d / .26) ** 2), axis=1)
    f = cv2.addWeighted(f, .7, cv2.multiply(f, doc.vig(), scale=1 / 255), .3, 0); return cv2.addWeighted(f, 1, doc.grain(k), .02, -128 * .02)
frame = frame2
def _chunk(args):
    a, b, out = args
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', '30', '-i', '-', '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for k in range(a, b): enc.stdin.write(np.ascontiguousarray(frame2(k)).tobytes())
    enc.stdin.close(); enc.wait(); return out
def preview(ts, out, cols=8):
    tiles = [cv2.resize(frame2(int(t * FPS)), (270, 480)) for t in ts]
    while len(tiles) % cols: tiles.append(np.zeros_like(tiles[0]))
    cv2.imwrite(out, np.vstack([np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]))
SH = SH2

"""Trial-reel engine: shared layout (hook -> insight -> payoff), typography, audio synth, renderer."""
import sys, os, json, math, random, subprocess
S = '/tmp/vt'
sys.path.insert(0, f'{S}/c2'); sys.path.insert(1, f'{S}/c1')
import numpy as np, cv2
import doc
from doc import W, H, FPS, clamp, sm, eo, eio, lerp, back, tex, twidth, put, text, OFFW, RED, LIME, IMG, tone, kb, warp, over
doc.FILES.update({'pb': 'Poppins-Bold.ttf', 'psb': 'Poppins-SemiBold.ttf', 'pm': 'Poppins-Medium.ttf'})
R3 = f'{S}/c3'; DUR = 7.0
CHAR = (22, 20, 20); GREY = (140, 140, 140); DIMT = (95, 95, 95); RED_HI = (72, 64, 238); GOOD = (0, 255, 190)

# ---------------------------------------------------------------- assets
DOCV = f'{S}/c2/out/worst_years_documentary_v2.mp4'
def assets(): return {}
def loadseg(a, b):
    cap = cv2.VideoCapture(DOCV); cap.set(cv2.CAP_PROP_POS_FRAMES, int(round(a * FPS))); fr = []
    for _ in range(int(round((b - a) * FPS))):
        ok, f = cap.read()
        if not ok: break
        fr.append(cv2.resize(f, (720, 1280), interpolation=cv2.INTER_AREA))
    cap.release(); return fr
def clipsrc(a, b, speed=1.0, freeze=None, zoom=(1.0, 1.08)):
    def fn(t, st):
        if 'fr' not in st: st['fr'] = loadseg(a, b)
        fr = st['fr']; n = len(fr)
        if freeze is not None: i = int(freeze * FPS)
        else:
            u = int(t * FPS * speed); p = u % (2 * n - 2) if n > 1 else 0; i = p if p < n else 2 * n - 2 - p
        f = cv2.resize(fr[min(i, n - 1)], (W, H), interpolation=cv2.INTER_CUBIC); z = lerp(zoom[0], zoom[1], clamp(t / DUR))
        if z > 1.001: M = np.float32([[z, 0, (1 - z) * W / 2], [0, z, (1 - z) * H / 2]]); f = cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR)
        return f
    return fn
def dark(): return np.full((H, W, 3), CHAR, np.uint8)

# ---------------------------------------------------------------- typography
def segw(segs, name, size, track=0, w=600, gap=None):
    gap = int(size * .26) if gap is None else gap; return sum(twidth(s, name, size, track, w) for s, c in segs) + gap * (len(segs) - 1), gap
def fit_size(segs, name, size, maxw, track=0, w=600):
    while segw(segs, name, size, track, w)[0] > maxw and size > 20: size -= 4
    return size
def line(f, segs, name, size, cx, cy, a=1.0, sc=1.0, track=0, w=600, shadow=.0, maxw=960, key_pop=0.0):
    """centered multi-colour line; segs = [(text, color)]"""
    size = fit_size(segs, name, size, maxw, track, w); tw, gap = segw(segs, name, size, track, w); x = cx - tw * sc / 2
    for s, c in segs:
        wd = twidth(s, name, size, track, w); text(f, s, name, size, x + wd * sc / 2, cy, c, a, track=track, w=w, sc=sc, shadow=shadow); x += (wd + gap) * sc
    return size
def grad_top(f, h=560, k=.82): g = (1 - np.clip(np.arange(f.shape[0], dtype=np.float32)[:h] / h, 0, 1)) ** 1.5 * k; f[:h] = (f[:h].astype(np.float32) * (1 - g)[:, None, None]).astype(np.uint8)
def grad_bot(f, y0=1330, k=.88): n = H - y0; g = np.clip(np.arange(n, dtype=np.float32) / (n * .5), 0, 1) ** 1.2 * k; f[y0:] = (f[y0:].astype(np.float32) * (1 - g)[:, None, None]).astype(np.uint8)
def vig(f): return cv2.multiply(f, doc.vig(), scale=1 / 255)

def hook(f, t, lines, y0=235, size=150, hold_to=5.4):
    """big Anton hook; fully visible at t=0 (paused first frame works); settles, then yields to payoff."""
    sc = 1 + .045 * (1 - eo(t / .35)); a = 1.0 if t < hold_to else 1 - sm((t - hold_to) / .35)
    if a <= .01: return
    y = y0
    for segs in lines:
        s = line(f, segs, 'anton', size, 540, y + size * .5, a, sc, 0, 600, .8); y += s * 1.1
    u = eo((t - .15) / .5)
    if u > 0: cv2.rectangle(f, (540 - int(150 * u), int(y + 14)), (540 + int(150 * u), int(y + 20)), RED, -1)
def sub(f, t, t0, t1, s, y, size=46, color=OFFW, name='psb', a=1.0, maxw=940):
    if not (t0 <= t < t1): return
    k = sm((t - t0) / .22) * (1 - sm((t - t1 + .2) / .2)) if t1 - t0 > .5 else 1.0
    segs = s if isinstance(s, list) else [(s, color)]; line(f, segs, name, size, 540, y, a * k, 1.0, 0, 600, .6, maxw)
def payoff(f, t, l1, l2=None, t0=5.45):
    if t < t0: return
    k = clamp((t - t0) / .22); sc = 1 + .12 * (1 - eo((t - t0) / .3)); y = 1500
    band = np.clip((np.arange(H, dtype=np.float32) - 1360) / 140, 0, 1)[:, None, None] * .93 * k; f[:] = (f.astype(np.float32) * (1 - band) + np.array(CHAR, np.float32) * band).astype(np.uint8)
    s = line(f, l1, 'bebas', 132, 540, y, k, sc, 3, 600, .5, 960)
    u = eo((t - t0 - .1) / .4); cv2.rectangle(f, (540 - int(110 * u), y + int(s * .52)), (540 + int(110 * u), y + int(s * .52) + 5), RED, -1)
    if l2: line(f, l2 if isinstance(l2, list) else [(l2, GREY)], 'psb', 42, 540, y + int(s * .52) + 60, k, 1.0, 1, 600, 0, 920)
def progress(f, t, dur): cv2.rectangle(f, (0, 0), (int(W * clamp(t / dur)), 5), RED, -1)
def finish(f, n):
    f = vig(f); g = doc.grain(n); return cv2.addWeighted(f, 1, g, .035, -128 * .035)

# ---------------------------------------------------------------- data graphics
def waveform(f, t, env, dur_raw, keep, x0=60, x1=1020, ymid=900, hmax=170, t_play=(1.0, 2.6), t_collapse=(3.0, 4.6), keep_col=OFFW, cut_col=RED_HI, labels=True, show_cut_label=True):
    n = len(env); bw = (x1 - x0) / n; bin_t = dur_raw / n; kept = []
    for i in range(n):
        c = (i + .5) * bin_t; kept.append(any(a <= c <= b for a, b in keep))
    p = eio((t - t_collapse[0]) / (t_collapse[1] - t_collapse[0])); nk = sum(kept); newbw = (x1 - x0) / max(nk, 1); xs = []; kx = 0
    for i in range(n):
        ox = x0 + i * bw
        if kept[i]: tx = x0 + kx * newbw; kx += 1; xs.append((lerp(ox, tx, p), lerp(bw, newbw, p), 1.0))
        else: xs.append((lerp(ox, x0 + kx * newbw, p), lerp(bw, 0, p), 1 - p))
    play = clamp((t - t_play[0]) / (t_play[1] - t_play[0]))
    for i in range(n):
        x, w_, alpha = xs[i]; h = max(int(env[i] ** .7 * hmax), 3)
        if w_ < .6 or alpha < .03: continue
        shown = i / n <= play or t > t_play[1]
        col = (keep_col if kept[i] else cut_col) if shown else (60, 60, 60)
        cv2.rectangle(f, (int(x), ymid - h), (int(x + max(w_ - 2, 1)), ymid + h), tuple(int(c * (alpha if not kept[i] else 1)) for c in col), -1)
    if t_play[0] <= t < t_play[1]: px = int(x0 + play * (x1 - x0)); cv2.line(f, (px, ymid - hmax - 30), (px, ymid + hmax + 30), (255, 255, 255), 3, cv2.LINE_AA)
def meter(f, y, label, db, t, t0, color, lo=-45, hi=-5, x0=250, x1=990, sub_label=None, h=62):
    k = eo((t - t0) / .6); frac = clamp((db - lo) / (hi - lo)) * k
    text(f, label, 'pb', 36, 130, y, OFFW, clamp(k * 3), track=1); cv2.rectangle(f, (x0, y - h // 2), (x1, y + h // 2), (46, 44, 44), -1); cv2.rectangle(f, (x0, y - h // 2), (int(x0 + (x1 - x0) * frac), y + h // 2), color, -1)
    if k > .9: text(f, f'{db:.0f} dBFS' + (f'  {sub_label}' if sub_label else ''), 'psb', 30, int(x0 + (x1 - x0) * frac) + 8 + (twidth(f'{db:.0f} dBFS' + (f'  {sub_label}' if sub_label else ''), 'psb', 30, 0) // 2), y, OFFW, 1.0) if frac < .75 else text(f, f'{db:.0f} dBFS', 'psb', 30, int(x0 + (x1 - x0) * frac) - 80, y, CHAR, 1.0)

# ---------------------------------------------------------------- audio synth (quiet; reels read fine on mute)
SR = 48000
def _n(n): return np.random.RandomState(n % 997).randn(n)
def _bp(x, lo, hi):
    from scipy.signal import butter, sosfilt; return sosfilt(butter(2, [lo / (SR / 2), min(hi, SR / 2 - 100) / (SR / 2)], 'band', output='sos'), x)
def _lp(x, fc):
    from scipy.signal import butter, sosfilt; return sosfilt(butter(2, fc / (SR / 2), 'low', output='sos'), x)
def _hp(x, fc):
    from scipy.signal import butter, sosfilt; return sosfilt(butter(2, fc / (SR / 2), 'high', output='sos'), x)
def s_pop(): n = int(.14 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(260 + 520 * np.exp(-t * 38)) / SR) * np.exp(-t * 32) * .6
def s_tick(): n = int(.012 * SR); return _bp(_n(n), 2400, 5200) * np.exp(-np.arange(n) / SR * 380) * 1.2
def s_whoosh(): n = int(.38 * SR); x = _bp(_n(n), 500, 4200); return x * np.sin(np.pi * np.linspace(0, 1, n)) ** 1.8 * .9
def s_thud(): n = int(.5 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(46 + 40 * np.exp(-t * 20)) / SR) * np.exp(-t * 8) * 1.0
def s_ding(): n = int(.8 * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * 1568 * t) + .3 * np.sin(2 * np.pi * 2349 * t)) * np.exp(-t * 6) * .5
SFX = {'pop': s_pop, 'tick': s_tick, 'whoosh': s_whoosh, 'thud': s_thud, 'ding': s_ding}
def make_audio(dur, spec, events, out):
    from scipy.io import wavfile
    N = int((dur + .3) * SR); t_ = np.arange(N) / SR; rs = np.random.RandomState(spec.get('seed', 1)); root = spec.get('root', 55.0); chord = spec.get('chord', (1, 1.2, 1.5)); music = np.zeros(N)
    for k, m in enumerate(chord):
        for dt in (-.5, .0, .5): music += np.sin(2 * np.pi * (root * 2 * m + dt) * t_ + rs.rand() * 6) * (.5 / (k + 1)) + .5 * np.sin(2 * np.pi * (root * 4 * m + dt) * t_ + rs.rand() * 6) * .15
    music += .9 * np.sin(2 * np.pi * root * t_) * (.5 + .5 * np.sin(2 * np.pi * .13 * t_ + rs.rand() * 6)); music = _lp(music, 900)
    bpm = spec.get('bpm', 0)
    if bpm:
        per = 60 / bpm; tt = .5
        while tt < dur: i = int(tt * SR); sg = s_tick() * .5; music[i:i + len(sg)] += sg[:N - i] * .35; tt += per
    fade = np.minimum(np.minimum(t_ / .5, (dur + .3 - t_) / .9), 1) ** 2; music *= fade * .11
    sfx = np.zeros(N)
    for t, kind, g in events:
        s = SFX[kind](); i = int(t * SR)
        if 0 <= i < N: n = min(len(s), N - i); sfx[i:i + n] += s[:n] * g
    mix = music + sfx * .30; mix = np.tanh(mix * 1.2) / 1.2; wavfile.write(out, SR, (np.clip(mix, -1, 1) * 32767).astype(np.int16))

# ---------------------------------------------------------------- renderer
def render_reel(r, out_dir=f'{R3}/out'):
    os.makedirs(out_dir, exist_ok=True); name = f"reel_{r['n']:02d}_{r['slug']}"; sil = f'{R3}/work/{name}_sil.mp4'; wav = f'{R3}/work/{name}.wav'; final = f'{out_dir}/{name}.mp4'
    assets(); dur = r.get('dur', DUR); nf = int(round(dur * FPS)); state = {}
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', sil], stdin=subprocess.PIPE)
    for k in range(nf):
        t = k / FPS; f = r['visual'](t, state); f = np.ascontiguousarray(f)
        if r.get('top', True): grad_top(f, 620, .8)
        hook(f, t, r['hook'], r.get('hook_y', 235), r.get('hook_size', 150)); r['insight'](f, t, state) if r.get('insight') else None
        payoff(f, t, r['payoff'][0], r['payoff'][1] if len(r['payoff']) > 1 else None); progress(f, t, dur)
        enc.stdin.write(np.ascontiguousarray(finish(f, k)).tobytes())
    enc.stdin.close(); enc.wait()
    make_audio(dur, r.get('music', {}), r.get('sfx', []), wav)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', sil, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', 'loudnorm=I=-17:TP=-2:LRA=7', '-c:a', 'aac', '-b:a', '160k', '-t', f'{dur:.2f}', '-movflags', '+faststart', final], check=True)
    os.remove(sil); os.remove(wav); return final
def sample_frames(r, ts, state=None):
    assets(); st = {}; out = []
    for t in ts:
        f = np.ascontiguousarray(r['visual'](t, st))
        if r.get('top', True): grad_top(f, 620, .8)
        hook(f, t, r['hook'], r.get('hook_y', 235), r.get('hook_size', 150)); r['insight'](f, t, st) if r.get('insight') else None
        payoff(f, t, r['payoff'][0], r['payoff'][1] if len(r['payoff']) > 1 else None); progress(f, t, r.get('dur', DUR)); out.append(finish(f, int(t * 30)))
    return out

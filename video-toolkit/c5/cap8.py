import sys, math
sys.path.insert(0, '/tmp/vt/c4')
import numpy as np, cv2
import film2 as F
from film2 import doc, W, H, clamp, sm, eo, eio, lerp, back, tex, twidth, put
doc.FILES.update({'serif': 'InstrumentSerif-Italic.ttf', 'inter': 'Inter.ttf'})
WHITE = (255, 255, 255)
def _clean(w, i=0):
    s = w.strip('.,?!').lower()
    return {'i': 'I', "i'm": "I'm", "i'd": "I'd", "i'll": "I'll", 'icp': 'ICP'}.get(s, s)
def phrases(words):
    out = []; cur = []
    for k, w in enumerate(words):
        if cur and (w[1] - cur[-1][2] > .22 or len(cur) >= 4 or w[0].lower().strip('.,') in ('number', 'because', 'maybe', 'and', 'but', 'i') and len(cur) >= 2): out.append(cur); cur = []
        cur.append(w)
        if w[0][-1] in '.?!': out.append(cur); cur = []
    if cur: out.append(cur)
    return out
def layout(items, name, size, maxw, track, gap):
    """items: list of strings; returns (widths, total) after fitting size"""
    while True:
        ws = [twidth(s, name, size, track) for s in items]; tot = sum(ws) + gap * (len(items) - 1)
        if tot <= maxw or size <= 28: return size, ws, tot
        size -= 3
def draw_w(f, s, name, size, x, y, a, sc=1.0, track=0, col=WHITE, blur=0.0, dy=0, clip=None):
    if a <= .01: return
    m = tex(s, name, size, track); put(f, m, x, y, col, a, sc, blur=blur, dy=dy, clip=clip)
def soft_shadow(f, s, name, size, x, y, a, sc=1.0, track=0, k=.28):
    m = tex(s, name, size, track); put(f, m, x, y + 5 * sc, (0, 0, 0), a * k, sc, blur=10)
# --------------------------------------------------------------------------- the eight treatments
def st1_word_reveal(f, t, ph, y, accent, keys):
    """Bebas, per-word rise + scale + fade, key word in accent."""
    toks = [_clean(w[0]).upper() for w in ph]; size, ws, tot = layout(toks, 'bebas', 96, 940, 3, 24); x = 540 - tot / 2
    out = clamp((ph[-1][2] + .22 - t) / .14)
    for w, s, wd in zip(ph, toks, ws):
        u = eo((t - w[1] + .04) / .26)
        if u > 0:
            col = accent if _clean(w[0]).lower() in keys else WHITE; sc = lerp(1.22, 1.0, u); soft_shadow(f, s, 'bebas', size, x + wd / 2, y + (1 - u) * 26, u * out, sc, 3)
            draw_w(f, s, 'bebas', size, x + wd / 2, y + (1 - u) * 26, u * out, sc, 3, col)
        x += wd + 24
def st2_key_slam(f, t, ph, y, accent, keys):
    """Anton: key word slams in large from 1.8x with blur, others small Inter above."""
    kw = next((w for w in ph if _clean(w[0]).lower() in keys), max(ph, key=lambda w: len(w[0])))
    others = ' '.join(_clean(w[0]) for w in ph if w is not kw); out = clamp((ph[-1][2] + .25 - t) / .15)
    u = eo((t - kw[1] + .05) / .22); s = _clean(kw[0]).upper(); size = 170
    while twidth(s, 'anton', size, 0) > 900 and size > 60: size -= 6
    sc = lerp(1.8, 1.0, u); draw_w(f, s, 'anton', size, 540, y, u * out, sc, 0, accent if _clean(kw[0]).lower() in keys else WHITE, blur=(1 - u) * 14)
    if others and u > .3: draw_w(f, others, 'inter', 40, 540, y - size * .72, eo((t - kw[1] - .08) / .25) * out, 1.0, 1, (225, 225, 225))
def st3_sentence_track(f, t, ph, y, accent, keys):
    """Inter: whole sentence fades in while tracking collapses from wide to tight."""
    s = ' '.join(_clean(w[0]) for w in ph); u = eo((t - ph[0][1] + .05) / .45); out = clamp((ph[-1][2] + .25 - t) / .18); tr = int(round(lerp(26, 2, u) / 2) * 2)
    size = 54
    while twidth(s, 'inter', size, tr) > 940 and size > 28: size -= 2
    draw_w(f, s, 'inter', size, 540, y, u * out, 1.0, tr, WHITE, w=None) if False else draw_w(f, s, 'inter', size, 540, y, u * out, 1.0, tr)
def st4_mask_wipe(f, t, ph, y, accent, keys):
    """Bebas phrase revealed left-to-right by a hard-edged soft mask, small underline sweeps."""
    s = ' '.join(_clean(w[0]) for w in ph).upper(); size = 120
    while twidth(s, 'bebas', size, 3) > 940 and size > 40: size -= 4
    m = tex(s, 'bebas', size, 3); wd = twidth(s, 'bebas', size, 3); u = eio((t - ph[0][1] + .05) / .38); out = clamp((ph[-1][2] + .25 - t) / .15)
    clip = np.zeros_like(m); xe = int(m.shape[1] * u); clip[:, :max(xe, 1)] = 1; clip = cv2.GaussianBlur(clip, (0, 0), 5); put(f, m * clip, 540, y, WHITE, out)
    x0 = 540 - wd / 2; cv2.line(f, (int(x0), int(y + size * .55)), (int(x0 + wd * u), int(y + size * .55)), accent, 4, cv2.LINE_AA) if out > .5 else None
def st5_stack(f, t, ph, y, accent, keys):
    """Two stacked Bebas lines, second line larger, each line pops on its own beat."""
    if len(ph) < 2: return st1_word_reveal(f, t, ph, y, accent, keys)
    h = len(ph) // 2; l1 = ' '.join(_clean(w[0]) for w in ph[:h]).upper(); l2 = ' '.join(_clean(w[0]) for w in ph[h:]).upper(); out = clamp((ph[-1][2] + .25 - t) / .15)
    z1 = 76; z2 = 128
    while twidth(l1, 'bebas', z1, 3) > 900 and z1 > 30: z1 -= 3
    while twidth(l2, 'bebas', z2, 3) > 900 and z2 > 40: z2 -= 4
    u1 = eo((t - ph[0][1] + .03) / .22); u2 = eo((t - ph[h][1] + .03) / .24)
    draw_w(f, l1, 'bebas', z1, 540, y - z2 * .52, u1 * out, lerp(1.15, 1, u1), 3, (232, 232, 232), dy=(1 - u1) * 18)
    draw_w(f, l2, 'bebas', z2, 540, y + z1 * .1, u2 * out, lerp(1.25, 1, u2), 3, accent if any(_clean(w[0]).lower() in keys for w in ph[h:]) else WHITE, dy=(1 - u2) * 20)
def st6_serif(f, t, ph, y, accent, keys):
    """Editorial serif italic, large, slow fade-up with slight scale and blur resolve."""
    s = ' '.join(_clean(w[0]) for w in ph); u = eo((t - ph[0][1] + .05) / .6); out = clamp((ph[-1][2] + .3 - t) / .25); size = 104
    while twidth(s, 'serif', size, 0) > 940 and size > 44: size -= 4
    draw_w(f, s, 'serif', size, 540, y, u * out, lerp(.93, 1.0, u), 0, WHITE, blur=(1 - u) * 8, dy=(1 - u) * 16)
def st7_blur_in(f, t, ph, y, accent, keys):
    """Inter bold per-word blur-to-sharp with horizontal drift, tight tracking."""
    toks = [_clean(w[0]) for w in ph]; size, ws, tot = layout(toks, 'inter', 64, 940, 1, 22); x = 540 - tot / 2; out = clamp((ph[-1][2] + .22 - t) / .14)
    for w, s, wd in zip(ph, toks, ws):
        u = eo((t - w[1] + .04) / .3)
        if u > 0: draw_w(f, s, 'inter', size, x + wd / 2 + (1 - u) * 34, y, u * out, 1.0, 1, accent if _clean(w[0]).lower() in keys else WHITE, blur=(1 - u) * 9)
        x += wd + 22
def st8_number_punch(f, t, ph, y, accent, keys):
    """Giant ghost word behind (white, low opacity) + clean line in front — for numbers / rankings."""
    kw = next((w for w in ph if _clean(w[0]).lower() in keys or _clean(w[0]).isdigit()), ph[0]); s = _clean(kw[0]).upper(); u = eo((t - kw[1] + .05) / .3); out = clamp((ph[-1][2] + .25 - t) / .15)
    size = 300
    while twidth(s, 'anton', size, 0) > 960 and size > 80: size -= 8
    draw_w(f, s, 'anton', size, 540, y - 40, .16 * u * out, lerp(1.3, 1, u), 0, WHITE)
    line = ' '.join(_clean(w[0]) for w in ph); z = 58
    while twidth(line, 'inter', z, 1) > 940 and z > 28: z -= 2
    draw_w(f, line, 'inter', z, 540, y + 10, u * out, 1.0, 1, WHITE)
STYLES = [st1_word_reveal, st2_key_slam, st3_sentence_track, st4_mask_wipe, st5_stack, st6_serif, st7_blur_in, st8_number_punch]
_ASSIGN = {}
def assign(phs, keys):
    """Pick a treatment per phrase from the meaning/length, avoiding repeats back to back."""
    prev = -1; res = []
    for i, ph in enumerate(phs):
        txt = ' '.join(_clean(w[0]) for w in ph).lower(); n = len(ph); has_key = any(_clean(w[0]).lower() in keys for w in ph)
        if any(w[0][-1] in '?' for w in ph) or ('wrong' in txt or 'right' in txt): c = 5      # serif for the dramatic / open questions
        elif any(w[0].lower().strip('.,') in ('number', 'five', 'four', 'three', 'two', 'one') for w in ph) and n <= 3: c = 7
        elif n == 1 or (n == 2 and has_key): c = 1
        elif has_key and n <= 3: c = 4
        elif n >= 5: c = [2, 6, 3, 4][i % 4]
        else: c = [0, 3, 6, 4, 2][i % 5]
        if c == prev: c = (c + 3) % 8
        prev = c; res.append(c)
    return res
def draw(f, t, words, y, accent, keys):
    key = id(words)
    if key not in _ASSIGN: phs = phrases(words); _ASSIGN[key] = (phs, assign(phs, keys))
    phs, sty = _ASSIGN[key]
    for ph, c in zip(phs, sty):
        if ph[0][1] - .05 <= t < ph[-1][2] + .28: STYLES[c](f, t, ph, y, accent, keys); return

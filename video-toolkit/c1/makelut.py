import numpy as np
N = 33; g = np.linspace(0, 1, N, dtype=np.float64)
B, G, Rr = np.meshgrid(g, g, g, indexing='ij'); r = Rr.ravel().copy(); gg = G.ravel().copy(); b = B.ravel().copy()   # b slowest, r fastest (.cube order)
def rgb2hsv(r, g, b):
    mx = np.maximum(np.maximum(r, g), b); mn = np.minimum(np.minimum(r, g), b); d = mx - mn + 1e-9
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    return h % 360, np.where(mx > 1e-6, (mx - mn) / (mx + 1e-9), 0), mx
def hsv2rgb(h, s, v):
    c = v * s; x = c * (1 - np.abs((h / 60) % 2 - 1)); m = v - c; h6 = (h // 60).astype(int) % 6
    R = np.choose(h6, [c, x, 0 * c, 0 * c, x, c]); Gc = np.choose(h6, [x, c, c, x, 0 * c, 0 * c]); Bc = np.choose(h6, [0 * c, 0 * c, x, c, c, x])
    return R + m, Gc + m, Bc + m
def win(x, a, b, f=20): return np.clip((x - (a - f)) / f, 0, 1) * np.clip(((b + f) - x) / f, 0, 1)
h, s, v = rgb2hsv(r, gg, b)
blue = win(h, 195, 255) * np.clip(s * 2, 0, 1)                 # tame the neon-blue shirt / cyan glare
red = win(h, 340, 360, 15) + win(h, 0, 12, 12)                 # deepen reds (curtain)
skin = win(h, 8, 42, 12) * np.clip((s - .12) / .2, 0, 1) * np.clip((.95 - s) / .25, 0, 1)
s = s * (1 - .30 * blue) * (1 + .06 * skin) * (1 - .06 * red); v = v * (1 - .12 * blue * s) * (1 - .05 * red)
h = h + 6 * blue * (h < 220) - 5 * blue * (h >= 220)           # nudge blues slightly toward teal/indigo for depth
r, gg, b = hsv2rgb(h % 360, np.clip(s, 0, 1), np.clip(v, 0, 1))
# filmic curve: toe + shoulder S-curve, gentle midtone lift
def curve(x):
    sg = 1 / (1 + np.exp(-(x - .5) * 5.4)); lo, hi = 1 / (1 + np.exp(2.7)), 1 / (1 + np.exp(-2.7)); sn = (sg - lo) / (hi - lo)
    y = x * .42 + sn * .58; y = .028 + y * .955; return np.clip(y, 0, 1) ** .955
r, gg, b = curve(r), curve(gg), curve(b)
luma = .2126 * r + .7152 * gg + .0722 * b; ws = (1 - luma) ** 2.3; wh = luma ** 2.1; keep = 1 - .75 * skin
r = r + wh * .038 - ws * .022 * keep; gg = gg + wh * .013 + ws * .006 * keep; b = b - wh * .040 + ws * .040 * keep   # teal shadows / warm highlights
l2 = .2126 * r + .7152 * gg + .0722 * b; sat = .96
r, gg, b = [np.clip(l2 + (c - l2) * sat, 0, 1) for c in (r, gg, b)]
with open('cinematic.cube', 'w') as f:
    f.write('TITLE "Cinematic teal-orange"\nLUT_3D_SIZE 33\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n')
    for a_, b_, c_ in zip(r, gg, b): f.write(f'{a_:.6f} {b_:.6f} {c_:.6f}\n')
print('wrote cinematic.cube', len(r))

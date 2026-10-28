import sys; sys.path.insert(0, '/tmp/vt/c5')
from inspo import *
def run(S, k, shots, overlays, hide_caps=()):
    t = k / FPS; s = next((x for x in shots if x['t0'] <= t < x['t1']), shots[-1]); d = t - s['t0']
    if s['kind'] == 'sp':
        u = clamp(d / (s['t1'] - s['t0'])); z0_, z1_ = s.get('z', (1.2, 1.24)); z = lerp(max(z0_, 1.2), max(z1_, 1.2), eio(u)); f = speaker(S, k, z, 540, 1920)
        gg = np.clip((np.arange(H, dtype=np.float32) - 1650) / 270, 0, 1)[:, None, None] * .35; f = (f.astype(np.float32) * (1 - gg)).astype(np.uint8)
        overlays(f, t, k); caps(f, t, S['words'], 1010, 44, hide_caps)
    else:
        f = s['fn'](t, s['t0'], s['t1'])
    if s.get('whip', True): f = whip_v(f, d, .3)
    return finish(f, k)

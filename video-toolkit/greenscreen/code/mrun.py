"""Shared runner: builds module-level _chunk/NF/DUR/EVENTS for a video from a segment list."""
from mscenes import *

KINDS = {'archive': sc_archive, 'paper': sc_paper, 'funnel': sc_funnel, 'persona': sc_persona, 'dash': sc_dash, 'stat': sc_stat, 'timeline': sc_timeline,
         'wave': sc_wave3, 'dm': sc_dm, 'pan': sc_pan, 'shift': sc_shift, 'clients': sc_clients, 'consist': sc_consist}
def build(vid, segs, extra=(), fix=None):
    S3.setup(vid, WHITE, extra=list(extra)); S = S3.STATE; VDUR, DUR, NF = S['VDUR'], S['DUR'], S['NF']
    S['words'] = [(('lead' if t.lower() == 'lean' else ('add' if (t.lower() == 'act' and a > 30) else t)), a, b) for t, a, b in S['words'] if t.lower() != 'or']
    if fix: S['words'] = [fix(w) for w in S['words']]
    def scene(sg, u, dur, k):
        kind = sg['kind']; p = dict(sg.get('p', {}))
        if kind == 'head': f = sc_head(u, dur, k, S, **p)
        elif kind.startswith('gd'):
            import gdscenes as GS; sp = sg.get('sp', 1.0); f = getattr(GS, 'sc_' + kind)(u * sp, dur * sp, k, S, **p)
        else:
            sp = sg.get('sp', 1.0); f = KINDS[kind](u * sp, dur * sp, k, **p)
            if kind not in ('archive', 'pan'): f = zoomfill(f, sg.get('zf', 1.09))
        return f
    ed = Edit(segs, scene)
    def frame(k):
        t = k / FPS; f = ed.frame(k)
        bottom_scrim(f, 1500, .35); captions(f, t, S['words'], 1650, 56)
        a = clamp(t / .5) * clamp((VDUR + .6 - t) / .8) if False else 1.0
        return cv2.addWeighted(f, .8, cv2.multiply(f, doc.vig(), scale=1 / 255), .2, 0)
    return S, frame, VDUR, DUR, NF
def events_from(segs, extra=()):
    ev = []
    for i, sg in enumerate(segs):
        t0 = sg['t0']; tr = sg.get('tr', 'cut'); kind = sg['kind']
        if i > 0 and tr == 'tear': ev.append((t0 + .05, 'paper', .9))
        if i > 0 and tr == 'burn': ev.append((t0, 'burn', .8)); ev.append((t0 + .22, 'shutter', .6))
        if i > 0 and tr == 'expand': ev.append((t0 + .02, 'whoosh', .6)); ev.append((t0 + .38, 'shutter', .55))
        if i > 0 and tr == 'slide': ev.append((t0 + .02, 'whoosh', .7))
        if i > 0 and tr == 'dip': ev.append((t0, 'swell', .5))
        n0 = len(ev)
        if kind in ('archive', 'pan'): ev.append((t0 + .1, 'shutter', .7)); ev.append((t0 + .1, 'hum', 1.0))
        if kind == 'paper':
            ev.append((t0 + .15, 'paper', .7))
            for j, ln in enumerate(sg['p'].get('lines', ())):
                for c_ in range(0, len(ln), 3): ev.append((t0 + .9 + j * .75 + c_ / 24, 'type', .35))
            if sg['p'].get('stamp'): ev.append((t0 + 2.2, 'thud', .9))
        if kind == 'funnel':
            for j in range(len(sg['p']['stages'])): ev.append((t0 + .35 + j * .32, 'tick', .5))
        if kind == 'persona':
            ev.append((t0 + .5, 'paper', .5)); ev.append((t0 + 1.5, 'tick', .5)); ev.append((t0 + 2.0, 'tick', .5)); ev.append((t0 + 2.5, 'tick', .6))
        if kind == 'dash':
            for j in range(10): ev.append((t0 + .55 + j * .2, 'tick', .3))
            ev.append((t0 + 2.5, 'thud', .6))
        if kind == 'stat':
            for j in range(12): ev.append((t0 + .25 + j * .2, 'tick', .35))
            ev.append((t0 + 2.6, 'thud', .85))
        if kind == 'timeline':
            for t_ in (2.65, 2.95, 3.25, 3.55): ev.append((t0 + t_, 'cut', .6))
            ev.append((t0 + 3.5, 'thud', .5))
        if kind == 'wave': ev.append((t0 + 1.8, 'riser', .5)); ev.append((t0 + 4.0, 'thud', .5))
        if kind == 'dm':
            for j in range(4): ev.append((t0 + .8 + j * .25, 'type', .5))
            ev.append((t0 + 2.0, 'pop', .6)); ev.append((t0 + 2.9, 'pop', .6)); ev.append((t0 + 3.3, 'tick', .5))
        if kind == 'clients': ev.append((t0 + .35, 'paper', .6)); ev.append((t0 + 2.6, 'thud', .6)); ev.append((t0 + 3.0, 'pop', .6))
        if kind == 'shift':
            for j in range(0, int(sg['t1'] - sg['t0'] - 1) * 5): ev.append((t0 + .9 + j * .2, 'tick', .22))
        if kind == 'consist':
            for j in range(0, 28, 2): ev.append((t0 + .5 + j * .07, 'tick', .25))
        if kind == 'head' and sg['p'].get('behind'): ev.append((t0 + .2, 'thud', .6))
        sp = sg.get('sp', 1.0)
        if sp != 1.0: ev[n0:] = [(t0 + (t_ - t0) / sp, k_, g_) for t_, k_, g_ in ev[n0:]]
    return sorted(ev + list(extra))

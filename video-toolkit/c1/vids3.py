import json, sys
from cc3 import *
import doodle as D

L = (172, 545); Rr = (908, 545); TOP = (540, 312)
def setup(N):
    d = json.load(open(f'{R}/work/cap{N}.json')); words = d['words']; dur = d['dur']
    norm = [(w.lower().strip('.,!?;:"“”'), a) for w, a, b in words]
    def at(tok, occ=1, off=0.0):
        hits = [a for w, a in norm if w == tok]
        return (hits[occ - 1] if occ > 0 else hits[occ]) + off
    chunks = build_chunks(words); plan = zoom_plan(dur, chunks)
    def ov(t0, length, fn, pos=TOP, scale=.95, rot=0.0, snd=None, first='pop'):
        o = Ov(t0, min(t0 + length, dur + .4), fn, pos, scale, rot); o.snd = [(t0 + .06, first, 1.0)] + (snd or []); return o
    def icon(tok, occ, off, length, fn, side, rot=0.0): return ov(at(tok, occ, off), length, fn, L if side == 'L' else Rr, 1.0, rot if rot else (-6 if side == 'L' else 6))
    faces = lambda t0, length=3.4, **k: ov(t0, length, lambda t: D.D_faces(t, **k), (540, 300), .95, -1, snd=[(t0 + 1.35, 'ding', 1.0)])
    def cta(word, tok_off, tt, cps=.13):
        t0 = at('comment', -1, tok_off); ts = t0 + tt + len(word) * cps + .35
        return ov(t0, 9.0, lambda t: D.D_cta(t, word, tt, cps), TOP, .95, 1, snd=[(ts + .02, 'ding', 1.2)], first='whoosh')
    if N == 1: o = [
        icon('business', 1, -.1, 1.6, D.I_store, 'L'), icon('convert', 1, -.6, 1.6, D.I_play, 'R'), icon('thing', 1, -.2, 1.7, D.I_bulb, 'L'), icon('blow', 1, -.25, 1.7, D.I_rocket, 'R'),
        faces(at('8k', 1, -.15)), icon('burning', 1, -.2, 1.6, D.I_fire, 'L'),
        ov(at('plan', 1, -.25), 3.0, D.D_calendar, rot=-2), ov(at('dispose', 1, -.1), 2.3, D.D_random, rot=2), ov(at('top', 1, -.15), 5.6, D.D_funnel, rot=-2),
        icon('free', 1, -.2, 1.7, D.I_gift, 'L'), cta('guide', -.25, .4)]
    elif N == 2: o = [
        icon('fail', 1, -.3, 1.8, D.I_mic, 'L'), ov(at('time', 1, -.25), 2.3, D.D_clock, rot=-2), icon('successful', 1, -.2, 1.7, D.I_trophy, 'R'),
        ov(at('dedicated', 1, -.8), 3.3, D.D_team, rot=2), icon('wrong', 1, -.3, 1.6, D.I_warn, 'L'),
        faces(at('8k', 1, -.15), 2.7), icon('leads', 1, -.2, 1.6, D.I_chat, 'L'), ov(at('107', 1, -.3), 2.7, D.D_leads, rot=2),
        icon('system', 1, -.2, 1.8, D.I_gear, 'R'), ov(at('team', 1, -.35), 5.4, lambda t: D.D_loop(t, 2.2), rot=-2), icon('iteration', 1, -.3, 1.7, D.I_bulb, 'R'),
        ov(at('spot', 1, -.6), 3.1, lambda t: D.D_check(t, ('spot mistakes', 'sort them out', 'improve weekly'), (.8, 1.5, 2.1), 'the free guide'), rot=1),
        icon('free', 1, -.2, 1.6, D.I_gift, 'R'), cta('guide', -.25, 1.0 - .25 + .25 * 0)]
    else: o = [
        icon('trick', 1, -.1, 1.7, D.I_bulb, 'L'), ov(at('never', 1, -.3), 3.5, D.D_flat, rot=-2), icon('mistake', 1, -.4, 1.6, D.I_warn, 'R'),
        faces(at('8k', 1, -.15), 2.9, ca='300 views', cb='viral'), ov(at('107', 1, -.3), 2.4, D.D_leads, rot=2),
        icon('research', 1, -.3, 1.7, D.I_mag, 'L'), ov(at('outlier', 1, -.7), 3.6, D.D_bars, rot=2),
        icon('copying', 1, -.3, 1.7, D.I_copy, 'R'), ov(at('lighting', 1, -1.3), 3.4, lambda t: D.D_check(t, ('lighting', 'scripts', 'everything'), (1.3, 1.8, 2.7)), rot=-1),
        ov(at('spin', 1, -.35), 3.3, D.D_spin, rot=2), icon('story', 1, -.2, 1.6, D.I_book, 'L'), icon('free', 1, -.2, 1.7, D.I_gift, 'R'), cta('calendar', -.15, .5, .1)]
    return plan, chunks, o

def sfx_events(N):
    plan, ch, o = setup(N); ev = []
    for x in o: ev += x.snd
    return ev

if __name__ == '__main__':
    N = int(sys.argv[1]); cmd = sys.argv[2]
    if cmd == 'pv': preview(N, 'vids3', [float(x) for x in sys.argv[4:]], sys.argv[3], 6)
    elif cmd == 'render': render(N, 'vids3', sys.argv[3])
    elif cmd == 'plan':
        plan, ch, o = setup(N); print('zoom cuts', [round(p[0], 1) for p in plan]); print('overlays', [(round(x.t0, 1), round(x.t1, 1)) for x in o]); print('sfx', len(sfx_events(N)))

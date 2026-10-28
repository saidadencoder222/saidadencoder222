import sys; sys.path.insert(0, '/tmp/vt/c5')
from runner import *
S3.setup(13, YEL); S = S3.STATE; S['words'] = [(t, a, b) for t, a, b in S['words'] if t.lower() != 'or']
VDUR, DUR, NF = S['VDUR'], S['DUR'], S['NF']; A = Wd
T1, T2, T3 = A('first') - .1, A('number', 1) - .05, A('number', 2) - .05
cA, cB = A('clients') - .3, A('clients') + 2.6
shots = [dict(kind='sp', t0=0, t1=cA, z=(1.0, 1.12), whip=False), dict(kind='dark', t0=cA, t1=cB, fn=lambda t, a, b: dark_scene(t, a, b, [('high-value client', 'can afford your offer', ['has an audience', 'could sell your product'], 3), ('your podcast', 'needs buyers, not just listeners', ['sponsors', 'products'], 0), ('the match', 'client + podcast = revenue', ['high value  x  reach'], 4)], 'ILLUSTRATION')),
         dict(kind='sp', t0=cB, t1=A('exact') - .2, z=(1.12, 1.25), cx=540, cy=640), dict(kind='sp', t0=A('exact') - .2, t1=A('number', 2) - .2, z=(1.0, 1.14)), dict(kind='sp', t0=A('number', 2) - .2, t1=VDUR + 1, z=(1.1, 1.0))]
ITEMS = [('dollar', 'Find high value clients'), ('scissors', 'Edit on point'), ('funnel', 'Post consistently + funnel')]
def overlays(f, t, k):
    title(f, t, .05, 3.5, 'NO MONEY FROM', 'YOUR PODCAST?', YEL, 1040)
    rows(f, t, ITEMS, [T1, T2, T3], 1.0 if t < cA else 1.0, VDUR + 1, 1150)
    keyword(f, t, A('exact') - .1, A('exact') + 1.7, 'EXACT EDITING GUIDELINE', 925); file_chip(f, t, A('guideline') + .3, A('comment') - .1, 'editing-guideline', 'by you', 1330) if False else None
    file_chip(f, t, A('guideline') - .1, A('comment') + 3.0, 'editing-guideline', 'by you', 1650)
    input_bar(f, t, A('comment') - .15, A('comment') + 3.0, 'EDIT', 1540)
    if t > A('lock') - .1: stroke_text(f, 'LOCK IN', 'poppins', 90, 540, 925, YEL, eo((t - A('lock') + .1) / .25), 1 + .15 * (1 - eo((t - A('lock')) / .3)), 7)
def frame(k): return run(S, k, shots, overlays, [(0.05, 3.5)])
_chunk = chunk_writer(frame); preview = make_preview(frame)
EVENTS = [(.05, 'thud', .3)] + [(x, 'tick', .8) for x in (T1, T2, T3)] + [(cA, 'swish', .35), (cB, 'swish', .35), (A('exact') - .1, 'pop', .6), (A('guideline') - .1, 'pop', .6), (A('comment') + 1.2, 'knock', .5), (A('lock') - .1, 'thud', .4)]
SILENCE = []
class story: SH = [dict(t0=cA, tr='whip'), dict(t0=cB, tr='whip')]

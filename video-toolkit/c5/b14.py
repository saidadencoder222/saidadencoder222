import sys; sys.path.insert(0, '/tmp/vt/c5')
from runner import *
S3.setup(14, YEL); S = S3.STATE; VDUR, DUR, NF = S['VDUR'], S['DUR'], S['NF']; A = Wd
T1, T2, T3 = A('number', 1) - .05, A('number', 2) - .05, A('number', 3) - .05
dA, dB = A('identify') - .3, A('identify') + 3.0
shots = [dict(kind='sp', t0=0, t1=dA, z=(1.2, 1.24), whip=False), dict(kind='dark', t0=dA, t1=dB, fn=lambda t, a, b: dark_scene(t, a, b, [('ICP', 'ideal client persona', ['who exactly are you talking to?'], 0), ('target avatar', 'one specific person', ['their problem', 'their budget'], 3), ('the match', 'your offer + their pain', ['makes content convert'], 4)], 'ILLUSTRATION')),
         dict(kind='sp', t0=dB, t1=VDUR + 1, z=(1.2, 1.24))]
ITEMS = [('target', 'Identify your ICP'), ('book', 'Tell your story'), ('magnet', 'Lead magnets')]
def overlays(f, t, k):
    title(f, t, .05, 3.8, 'THOUSANDS OF VIEWS', 'NO CASH?', YEL, 1040)
    rows(f, t, ITEMS, [T1, T2, T3], 4.4, VDUR + 1, 1150)
    keyword(f, t, A('leads') - .3, A('leads') + 2.0, '120 NEW LEADS IN 4 WEEKS', 925)
    file_chip(f, t, A('guideline') - .1, A('comment') - .1, 'lead-generation-guideline', 'by you', 1650)
    input_bar(f, t, A('comment') - .15, A('comment') + 3.2, 'LEAD', 1540)
    keyword(f, t, A('follow') - .1, A('follow') + 1.4, 'FOLLOW FOR MORE TIPS', 925)
def frame(k): return run(S, k, shots, overlays, [(0.05, 3.8)])
_chunk = chunk_writer(frame); preview = make_preview(frame)
EVENTS = [(.05, 'thud', .3)] + [(x, 'tick', .8) for x in (T1, T2, T3)] + [(dA, 'swish', .35), (dB, 'swish', .35), (A('leads') - .3, 'pop', .6), (A('guideline') - .1, 'pop', .6), (A('comment') + 1.3, 'knock', .5), (A('follow') - .1, 'pop', .6)]
SILENCE = []
class story: SH = [dict(t0=dA, tr='whip'), dict(t0=dB, tr='whip')]

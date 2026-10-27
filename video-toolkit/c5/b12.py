import sys; sys.path.insert(0, '/tmp/vt/c5')
from runner import *
S3.setup(12, YEL); S = S3.STATE
S['words'] = [(('lead' if t.lower() == 'lean' else ('add' if (t.lower() == 'act' and a > 30) else t)), a, b) for t, a, b in S['words']]
VDUR, DUR, NF = S['VDUR'], S['DUR'], S['NF']; A = Wd
T1, T2, T3 = A('number', 1) - .05, A('number', 2) - .05, A('finally') - .05
dA, dB = A('qualifying') + .6, A('afford') + 1.2
shots = [dict(kind='sp', t0=0, t1=dA, z=(1.2, 1.24), whip=False), dict(kind='dark', t0=dA, t1=dB, fn=lambda t, a, b: dark_scene(t, a, b, [('ICP', 'ideal client persona', ['who do you want to sell to?'], 0), ("can't afford it", 'no point selling high ticket here', ['wrong audience'], 4), ('can afford it', 'the persona you should target', ['qualified by your lead magnet'], 3)], 'ILLUSTRATION')),
         dict(kind='sp', t0=dB, t1=A('finally'), z=(1.2, 1.24)), dict(kind='dark', t0=A('subtitles') - .3, t1=A('subtitles') + 2.8, fn=lambda t, a, b: dark_scene(t, a, b, [('different languages', 'subtitles on every video', ['reach a new audience'], 2), ('first-world audience', 'slowly converts over time', ['higher-ticket buyers'], 3)], 'ILLUSTRATION')),
         dict(kind='sp', t0=A('subtitles') + 2.8, t1=VDUR + 1, z=(1.2, 1.24))]
shots.sort(key=lambda x: x['t0'])
# fix overlaps: shot before subtitles ends where the subtitle scene starts
for i in range(len(shots) - 1):
    if shots[i]['kind'] == 'sp' and shots[i]['t1'] > shots[i + 1]['t0']: shots[i]['t1'] = shots[i + 1]['t0']
ITEMS = [('book', 'Tell your story'), ('magnet', 'Lead magnets + ICP'), ('globe', 'Convert your audience')]
def overlays(f, t, k):
    title(f, t, .05, 3.8, 'HIGH TICKET FOR', 'FITNESS CREATORS', YEL, 1040)
    rows(f, t, ITEMS, [T1, T2, T3], 4.2, VDUR + 1, 1150)
    keyword(f, t, A('ideal') - .1, A('ideal') + 1.6, 'IDEAL CLIENT PERSONA', 925) if dA > A('ideal') else None
def frame(k): return run(S, k, shots, overlays, [(0.05, 3.8)])
_chunk = chunk_writer(frame); preview = make_preview(frame)
EVENTS = [(.05, 'thud', .3)] + [(x, 'tick', .8) for x in (T1, T2, T3)] + [(dA, 'swish', .35), (dB, 'swish', .35), (A('subtitles') - .3, 'swish', .35), (A('subtitles') + 2.8, 'swish', .35), (A('ideal') - .1, 'pop', .6)]
SILENCE = []
class story: SH = [dict(t0=dA, tr='whip'), dict(t0=dB, tr='whip')]

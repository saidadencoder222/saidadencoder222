import json, sys
from cc import *
import anims as A

EMPH = {
    1: {'8K', '40K', '4', 'BLOW', 'BURNING', 'PLAN', 'ROUTINE', 'FUNNEL', 'RANDOMIZED', '6', '40', 'FREE', 'GUIDE', 'COMMENT', 'LEGIT'},
    2: {'FAIL', 'TIME', 'DEDICATED', '8K', '40K', '107', 'LEADS', 'SYSTEM', 'TEAM', 'ANALYSE', 'IMPROVEMENT', 'WEEK', 'ITERATION', 'FREE', 'GUIDE', 'COMMENT', '500', 'WRONG'},
    3: {'TRICK', 'NEVER', '300', '8K', '40K', '107', 'FIVE', 'OUTLIER', 'COPY', 'LIGHTING', 'SCRIPTS', 'EVERYTHING', 'SPIN', 'STORY', 'FREE', 'GUIDE', 'CALENDAR', 'COMMENT'},
}
def S(t0, kind, anim=None, title=None, z=(1.0, 1.06), cy=820): return Sc(t0, kind, anim, title, None, z, cy)
FA = (1.0, 1.06); FB = (1.13, 1.19); FC = (1.07, 1.13)

# speaker ('full') time per video: v1 21.0s, v2 20.6s, v3 21.4s; no text hook
def scenes_for(N):
    if N == 1: return [
        S(0.0, 'full', z=FA), S(3.4, 'full', z=FB), S(5.0, 'full', z=FA), S(7.0, 'full', z=FC),
        S(8.9, 'anim', A.A_growth(t0=.3, dur=2.2), ('The result', '8K to 40K')),
        S(12.0, 'full', z=FB),
        S(15.6, 'anim', A.A_calendar(t0=.4, step=.08), ('Step 1', 'Build a routine')),
        S(18.9, 'full', z=FA),
        S(21.2, 'anim', A.A_chaos(tx=.9), ('Step 2', 'No random posting')),
        S(23.3, 'anim', A.A_funnel(times=(.5, 1.8, 3.0)), ('Step 2', 'The funnel system')),
        S(27.6, 'full', z=FC), S(30.2, 'full', z=FB), S(32.0, 'full', z=FA),
        S(33.8, 'anim', A.A_cta('GUIDE', tt=.2), ('Free guide', 'Comment below'))]
    if N == 2: return [
        S(0.0, 'full', z=FA), S(2.4, 'full', z=FB),
        S(4.8, 'anim', A.A_team(), ('Successful businesses', 'have someone dedicated')),
        S(8.2, 'full', z=FA),
        S(10.0, 'anim', A.A_growth(t0=.2, dur=1.0), ('The result', '8K to 40K')),
        S(12.2, 'anim', A.A_leads(t0=.9, dur=1.3), ('The result', '107 new leads')),
        S(14.8, 'full', z=FB), S(17.0, 'full', z=FA), S(19.9, 'full', z=FC),
        S(22.2, 'anim', A.A_loop(2.0), ('The system', 'Analyze. Improve. Repeat.')),
        S(26.0, 'full', z=FB), S(28.4, 'full', z=FA),
        S(30.2, 'anim', A.A_check(('Spot the mistakes', 'Sort them out', 'Improve weekly'), (1.7, 2.3, 2.7), 'the free guide'), ('The free guide', 'Spot. Sort. Improve.')),
        S(32.8, 'full', z=FC),
        S(35.2, 'anim', A.A_cta('GUIDE', tt=1.0), ('Under 500 followers?', 'This is for you'))]
    if N == 3: return [
        S(0.0, 'full', z=FA),
        S(2.6, 'anim', A.A_stuck(1.6), ('The ceiling', '300 views')),
        S(5.0, 'full', z=FB),
        S(7.0, 'anim', A.A_growth(t0=.3, dur=1.5), ('The result', '8K to 40K')),
        S(9.3, 'full', z=FA), S(11.9, 'full', z=FC),
        S(14.0, 'anim', A.A_outliers(1.2), ('Step 1', 'Find 5 outlier videos')),
        S(17.2, 'full', z=FB), S(19.4, 'full', z=FA),
        S(21.8, 'anim', A.A_check(('Lighting', 'Scripts', 'Everything'), (.8, 1.3, 2.4), 'copy what works'), ('Then copy', 'what already works')),
        S(24.6, 'full', z=FC),
        S(27.0, 'anim', A.A_spin(), ('Step 2', 'Make it your own')),
        S(29.4, 'full', z=FB), S(31.9, 'full', z=FA),
        S(34.5, 'anim', A.A_cta('CALENDAR', tt=.9, cps=.1), ('Free guide', 'The content calendar'))]

def setup(N):
    d = json.load(open(f'{R}/work/cap{N}.json')); sc = build(scenes_for(N), d['dur']); G = build_groups(d['words'], EMPH[N]); return sc, G

if __name__ == '__main__':
    N = int(sys.argv[1]); cmd = sys.argv[2]
    if cmd == 'pv': preview(N, 'vids', [float(x) for x in sys.argv[4:]], sys.argv[3], 6)
    elif cmd == 'render': render(N, 'vids', sys.argv[3])
    elif cmd == 'stats':
        sc, G = setup(N); tot = sc[-1].t1 - .5
        sp = sum(s.t1 - s.t0 for s in sc if s.kind == 'full'); print(f'v{N}: total {tot:.1f}s, speaker {sp:.1f}s, anim {tot - sp:.1f}s')

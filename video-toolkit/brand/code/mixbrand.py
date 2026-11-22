import sys; sys.path.insert(0,'.')
import importlib, brand_av
name, voice, out = sys.argv[1:4]; m = importlib.import_module(name)
cues = []
cues.append(('trailer_riser', .02, -17, 2.6)); cues.append(('zoom_impact', 0.33, -12, None))           # title hits
for k, s in enumerate(m.STACKS): cues.append(('soft_punch', s[0] + .08, -12, None)); cues.append(('sparkle_sweep' if k % 2 == 0 else 'wind_sweep', s[0] - .05, -20, 1.4))
if hasattr(m, 'HABIT_T'):
    for t in m.HABIT_T: cues.append(('bubble_pop', t + .02, -16, None))
cues.append(('bass_hit', m.STACKS[-1][0] + .05, -14, None))
for ci, g in enumerate(m.GS): cues.append(('light_pop', g[0][1] + .02, -27, .12))
cues.sort(key=lambda c: c[1])
print(brand_av.mix(voice, cues, m.DUR, f'work/mixb_{name}.wav', music_db=-29, music_path='work/music_loop40.wav'), len(cues), 'cues')

import sys; sys.path.insert(0,'.')
import brand_av, m100 as m
cues=[]
for a_, b_, *_ in m.ACCENTS: cues.append(('tiny_click', m.T0(a_)+.01, -21, None)); cues.append(('soft_punch', m.T0(a_)+.04, -15, None))
for a_, b_, kind in m.GFX: cues.append(('light_pop', m.T0(a_)+.05, -23, .14))
for g in m.GS:
    if g[0][1] > 1.0: cues.append(('light_pop', g[0][1]+.02, -27, .12))
cues.sort(key=lambda c:c[1])
print(brand_av.mix('work/voice100.wav', cues, m.DUR, 'work/mixb_m100.wav', music_db=-29, music_path='../c13/work/music90.wav'), len(cues))

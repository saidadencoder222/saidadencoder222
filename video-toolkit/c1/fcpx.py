import os, sys, json, subprocess
from cc import R
import vids
OUT = f'{R}/out/capcut'
def fr(t): return f'{int(round(t * 30))}/30s'
def dur_of(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)
for N in (1, 2, 3):
    D = f'{OUT}/video{N}'; scenes, G = vids.setup(N); total = json.load(open(f'{R}/work/cap{N}.json'))['dur']
    spk = '00_speaker_cut_graded.mp4'; sd = dur_of(f'{D}/{spk}')
    anims = [(k, s) for k, s in enumerate(scenes) if s.kind == 'anim']
    res = [f'<format id="r1" name="FFVideoFormat1080x1920p30" frameDuration="1/30s" width="1080" height="1920" colorSpace="1-1-1 (Rec. 709)"/>',
           f'<asset id="a0" name="speaker" src="{spk}" start="0s" duration="{fr(sd)}" hasVideo="1" format="r1" hasAudio="1" audioSources="1" audioChannels="2" audioRate="48000"/>']
    kids = []
    for i, (k, s) in enumerate(anims, 1):
        fn = f'anim_{k:02d}_{int(s.t0 * 10):03d}s.mp4'; d = min(s.t1, total) - s.t0
        res.append(f'<asset id="a{i}" name="{fn}" src="{fn}" start="0s" duration="{fr(d)}" hasVideo="1" format="r1"/>')
        kids.append(f'<asset-clip ref="a{i}" lane="1" offset="{fr(s.t0)}" name="{s.title[1]}" start="0s" duration="{fr(d)}" format="r1"/>')
    x = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fcpxml>
<fcpxml version="1.9">
  <resources>
    {chr(10).join('    ' + r for r in res).strip()}
  </resources>
  <library>
    <event name="reel{N}">
      <project name="reel{N}_timeline">
        <sequence format="r1" duration="{fr(sd)}" tcStart="0s" tcFormat="NDF" audioLayout="stereo" audioRate="48k">
          <spine>
            <asset-clip ref="a0" offset="0s" name="speaker + voice" start="0s" duration="{fr(sd)}" format="r1" tcFormat="NDF" audioRole="dialogue">
              {chr(10).join('              ' + k for k in kids).strip()}
            </asset-clip>
          </spine>
        </sequence>
      </project>
    </event>
  </library>
</fcpxml>
'''
    open(f'{D}/reel{N}_resolve.fcpxml', 'w').write(x); print(N, len(kids), 'overlays', round(sd, 1), 's')

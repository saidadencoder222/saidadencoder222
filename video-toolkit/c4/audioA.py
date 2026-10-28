import sys; sys.path.insert(0,'.')
import numpy as np, json, subprocess
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
from scipy.ndimage import maximum_filter1d, uniform_filter1d
import alex
SR=48000; VD=alex.VDUR; DUR=VD+.9; N=int(DUR*SR); t=np.arange(N)/SR; rs=np.random.RandomState(12)
subprocess.run(['ffmpeg','-v','error','-y','-i','work/clipA.mkv','-vn','-ac','1','-ar',str(SR),'-af','highpass=f=85,afftdn=nr=10:nf=-40,acompressor=threshold=-24dB:ratio=2.5:attack=8:release=140,loudnorm=I=-15:TP=-2:LRA=7','work/voiceA.wav'],check=True)
sr,v=wavfile.read('work/voiceA.wav'); v=v.astype(np.float32)/32768; voice=np.zeros(N,np.float32); voice[:min(N,len(v))]=v[:N]
src=open('audio5.py').read(); a=src.index('def bp'); b=src.index('mus=np.zeros(N)'); exec(src[a:b])
mus=np.zeros(N)
# A-minor bed: slow pads with building plucked arpeggio
chords=[(45,52,57,60),(41,48,53,57),(36,43,48,52),(43,50,55,59)]; at=0.0; ci=0
while at<DUR:
    dur=3.6; ch=chords[ci%4]
    for m in ch: put(mus,organ(midi(m),dur,att=1.2,rel=1.4),at,.55 if m<48 else .35)
    ar=60/100/2; lvl=min(1.0,.25+at/DUR)
    for k in range(int(dur/ar)): put(mus,pluck(midi(ch[k%4]+24),.55),at+k*ar,.22*lvl)
    at+=dur; ci+=1
mus=lp(mus,3800)
fade=np.minimum(np.minimum(t/1.0,(DUR-t)/1.1),1)**2; cur=np.ones(N)
def ramp(a,b,v0,v1): i,j=int(a*SR),int(b*SR); cur[i:j]=np.linspace(v0,v1,j-i)
GA=alex.GA; GB=alex.GB; ramp(GA-.3,GA+.1,1,.5); ramp(GB-.1,GB+.5,.5,1)
mus=mus*cur*fade
env=uniform_filter1d(maximum_filter1d(np.abs(voice),int(.12*SR)),int(.15*SR)); env=np.clip(env*5,0,1); mus*=1-.66*env
sfx=np.zeros(N); T=alex.T
put(sfx,thud(),.12,.40); put(sfx,crackle(.9),.2,.12); put(sfx,tink(),.8,.3)
put(sfx,thud(),4.2,.30); put(sfx,crackle(.8),4.25,.12); put(sfx,whoosh(),3.5,.10)
a0=T('introduce')-.1; put(sfx,whoosh(),a0-.1,.10); put(sfx,tink(),T('alex'),.35)
put(sfx,whoosh(),GA-.1,.12); put(sfx,riser(.4),GA-.4,.08)
for i in range(5): put(sfx,tink(),GA+.4+.42*i,.30); put(sfx,tick(),GA+.4+.42*i,.5)
put(sfx,whoosh(),GB-.1,.10); put(sfx,tink(),alex.T('copy')-.1,.3)
s0=T('storytelling')-.2
for i in range(4): put(sfx,tink(),s0+.1+i*.28,.26); put(sfx,tick(),s0+.1+i*.28,.4)
put(sfx,whoosh(),T('lead')-.15,.10); put(sfx,thud(),T('guide')-.15,.40); put(sfx,crackle(.8),T('guide')-.1,.12); put(sfx,tink(),T('dm')-.1,.35)
put(sfx,whoosh(),VD,.10); put(sfx,thud(),VD,.20)
mix=voice+mus*.32+sfx*.30; mix=np.tanh(mix*1.1)/1.1
wavfile.write('work/mixA_raw.wav',SR,(np.clip(mix,-1,1)*32767).astype(np.int16))
subprocess.run(['ffmpeg','-v','error','-y','-i','work/mixA_raw.wav','-af','loudnorm=I=-14:TP=-2:LRA=8,alimiter=limit=0.85','work/mixA.wav'],check=True)
def db(x): return 20*np.log10(np.sqrt(np.mean(x**2))+1e-9)
m=voice>.02; print('voice',db(voice[m]),'music during speech',db((mus*.32)[m]),'sfx peak',db(np.array([np.abs(sfx*.3).max()])))

import numpy as np, json, subprocess
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, lfilter
from scipy.ndimage import maximum_filter1d, uniform_filter1d
SR=48000; D=json.load(open('work/cut.json')); VD=D['dur']; DUR=VD+.9; N=int(DUR*SR); t=np.arange(N)/SR
sr,v=wavfile.read('work/voice.wav'); v=v.astype(np.float32)/32768; voice=np.zeros(N,np.float32); voice[:min(N,len(v))]=v[:N]
rs=np.random.RandomState(9)
def bp(x,a,b): return sosfilt(butter(2,[a/(SR/2),min(b,SR/2-200)/(SR/2)],'band',output='sos'),x)
def lp(x,f): return sosfilt(butter(2,f/(SR/2),'low',output='sos'),x)
def midi(m): return 440*2**((m-69)/12)
def put(buf,x,at,g=1.0):
    i=int(at*SR)
    if i>=N or i<0 and -i>=len(x): return
    if i<0: x=x[-i:]; i=0
    n=min(len(x),N-i); buf[i:i+n]+=x[:n]*g
def pluck(f,dur=.7):
    n=int(dur*SR); p=int(SR/f); b=rs.uniform(-1,1,p); out=np.zeros(n); 
    for i in range(n):
        out[i]=b[i%p]; b[i%p]=.5*(b[i%p]+b[(i+1)%p])*.996
    return out*np.exp(-np.arange(n)/SR*2.2)
def pad(f,dur,att=.9,rel=1.2,bright=1400):
    n=int((dur+rel)*SR); tt=np.arange(n)/SR; x=np.zeros(n)
    for d in(-.7,0,.7): x+=np.sign(np.sin(2*np.pi*(f+d)*tt+rs.rand()*6))*.5+np.sin(2*np.pi*(f+d)*tt)
    x=lp(x,bright); env=np.minimum(tt/att,1)*np.where(tt<dur,1,np.exp(-(tt-dur)/(rel/3.5))); return x*env*.4
def organ(f,dur,att=1.4,rel=1.8):
    n=int((dur+rel)*SR); tt=np.arange(n)/SR; x=sum(np.sin(2*np.pi*f*h*tt+rs.rand()*6)*a for h,a in((1,1),(2,.7),(3,.4),(4,.45),(6,.2),(8,.12)))
    env=np.minimum(tt/att,1)**1.5*np.where(tt<dur,1,np.exp(-(tt-dur)/(rel/3.5))); return x*env*.28
def tom(f0=95,g=1):
    n=int(.55*SR); tt=np.arange(n)/SR; return (np.sin(2*np.pi*np.cumsum(f0*.58+f0*.42*np.exp(-tt*22))/SR)*np.exp(-tt*7)+bp(rs.randn(n),1500,4000)*np.exp(-tt*90)*.15)*g
def sawbass(f,dur):
    n=int(dur*SR); tt=np.arange(n)/SR; x=lp(((tt*f)%1)*2-1,420); return x*np.minimum(tt/.01,1)*np.exp(-tt*5)
def tink(): n=int(.35*SR); tt=np.arange(n)/SR; return (np.sin(2*np.pi*1760*tt)+.35*np.sin(2*np.pi*2637*tt))*np.exp(-tt*16)*.5
def tick(): n=int(.012*SR); return bp(rs.randn(n),2400,5200)*np.exp(-np.arange(n)/SR*380)*1.0
def thud(): n=int(1.0*SR); tt=np.arange(n)/SR; return np.sin(2*np.pi*np.cumsum(50+60*np.exp(-tt*15))/SR)*np.exp(-tt*5)
def riser(d): n=int(d*SR); return bp(rs.randn(n),300,5500)*np.linspace(0,1,n)**2.2*.5
def whoosh(): n=int(.45*SR); return bp(rs.randn(n),400,3800)*np.sin(np.pi*np.linspace(0,1,n))**1.8*.5
def crackle(d): n=int(d*SR); x=rs.randn(n); x=np.where(rs.rand(n)>.992,x*3,0); return bp(x,1500,6000)*np.hanning(n)*.7
mus=np.zeros(N)
# base drone for hook/intro (0-7) and tails
for f0,g in((55,1.0),(82.4,.5),(110,.4)):
    for dt in(-.6,0,.6): mus+=g*np.sin(2*np.pi*(f0+dt)*t+rs.rand()*6)*(.6+.4*np.sin(2*np.pi*.08*t+rs.rand()*6))
mus=lp(mus,900)*.55; m_int=np.clip((t-6.4)/.6,0,1); mus*=(1-m_int*.0)
sec=np.zeros(N)
# PIRATES 7.0-15.5 : D minor modal, toms + plucks
per=60/112/1; prog=[(50,53,57),(46,50,53),(48,52,55),(50,53,57)]  # Dm Bb C Dm (midi roots)
tt0=7.0; bar=0
while tt0<15.45:
    ch=prog[bar%4]; 
    put(sec,pad(midi(ch[0]),per*6,att=.5),tt0,.55); put(sec,pad(midi(ch[0]+12),per*6,att=.5),tt0,.3)
    for k in range(6):
        put(sec,tom(95 if k%3==0 else 120,1.0 if k%3==0 else .45),tt0+k*per,.9)
        put(sec,pluck(midi(ch[(k)%3]+24),.5),tt0+k*per+per/2,.35)
    tt0+=per*6; bar+=1
# TDK 15.5-21.0 : B pedal pulse + rising tension
tt0=15.45; per16=60/140/4; k=0
while tt0<20.65:
    amp=.5+.5*np.sin(k*np.pi/16)**2; put(sec,sawbass(midi(35),per16*.9),tt0,.55*amp); 
    if k%8==0: put(sec,tom(70,1.0),tt0,.8)
    tt0+=per16; k+=1
n=int(5.2*SR); glide=np.sin(2*np.pi*np.cumsum(np.linspace(300,520,n))/SR)*np.linspace(.05,.5,n)**1.5; put(sec,glide,15.5,.35)
# INTERSTELLAR 21.58-end : organ swell + arpeggio
chords=[(45,52,57,60),(41,48,53,57),(36,43,48,52),(43,50,55,59)]; at=21.58; ci=0
while at<DUR+1:
    dur=3.4 if ci<3 else 4.2; ch=chords[ci%4]
    for m in ch: put(sec,organ(midi(m),dur),at,.9 if m<48 else .6)
    ar=60/96/2
    for k in range(int(dur/ar)): put(sec,pluck(midi(ch[k%4]+24),.6),at+k*ar,.30*min(1,(at-21.58+k*ar)/3+.2))
    at+=dur; ci+=1
sec=lp(sec,3800)
cur=np.ones(N)
def ramp(a,b,v0,v1): i,j=int(a*SR),int(b*SR); cur[i:j]=np.linspace(v0,v1,j-i)
ramp(20.55,21.05,1,0); cur[int(21.05*SR):int(21.5*SR)]=0; ramp(21.5,21.6,0,1.2)
# phase A dips before reveals
for a,b in((6.3,7.05),(14.7,15.55)): ramp(a,b,1,.35); 
mus_all=(mus*np.clip(1-(t>6.9)*1.0,0,1)+sec)  # drone only in intro; sections own music
# intro drone fade handoff
mus_all=mus*np.where(t<7.0,1,np.exp(-(t-7.0)*3))*np.where(t>3.4,1,1)+sec
fade=np.minimum(np.minimum(t/1.0,(DUR-t)/1.1),1)**2
mus_all=mus_all*cur*fade
env=uniform_filter1d(maximum_filter1d(np.abs(voice),int(.12*SR)),int(.15*SR)); env=np.clip(env*5,0,1); mus_all*=1-.66*env
sfx=np.zeros(N)
put(sfx,riser(.55),.3,.10); put(sfx,crackle(.9),.85,.12); put(sfx,crackle(.9),4.2,.12); put(sfx,whoosh(),3.45,.14); put(sfx,whoosh(),6.95,.12)
for r,th in((6.2,7.08),(14.7,15.62),(20.9,21.58)): 
    if r<20: put(sfx,riser(th-r),r,.12)
    put(sfx,thud(),th,.55 if th>21 else .42)
put(sfx,crackle(.8),21.6,.12)
for a in (9.0,16.5,23.45,18.55,26.42,27.2,28.9): put(sfx,whoosh(),a-.1,.10)
for tp in (12.53,13.31,14.03,16.81,17.67,19.87,24.52,26.4,27.18,28.0): put(sfx,tink(),tp,.30); put(sfx,tick(),tp,.5)
put(sfx,thud(),29.0,.25); put(sfx,whoosh(),VD,.10)
mix=voice+mus_all*float(__import__('os').environ.get('MG','.22'))+sfx*.30
mix=np.tanh(mix*1.1)/1.1
wavfile.write('work/mix_raw.wav',SR,(np.clip(mix,-1,1)*32767).astype(np.int16))
subprocess.run(['ffmpeg','-v','error','-y','-i','work/mix_raw.wav','-af','loudnorm=I=-14:TP=-2:LRA=8,alimiter=limit=0.85','work/mix.wav'],check=True)
def db(x): return 20*np.log10(np.sqrt(np.mean(x**2))+1e-9)
m=voice>.02; g=float(__import__('os').environ.get('MG','.22'))
print('voice',db(voice[m]),'music during speech',db((mus_all*g)[m]),'music rms whole',db(mus_all*g),'sfx peak',db(np.array([np.abs(sfx*.3).max()])))

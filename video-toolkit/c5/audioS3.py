import sys; sys.path.insert(0,'.')
import numpy as np, json, subprocess, importlib
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
from scipy.ndimage import maximum_filter1d, uniform_filter1d
vid=int(sys.argv[1]); mod=importlib.import_module(f'b{vid}')
SR=48000; VD=mod.VDUR; DUR=mod.DUR; N=int(DUR*SR); t=np.arange(N)/SR; rs=np.random.RandomState(30+vid)
subprocess.run(['ffmpeg','-v','error','-y','-i',f'work/clip{vid}.mkv','-vn','-ac','1','-ar',str(SR),'-af','highpass=f=90,afftdn=nr=14:nf=-48,agate=threshold=0.018:ratio=1.8:attack=5:release=160,acompressor=threshold=-24dB:ratio=2.4:attack=8:release=140,loudnorm=I=-15:TP=-2:LRA=7',f'work/voice{vid}.wav'],check=True)
sr,v=wavfile.read(f'work/voice{vid}.wav'); v=v.astype(np.float32)/32768; voice=np.zeros(N,np.float32); voice[:min(N,len(v))]=v[:N]
src=open('audio5.py').read() if False else open('../c4/audio5.py').read(); a=src.index('def bp'); b=src.index('mus=np.zeros(N)'); exec(src[a:b])
def put_(buf,x,at,g=1.0):
    i=int(at*SR)
    if i>=N: return
    n=min(len(x),N-i); buf[i:i+n]+=x[:n]*g
def brown(n): x=np.cumsum(rs.randn(n)); x-=uniform_filter1d(x,int(.5*SR)); return x/np.abs(x).max()
def swish(d=.5,lo=300,hi=3000):
    n=int(d*SR); x=rs.randn(n); u=np.linspace(0,1,n); a=bp(x,lo,lo*2.5)*(1-u)+bp(x,hi*.5,hi)*u; env=np.sin(np.pi*u**.8)**1.6; return a*env*.6
def boom(f0=48,d=2.6,body=1.0):
    n=int(d*SR); tt=np.arange(n)/SR; s=np.sin(2*np.pi*np.cumsum(f0*(1+1.2*np.exp(-tt*9)))/SR)*np.exp(-tt*2.2); nz=lp(rs.randn(n),260)*np.exp(-tt*6)*.9; return (s+nz*body)*np.minimum(tt/.004,1)
def rumble(d,f=70): n=int(d*SR); x=lp(brown(n),f); return x*np.linspace(0,1,n)**1.6
def rainbed(d): n=int(d*SR); x=bp(rs.randn(n),1800,9000)*.35+bp(rs.randn(n),400,1200)*.12; drops=(rs.rand(n)>.9985)*rs.randn(n); x+=bp(drops,2500,7000)*1.2; return x
def thunder(d=4.0): n=int(d*SR); tt=np.arange(n)/SR; x=lp(brown(n),160)*(np.exp(-tt*1.1)*(1+.6*np.sin(tt*5)**2)); x[:int(.05*SR)]*=np.linspace(0,1,int(.05*SR)); return x
def bell(f=196,d=5.0):
    n=int(d*SR); tt=np.arange(n)/SR; x=sum(np.sin(2*np.pi*f*r*tt+rs.rand()*6)*a*np.exp(-tt*dc) for r,a,dc in((1,1,.7),(2.01,.55,1.0),(2.76,.4,1.5),(4.07,.25,2.2),(5.4,.15,3.0))); return x*np.minimum(tt/.003,1)*.5
def heart(): 
    n=int(.35*SR); tt=np.arange(n)/SR; th=lambda f,g: np.sin(2*np.pi*f*tt)*np.exp(-tt*28)*g; x=th(58,1.0); x2=np.zeros(n); k=int(.17*SR); x2[k:]=th(52,.7)[:n-k]; return lp(x+x2,140)
def riser(d,g=1.0): n=int(d*SR); return bp(rs.randn(n),250,5200)*np.linspace(0,1,n)**2.4*.6*g
def rev_swell(d): n=int(d*SR); return lp(rs.randn(n),1500)*np.linspace(0,1,n)**3*.5

def tap():
    n=int(.05*SR); tt=np.arange(n)/SR; return (bp(rs.randn(n),1500,4500)*np.exp(-tt*140)+np.sin(2*np.pi*900*tt)*np.exp(-tt*90)*.4)*.9
def knock():
    n=int(.25*SR); tt=np.arange(n)/SR; return (np.sin(2*np.pi*150*tt)*np.exp(-tt*28)+lp(rs.randn(n),600)*np.exp(-tt*50)*.5)
def crackle2(d=.7):
    n=int(d*SR); x=rs.randn(n); x=np.where(rs.rand(n)>.993,x*3,0); return bp(x,1500,6000)*np.hanning(n)*.7
def pop_():
    n=int(.12*SR); tt=np.arange(n)/SR; return np.sin(2*np.pi*np.cumsum(300+500*np.exp(-tt*40))/SR)*np.exp(-tt*30)*.6
KIND={'pop':pop_,'tick':tap,'swish':lambda:swish(.4,320,2800),'thud':lambda:boom(52,1.6,.8),'tap':tap,'knock':knock,'crackle':crackle2,'riser':lambda:riser(.8,.6),'whoosh':lambda:swish(.5,400,3500)}
mus=np.zeros(N); sfx=np.zeros(N)
from score import Score, drive, midi as smidi
sc=Score(N,seed=40+vid)
CH={2:[(45,57,60,64),(41,53,57,60),(48,60,64,67),(43,55,59,62)],3:[(38,57,62,65),(46,58,62,65),(41,57,60,65),(36,55,60,64)]}.get(vid)
BPM={2:100,3:96}.get(vid)
from score import phonk, lofi
lv=lambda tt: min(1.0,.4+.7*tt/DUR)
if vid in (2,15):
    phonk(sc,0.0,DUR+.5,140 if vid==15 else 130,level=lv)
    for tp,m_ in ([(t_,30) for t_,k_,g_ in mod.EVENTS if k_=='thud'] if vid==15 else [(0.5,30),(4.62,30),(7.78,28),(12.2,33),(16.6,30),(22.05,28),(29.1,28)]): sc.put(sc.braam(smidi(m_),2.0),tp,.55,wet=.6)
elif vid==12:
    drive(sc,0.0,DUR+.5,92,[(45,57,60,64),(41,53,57,60),(48,60,64,67),(43,55,59,62)],level=lv)
    for tp in (0.05,9.0,24.3,35.0): sc.put(sc.braam(smidi(26),2.0),tp,.5,wet=.6)
elif vid==14:
    phonk(sc,0.0,DUR+.5,118,level=lv)
    for tp in (0.05,9.6,18.9): sc.put(sc.braam(smidi(28),2.0),tp,.5,wet=.6)
else:
    lofi(sc,0.0,DUR+.5,82,level=lv)
    sc.dry+=sc.vinyl(N)*.25
    for tp in (6.2,11.2,21.2,28.5,38.35): sc.put(sc.ep(smidi(40),3.0),tp,.5,wet=.7)
sc.put(sc.sub808(36.7,2.5),VD-.1,.9)
mus=sc.out()
import os as _os
MUSICFILE=f'/tmp/vt/c9/music/m{vid}.wav'
if _os.path.exists(MUSICFILE):
    sr_,mw=wavfile.read(MUSICFILE); mw=mw.astype(np.float32)/32768; mw=mw.mean(1) if mw.ndim>1 else mw; st=int(18*SR); seg=mw[st:st+N]
    if len(seg)<N: seg=np.pad(seg,(0,N-len(seg)))
    mus=seg.astype(np.float64)

for tp,kind,gn in mod.EVENTS: put_(sfx,KIND[kind](),tp,gn)
for sh_ in mod.story.SH:
    if sh_.get('tr') in ('whip','flash') and sh_['t0']>0.1: put_(sfx,KIND['swish'](),sh_['t0']-.06,.5)
cur=np.ones(N)
for a,b in mod.SILENCE:
    i,j=int(a*SR),int(b*SR); cur[i:j]=np.linspace(1,0,j-i) if False else 0
fade=np.minimum(np.minimum(t/.8,(DUR-t)/1.0),1)**2
env=uniform_filter1d(maximum_filter1d(np.abs(voice),int(.12*SR)),int(.15*SR)); env=np.clip(env*5,0,1)
musd=mus*cur*fade*(1-.66*env)
def db0(x): return 20*np.log10(np.sqrt(np.mean(x**2))+1e-9)
m0=voice>.02; MG=10**((-33.0-db0(musd[m0]))/20); SG=10**((-14.5-db0(np.array([np.abs(sfx).max()])))/20); mix=voice+musd*MG+sfx*SG*(1-.35*env); mix=np.tanh(mix*1.1)/1.1
wavfile.write(f'work/mix{vid}v3_raw.wav',SR,(np.clip(mix,-1,1)*32767).astype(np.int16))
subprocess.run(['ffmpeg','-v','error','-y','-i',f'work/mix{vid}v3_raw.wav','-af','loudnorm=I=-14:TP=-2:LRA=9,alimiter=limit=0.85',f'work/mix{vid}v3.wav'],check=True)
def db(x): return 20*np.log10(np.sqrt(np.mean(x**2))+1e-9)
m=voice>.02; print('voice',db(voice[m]),'music during speech',db((musd*MG)[m]),'sfx peak',db(np.array([np.abs(sfx*SG).max()])))

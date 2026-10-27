import json, subprocess, numpy as np, sys, os
from scipy.ndimage import uniform_filter1d
def energy(src):
    x=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',src,'-vn','-ac','1','-ar','16000','-af','volume=14dB','-f','f32le','-']),np.float32); h=160
    e=np.array([np.sqrt(np.mean(x[i:i+h]**2)) for i in range(0,len(x)-h,h)]); db=20*np.log10(uniform_filter1d(e,5)+1e-6); return db, np.percentile(db,10)+9
def speech(db,thr,a,b,gap=.42):
    on=db[int(a*100):int(b*100)]>thr; segs=[];s=None
    for i,v in enumerate(on):
        t=a+i*.01
        if v and s is None: s=t
        if not v and s is not None: segs.append([s,t]); s=None
    if s is not None: segs.append([s,b])
    m=[]
    for p,q in segs:
        if m and p-m[-1][1]<gap: m[-1][1]=q
        else: m.append([p,q])
    return [[p,q] for p,q in m if q-p>.1]
def build(vid, src, mname, keep_fn, end, refine, drop):
    w=[tuple(x) for x in json.load(open(mname))]; w=[x for x in w if keep_fn(x[1]) and not any(a<=x[1]<=b for a,b in drop)]
    w=[(('Polargeist' if t=='polygressed' else t),a,b) for t,a,b in w]
    PRE,POST,GAP=.07,.16,.34; iv=[]
    for t,a,b in w:
        s,e=max(a-PRE,0),b+POST
        if iv and s-iv[-1][1]<GAP: iv[-1][1]=max(iv[-1][1],e)
        else: iv.append([s,e])
    iv[-1][1]=end
    if refine:
        db,thr=energy(src); new=[]
        for a,b in iv:
            for p,q in speech(db,thr,a,b): new.append([max(p-.1,a),min(q+.14,b)])
        m=[]
        for p,q in new:
            if m and p-m[-1][1]<.05: m[-1][1]=q
            else: m.append([p,q])
        iv=m
    # also cut any retake gap boundaries exactly at drop edges
    off=0; nw=[]
    for a,b in iv:
        for t,x,y in w:
            if a-.001<=x<b-.02: nw.append((t,round(x-a+off,3),round(min(y,b)-a+off,3)))
        off+=b-a
    json.dump(dict(iv=iv,words=nw,dur=off),open(f'work/cut{vid}.json','w'))
    F=.008; n=len(iv)
    fa=';'.join(f'[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d={F}:st=0,afade=t=out:d={F}:st={max(b-a-F,0):.3f}[a{i}]' for i,(a,b) in enumerate(iv))
    fa+=';'+''.join(f'[v{i}][a{i}]' for i in range(n))+f'concat=n={n}:v=1:a=1[v][a]'
    open(f'work/fa{vid}.txt','w').write(fa)
    subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-filter_complex_script',f'work/fa{vid}.txt','-map','[v]','-map','[a]','-r','30','-c:v','libx264','-crf','12','-preset','fast','-c:a','pcm_s16le',f'work/clip{vid}.mkv'],check=True)
    os.system(f'rm -rf work/fd{vid}; mkdir -p work/fd{vid}; ffmpeg -v error -y -i work/clip{vid}.mkv -qscale:v 2 work/fd{vid}/%04d.jpg')
    print(vid,'done',round(off,2),flush=True)
build(15,'../c7/raw/r1.mp4','../c7/raw/m1.json',lambda a: 8.5<=a<=19.6 or 20.1<=a<=26.95 or 34.1<=a<=35.2 or 35.5<=a<=74.0,74.2,True,[(62.5,65.19)])
build(12,'../c7/raw/r2.mp4','../c7/raw/m2.json',lambda a: a>=10.7,53.1,False,[(16.4,19.5)])
open('work/cutbuild.done','w').write('ok')

import sys; sys.path.insert(0,'.')
import importlib, subprocess
name=sys.argv[1]; mixf=sys.argv[2]; outf=sys.argv[3]; mod=importlib.import_module(name)
from multiprocessing import Pool
def job(a): return mod._chunk(a)
if __name__=='__main__':
    n=mod.NF; cs=[(a,min(a+130,n),f'work/s_{name}_{i}.mp4') for i,a in enumerate(range(0,n,130))]
    with Pool(4) as p: outs=p.map(job,cs)
    open(f'work/l_{name}.txt','w').write(''.join(f"file '{o.split('/')[-1]}'\n" for o in outs))
    subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-i',f'work/l_{name}.txt','-c','copy',f'work/sil_{name}.mp4'],check=True)
    subprocess.run(['ffmpeg','-v','error','-y','-i',f'work/sil_{name}.mp4','-i',mixf,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','224k','-t',f'{mod.DUR:.2f}','-movflags','+faststart',outf],check=True)
    print('done',name,n)

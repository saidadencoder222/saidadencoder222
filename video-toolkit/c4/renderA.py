import sys; sys.path.insert(0,'.')
import alex, subprocess
from multiprocessing import Pool
if __name__=='__main__':
    n=alex.NF; cs=[(a,min(a+130,n),f'work/segA_{i}.mp4') for i,a in enumerate(range(0,n,130))]
    with Pool(4) as p: outs=p.map(alex._chunk,cs)
    open('work/listA.txt','w').write(''.join(f"file '{o.split('/')[-1]}'\n" for o in outs))
    subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-i','work/listA.txt','-c','copy','work/silentA.mp4'],check=True)
    subprocess.run(['ffmpeg','-v','error','-y','-i','work/silentA.mp4','-i','work/mixA.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-t',f'{alex.DUR:.2f}','-movflags','+faststart','out/alex_audit.mp4'],check=True)
    print('done',n)

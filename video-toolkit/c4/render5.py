import sys; sys.path.insert(0,'.')
import film2 as film, subprocess
from multiprocessing import Pool
if __name__=='__main__':
    n=film.NF; cs=[(a,min(a+130,n),f'work/seg_{i}.mp4') for i,a in enumerate(range(0,n,130))]
    with Pool(4) as p: outs=p.map(film._chunk,cs)
    open('work/list.txt','w').write(''.join(f"file '{o.split('/')[-1]}'\n" for o in outs))
    subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-i','work/list.txt','-c','copy','work/silent.mp4'],check=True)
    subprocess.run(['ffmpeg','-v','error','-y','-i','work/silent.mp4','-i','work/mix.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-t',f'{film.DUR:.2f}','-movflags','+faststart','out/top3_films_v2.mp4'],check=True)
    print('done',n)

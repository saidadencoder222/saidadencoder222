import sys; sys.path.insert(0,'/tmp/vt/c3')
from reels import *
from multiprocessing import Pool
def job(i): return render_reel(R[i])
if __name__=='__main__':
    with Pool(4) as p:
        for o in p.imap_unordered(job, range(len(R))): print(o, flush=True)

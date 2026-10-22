import sys; sys.path.insert(0,'/tmp/vt/c3')
from reels import *
ns=[int(x) for x in sys.argv[1:]]; tiles=[]
for r in R:
    if r['n'] in ns:
        fr=sample_frames(r,[0,2.0,4.2,6.6]); tiles.append(np.hstack([cv2.resize(f,(270,480)) for f in fr]))
cv2.imwrite(f'{R3}/work/prev.jpg',np.vstack(tiles)); print(len(R))

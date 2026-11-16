"""Look helpers for the speaker clip (re-created). WB is derived from the clip's own wall, keeping ~28% of the warmth."""
from mscenes import *
WALL_GAIN = None
WALL = np.array([96.98, 149.94, 198.76], np.float32)         # BGR of the wall in the original room; override per video with set_wall()
def set_wall(bgr):
    global WALL_GAIN, WALL; WALL = np.array(bgr, np.float32); WALL_GAIN = None
def wb_gain():
    global WALL_GAIN
    if WALL_GAIN is None:
        g = WALL.mean() / WALL; WALL_GAIN = 1 + (g - 1) * .72
    return WALL_GAIN
def look(fr):
    a = fr.astype(np.float32) * wb_gain(); a = np.clip(a, 0, 255).astype(np.uint8); return grade_modern(a)

import sys, os, numpy as np, cv2, glob
import mediapipe as mp
C5 = '/tmp/claude-0/-home-user-saidadencoder222/21382d86-4091-5f53-a3a6-32d6a75a5607/scratchpad/c5'
fs = sorted(glob.glob(f'{C5}/work/fd15/*.jpg')); N = len(fs)
hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=2, model_complexity=0, min_detection_confidence=.4, min_tracking_confidence=.4)
out = np.full((N, 3), np.nan, np.float32); prev = None
for i, f in enumerate(fs):
    im = cv2.imread(f); sm = cv2.resize(im, (540, 960)); r = hands.process(cv2.cvtColor(sm, cv2.COLOR_BGR2RGB))
    if r.multi_hand_landmarks:
        cands = []
        for hl in r.multi_hand_landmarks:
            pts = np.array([[hl.landmark[j].x * 1080, hl.landmark[j].y * 1920] for j in (0, 5, 9, 13, 17)]); c = pts.mean(0)
            xs = np.array([[l.x * 1080, l.y * 1920] for l in hl.landmark]); sz = np.ptp(xs[:, 0]) * np.ptp(xs[:, 1]); cands.append((c, sz))
        if prev is not None: cands.sort(key=lambda a: np.hypot(*(a[0] - prev)))
        else: cands.sort(key=lambda a: -a[1])
        c = cands[0][0]; out[i] = (c[0], c[1], 1); prev = c
    if i % 200 == 0: print(i, N, flush=True)
np.save(f'{C5}/work/hand15_raw.npy', out); print('hands done', np.isfinite(out[:, 0]).mean())

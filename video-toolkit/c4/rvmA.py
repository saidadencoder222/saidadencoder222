import numpy as np, onnxruntime as ort, subprocess, sys, time
W, H = 1080, 1920
sess = ort.InferenceSession('../c2/work/rvm.onnx', providers=['CPUExecutionProvider'])
print([i.name for i in sess.get_inputs()], [o.name for o in sess.get_outputs()])
dec = subprocess.Popen(['ffmpeg','-v','error','-i','work/clipA.mkv','-f','rawvideo','-pix_fmt','rgb24','-'], stdout=subprocess.PIPE, bufsize=W*H*3*2)
enc = subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','gray','-s','540x960','-r','30','-i','-','-c:v','ffv1','work/alphaA.mkv'], stdin=subprocess.PIPE)
st = [np.zeros((1,1,1,1),np.float32) for _ in range(4)]; ratio = np.array([0.45], np.float32); n = 0; t0 = time.time()
import cv2
while True:
    b = dec.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3); x = cv2.resize(fr, (540, 960), interpolation=cv2.INTER_AREA).astype(np.float32).transpose(2,0,1)[None]/255
    out = sess.run(None, {'src': x, 'r1i': st[0], 'r2i': st[1], 'r3i': st[2], 'r4i': st[3], 'downsample_ratio': ratio})
    pha = out[1][0,0]; st = list(out[2:6]); enc.stdin.write((np.clip(pha,0,1)*255).astype(np.uint8).tobytes()); n += 1
    if n % 100 == 0: print(n, round(time.time()-t0), 's', flush=True)
enc.stdin.close(); enc.wait(); print('done', n, 'frames')

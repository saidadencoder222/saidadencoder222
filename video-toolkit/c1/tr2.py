import sys, json
from faster_whisper import WhisperModel
m = WhisperModel('medium.en', device='cpu', compute_type='int8')
for p in sys.argv[1:]:
    segs, _ = m.transcribe(p, word_timestamps=True, condition_on_previous_text=False, language='en', initial_prompt='Instagram content strategy. 8K to 40K followers, 107 leads, outlier videos, funnel, comment the word guide.', vad_filter=False)
    out = []
    for s in segs:
        for w in s.words: out.append((w.word.strip(), round(w.start, 2), round(w.end, 2)))
    json.dump(out, open(p.rsplit('.', 1)[0] + '.words.json', 'w'))
    print(p); print(' '.join(f'{w}' for w, a, b in out))

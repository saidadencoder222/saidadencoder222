import sys, re, time, json
sys.path.insert(0, '/tmp/vt/batch2/eng')
import fetch
fetch.CACHE = '/tmp/vt/c2/assets'; fetch.META = fetch.CACHE + '/meta.json'
names = {'justinian': 'Meister von San Vitale in Ravenna 004.jpg', 'pinatubo': 'Pinatubo91eruption plume.jpg', 'famine': 'Great famine.jpg'}
for key, n in names.items():
    li = fetch.license_of(n); print(key, n, '->', li and (li['license'], li['artist'][:40], li['w'], li['h']), flush=True)
    if li: fetch.save_img(key, li['url'], dict(li, name=n, key=key))
    time.sleep(2)
for key, art in (('crash', 'Wall Street Crash of 1929'), ('depression', 'Great Depression'), ('migrant', 'Migrant Mother')):
    r = fetch.wp_image(art, key=key, min_w=500); print(key, art, '->', r and (r['license'], r['artist'][:40], r['w'], r['h'], r['page']), flush=True); time.sleep(2)

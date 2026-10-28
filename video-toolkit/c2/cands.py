import sys, re, time, json
sys.path.insert(0, '/tmp/vt/batch2/eng')
import fetch
arts = ['Extreme weather events of 535–536', 'Justinian I', 'Procopius', 'Great Famine of 1315–1317', 'Wall Street Crash of 1929', 'Great Depression', 'Hoovervilles', 'Migrant Mother']
out = {}
for a in arts:
    j = fetch.api('en.wikipedia.org', action='query', titles=a, prop='images', imlimit=60, redirects=1); names = []
    for p in (j.get('query', {}).get('pages', {}) or {}).values():
        for im in p.get('images', []) or []:
            n = im['title'].replace('File:', '')
            if re.search(r'\.(jpe?g|png)$', n, re.I) and not re.search(r'(logo|icon|flag|symbol|commons-logo|wiki|stub|ambox|question|edit|folder|padlock|portal|OOjs|increase|decrease|steady|Nuvola)', n, re.I): names.append(n)
    print('==', a, len(names), flush=True); out[a] = []
    for n in names[:14]:
        li = fetch.license_of(n); time.sleep(.5)
        if li: print('  ', n[:70], '|', li['license'], '|', li['w'], 'x', li['h'], '|', li['artist'][:30], flush=True); out[a].append((n, li))
json.dump({k: [(n, l) for n, l in v] for k, v in out.items()}, open('work/cands.json', 'w'))

import requests, json, os, re, time, hashlib, io
from PIL import Image
UA = {'User-Agent': 'OutreachVideoEdit/1.0 (personal video project; contact via owner) python-requests'}
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'imgcache')
META = os.path.join(CACHE, 'meta.json')
def _meta(): return json.load(open(META)) if os.path.exists(META) else {}
def _save(m): json.dump(m, open(META, 'w'), indent=1)
def _get(url, params=None, tries=6, stream=False):
    for i in range(tries):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=60)
            if r.status_code == 200: return r
            if r.status_code in (429, 503): time.sleep(6 * (i + 1)); continue
            return r
        except Exception: time.sleep(4)
    return None
def api(host, **p):
    p['format'] = 'json'; r = _get(f'https://{host}/w/api.php', p)
    try: return r.json()
    except Exception: return {}
FREE = ('CC0', 'CC BY', 'CC-BY', 'Public domain', 'PD', 'CC BY-SA', 'CC-BY-SA', 'GFDL', 'No restrictions', 'Attribution')
def license_of(fname):
    j = api('commons.wikimedia.org', action='query', titles='File:' + fname, prop='imageinfo', iiprop='extmetadata|url|size', iiurlwidth=1600)
    for p in (j.get('query', {}).get('pages', {}) or {}).values():
        ii = (p.get('imageinfo') or [None])[0]
        if not ii: continue
        em = ii.get('extmetadata', {}); lic = (em.get('LicenseShortName', {}) or {}).get('value', ''); art = re.sub('<[^>]+>', '', (em.get('Artist', {}) or {}).get('value', ''))[:60]
        return dict(license=lic, artist=art, url=ii.get('thumburl') or ii.get('url'), w=ii['width'], h=ii['height'], page='https://commons.wikimedia.org/wiki/File:' + fname.replace(' ', '_'))
    return None
def save_img(key, url, info):
    m = _meta(); fn = os.path.join(CACHE, hashlib.md5(key.encode()).hexdigest()[:12] + '.jpg')
    if not os.path.exists(fn):
        r = _get(url)
        if r is None or r.status_code != 200: return None
        try: im = Image.open(io.BytesIO(r.content)).convert('RGB')
        except Exception: return None
        if max(im.size) > 2400: im.thumbnail((2400, 2400))
        im.save(fn, quality=93)
    info = dict(info); info['file'] = fn; m[key] = info; _save(m); return info
def wp_image(title, key=None, min_w=700):
    """Lead image of the English Wikipedia article, only if it is a free-licence file on Commons."""
    key = key or ('wp:' + title); m = _meta()
    if key in m and os.path.exists(m[key]['file']): return m[key]
    j = api('en.wikipedia.org', action='query', titles=title, prop='pageimages|images', piprop='original|name', imlimit=20, redirects=1)
    for p in (j.get('query', {}).get('pages', {}) or {}).values():
        cands = []
        if p.get('pageimage'): cands.append(p['pageimage'])
        for im in p.get('images', []) or []:
            n = im['title'].replace('File:', '')
            if re.search(r'\.(jpe?g|png)$', n, re.I) and not re.search(r'(logo|icon|flag of|map|symbol|commons-logo|wiki)', n, re.I): cands.append(n)
        for n in cands[:8]:
            li = license_of(n); time.sleep(.6)
            if li and any(f.lower() in li['license'].lower() for f in FREE) and li['w'] >= min_w:
                info = dict(li); info['title'] = title; info['src'] = 'Wikipedia: ' + title; return save_img(key, li['url'], info)
    return None
def commons_search(query, key=None, min_w=1200, want_land=True):
    key = key or ('cs:' + query); m = _meta()
    if key in m and os.path.exists(m[key]['file']): return m[key]
    j = api('commons.wikimedia.org', action='query', generator='search', gsrsearch=query + ' filetype:bitmap', gsrnamespace=6, gsrlimit=12, prop='imageinfo', iiprop='url|size|extmetadata', iiurlwidth=1800)
    best = None
    for p in (j.get('query', {}).get('pages', {}) or {}).values():
        ii = (p.get('imageinfo') or [None])[0]
        if not ii or ii['width'] < min_w: continue
        em = ii.get('extmetadata', {}); lic = (em.get('LicenseShortName', {}) or {}).get('value', '')
        if not any(f.lower() in lic.lower() for f in FREE): continue
        if want_land and ii['width'] < ii['height']: continue
        art = re.sub('<[^>]+>', '', (em.get('Artist', {}) or {}).get('value', ''))[:60]
        sc = ii['width'] * (1.2 if want_land else 1)
        if best is None or sc > best[0]: best = (sc, dict(license=lic, artist=art, url=ii.get('thumburl') or ii['url'], w=ii['width'], h=ii['height'], page=ii.get('descriptionurl', ''), title=p['title'], src='Commons: ' + query))
    if best: return save_img(key, best[1]['url'], best[1])
    return None

import requests, re, json, time, io
from PIL import Image
UA={'User-Agent':'VideoEditProject/1.0 (personal video project)'}
def api(**p):
    p['format']='json'
    for i in range(5):
        try:
            r=requests.get('https://commons.wikimedia.org/w/api.php',params=p,headers=UA,timeout=60)
            if r.status_code==200: return r.json()
        except Exception: pass
        time.sleep(10*(i+1))
Q={'actor':'Matthew McConaughey','brain':'human brain neurons illustration','psych':'psychology brain scan MRI','cam':'cinema camera lens film set','edit':'video editing suite timeline monitor','story':'father and daughter silhouette sunset','neuron':'neurons fluorescence microscopy'}
OK=('public domain','cc0','cc by','cc-by','pdm')
meta={}
for k,q in Q.items():
    j=api(action='query',generator='search',gsrsearch=q+' filetype:bitmap',gsrnamespace=6,gsrlimit=12,prop='imageinfo',iiprop='url|size|extmetadata',iiurlwidth=2400)
    c=0
    pages=sorted((j.get('query',{}).get('pages') or {}).values(), key=lambda p:-(p.get('imageinfo') or [{'width':0}])[0].get('width',0)) if j else []
    for p in pages:
        ii=(p.get('imageinfo') or [None])[0]
        if not ii or min(ii['width'],ii['height'])<1100: continue
        em=ii.get('extmetadata',{}); lic=(em.get('LicenseShortName') or {}).get('value',''); art=re.sub('<[^>]+>','',(em.get('Artist') or {}).get('value',''))[:60]
        if not any(x in lic.lower() for x in OK): continue
        url=ii.get('thumburl') or ii['url']
        for i in range(4):
            r=requests.get(url,headers=UA,timeout=90)
            if r.status_code==200: break
            time.sleep(12*(i+1))
        if r.status_code!=200: continue
        try: I=Image.open(io.BytesIO(r.content)).convert('RGB')
        except Exception: continue
        I.save(f'wm/{k}_{c}.jpg',quality=93); meta[f'{k}_{c}']=dict(title=p['title'],lic=lic,artist=art,page=ii.get('descriptionurl',''),size=I.size); print(k,c,I.size,p['title'][:70],'|',lic,'|',art[:30],flush=True); c+=1; time.sleep(3)
        if c>=3: break
    time.sleep(3)
json.dump(meta,open('wm/meta.json','w'),indent=1); print('DONE')

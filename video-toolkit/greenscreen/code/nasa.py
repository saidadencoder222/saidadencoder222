import requests, json, io, time, sys
from PIL import Image
Q={'bh':'black hole simulation accretion disk','bh2':'supermassive black hole artist concept','lens':'gravitational lensing','saturn':'Saturn rings Cassini portrait','earthrise':'Earthrise Apollo 8','bluemarble':'Blue Marble Earth from space','eclipse':'total solar eclipse corona','astro':'astronaut spacewalk Earth horizon','mw':'Milky Way core stars panorama','neb':'Hubble nebula pillars of creation','voy':'Pale Blue Dot Voyager','jup':'Jupiter Juno swirling storms','iss':'International Space Station sunrise','launch':'rocket launch night Saturn V','gal':'Hubble galaxy spiral deep field'}
meta={}
for k,q in Q.items():
    try: j=requests.get('https://images-api.nasa.gov/search',params={'q':q,'media_type':'image'},timeout=40).json()['collection']['items'][:4]
    except Exception as e: print(k,'err',e); continue
    c=0
    for it in j:
        m=it['data'][0]; nid=m['nasa_id']
        try:
            a=requests.get(f'https://images-api.nasa.gov/asset/{nid}',timeout=40).json()['collection']['items']
            urls=[x['href'] for x in a if x['href'].lower().endswith(('.jpg','.jpeg'))]
            pick=[u for u in urls if '~large' in u] or [u for u in urls if '~medium' in u] or urls
            if not pick: continue
            r=requests.get(pick[0],timeout=90); I=Image.open(io.BytesIO(r.content)).convert('RGB')
            if min(I.size)<700: continue
            I.save(f'img/{k}_{c}.jpg',quality=92); meta[f'{k}_{c}']=dict(id=nid,title=m['title'],center=m.get('center'),desc=(m.get('description') or '')[:200],date=m.get('date_created'),size=I.size)
            print(k,c,I.size,nid,'|',m['title'][:60],flush=True); c+=1
            if c>=2: break
        except Exception as e: continue
json.dump(meta,open('img/meta.json','w'),indent=1); print('DONE')

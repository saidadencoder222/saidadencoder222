import requests, json, io
from PIL import Image
Q={'sat':'Saturn Cassini rings natural color','sat2':'Saturn from Cassini mosaic','jup':'Jupiter Juno JunoCam color','pil':'Pillars of Creation Hubble','orion':'Orion Nebula Hubble','night':'Earth at night city lights ISS','mw':'Milky Way night sky over observatory','moon':'Moon surface Apollo high resolution','nebc':'Carina Nebula cosmic cliffs Webb','webb':'James Webb deep field','sunset':'Earth limb sunrise ISS atmosphere','galaxy':'Andromeda galaxy Hubble'}
meta={}
for k,q in Q.items():
    try: items=requests.get('https://images-api.nasa.gov/search',params={'q':q,'media_type':'image'},timeout=40).json()['collection']['items'][:10]
    except Exception as e: print(k,'err'); continue
    c=0
    for it in items:
        m=it['data'][0]; nid=m['nasa_id']
        try:
            a=requests.get(f'https://images-api.nasa.gov/asset/{nid}',timeout=40).json()['collection']['items']
            urls=[x['href'] for x in a if x['href'].lower().endswith(('.jpg','.jpeg'))]
            pick=[u for u in urls if '~orig' in u] or [u for u in urls if '~large' in u]
            if not pick: continue
            r=requests.get(pick[0],timeout=120); I=Image.open(io.BytesIO(r.content)).convert('RGB')
            if min(I.size)<1400: continue
            if max(I.size)>3200: I.thumbnail((3200,3200))
            I.save(f'hd/{k}_{c}.jpg',quality=93); meta[f'{k}_{c}']=dict(id=nid,title=m['title'],size=I.size); print(k,c,I.size,nid,'|',m['title'][:55],flush=True); c+=1
            if c>=2: break
        except Exception: continue
json.dump(meta,open('hd/meta.json','w'),indent=1); print('DONE')

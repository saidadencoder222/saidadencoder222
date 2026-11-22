import requests,json,time,re
H={'User-Agent':'edit-assets/1.0 (sample video; contact via claude.ai)'}
Q={'chess':'chess board pieces','carving':'sculptor carving stone chisel','notebook':'open notebook handwriting pen','dome':'rose under glass dome','library':'old library bookshelves books','reading':'young woman reading book bed painting','fish':'goldfish water illustration','climb':'mountaineer summit ridge'}
out={}
for k,q in Q.items():
    for attempt in range(4):
        try:
            r=requests.get('https://commons.wikimedia.org/w/api.php',params=dict(action='query',generator='search',gsrsearch=q,gsrnamespace=6,gsrlimit=30,prop='imageinfo',iiprop='url|size|extmetadata',iiurlwidth=1400,format='json'),headers=H,timeout=40)
            if r.status_code!=200: time.sleep(15); continue
            res=[]
            for p in r.json().get('query',{}).get('pages',{}).values():
                ii=p['imageinfo'][0]; md=ii.get('extmetadata',{}); lic=md.get('LicenseShortName',{}).get('value','')
                if not re.search(r'CC0|Public|CC BY|PD',lic): continue
                res.append(dict(title=p['title'],lic=lic,w=ii['width'],h=ii['height'],url=ii['thumburl'],artist=re.sub('<[^>]+>','',md.get('Artist',{}).get('value',''))[:60]))
            res=[x for x in res if x['w']>=1200]; res=sorted(res,key=lambda x:-x['w'])[:5]; out[k]=res
            for i,x in enumerate(res):
                p=f'cand/{k}{i}.jpg'
                for a in range(3):
                    rr=requests.get(x['url'],headers=H,timeout=60)
                    if rr.status_code==200: open(p,'wb').write(rr.content); break
                    time.sleep(8)
                time.sleep(1.2)
            print(k,len(res),flush=True); break
        except Exception as e: time.sleep(10)
    time.sleep(7)
json.dump(out,open('gi9d.json','w'),indent=1); print('ALLDONE',flush=True)

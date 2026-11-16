import requests,json,io,time,sys,re
from PIL import Image
UA={'User-Agent':'Mozilla/5.0'}
API='https://gameofthrones.fandom.com/api.php'
def pages(title):
    out=[];cont={}
    for _ in range(3):
        try: d=requests.get(API,params=dict(action='query',generator='images',titles=title,gimlimit=60,prop='imageinfo',iiprop='url|size',format='json',**cont),headers=UA,timeout=40).json()
        except Exception as e: print('err',title,e); break
        for p in (d.get('query',{}).get('pages') or {}).values():
            ii=(p.get('imageinfo') or [None])[0]
            if ii: out.append((p['title'],ii['url'],ii['width'],ii['height']))
        if 'continue' in d: cont=d['continue']
        else: break
    return out
res={}
for key,titles in {'stark':['House Stark'],'targ':['House Targaryen'],'lann':['House Lannister'],'winterfell':['Winterfell'],'dorne':['Dorne','Sunspear','Water Gardens'],'kl':["King's Landing",'Red Keep'],'got':['Game of Thrones (TV series)']}.items():
    L=[]
    for t in titles: L+=pages(t)
    seen=set(); R=[]
    for x in L:
        if x[1] in seen: continue
        seen.add(x[1]); R.append(x)
    res[key]=R; print(key,len(R),[(x[0][5:40],x[2],x[3]) for x in sorted(R,key=lambda z:-z[2]*z[3])[:6]],flush=True)
json.dump(res,open('got/list.json','w'))

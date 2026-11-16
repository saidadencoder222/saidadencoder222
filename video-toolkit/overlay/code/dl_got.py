import requests,json,io,re
from PIL import Image
UA={'User-Agent':'Mozilla/5.0'}
res=json.load(open('got/list.json')); allf={}
for k,v in res.items():
    for t,u,w,h in v: allf[t[5:]]=(u,w,h)
want={'sig_stark':'House Stark.svg','sig_targ':'House Targaryen.svg','sig_lann':'House Lannister.svg','sig_martell':'House Martell.svg','logo':'Game of Thrones.png',
 'wf1':'Winterfell-season7.png','wf2':'801 Winterfell Overview.png','wf3':'Winterfell Title Sequence.jpg','wf4':'Winterfell direwolf tapestry.jpg','wf5':'Battle of Winterfell 1.png',
 'dorne1':'Dorne - Water Gardens 5x06.png','dorne2':'Dorne Season 5.png','dorne3':'Jaime in Sunspear with Areo Hotah.png',
 'kl1':"King's Landing.jpg",'kl2':'Redkeep kingslanding.jpg','kl3':'S05E06 - King\'s Landing.jpg','kl4':"OT Dragon King's Landing.png",'kl5':'Red Keep Full Shot.jpg','kl6':"S05E10 - Red Keep.jpg",
 'dragon1':'Daenerys and dragon.jpg','dragon2':'Dragon Riding S8 Ep 1.jpg','dragon3':'Dragonstone-gates.png','lann1':'Lannister LTA.jpg','stark1':'Stark Siblings S8 EP4.jpg','stark2':'House Stark tapestry.jpg'}
for k,fn in want.items():
    if fn not in allf: print('missing',k,fn); continue
    u=allf[fn][0]; r=requests.get(u,headers=UA,timeout=90)
    if r.status_code!=200: print('fail',k,r.status_code); continue
    if fn.endswith('.svg'):
        open(f'got/{k}.svg','wb').write(r.content)
        try:
            import cairosvg; cairosvg.svg2png(bytestring=r.content,write_to=f'got/{k}.png',output_width=1600)
        except Exception as e: print('svg fail',k,e)
    else:
        I=Image.open(io.BytesIO(r.content)); I=I.convert('RGBA') if fn.endswith('.png') else I.convert('RGB')
        if max(I.size)>3840: I.thumbnail((3840,3840))
        I.save(f'got/{k}.png' if I.mode=='RGBA' else f'got/{k}.jpg',quality=94)
    print('ok',k,allf[fn][1:],flush=True)

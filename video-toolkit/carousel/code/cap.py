import asyncio,sys,os,subprocess
from playwright.async_api import async_playwright
SL=[int(x) for x in sys.argv[1:]]; FPS=30; DUR=7.0
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium',args=['--no-sandbox','--autoplay-policy=no-user-gesture-required']); pg=await b.new_page(viewport={'width':1080,'height':1350})
        for n in SL:
            await pg.goto(f'file://{os.getcwd()}/v/s{n}.html'); await pg.evaluate('window.ready'); await pg.wait_for_timeout(500)
            ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-framerate',str(FPS),'-i','-','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',f'out/slide_{n:02d}.mp4'],stdin=subprocess.PIPE)
            for i in range(int(DUR*FPS)):
                u=i/FPS; await pg.evaluate(f'setU({u})'); buf=await pg.screenshot(type='jpeg',quality=93); ff.stdin.write(buf)
                if i==int(5.9*FPS): open(f'out/still_{n:02d}.jpg','wb').write(buf)
            ff.stdin.close(); ff.wait(); print('slide',n,'done',flush=True)
        await b.close()
asyncio.run(main())

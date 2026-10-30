import asyncio,os,sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium',args=['--no-sandbox']); pg=await b.new_page(viewport={'width':1080,'height':1350})
        for n in [int(x) for x in sys.argv[2:]]:
            await pg.goto(f'file://{os.getcwd()}/v/s{n}.html'); await pg.evaluate('window.ready'); await pg.wait_for_timeout(400)
            await pg.evaluate(f'setU({sys.argv[1]})'); await pg.screenshot(path=f'out/t_{n:02d}.jpg',type='jpeg',quality=90)
        await b.close()
asyncio.run(main())

import asyncio,sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/opt/pw-browsers/chromium',args=['--no-sandbox']); pg=await b.new_page(viewport={'width':1080,'height':1350})
        for i in range(1,9):
            await pg.goto(f'file://{__import__("os").getcwd()}/a/s{i}.html'); await pg.wait_for_timeout(400); await pg.screenshot(path=f'a/s{i}.png')
        await b.close()
asyncio.run(main())

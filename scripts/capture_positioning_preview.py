from pathlib import Path
import base64,subprocess
from playwright.sync_api import sync_playwright
out=Path(__file__).resolve().parents[1]/'assets/previews';tmp=Path('/tmp/urban-review/combined');tmp.mkdir(exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1200,'height':900});page.goto('http://localhost:8080/positioning/',wait_until='networkidle');page.wait_for_function('!!window.positioningScene');page.evaluate('window.positioningScene.stop()');page.add_style_tag(content='#positioning-canvas{width:800px!important;height:450px!important}');page.wait_for_timeout(100)
 for i in range(90):
  page.evaluate('(i)=>window.positioningScene.render(225+74*i/89)',i);data=page.locator('#positioning-canvas').evaluate('(c)=>c.toDataURL().split(",")[1]');(tmp/f'{i:03}.png').write_bytes(base64.b64decode(data))
 b.close()
subprocess.run(['ffmpeg','-v','error','-y','-framerate','8','-i',str(tmp/'%03d.png'),'-c:v','libx264','-crf','26','-pix_fmt','yuv420p','-movflags','+faststart',str(out/'positioning-raw.mp4')],check=True)
print('combined scene rendered')

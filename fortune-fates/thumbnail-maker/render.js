const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{const [src,out]=process.argv.slice(2);const b=await chromium.launch();const p=await b.newPage({viewport:{width:1280,height:720},deviceScaleFactor:1});
for(const f of fs.readdirSync(src).filter(f=>f.endsWith('.html'))){await p.goto('file://'+path.join(src,f));await p.waitForTimeout(300);await p.screenshot({path:path.join(out,f.replace('.html','.png'))});console.log(f)}
await b.close()})();

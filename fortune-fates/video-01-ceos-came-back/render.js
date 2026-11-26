// Usage: node render.js stills <t1,t2,...> | thumb | video [fps]
const {chromium}=require('playwright'); const fs=require('fs'); const path=require('path'); const {spawn}=require('child_process');
const DIR=__dirname, OUT=path.join(DIR,'out');
(async()=>{
 const mode=process.argv[2]||'stills';
 const cards=JSON.parse(fs.readFileSync(path.join(DIR,'cards.json'),'utf8'));
 cards.forEach(c=>c.hasPhoto=fs.existsSync(path.join(DIR,'photos',c.photo+'.jpg')));
 const missing=cards.filter(c=>!c.hasPhoto).map(c=>c.name); if(missing.length) console.log('No photo yet:',missing.join(', '));
 const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
 await p.goto('file://'+path.join(DIR,'scene.html')); await p.evaluate(()=>document.fonts.ready);
 const b64=f=>'url(data:image/png;base64,'+fs.readFileSync(path.join(DIR,'assets',f)).toString('base64')+')';
 await p.addStyleTag({content:`:root{--grunge:${b64('grunge.png')};--inkmask:${b64('inkmask.png')}}`});
 const info=await p.evaluate(c=>setup(c),cards); fs.writeFileSync(path.join(OUT,'timing.json'),JSON.stringify(info));
 await p.waitForTimeout(500);
 if(mode==='stills'){
  for(const t of (process.argv[3]||'1.6,10,60').split(',').map(Number)){await p.evaluate(t=>render(t),t);await p.screenshot({path:path.join(OUT,`still_${t}.png`)});console.log('still',t)}
 } else if(mode==='thumb'){
  const ids=[0,cards.findIndex(c=>c.name==='Sam Altman'),cards.length-1];
  await p.evaluate(ids=>thumb(ids),ids); await p.waitForTimeout(300);
  await p.screenshot({path:path.join(OUT,'thumb_1920.png')});
  const p2=await b.newPage({viewport:{width:1280,height:720}});
  await p2.setContent(`<body style="margin:0"><img src="data:image/png;base64,${fs.readFileSync(path.join(OUT,'thumb_1920.png')).toString('base64')}" style="width:1280px;height:720px;display:block"></body>`);
  await p2.screenshot({path:path.join(OUT,'thumbnail.png')}); console.log('thumb ok');
 } else if(mode==='video'){
  const fps=Number(process.argv[3]||30), N=Math.ceil(info.duration*fps);
  const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(fps),'-i','-','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',path.join(OUT,'video_noaudio.mp4')],{stdio:['pipe','inherit','inherit']});
  const t0=Date.now();
  for(let i=0;i<N;i++){
   await p.evaluate(t=>render(t),i/fps);
   const buf=await p.screenshot({type:'jpeg',quality:92});
   if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
   if(i%300===0) console.log(`frame ${i}/${N}  ${((Date.now()-t0)/1000).toFixed(0)}s`);
  }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); console.log('video done',N,'frames');
 }
 await b.close();
})();

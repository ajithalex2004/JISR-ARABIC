const path=require('path');const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1296,height:2304}});
await p.goto('file://'+path.join(__dirname,'overlays_v3.html'));await p.evaluate(()=>document.fonts.ready);
await p.locator('#sheet').screenshot({path:'cap3/sheet.png'});
for(const id of ['hook1','hook2','s3','s3b','s4','s5','s6','s7']) await p.locator('#'+id).screenshot({path:`cap3/${id}.png`,omitBackground:true});
await b.close();})();

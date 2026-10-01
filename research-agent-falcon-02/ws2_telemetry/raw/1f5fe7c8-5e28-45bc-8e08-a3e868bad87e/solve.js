const fs=require('fs');
let code=fs.readFileSync('tool_outputs/chal_script.js','utf8');
const el=()=>({style:{setProperty(){}},remove(){},classList:{add(){},remove(){}},textContent:'',className:''});
global.document={getElementById:()=>el(),createElement:()=>({style:{},setAttribute(){}}),querySelector:()=>el(),querySelectorAll:()=>[],body:el(),addEventListener(){},removeEventListener(){},documentElement:el()};
global.window={location:{reload(){},href:''},addEventListener(){},matchMedia:()=>({matches:false,addEventListener(){}})};
global.location=global.window.location;
global.navigator={userAgent:'Mozilla/5.0 Chrome/126 Safari/537.36',webdriver:false,platform:'Linux x86_64',languages:['en-US'],plugins:[],mimeTypes:[]};
global.screen={width:1920,height:1080,availWidth:1920,availHeight:1040,colorDepth:24,pixelDepth:24};
global.chrome={runtime:{}};
const msgs=[];
class MC{constructor(){this.port1={postMessage:(m)=>{msgs.push(m);},start(){},addEventListener(){}};this.port2={postMessage:()=>{},start(){},close(){}};}
global.MessageChannel=MC;
global.Worker=class{constructor(){} postMessage(){} terminate(){} addEventListener(){}};
global.XMLHttpRequest=class{open(){} send(){} setRequestHeader(){} addEventListener(){}};
global.fetch=()=>Promise.resolve({});
global.atob=(s)=>Buffer.from(s,'base64').toString('binary');
try{ eval(code); }catch(e){ console.log('EVALERR',e.message); }
setTimeout(()=>{console.log('MSGS',JSON.stringify(msgs).slice(0,4000));},800);

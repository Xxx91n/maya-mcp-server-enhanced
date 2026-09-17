import { spawn } from 'node:child_process';
const srv = spawn('python', ['-m', 'maya_mcp_server'], { stdio: ['pipe','pipe','ignore'] });
let buf=''; const pending=new Map(); let id=1;
srv.stdout.on('data', d=>{ buf+=d.toString(); let i; while((i=buf.indexOf('\n'))>=0){ const l=buf.slice(0,i).trim(); buf=buf.slice(i+1); if(!l) continue; let m; try{m=JSON.parse(l)}catch{continue} if(m.id!==undefined&&pending.has(m.id)){pending.get(m.id)(m); pending.delete(m.id);} }});
const call=(method,params)=>new Promise((res,rej)=>{const i=id++; pending.set(i,res); srv.stdin.write(JSON.stringify({jsonrpc:'2.0',id:i,method,params})+'\n'); setTimeout(()=>rej(new Error('to')),20000);});
await call('initialize',{protocolVersion:'2024-11-05',capabilities:{},clientInfo:{name:'fix',version:'0'}});
srv.stdin.write(JSON.stringify({jsonrpc:'2.0',method:'notifications/initialized',params:{}})+'\n');
const cases = [
  ['scene_snapshot', {}],
  ['execute_code', {code:'print(1)'}],
  ['scene_rollback', {filename:'a..b.ma'}],
  ['scene_rollback', {filename:'../x.ma'}],
  ['scene_rollback', {filename:'..\\x.ma'}],
  ['maya_setup_guide', {action:'install', dry_run:true, target_version:'2099'}],
];
for (const [name,args] of cases) {
  const r = await call('tools/call',{name,arguments:args});
  const t = r.result?.content?.[0]?.text ?? JSON.stringify(r.error ?? r.result);
  console.log(name+' '+JSON.stringify(args)+' => isError='+(r.result?.isError)+' text='+(t||'').slice(0,160));
}
srv.kill(); process.exit(0);
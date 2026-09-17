import { spawn } from 'node:child_process';
const srv = spawn('python', ['-m', 'maya_mcp_server'], { stdio: ['pipe', 'pipe', 'ignore'] });
let buf = ''; const pending = new Map(); let nextId = 1;
srv.stdout.on('data', (d) => {
  buf += d.toString('utf8'); let idx;
  while ((idx = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, idx).trim(); buf = buf.slice(idx + 1);
    if (!line) continue;
    let msg; try { msg = JSON.parse(line); } catch { continue; }
    if (msg.id !== undefined && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
  }
});
function call(method, params) {
  const id = nextId++;
  return new Promise((resolve, reject) => {
    pending.set(id, resolve);
    srv.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
    setTimeout(() => { if (pending.has(id)) { pending.delete(id); reject(new Error('timeout')); } }, 15000);
  });
}
await call('initialize', { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'rl', version: '0' } });
srv.stdin.write(JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized', params: {} }) + '\n');
let firstLimited = -1; const codes = {};
for (let i = 1; i <= 105; i++) {
  const r = await call('tools/call', { name: 'list_sessions', arguments: {} });
  const isErr = r.result?.isError === true;
  const text = r.result?.content?.[0]?.text || '';
  const m = text.match(/\[([a-z_]+)\]/); const c = m ? m[1] : (isErr ? 'err' : 'ok');
  codes[c] = (codes[c] || 0) + 1;
  if (isErr && firstLimited < 0) firstLimited = i;
}
console.log('READ x105 -> firstLimited=' + firstLimited + ' codes=' + JSON.stringify(codes));
// write-class bucket: scene_plan is mutation-class, 20/60s. Fire 25.
firstLimited = -1; const codes2 = {};
for (let i = 1; i <= 25; i++) {
  const r = await call('tools/call', { name: 'scene_plan', arguments: { objective: 'x' } });
  const isErr = r.result?.isError === true;
  const text = r.result?.content?.[0]?.text || '';
  const m = text.match(/\[([a-z_]+)\]/); const c = m ? m[1] : (isErr ? 'err' : 'ok');
  codes2[c] = (codes2[c] || 0) + 1;
  if (isErr && firstLimited < 0) firstLimited = i;
}
console.log('WRITE x25 -> firstLimited=' + firstLimited + ' codes=' + JSON.stringify(codes2));
srv.kill(); process.exit(0);

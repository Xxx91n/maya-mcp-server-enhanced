import { spawn } from 'node:child_process';

const srv = spawn('python', ['-m', 'maya_mcp_server'], { stdio: ['pipe', 'pipe', 'inherit'] });
let buf = '';
const pending = new Map();
let nextId = 1;

srv.stdout.on('data', (d) => {
  buf += d.toString('utf8');
  let idx;
  while ((idx = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, idx).trim();
    buf = buf.slice(idx + 1);
    if (!line) continue;
    let msg;
    try { msg = JSON.parse(line); } catch { continue; }
    if (msg.id !== undefined && pending.has(msg.id)) {
      pending.get(msg.id)(msg);
      pending.delete(msg.id);
    }
  }
});

function call(method, params) {
  const id = nextId++;
  return new Promise((resolve, reject) => {
    pending.set(id, resolve);
    srv.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
    setTimeout(() => { if (pending.has(id)) { pending.delete(id); reject(new Error('timeout ' + method)); } }, 20000);
  });
}
function notify(method, params) {
  srv.stdin.write(JSON.stringify({ jsonrpc: '2.0', method, params }) + '\n');
}

const out = {};
try {
  const init = await call('initialize', {
    protocolVersion: '2024-11-05',
    capabilities: {},
    clientInfo: { name: 'audit-smoke', version: '0.0.1' },
  });
  out.init = { serverInfo: init.result?.serverInfo, protocolVersion: init.result?.protocolVersion };
  notify('notifications/initialized', {});

  const list = await call('tools/list', {});
  const tools = list.result?.tools ?? [];
  out.toolCount = tools.length;
  out.toolNames = tools.map(t => t.name);
  out.missingAnnotations = tools.filter(t => !t.annotations).map(t => t.name);
  out.hintGaps = tools.filter(t => {
    const a = t.annotations || {};
    return !('readOnlyHint' in a) || !('destructiveHint' in a) || !('idempotentHint' in a) || !('openWorldHint' in a);
  }).map(t => t.name);
  out.annotationMatrix = tools.map(t => ({ n: t.name, ro: t.annotations?.readOnlyHint, de: t.annotations?.destructiveHint, id: t.annotations?.idempotentHint, ow: t.annotations?.openWorldHint }));

  const ping = await call('ping', {});
  out.ping = ping.result;

  const blocked = await call('tools/call', { name: 'execute_code', arguments: { code: 'os.system("x")' } });
  out.blockedCall = blocked.result ?? blocked.error;

  const badType = await call('tools/call', { name: 'execute_code', arguments: { code: '1+1', result_type: 'BOGUS' } });
  out.badResultType = badType.result ?? badType.error;

  console.log(JSON.stringify(out, null, 2));
} catch (e) {
  console.log('SMOKE_FAIL ' + e.message + ' partial=' + JSON.stringify(out));
} finally {
  srv.kill();
  process.exit(0);
}

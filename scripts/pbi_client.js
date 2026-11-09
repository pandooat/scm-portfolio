// ponytail: stdlib node child_process bridge to @microsoft/powerbi-modeling-mcp via stdio JSON-RPC. Ceiling: local single instance. Upgrade: full daemon when concurrent requests needed.
const { spawn } = require('child_process');

async function callMcp(toolName, args = {}) {
  return new Promise((resolve, reject) => {
    const cp = spawn('cmd.exe', ['/c', 'npx', '-y', '@microsoft/powerbi-modeling-mcp@latest', '--start', '--accepteula'], {
      stdio: ['pipe', 'pipe', 'ignore'],
      env: { ...process.env, PBI_MODELING_MCP_ACCEPT_EULA: 'true' }
    });

    let buffer = '';
    let dbName = null;

    cp.stdout.on('data', data => {
      buffer += data.toString();
      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const msg = JSON.parse(line.trim());
          if (msg.id === 1) {
            cp.stdin.write(JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized' }) + '\n');
            cp.stdin.write(JSON.stringify({
              jsonrpc: '2.0', id: 2, method: 'tools/call',
              params: { name: 'connection_operations', arguments: { request: { operation: 'ListLocalInstances' } } }
            }) + '\n');
          } else if (msg.id === 2) {
            const res = JSON.parse(msg.result?.content?.[0]?.text || '{}');
            const inst = res.data?.[0];
            if (!inst?.port) {
              cp.kill();
              return reject(new Error('No running Power BI Desktop instance found'));
            }
            cp.stdin.write(JSON.stringify({
              jsonrpc: '2.0', id: 3, method: 'tools/call',
              params: { name: 'connection_operations', arguments: { request: { operation: 'Connect', dataSource: `localhost:${inst.port}` } } }
            }) + '\n');
          } else if (msg.id === 3) {
            cp.stdin.write(JSON.stringify({
              jsonrpc: '2.0', id: 4, method: 'tools/call',
              params: { name: 'database_operations', arguments: { request: { operation: 'List' } } }
            }) + '\n');
          } else if (msg.id === 4) {
            const res = JSON.parse(msg.result?.content?.[0]?.text || '{}');
            dbName = res.data?.[0]?.name;
            if (args.request && !args.request.databaseName) {
              args.request.databaseName = dbName;
            }
            cp.stdin.write(JSON.stringify({
              jsonrpc: '2.0', id: 5, method: 'tools/call',
              params: { name: toolName, arguments: args }
            }) + '\n');
          } else if (msg.id === 5) {
            cp.kill();
            resolve(msg.result);
          }
        } catch (e) {}
      }
    });

    cp.on('error', reject);
    cp.stdin.write(JSON.stringify({
      jsonrpc: '2.0', id: 1, method: 'initialize',
      params: { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'pbi-client', version: '1.0' } }
    }) + '\n');

    setTimeout(() => {
      cp.kill();
      reject(new Error('Operation timed out after 30s'));
    }, 30000);
  });
}

const [,, cmd, ...rest] = process.argv;

if (!cmd || cmd === 'help') {
  console.log('Usage: node scripts/pbi_client.js [tables|measures|dax <query>|raw <tool> <jsonArgs>]');
  process.exit(0);
}

(async () => {
  try {
    if (cmd === 'tables') {
      const res = await callMcp('table_operations', { request: { operation: 'List' } });
      const parsed = JSON.parse(res.content?.[0]?.text || '{}');
      console.log(JSON.stringify(parsed.data || parsed, null, 2));
    } else if (cmd === 'measures') {
      const res = await callMcp('measure_operations', { request: { operation: 'List' } });
      const parsed = JSON.parse(res.content?.[0]?.text || '{}');
      console.log(JSON.stringify(parsed.data || parsed, null, 2));
    } else if (cmd === 'dax') {
      const query = rest.join(' ');
      const res = await callMcp('dax_query_operations', { request: { operation: 'Execute', query } });
      console.log(res.content?.[0]?.resource?.text || res.content?.[0]?.text || JSON.stringify(res));
    } else if (cmd === 'raw') {
      const [tool, jsonArgs] = rest;
      const res = await callMcp(tool, JSON.parse(jsonArgs || '{}'));
      console.log(JSON.stringify(res, null, 2));
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
})();

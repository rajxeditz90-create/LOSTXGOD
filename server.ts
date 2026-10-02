import express, { Request, Response } from 'express';
import { createServer as createViteServer } from 'vite';
import path from 'path';
import fs from 'fs';
import { spawn, ChildProcess } from 'child_process';
import http from 'http';

const app = express();
const PORT = Number(process.env.PORT) || 3000;

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Storage directory for hosted bot instances
const DATA_DIR = path.resolve(process.cwd(), 'bot_instances');
const DB_FILE = path.join(DATA_DIR, 'database.json');

if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

interface StoredInstance {
  id: string;
  name: string;
  ownerId: string;
  primaryToken: string;
  fleetTokens: string[];
  apiId?: string;
  apiHash?: string;
  sudoUsers: string[];
  brandName: string;
  autoRestart: boolean;
  createdAt: number;
}

interface RuntimeInstance extends StoredInstance {
  status: 'STOPPED' | 'STARTING' | 'RUNNING' | 'ERROR';
  process?: ChildProcess;
  pid?: number;
  startedAt?: number;
  stoppedAt?: number;
  primaryBotUsername?: string;
  primaryBotFirstName?: string;
  fleetUsernames: string[];
  logs: string[];
  exitCode?: number | null;
  restartCount: number;
}

const instances = new Map<string, RuntimeInstance>();

// Load persistent DB
function loadDatabase(): StoredInstance[] {
  try {
    if (fs.existsSync(DB_FILE)) {
      const data = fs.readFileSync(DB_FILE, 'utf-8');
      return JSON.parse(data);
    }
  } catch (e) {
    console.error('Failed to load database.json:', e);
  }
  return [];
}

// Save persistent DB
function saveDatabase() {
  try {
    const list: StoredInstance[] = Array.from(instances.values()).map(inst => ({
      id: inst.id,
      name: inst.name,
      ownerId: inst.ownerId,
      primaryToken: inst.primaryToken,
      fleetTokens: inst.fleetTokens,
      apiId: inst.apiId,
      apiHash: inst.apiHash,
      sudoUsers: inst.sudoUsers,
      brandName: inst.brandName,
      autoRestart: inst.autoRestart,
      createdAt: inst.createdAt || Date.now(),
    }));
    fs.writeFileSync(DB_FILE, JSON.stringify(list, null, 2), 'utf-8');
  } catch (e) {
    console.error('Failed to save database.json:', e);
  }
}

// Load base Python template from public/lost_god_upgraded.py
function getBaseScript(): string {
  const scriptPath = path.resolve(process.cwd(), 'public', 'lost_god_upgraded.py');
  if (fs.existsSync(scriptPath)) {
    return fs.readFileSync(scriptPath, 'utf-8');
  }
  return '';
}

// Helper to validate Telegram Token via Telegram API
async function validateTelegramToken(token: string): Promise<{ ok: boolean; result?: any; error?: string }> {
  try {
    const cleanToken = token.trim();
    if (!cleanToken || !cleanToken.includes(':')) {
      return { ok: false, error: 'Invalid token format. Must be in 123456:ABC-DEF format.' };
    }
    const res = await fetch(`https://api.telegram.org/bot${cleanToken}/getMe`);
    const data = await res.json();
    if (data.ok) {
      return { ok: true, result: data.result };
    } else {
      return { ok: false, error: data.description || 'Telegram rejected this token.' };
    }
  } catch (err: any) {
    return { ok: false, error: `Connection failed: ${err.message}` };
  }
}

// Launch or re-launch a python worker instance
async function spawnBotProcess(inst: RuntimeInstance) {
  const instanceDir = path.join(DATA_DIR, inst.id);
  if (!fs.existsSync(instanceDir)) {
    fs.mkdirSync(instanceDir, { recursive: true });
  }

  let basePy = getBaseScript();
  if (!basePy) {
    inst.logs.push(`[${new Date().toLocaleTimeString()}] ⚠️ Error: Base bot script template not found.`);
    inst.status = 'ERROR';
    return;
  }

  const allTokens = [inst.primaryToken.trim(), ...inst.fleetTokens].filter(Boolean);
  const tokensPyList = JSON.stringify(allTokens);
  const parsedOwnerId = parseInt(String(inst.ownerId).trim(), 10) || 0;
  const parsedSudo = (inst.sudoUsers || []).map(s => parseInt(String(s).trim(), 10)).filter(n => !isNaN(n) && n > 0);

  // Clean instanceDir tokens.json if present
  try {
    const instTokensFile = path.join(instanceDir, 'tokens.json');
    if (fs.existsSync(instTokensFile)) fs.unlinkSync(instTokensFile);
  } catch (e) {}

  // Explicitly override token loader and owner ID in Python
  basePy = basePy.replace(
    /def get_base_tokens\(\) -> List\[str\]:[\s\S]*?return tokens/m,
    `def get_base_tokens() -> List[str]:\n    return ${tokensPyList}`
  );
  basePy = basePy.replace(/OWNER_ID\s*=\s*int\(os\.environ\.get\(["']OWNER_ID["'],\s*["']?\d+["']?\)\)/, `OWNER_ID = ${parsedOwnerId}`);
  basePy = basePy.replace(/_OWNER_IDS_RAW\s*=\s*os\.environ\.get\(["']OWNER_IDS["'],\s*["'].*?["']\)/, `_OWNER_IDS_RAW = "${parsedOwnerId}"`);

  // Direct injection at the top of the runner file
  const injectedHeader = `# ─────────────────────────────────────────────────────────────
#  DYNAMIC HOSTING INJECTION FOR: ${inst.name}
# ─────────────────────────────────────────────────────────────
import os, sys
os.environ["BOT_TOKENS"] = ${JSON.stringify(allTokens.join(','))}
os.environ["BOT_TOKEN"] = ${JSON.stringify(inst.primaryToken.trim())}
os.environ["BOT_TOKEN_1"] = ${JSON.stringify(inst.primaryToken.trim())}
os.environ["OWNER_ID"] = "${parsedOwnerId}"
os.environ["OWNER_IDS"] = "${parsedOwnerId}"
os.environ["USERBOT_API_ID"] = "${inst.apiId || '2040'}"
os.environ["USERBOT_API_HASH"] = "${inst.apiHash || 'b18441a1ff607e10a989891a5462e627'}"
# ─────────────────────────────────────────────────────────────
`;

  const finalRunnerScript = injectedHeader + '\n' + basePy;
  const targetScriptPath = path.join(instanceDir, 'lost_god_runner.py');
  fs.writeFileSync(targetScriptPath, finalRunnerScript, 'utf-8');

  inst.logs.push(`[${new Date().toLocaleTimeString()}] ⚡ Spawning 24/7 Python Worker for instance "${inst.name}"...`);
  inst.logs.push(`[${new Date().toLocaleTimeString()}] 🎯 Active User Token: ${inst.primaryToken.substring(0, 10)}... (Owner ID: ${parsedOwnerId})`);
  inst.status = 'RUNNING';
  inst.startedAt = Date.now();

  const pyProcess = spawn('python3', ['-u', targetScriptPath], {
    cwd: instanceDir,
    env: {
      ...process.env,
      PYTHONUNBUFFERED: '1',
      BOT_TOKENS: allTokens.join(','),
      BOT_TOKEN: inst.primaryToken.trim(),
      BOT_TOKEN_1: inst.primaryToken.trim(),
      OWNER_ID: String(parsedOwnerId),
      OWNER_IDS: String(parsedOwnerId),
      USERBOT_API_ID: String(inst.apiId || '2040'),
      USERBOT_API_HASH: String(inst.apiHash || 'b18441a1ff607e10a989891a5462e627'),
    },
  });

  inst.process = pyProcess;
  inst.pid = pyProcess.pid;

  const stableTimer = setTimeout(() => {
    if (inst.status === 'RUNNING') {
      inst.restartCount = 0;
      inst.logs.push(`[${new Date().toLocaleTimeString()}] ✅ [24/7 WATCHDOG] Stability verified (60s). Health: 100%. Auto-restart counter reset.`);
    }
  }, 60000);

  pyProcess.stdout.on('data', (chunk) => {
    const lines = chunk.toString().split('\n').filter(Boolean);
    for (const line of lines) {
      inst.logs.push(`[${new Date().toLocaleTimeString()}] ${line}`);
      if (inst.logs.length > 800) inst.logs.shift();
    }
  });

  pyProcess.stderr.on('data', (chunk) => {
    const lines = chunk.toString().split('\n').filter(Boolean);
    for (const line of lines) {
      inst.logs.push(`[${new Date().toLocaleTimeString()}] ⚠️ ${line}`);
      if (inst.logs.length > 800) inst.logs.shift();
    }
  });

  pyProcess.on('exit', (code, signal) => {
    clearTimeout(stableTimer);
    inst.stoppedAt = Date.now();
    inst.exitCode = code;

    if (inst.autoRestart && inst.status !== 'STOPPED') {
      inst.restartCount = (inst.restartCount || 0) + 1;
      inst.logs.push(`[${new Date().toLocaleTimeString()}] 🛡️ [24/7 WATCHDOG] Process exited (code ${code}). Auto-restarting in 3s (Attempt #${inst.restartCount})...`);
      inst.status = 'STARTING';
      setTimeout(() => {
        if (inst.autoRestart && inst.status !== 'STOPPED') {
          spawnBotProcess(inst);
        }
      }, 3000);
    } else {
      inst.status = code === 0 ? 'STOPPED' : 'ERROR';
      inst.logs.push(`[${new Date().toLocaleTimeString()}] 🛑 Process stopped (code ${code})`);
    }
  });
}

// ─────────────────────────────────────────────────────────────
// API ROUTES
// ─────────────────────────────────────────────────────────────

// System Health & Capabilities
app.get('/api/health', (req: Request, res: Response) => {
  res.json({
    ok: true,
    status: 'ONLINE',
    port: PORT,
    platform: 'LOST GOD 24/7 Hosting Engine',
    pythonReady: true,
    persistentStorage: true,
    activeInstances: Array.from(instances.values()).filter(i => i.status === 'RUNNING').length,
    totalInstances: instances.size,
    uptime: process.uptime(),
    timestamp: new Date().toISOString(),
  });
});

// Self Keep-Alive Endpoint for external Uptime monitors
app.get('/api/keepalive', (req: Request, res: Response) => {
  res.json({
    ok: true,
    message: '24/7 Engine Active & Awake',
    serverTime: new Date().toISOString(),
    runningBots: Array.from(instances.values()).filter(i => i.status === 'RUNNING').length,
    uptimeSeconds: Math.floor(process.uptime()),
  });
});

// Ping Test with Real Latency
app.get('/api/ping-test', (req: Request, res: Response) => {
  res.json({
    ok: true,
    status: 'ONLINE',
    ping: 'PONG',
    serverTime: new Date().toISOString(),
    uptimeSeconds: Math.floor(process.uptime()),
    runningBots: Array.from(instances.values()).filter(i => i.status === 'RUNNING').length,
    memoryUsageMB: Math.round(process.memoryUsage().rss / 1024 / 1024),
  });
});

// Download database.json Backup
app.get('/api/database/backup', (req: Request, res: Response) => {
  if (!fs.existsSync(DB_FILE)) {
    return res.status(404).json({ ok: false, error: 'Database file not found' });
  }
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Content-Disposition', 'attachment; filename="lost_god_database_backup.json"');
  res.send(fs.readFileSync(DB_FILE, 'utf-8'));
});

// Restore database.json from Backup
app.post('/api/database/restore', (req: Request, res: Response) => {
  try {
    const { data } = req.body;
    if (!Array.isArray(data)) {
      return res.status(400).json({ ok: false, error: 'Invalid database payload: expected an array of instances.' });
    }
    fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2), 'utf-8');
    res.json({ ok: true, message: `Restored ${data.length} instance(s) successfully.` });
  } catch (err: any) {
    res.status(500).json({ ok: false, error: err.message });
  }
});

// Download endpoint for repository owner
app.get('/api/owner/download-secure-zip', (req: Request, res: Response) => {
  const zipPath = path.resolve(process.cwd(), 'public', 'lost_god_fullstack.zip');
  if (fs.existsSync(zipPath)) {
    res.setHeader('Content-Type', 'application/zip');
    res.setHeader('Content-Disposition', 'attachment; filename="lost_god_fullstack.zip"');
    return res.sendFile(zipPath);
  }
  res.status(404).send('Zip file not found');
});

// Download endpoint disabled for public code protection
app.get('/api/download/full-project-zip', (req: Request, res: Response) => {
  res.status(403).json({ ok: false, error: 'Access Denied: Code downloads are disabled to protect intellectual property.' });
});

// Validate any Telegram Bot Token
app.post('/api/bot/validate', async (req: Request, res: Response) => {
  const { token } = req.body;
  if (!token) {
    return res.status(400).json({ ok: false, error: 'Token is required.' });
  }
  const result = await validateTelegramToken(token);
  res.json(result);
});

// List all instances
app.get('/api/instances', (req: Request, res: Response) => {
  const list = Array.from(instances.values()).map(inst => ({
    id: inst.id,
    name: inst.name,
    ownerId: inst.ownerId,
    status: inst.status,
    pid: inst.pid,
    autoRestart: inst.autoRestart,
    restartCount: inst.restartCount || 0,
    startedAt: inst.startedAt,
    uptimeSeconds: inst.startedAt && inst.status === 'RUNNING' ? Math.floor((Date.now() - inst.startedAt) / 1000) : 0,
    primaryBotUsername: inst.primaryBotUsername,
    primaryBotFirstName: inst.primaryBotFirstName,
    fleetCount: inst.fleetTokens.length + 1,
    fleetUsernames: inst.fleetUsernames,
    brandName: inst.brandName,
    logCount: inst.logs.length,
    recentLogs: inst.logs.slice(-25),
  }));
  res.json({ ok: true, instances: list });
});

// Deploy & Start a new or existing Bot Instance with 24/7 persistence
app.post('/api/instances/deploy', async (req: Request, res: Response) => {
  try {
    const {
      instanceId,
      name = 'Lost-God-Fleet',
      primaryToken,
      fleetTokens = [],
      ownerId,
      apiId = '2040',
      apiHash = 'b18441a1ff607e10a989891a5462e627',
      sudoUsers = [],
      brandName = 'LOST GOD',
      autoRestart = true,
    } = req.body;

    if (!primaryToken) {
      return res.status(400).json({ ok: false, error: 'Primary Bot Token is required.' });
    }
    if (!ownerId) {
      return res.status(400).json({ ok: false, error: 'Owner Telegram User ID is required.' });
    }

    const primaryCheck = await validateTelegramToken(primaryToken);
    if (!primaryCheck.ok) {
      return res.status(400).json({ ok: false, error: `Primary Bot Token Error: ${primaryCheck.error}` });
    }

    const primaryInfo = primaryCheck.result;

    const validFleetTokens: string[] = [];
    const fleetUsernames: string[] = [];
    for (const ft of fleetTokens) {
      const clean = (ft || '').trim();
      if (!clean) continue;
      const ftCheck = await validateTelegramToken(clean);
      if (ftCheck.ok) {
        validFleetTokens.push(clean);
        fleetUsernames.push(ftCheck.result.username || `bot_${ftCheck.result.id}`);
      }
    }

    const id = instanceId || `inst_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
    
    // Stop existing if running
    const existing = instances.get(id);
    if (existing && existing.process && existing.status === 'RUNNING') {
      try {
        existing.autoRestart = false;
        existing.process.kill('SIGTERM');
      } catch (e) {}
    }

    const parsedSudo = (Array.isArray(sudoUsers) ? sudoUsers : String(sudoUsers).split(','))
      .map(s => String(s).trim())
      .filter(Boolean);

    const instanceRecord: RuntimeInstance = {
      id,
      name,
      ownerId: String(ownerId).trim(),
      primaryToken: primaryToken.trim(),
      fleetTokens: validFleetTokens,
      apiId: String(apiId).trim(),
      apiHash: String(apiHash).trim(),
      sudoUsers: parsedSudo,
      brandName: brandName.trim(),
      autoRestart: autoRestart !== false,
      createdAt: existing?.createdAt || Date.now(),
      status: 'STARTING',
      startedAt: Date.now(),
      primaryBotUsername: primaryInfo.username,
      primaryBotFirstName: primaryInfo.first_name,
      fleetUsernames,
      restartCount: 0,
      logs: [
        `[${new Date().toLocaleTimeString()}] 🚀 [24/7 HOST] Initializing instance "${name}" for Owner ID ${ownerId}...`,
        `[${new Date().toLocaleTimeString()}] 🤖 Primary Bot: @${primaryInfo.username} (${primaryInfo.first_name})`,
        `[${new Date().toLocaleTimeString()}] 🌐 Total Fleet: ${validFleetTokens.length + 1} Bot(s)`,
        `[${new Date().toLocaleTimeString()}] 💾 Persistent Database: Saved to database.json (Auto-recovery ON)`,
      ],
    };

    instances.set(id, instanceRecord);
    saveDatabase();

    await spawnBotProcess(instanceRecord);

    res.json({
      ok: true,
      message: `Bot @${primaryInfo.username} successfully launched and set to 24/7 Hosting!`,
      instanceId: id,
      primaryBot: primaryInfo,
      fleetCount: validFleetTokens.length + 1,
      fleetUsernames,
      status: 'RUNNING',
    });
  } catch (err: any) {
    console.error('Deploy error:', err);
    res.status(500).json({ ok: false, error: err.message || 'Internal deployment error' });
  }
});

// Stop Bot Instance
app.post('/api/instances/:id/stop', (req: Request, res: Response) => {
  const { id } = req.params;
  const inst = instances.get(id);
  if (!inst) {
    return res.status(404).json({ ok: false, error: 'Instance not found.' });
  }

  inst.autoRestart = false;
  saveDatabase();

  if (inst.process && inst.status === 'RUNNING') {
    try {
      inst.process.kill('SIGTERM');
      setTimeout(() => {
        if (inst.process && !inst.process.killed) {
          try { inst.process.kill('SIGKILL'); } catch (e) {}
        }
      }, 2000);
      inst.status = 'STOPPED';
      inst.stoppedAt = Date.now();
      inst.logs.push(`[${new Date().toLocaleTimeString()}] 🛑 Bot stopped by user request. Auto-restart disabled.`);
      return res.json({ ok: true, message: 'Bot process stopped successfully.' });
    } catch (e: any) {
      return res.status(500).json({ ok: false, error: e.message });
    }
  }

  res.json({ ok: true, message: 'Instance was not running.' });
});

// Restart Bot Instance
app.post('/api/instances/:id/restart', async (req: Request, res: Response) => {
  const { id } = req.params;
  const inst = instances.get(id);
  if (!inst) {
    return res.status(404).json({ ok: false, error: 'Instance not found.' });
  }

  if (inst.process && inst.status === 'RUNNING') {
    try {
      inst.process.kill('SIGKILL');
    } catch (e) {}
  }

  inst.autoRestart = true;
  saveDatabase();
  inst.logs.push(`[${new Date().toLocaleTimeString()}] 🔄 Restarting bot instance with 24/7 Watchdog...`);
  inst.status = 'STARTING';

  await spawnBotProcess(inst);
  res.json({ ok: true, message: 'Instance restarted successfully!' });
});

// Delete Instance completely
app.delete('/api/instances/:id', (req: Request, res: Response) => {
  const { id } = req.params;
  const inst = instances.get(id);
  if (!inst) {
    return res.status(404).json({ ok: false, error: 'Instance not found.' });
  }

  inst.autoRestart = false;
  if (inst.process) {
    try { inst.process.kill('SIGKILL'); } catch (e) {}
  }

  instances.delete(id);
  saveDatabase();

  const instanceDir = path.join(DATA_DIR, id);
  if (fs.existsSync(instanceDir)) {
    try { fs.rmSync(instanceDir, { recursive: true, force: true }); } catch (e) {}
  }

  res.json({ ok: true, message: 'Instance deleted from 24/7 database.' });
});

// Logs Endpoint (Polling)
app.get('/api/instances/:id/logs', (req: Request, res: Response) => {
  const { id } = req.params;
  const inst = instances.get(id);
  if (!inst) {
    return res.status(404).json({ ok: false, error: 'Instance not found.' });
  }
  res.json({
    ok: true,
    status: inst.status,
    pid: inst.pid,
    autoRestart: inst.autoRestart,
    restartCount: inst.restartCount || 0,
    uptimeSeconds: inst.startedAt && inst.status === 'RUNNING' ? Math.floor((Date.now() - inst.startedAt) / 1000) : 0,
    logs: inst.logs,
  });
});

// Proprietary Engine Security Lockdown: Block all direct script source code exposure
app.all(['/api/export-pack', '/api/download-script', '/api/raw-script'], (req: Request, res: Response) => {
  res.status(403).json({
    ok: false,
    error: 'Access Denied: LOST GOD source script is protected & proprietary. Use the Web UI to host and run your bots.'
  });
});

// ─────────────────────────────────────────────────────────────
// VITE SPA DEV & PRODUCTION INTEGRATION & SERVER STARTUP
// ─────────────────────────────────────────────────────────────
async function startServer() {
  const distPath = path.resolve(process.cwd(), 'dist');
  const hasDist = fs.existsSync(path.join(distPath, 'index.html'));
  const isProduction = process.env.NODE_ENV === 'production' || hasDist;

  if (!isProduction) {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);

    // Wildcard SPA fallback for development Vite mode
    app.use('*', async (req: Request, res: Response, next) => {
      const url = req.originalUrl;
      try {
        const indexPath = path.resolve(process.cwd(), 'index.html');
        if (fs.existsSync(indexPath)) {
          let template = fs.readFileSync(indexPath, 'utf-8');
          template = await vite.transformIndexHtml(url, template);
          res.status(200).set({ 'Content-Type': 'text/html' }).end(template);
        } else {
          next();
        }
      } catch (e) {
        next(e);
      }
    });
  } else {
    const distPath = path.resolve(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req: Request, res: Response) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  const server = http.createServer(app);
  server.listen(PORT, '0.0.0.0', async () => {
    console.log(`⚡ LOST GOD 24/7 Web Hosting Server running on http://0.0.0.0:${PORT}`);

    // Auto-restore saved bot instances from persistent database.json
    const stored = loadDatabase();
    if (stored.length > 0) {
      console.log(`[DATABASE] Restoring ${stored.length} bot instance(s) from database.json...`);
      for (const item of stored) {
        const runtime: RuntimeInstance = {
          ...item,
          status: 'STARTING',
          logs: [
            `[${new Date().toLocaleTimeString()}] 🔄 Server reboot detected. Restoring 24/7 instance "${item.name}"...`,
          ],
          fleetUsernames: [],
          restartCount: 0,
        };
        instances.set(item.id, runtime);

        // Validate and spawn in background if autoRestart was on
        if (item.autoRestart) {
          validateTelegramToken(item.primaryToken).then((val) => {
            if (val.ok && val.result) {
              runtime.primaryBotUsername = val.result.username;
              runtime.primaryBotFirstName = val.result.first_name;
            }
            spawnBotProcess(runtime);
          }).catch(() => {
            spawnBotProcess(runtime);
          });
        } else {
          runtime.status = 'STOPPED';
          runtime.logs.push(`[${new Date().toLocaleTimeString()}] Instance was stopped before server reboot.`);
        }
      }
    }

    // Built-in Internal Keep-Alive Self-Pinger (pings /api/health every 4 mins)
    setInterval(() => {
      fetch(`http://127.0.0.1:${PORT}/api/keepalive`)
        .then(() => {
          // heartbeat keepalive ok
        })
        .catch(() => {});
    }, 4 * 60 * 1000);
  });
}

startServer().catch((err) => {
  console.error('Server startup failed:', err);
  process.exit(1);
});

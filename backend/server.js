const http = require('http');
const fs = require('fs');
const path = require('path');
const WebSocket = require('ws');
require('dotenv').config();

const PORT = process.env.PORT || 3000;
const PRIMARY_RPC = process.env.RPC_URL;

const PROBE_CONFIG = {
    POLL_INTERVAL: 200,
    TIMEOUT: 2000,
    HEARTBEAT_SIZE: 64,
    OSCILLATOR_BASE_FREQ: 1.0,
    OSCILLATOR_FREQ_RANGE: 5.0
};

const REGIONAL_RPCS = [
    { id: 'LDN-RPC-01', name: 'London', url: 'https://eth.drpc.org', lat: 51.5074, lon: -0.1278 },
    { id: 'NYC-RPC-02', name: 'New York', url: 'https://eth.llamarpc.com', lat: 40.7128, lon: -74.0060 },
    { id: 'SIN-RPC-03', name: 'Singapore', url: 'https://singapore.rpc.blxrbdn.com', lat: 1.3521, lon: 103.8198 },
    { id: 'TYO-RPC-04', name: 'Tokyo', url: 'https://ethereum.publicnode.com', lat: 35.6895, lon: 139.6917 },
    { id: 'SFO-RPC-05', name: 'San Francisco', url: 'https://rpc.flashbots.net', lat: 37.7749, lon: -122.4194 },
    { id: 'FRA-RPC-06', name: 'Frankfurt', url: 'https://eth-mainnet.public.blastapi.io', lat: 50.1109, lon: 8.6821 },
    { id: 'SYD-RPC-10', name: 'Sydney', url: 'https://ethereum.publicnode.com', lat: -33.8688, lon: 151.2093 },
    { id: 'GRU-RPC-08', name: 'Sao Paulo', url: 'https://eth.llamarpc.com', lat: -23.5505, lon: -46.6333 },
    { id: 'TOR-RPC-07', name: 'Toronto', url: 'https://eth.drpc.org', lat: 45.6532, lon: -82.3832 },
];

class TelemetryProbe {
    constructor() {
        this.clients = new Set();
        this.heartbeatBuffer = new Array(PROBE_CONFIG.HEARTBEAT_SIZE).fill(0);
        this.lastBlock = { hash: null, time: Date.now(), baseFee: 0, volatility: 0 };
        this.nodesData = [];
    }

    async pollNode(node) {
        const start = performance.now();
        try {
            const res = await fetch(node.url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ jsonrpc: '2.0', method: 'eth_getBlockByNumber', params: ['latest', false], id: 1 }),
                signal: AbortSignal.timeout(PROBE_CONFIG.TIMEOUT)
            });
            
            if (!res.ok) return null;
            const data = await res.json();
            const result = data.result;

            if (result) {
                const latency = performance.now() - start;
                const gwei = parseInt(result.baseFeePerGas, 16) / 1e9;
                return { 
                    id: node.id, 
                    lat: node.lat, 
                    lon: node.lon, 
                    latency, 
                    gwei: Math.round(gwei * 10) / 10,
                    hash: result.hash
                };
            }
        } catch (e) {
            // Silence errors for cleaner live-only data
        }
        return null;
    }

    updateHeartbeat() {
        const activeNodes = this.nodesData;
        const avgLat = activeNodes.length > 0 
            ? activeNodes.reduce((a, b) => a + b.latency, 0) / activeNodes.length 
            : 0;
        const volatility = this.lastBlock.volatility;
        const t = Date.now() / 1000;

        for (let i = 0; i < PROBE_CONFIG.HEARTBEAT_SIZE; i++) {
            const freq = PROBE_CONFIG.OSCILLATOR_BASE_FREQ + (i / PROBE_CONFIG.HEARTBEAT_SIZE) * PROBE_CONFIG.OSCILLATOR_FREQ_RANGE;
            const phase = i * (Math.PI / 32);
            const noise = (Math.sin(t * freq + phase) * 0.4) + (Math.sin(t * (freq * 0.5) + phase) * 0.6);
            const activity = 0.2 + (avgLat / 400) + (volatility * 1.2);
            const val = Math.abs(noise * activity);
            this.heartbeatBuffer[i] = Math.max(0.05, Math.min(1.0, val));
        }
    }

    async run() {
        while (true) {
            const results = await Promise.all(REGIONAL_RPCS.map(n => this.pollNode(n)));
            this.nodesData = results.filter(Boolean);

            const latest = this.nodesData.find(n => n.hash);
            if (latest && latest.hash !== this.lastBlock.hash) {
                if (this.lastBlock.baseFee > 0) {
                    this.lastBlock.volatility = Math.abs(latest.gwei - this.lastBlock.baseFee);
                }
                this.lastBlock.hash = latest.hash;
                this.lastBlock.time = Date.now();
                this.lastBlock.baseFee = latest.gwei;
            }

            this.updateHeartbeat();

            const payload = JSON.stringify({
                nodes: this.nodesData,
                heartbeat: this.heartbeatBuffer,
                global: {
                    timeSinceBlock: (Date.now() - this.lastBlock.time) / 1000,
                    avgGwei: this.nodesData.length > 0 
                        ? this.nodesData.reduce((a, b) => a + b.gwei, 0) / this.nodesData.length 
                        : 0
                }
            });

            this.clients.forEach(c => {
                if (c.readyState === WebSocket.OPEN) c.send(payload);
            });

            await new Promise(r => setTimeout(r, PROBE_CONFIG.POLL_INTERVAL));
        }
    }
}

const probe = new TelemetryProbe();
probe.run();

const server = http.createServer((req, res) => {
    // CORS: Allow access from your Vercel domain
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');

    let filePath = path.join(__dirname, '..', 'frontend', req.url === '/' ? 'index.html' : req.url);
    const ext = path.extname(filePath);
    const mimeTypes = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' };

    fs.readFile(filePath, (err, content) => {
        if (err) {
            res.writeHead(404);
            res.end('File not found');
        } else {
            res.writeHead(200, { 'Content-Type': mimeTypes[ext] || 'text/plain' });
            res.end(content);
        }
    });
});

const wss = new WebSocket.Server({ server });
wss.on('connection', ws => {
    probe.clients.add(ws);
    ws.on('close', () => probe.clients.delete(ws));
});

server.listen(PORT, () => console.log(`TELEMETRY_GRID server active at http://localhost:${PORT}`));

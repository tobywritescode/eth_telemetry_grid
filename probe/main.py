import asyncio
import json
import os
import time
import math
import aiohttp
import websockets
from dotenv import load_dotenv

load_dotenv()

# Regional Node Registry
# In a real scenario, these would be real RPC URLs. 
# For this "militaristic" version, we'll use a mix of real and simulated data if RPC_URL is the only one.
RPC_URL = os.getenv("RPC_URL")
WS_PORT = int(os.getenv("WS_PORT", "8765"))

REGIONS = [
    {"id": "LDN-RPC-01", "name": "London", "lat": 51.5074, "lon": -0.1278},
    {"id": "NYC-RPC-02", "name": "New York", "lat": 40.7128, "lon": -74.0060},
    {"id": "SIN-RPC-03", "name": "Singapore", "lat": 1.3521, "lon": 103.8198},
    {"id": "TYO-RPC-04", "name": "Tokyo", "lat": 35.6895, "lon": 139.6917},
    {"id": "SFO-RPC-05", "name": "San Francisco", "lat": 37.7749, "lon": -122.4194},
    {"id": "FRA-RPC-06", "name": "Frankfurt", "lat": 50.1109, "lon": 8.6821},
]

class RegionalTelemetryProbe:
    def __init__(self, primary_rpc_url):
        self.primary_rpc_url = primary_rpc_url
        self.clients = set()
        self.last_block_data = {
            "hash": None,
            "time": time.time(),
            "base_fee": 0,
            "volatility": 0
        }
        self.heartbeat_buffer = [0.0] * 64 # Spectral density buffer
        
    async def fetch_node_data(self, session, region):
        # In a real deployment, each region would have its own RPC_URL.
        # Here we simulate regional latency variations based on the primary RPC.
        start_time = time.perf_counter()
        
        # Simulate regional network jitter
        jitter = (math.sin(time.time() + hash(region['id'])) + 1.0) * 10.0
        
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getBlockByNumber",
            "params": ["latest", False],
            "id": 1
        }
        
        try:
            async with session.post(self.primary_rpc_url, json=payload, timeout=2) as response:
                real_latency = (time.perf_counter() - start_time) * 1000
                data = await response.json()
                result = data.get("result")
                
                if result:
                    base_fee = int(result["baseFeePerGas"], 16) / 1e9 if "baseFeePerGas" in result else 0
                    return {
                        "id": region["id"],
                        "lat": region["lat"],
                        "lon": region["lon"],
                        "latency": real_latency + jitter,
                        "gwei": round(base_fee, 1),
                        "block_hash": result["hash"]
                    }
        except Exception as e:
            return {
                "id": region["id"],
                "lat": region["lat"],
                "lon": region["lon"],
                "latency": 999, # Offline
                "gwei": 0,
                "block_hash": None
            }
        return None

    def update_heartbeat(self, nodes_data):
        # Calculate "Spectral Density" for the Waveform Array
        # Fuses gas spikes, latency variance, and time
        avg_latency = sum(n['latency'] for n in nodes_data if n['latency'] < 999) / len(nodes_data)
        latency_variance = sum((n['latency'] - avg_latency)**2 for n in nodes_data if n['latency'] < 999) / len(nodes_data)
        
        # Shift buffer and add new integrated value
        self.heartbeat_buffer.pop(0)
        
        # Chaotic integration
        noise = (math.sin(time.time() * 5.0) * 0.2) + (math.sin(time.time() * 1.2) * 0.5)
        impact = (latency_variance / 500.0) + (self.last_block_data["volatility"] * 2.0)
        new_val = clamp(abs(noise * impact), 0.05, 1.0)
        
        self.heartbeat_buffer.append(new_val)

    async def broadcast(self, message):
        if not self.clients:
            return
        msg_json = json.dumps(message)
        await asyncio.gather(
            *[client.send(msg_json) for client in list(self.clients)],
            return_exceptions=True
        )

    async def run(self):
        async with aiohttp.ClientSession() as session:
            while True:
                tasks = [self.fetch_node_data(session, r) for r in REGIONS]
                nodes_results = await asyncio.gather(*tasks)
                nodes_data = [r for r in nodes_results if r]
                
                # Global Block Logic (from primary/any node)
                latest_valid = next((n for n in nodes_data if n['block_hash']), None)
                if latest_valid:
                    if latest_valid["block_hash"] != self.last_block_data["hash"]:
                        if self.last_block_data["base_fee"] > 0:
                            self.last_block_data["volatility"] = abs(latest_valid["gwei"] - self.last_block_data["base_fee"])
                        self.last_block_data["hash"] = latest_valid["block_hash"]
                        self.last_block_data["time"] = time.time()
                        self.last_block_data["base_fee"] = latest_valid["gwei"]
                
                self.update_heartbeat(nodes_data)
                
                payload = {
                    "nodes": nodes_data,
                    "heartbeat": self.heartbeat_buffer,
                    "global": {
                        "time_since_block": time.time() - self.last_block_data["time"],
                        "avg_gwei": sum(n['gwei'] for n in nodes_data) / len(nodes_data) if nodes_data else 0
                    }
                }
                
                await self.broadcast(payload)
                if int(time.time()) % 10 == 0:
                    print(f"DEBUG: Broadcast cycle active. Latency: {nodes_data[0]['latency']:.2f}ms")
                await asyncio.sleep(0.1) # High-frequency updates

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

async def main():
    if not RPC_URL:
        print("Error: RPC_URL environment variable is not set.")
        return

    probe = RegionalTelemetryProbe(RPC_URL)
    
    async def handler(websocket):
        probe.clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            probe.clients.remove(websocket)

    server = await websockets.serve(handler, "0.0.0.0", WS_PORT)
    print(f"REGIONAL_NODES_v1 Probe started on ws://0.0.0.0:{WS_PORT}")
    await probe.run()

if __name__ == "__main__":
    asyncio.run(main())

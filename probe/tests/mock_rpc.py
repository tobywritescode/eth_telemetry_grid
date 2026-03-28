from aiohttp import web
import json
import time
import random
import asyncio

async def handle_rpc(request):
    data = await request.json()
    if data.get("method") == "eth_getBlockByNumber":
        # Simulate a block change every 15 seconds (slight delay)
        current_time = int(time.time())
        block_number = current_time // 15
        
        # High volatility for stress test (Z Distortion)
        base_fee = 150 + random.uniform(-50, 50) 
        
        # Artificial delay for RPC call (X Distortion)
        await asyncio.sleep(random.uniform(0.1, 0.3)) # 100-300ms latency
        
        return web.json_response({
            "jsonrpc": "2.0",
            "id": data.get("id"),
            "result": {
                "hash": hex(block_number),
                "number": hex(block_number),
                "baseFeePerGas": hex(int(base_fee * 1e9))
            }
        })
    return web.json_response({"error": "Method not found"}, status=404)

app = web.Application()
app.router.add_post("/", handle_rpc)

if __name__ == "__main__":
    web.run_app(app, port=8545)

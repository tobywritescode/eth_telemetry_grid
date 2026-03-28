import asyncio
import os
import subprocess
import time
import json
import websockets
import aiohttp
from aiohttp import web

# This script will:
# 1. Start the mock RPC server.
# 2. Start the probe.
# 3. Connect as a client to the probe's WebSocket.
# 4. Verify telemetry data is being broadcast.

async def test_probe():
    # Set environment variables for the test
    os.environ["RPC_URL"] = "http://localhost:8545"
    os.environ["WS_PORT"] = "8766"

    # Start mock RPC server in a separate process
    mock_rpc_process = subprocess.Popen(["python3", "tests/mock_rpc.py"])
    print("Started mock RPC server.")

    # Wait for mock RPC server to start
    await asyncio.sleep(2)

    # Start the probe in a separate process
    probe_process = subprocess.Popen(["python3", "main.py"])
    print("Started telemetry probe.")

    # Wait for probe to start
    await asyncio.sleep(2)

    try:
        # Connect to the probe's WebSocket
        uri = "ws://localhost:8766"
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            
            # Read first few messages
            for i in range(5):
                message = await websocket.recv()
                data = json.loads(message)
                print(f"Received message {i+1}: {data}")
                
                # Basic validation
                assert "x" in data, "Missing latency (x)"
                assert "y" in data, "Missing block delta (y)"
                assert "z" in data, "Missing gas volatility (z)"
                assert isinstance(data["x"], (int, float)), "Latency should be a number"
                assert isinstance(data["y"], (int, float)), "Block delta should be a number"
                assert isinstance(data["z"], (int, float)), "Gas volatility should be a number"

            print("Test passed: Telemetry data is valid.")

    finally:
        # Clean up processes
        probe_process.terminate()
        mock_rpc_process.terminate()
        print("Cleaned up processes.")

if __name__ == "__main__":
    asyncio.run(test_probe())

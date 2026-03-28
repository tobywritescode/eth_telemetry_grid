#!/bin/bash

# Ensure we are in the project root
PROJECT_ROOT=$(pwd)

# 1. Start Mock RPC
echo "Starting Mock RPC..."
cd $PROJECT_ROOT/probe && poetry run python3 tests/mock_rpc.py &
MOCK_PID=$!

# 2. Start Telemetry Probe
echo "Starting Telemetry Probe..."
cd $PROJECT_ROOT/probe && export RPC_URL="http://localhost:8545" && export WS_PORT="8765" && poetry run python3 main.py &
PROBE_PID=$!

# 3. Start Static Server for Client
echo "Starting Web Server at http://localhost:8080"
cd $PROJECT_ROOT/client && python3 -m http.server 8080 &
SERVER_PID=$!

# Cleanup on exit
trap "kill $MOCK_PID $PROBE_PID $SERVER_PID" EXIT

echo "TELEMETRY_GRID is live at http://localhost:8080"
echo "Press Ctrl+C to stop."
wait

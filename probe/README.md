# Telemetry Probe

The Ingestion Engine for TELEMETRY_GRID.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your Ethereum RPC URL:
   ```env
   RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
   WS_PORT=8765
   ```

3. Run the probe:
   ```bash
   python main.py
   ```

## Output Format

The probe broadcasts a JSON payload every 0.5s:

```json
{
  "x": 42.5,  // RPC Latency (ms)
  "y": 8.2,   // Seconds since last block
  "z": 0.15   // Base Fee Volatility (Δ Gwei)
}
```

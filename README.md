# TELEMETRY_GRID v2.0 // ETH_MAINNET

A high-fidelity, retro-militaristic telemetry dashboard for the Ethereum Network. This tool provides a real-time "command center" view of global RPC latency, block propagation, and network volatility.

## //The Mission
The **TELEMETRY_GRID** is designed for node operators and network enthusiasts who require a low-latency, high-contrast visualization of Ethereum's global health. It transforms raw JSON-RPC data into a 3D tactical interface, complete with a custom CRT shader aesthetic.

## //Features
- **Global Sensor Network:** Monitors 9 unique regional RPC sensors (London, NY, Singapore, Tokyo, San Francisco, Frankfurt, Sydney, Sao Paulo, Toronto).
- **Spectral Density Monitor:** A 64-bar real-time frequency analyzer modulated by network congestion and base-fee volatility.
- **Tactical HUD:** Interactive documentation keys with hover-activated pencil-thin arrow pointers and tooltips.
- **3D Regional Deep-Dive:** Raycasted 3D nodes that provide detailed regional telemetry (latency, GWEI) upon hover.
- **CRT Post-Processing:** Hand-written GLSL shaders for barrel distortion, chromatic aberration, scanline simulation, and Gaussian noise.

## //Technical Architecture

### **Backend (Node.js)**
The "Engine" of the project. It runs a high-frequency asynchronous probe that polls global RPC entry points every 200ms. 
- **WebSocket Bridge:** Uses `ws` to broadcast unified telemetry payloads to all connected clients.
- **Fault Tolerance:** Implements a silent filtering system to ensure the grid only reflects live, responsive sensors.

### **Frontend (Three.js & Vite)**
The "Dashboard" is a high-performance WebGL application.
- **Dual-Scene Pipeline:** Combines a 3D Perspective world map with a 2D Orthographic HUD.
- **Vite Build Setup:** Optimized for modern CI/CD pipelines (Vercel) with support for environment variable injection.

## //Deployment Guide

### **1. Prerequisites**
You **MUST** have your own Ethereum RPC URL. We recommend a free **Alchemy** or **Infura** account.

### **2. Local Setup**
1. Clone the repository.
2. Create a `.env` file in the `backend/` directory:
   ```env
   RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY
   PORT=3000
   ```
3. Install dependencies and start the engine:
   ```bash
   cd backend
   npm install
   node server.js
   ```
4. In a separate terminal, run the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### **3. Production Deployment (Render + Vercel)**

#### **Backend (Render.com)**
- **Root Directory:** `backend`
- **Environment Variables:** Add `RPC_URL` (your Alchemy key).
- **Port:** Render will automatically assign a port.

#### **Frontend (Vercel.com)**
- **Root Directory:** `frontend`
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Environment Variables:** Add `VITE_RENDER_BACKEND_HOST` set to your Render domain (e.g., `eth-telemetry.onrender.com`).

## //Configuration
Tuning the aesthetic can be done in `frontend/main.js` via the `CONFIG` object:
```javascript
const CONFIG = {
    CRT: {
        curvature: 0.06,
        scanline: 0.1,
        chroma: 0.001,
        noise: 0.04
    }
};
```

---
*Created by [toby-nichol](https://tobynichol.computer)*

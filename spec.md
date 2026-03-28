SYSTEM SPECIFICATION: TELEMETRY_GRID // ETH_MAINNET_V1
Operational Directive
The industry monitors high-stakes infrastructure through bloated, DOM-crushing dashboards. These applications consume massive memory to render static graphs. TELEMETRY_GRID rejects the dashboard. It is a zero-latency, WebGL-powered visualizer that translates the physical state of the Ethereum mainnet into a deterministic visual environment. JavaScript is relegated to a bootloader. Rust commands the GPU. The blockchain dictates the reality.

1. The Ingestion Engine (Python Telemetry Probe)
The backend does not serve complex APIs. It is a single-purpose asynchronous daemon engineered to extract network physics.

Execution: Written in asynchronous Python, leveraging your specialization in contract logic and backend routing. It establishes a persistent WebSocket connection to a primary RPC node (e.g., Alchemy or Infura).

The Variables: The engine tracks three explicit data points:

X (Local Pulse): RPC Latency (ms). The physical routing friction between the node and the chain.

Y (Global Pulse): Time Since Last Block (s). The consensus health. The strict 12-second target.

Z (Congestion State): Base Fee Volatility (Δ Gwei). The derivative of the gas price, indicating sudden capital influx or network attacks.

The Pipeline: The probe flattens these variables into a microscopic JSON payload and broadcasts it continuously via a localized WebSocket server. No database. No historical storage. Pure real-time state.

2. The Execution Core (Rust WebAssembly Engine)
The client environment strictly prohibits DOM manipulation. HTML exists solely to mount the canvas.

The Toolchain: The core is written in strict Rust, compiled to a wasm32-unknown-unknown binary utilizing the wasm-bindgen and web-sys crates.

The Override: The binary intercepts the Python WebSocket stream. It bypasses standard browser rendering, seizing the WebGL2 context directly from the Wasm sandbox.

Memory Management: Rust calculates the delta of the incoming telemetry and pushes the values directly to the GPU memory as GLSL uniform variables (u_latency, u_block_delta, u_gas_volatility). Frame execution is locked, impervious to JavaScript garbage collection.

3. The Visual Matrix (GLSL Shader Mechanics)
The environment is painted with mathematics. The shaders translate the incoming uniform variables into immediate physical reactions.

Condition Green (The Baseline):

State: Latency < 50ms, Block Delta ≤ 12s, Gas Volatility = 0.

Mechanic: A deep, infinite wireframe grid moving at a constant velocity. The color space is a stable cyan. A geometric pulse ripples across the matrix exactly every 12 seconds as consensus is reached.

Vector X Distortions (RPC Latency Spikes):

Mechanic: The fragment shader introduces horizontal shear and barrel distortion. As latency increases, the grid physically tears, mirroring a damaged CRT monitor losing its tracking signal.

Vector Y Distortions (Missed Slots / Block Delay):

Mechanic: If the 12-second timer expires, the u_block_delta uniform forces the grid to rapidly decelerate. Ambient light calculations are suppressed. The environment loses power. When the delayed block arrives, a violent, over-exposed flash resets the state.

Vector Z Distortions (High-Stakes Congestion):

Mechanic: As the Base Fee spikes, the shader introduces heavy chromatic aberration. The color space shifts violently from cold cyan to an aggressive, radioactive orange. The geometry becomes erratic, representing physical financial friction.

4. Deployment Vector
The Client: The HTML/Wasm package is deployed as a zero-config static site on Vercel.

The Probe: The Python daemon is deployed as a microscopic, always-on container within your existing infrastructure, maintaining the infinite ping loop.

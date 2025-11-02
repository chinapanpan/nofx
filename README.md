# nofx

<img width="3840" height="1498" alt="image" src="https://github.com/user-attachments/assets/dac4b5d1-3da7-4b54-97e5-cef226d99547" />

<img width="2882" height="1792" alt="image" src="https://github.com/user-attachments/assets/66a5283b-3761-4992-82d1-8cd01f4d518d" />

This is a project inspired by [nof1 Alpha Arena](https://nof1.ai), you can setup AI trading bot on crypto market.

DONE:
- Paper Trading
- OpenAI compatible API
- AWS Bedrock integration (Claude Sonnet 4.5, Qwen 3, DeepSeek 3.1)
- LEVERAGE
- cctx quotes

TODO:
- real trading

## Documentation

### 📚 Architecture Documentation
For detailed system architecture documentation, please refer to: [architecture.md](./architecture.md)

This document includes:
- 🏗️ Overall system architecture design
- 🔄 Core business process descriptions
- 📊 Database design and model relationships
- 🔌 API interface documentation
- 🤖 AI decision service implementation details
- 📈 Trade execution and order matching mechanisms

### ☁️ AWS Bedrock Integration Guide
Complete AWS Bedrock integration guide: [AI Model Guidance.md](./AI-Model-Guidance.md)

This document includes:
- 🎯 Supported AI models (Claude Sonnet 4.5, Qwen 3, DeepSeek 3.1)
- ⚙️ Detailed configuration steps and account setup
- 🔐 API Key acquisition and authentication methods
- 📊 API call chain sequence diagrams
- ❓ Frequently Asked Questions (FAQ)
- 🔧 Troubleshooting guide


## Getting Started

### Prerequisites
- Node.js 18+ and pnpm
- Python 3.10+ and uv

### Install
```bash
# install JS deps and sync Python env
pnpm run install:all
```

### Development
By default, the workspace scripts launch:
- Backend on port 5611
- Frontend on port 5621

Start both dev servers:
```bash
pnpm run dev
```
Open:
- Frontend: http://localhost:5621
- Backend WS: ws://localhost:5611/ws

Important: The frontend source is currently configured for port  5621. To use the workspace defaults (5611), update the following in frontend/app/main.tsx:
- WebSocket URL: ws://localhost:5611/ws
- API_BASE: http://127.0.0.1:5611

Alternatively, run the backend on  5621:
```bash
# from repo root
cd backend
uv sync
uv run uvicorn main:app --reload --port  5621 --host 0.0.0.0
```

### Build
```bash
# build frontend; backend has no dedicated build step
pnpm run build
```
Static assets for the frontend are produced by Vite. The backend is a standard FastAPI app that can be run with Uvicorn or any ASGI server.



## License
MIT

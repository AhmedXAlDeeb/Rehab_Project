# React Frontend Bootstrap Guide (Vite + TypeScript)

This frontend is built to communicate with:
- integration_service on port 8001 (forward + bridge mode)
- classification_service on port 8000 (direct mode)
- simulation WebSocket server on port 8765

## 1) Setup Commands

Run from the workspace root:

```powershell
pnpm create vite@latest react-control-frontend --template react-ts --yes
pnpm --dir .\react-control-frontend add axios react-use-websocket zod @mui/material @emotion/react @emotion/styled @mui/icons-material
```

Development and production:

```powershell
pnpm --dir .\react-control-frontend dev
pnpm --dir .\react-control-frontend build
pnpm --dir .\react-control-frontend preview
```

## 2) Project Structure

```text
src/
  components/
    GestureStreamPanel.tsx
    SignalSenderCard.tsx
  hooks/
    useGestureWebSocket.ts
  services/
    httpClients.ts
    inferenceApi.ts
  theme/
    appTheme.ts
  types/
    api.ts
  utils/
    signal.ts
  App.tsx
  index.css
  main.tsx
```

## 3) Vite Proxy Configuration

Proxy is configured in vite.config.ts:
- /api -> http://localhost:8001 (rewritten to remove /api)
- /directapi -> http://localhost:8000 (rewritten to remove /directapi)

This avoids CORS issues during browser development.

## 4) Core Implementation

- Signal sender:
  - src/services/inferenceApi.ts
  - src/components/SignalSenderCard.tsx
  - src/utils/signal.ts
  - Sends strict 12x400 mock signal matrix to:
    - /api/forward_signal (integration mode)
    - /directapi/predict (direct mode)

- WebSocket listener:
  - src/hooks/useGestureWebSocket.ts
  - src/components/GestureStreamPanel.tsx
  - Connects to ws://localhost:8765
  - Parses and displays real-time gesture events

## 5) App Assembly

App composition is in src/App.tsx and includes:
- mode-aware single-shot signal dispatch card
- live WebSocket stream panel
- last inference summary chips

Theme and baseline setup are in:
- src/theme/appTheme.ts
- src/main.tsx

## Optional Simulator Bridge Broadcast Patch

To support real-time listener clients, the WebSocket bridge server now broadcasts received gestures to all connected clients while keeping sender acknowledgment unchanged.

Updated file:
- simulation-frontend/bridge/ws_server.py

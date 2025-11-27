# ArbiterAI Celestial - Desktop App

A stunning desktop application for ArbiterAI with a celestial theme.

## 🌌 Features

- **Celestial Theme**: Cosmic purple/pink/blue gradients with animated stars
- **Glassmorphism UI**: Modern frosted glass effects
- **Custom Titlebar**: Frameless window with custom controls
- **WebSocket Integration**: Real-time connection to ArbiterAI backend
- **Auto-reconnect**: Automatic reconnection on disconnect

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Run the app
npm start

# Build for distribution
npm run build
```

## 📋 Requirements

- Node.js 16+
- ArbiterAI backend running on `ws://localhost:8000/ws`

## 🎨 Design

- Deep space background (#0a0118)
- Animated 4-pointed stars
- Glassmorphism cards with backdrop blur
- Cosmic gradients and glow effects
- Smooth animations and transitions

## 🔌 Backend Connection

The app connects to the ArbiterAI WebSocket server at `ws://localhost:8000/ws`. Make sure the backend is running before launching the app.

## 📦 Build

The app can be packaged for Linux using electron-builder:

```bash
npm run build
```

This will create AppImage and .deb packages in the `dist/` directory.

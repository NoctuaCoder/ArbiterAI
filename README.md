# 🦉 ArbiterAI - Autonomous Code Agent

<div align="center">

![ArbiterAI Banner](https://img.shields.io/badge/AI-Code_Agent-blueviolet?style=for-the-badge&logo=openai)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)
![Ollama](https://img.shields.io/badge/Ollama-Powered-000000?style=for-the-badge)

**Um agente de código autônomo que planeja, executa e entrega soluções em tempo real.**

[🚀 Quick Start](#-quick-start) • [📖 Docs](#-documentation) • [🎯 Features](#-features) • [🐳 Docker](#-docker-deployment)

</div>

---

## 🎯 O Que É ArbiterAI?

**ArbiterAI** é um agente de código inteligente inspirado em assistentes como **Cursor**, **Copilot** e **Antigravity**. Ele usa **LLMs locais** (via Ollama) para:

1. 🧠 **Planejar** tarefas de programação em etapas detalhadas
2. ⚙️ **Executar** cada etapa com simulação realista
3. 📡 **Transmitir** resultados em tempo real via WebSocket
4. 💬 **Interagir** através de uma interface de chat moderna

**Diferencial**: 100% local, sem APIs pagas, sem limites de tokens, sem censura.

---

## ✨ Features

### Backend (Python + FastAPI)
- 🦾 **SimpleAgent**: Classe de agente com integração Ollama
- 🌐 **WebSocket Server**: Comunicação em tempo real
- 🐳 **Docker Ready**: Detecção inteligente de rede (host.docker.internal)
- 🔄 **Auto-Reconnect**: Lógica de reconexão automática
- 📊 **Health Checks**: Endpoints de monitoramento

### Frontend (React + TypeScript)
- 💬 **Chat Interface**: UI moderna e responsiva
- 🎨 **Tailwind CSS**: Design system premium
- 🔌 **WebSocket Client**: Conexão em tempo real
- 📱 **Responsive**: Mobile-first design
- 🎭 **Status Tracking**: Idle → Planning → Executing

### Deployment
- 🐳 **Docker Compose**: Orquestração simplificada
- 🐧 **Linux Compatible**: Testado em Arch, Ubuntu, Debian
- 🍎 **Mac/Windows**: Suporte via Docker Desktop
- 🔧 **Environment Vars**: Configuração flexível

---

## 🚀 Quick Start

### Pré-requisitos

```bash
# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Baixar um modelo (escolha um)
ollama pull llama2          # Geral
ollama pull deepseek-coder  # Especializado em código
ollama pull codellama       # Code-focused

# Iniciar Ollama
ollama serve
```

### Opção 1: Docker Compose (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/NoctuaCoder/ArbiterAI.git
cd ArbiterAI

# Configure o modelo (opcional)
export OLLAMA_MODEL=deepseek-coder

# Inicie o backend
docker-compose up -d

# Inicie o frontend
cd frontend
npm install
npm run dev
```

Acesse: **http://localhost:5173** 🎉

### Opção 2: Desenvolvimento Local

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python websocket_server.py

# Frontend (novo terminal)
cd frontend
npm install
npm run dev
```

---

## 🎮 Como Usar

1. **Abra** `http://localhost:5173`
2. **Digite** uma tarefa de programação:
   ```
   Create a Python REST API with FastAPI for user management
   ```
3. **Observe** o agente:
   - 🧠 Gerar um plano detalhado
   - ⚙️ Executar cada etapa
   - 📊 Mostrar resultados em tempo real
   - ✅ Concluir a tarefa

---

## 🏗️ Arquitetura

```
┌─────────────────┐      WebSocket      ┌──────────────────┐
│  React Frontend │ ◄─────────────────► │  FastAPI Backend │
│   (Port 5173)   │   ws://localhost    │   (Port 8000)    │
└─────────────────┘       :8000/ws       └──────────────────┘
                                                  │
                                                  │ HTTP
                                                  ▼
                                         ┌──────────────────┐
                                         │  Ollama Server   │
                                         │  (Port 11434)    │
                                         │  [DeepSeek/Llama]│
                                         └──────────────────┘
```

### Fluxo de Execução

1. **User** → Envia prompt via interface
2. **Frontend** → Transmite via WebSocket
3. **Backend** → Chama `agent.plan(task)`
4. **Ollama** → Gera plano com LLM
5. **Backend** → Executa cada step com `agent.execute_step()`
6. **Frontend** → Recebe e exibe resultados em tempo real

---

## 🐳 Docker Deployment

### Para Mac/Windows (Docker Desktop)

```bash
docker-compose up -d
```

O agente **detecta automaticamente** `host.docker.internal`.

### Para Linux

```bash
# Opção 1: Gateway IP
docker run -d --name arbiter-backend -p 8000:8000 \
  -e OLLAMA_URL=http://172.17.0.1:11434/api/generate \
  arbiterai-backend

# Opção 2: Host Network (mais simples)
docker run -d --name arbiter-backend --network host arbiterai-backend
```

### Verificação

```bash
# Logs do container
docker logs arbiter-backend

# Procure por:
# 🦉 SimpleAgent initialized with Ollama URL: http://host.docker.internal:11434/api/generate

# Health check
curl http://localhost:8000/health
# {"status":"healthy"}
```

---

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# Backend (.env ou export)
OLLAMA_URL=http://localhost:11434/api/generate  # URL do Ollama
OLLAMA_MODEL=deepseek-coder                     # Modelo a usar

# Frontend (src/components/AgentProvider.tsx)
wsUrl='ws://localhost:8000/ws'  # WebSocket URL
```

### Modelos Recomendados

| Modelo | Tamanho | Uso | Performance |
|--------|---------|-----|-------------|
| `llama2` | 7B | Geral | ⭐⭐⭐ |
| `deepseek-coder` | 6.7B | **Código** | ⭐⭐⭐⭐⭐ |
| `codellama` | 7B | Código | ⭐⭐⭐⭐ |
| `mistral` | 7B | Geral | ⭐⭐⭐⭐ |

**Recomendação**: Use `deepseek-coder` para melhor qualidade em tarefas de programação.

---

## 📁 Estrutura do Projeto

```
ArbiterAI/
├── backend/
│   ├── agent_framework.py      # 🧠 Classe SimpleAgent
│   ├── websocket_server.py     # 🌐 FastAPI WebSocket
│   ├── requirements.txt        # 📦 Dependências Python
│   ├── Dockerfile             # 🐳 Container config
│   └── .env.example           # ⚙️ Exemplo de config
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AgentProvider.tsx  # 🔌 WebSocket Context
│   │   │   └── Home.tsx          # 💬 Chat Interface
│   │   ├── App.tsx               # 🎯 Main App
│   │   └── main.tsx              # 🚀 Entry Point
│   ├── package.json              # 📦 Dependências Node
│   └── vite.config.ts            # ⚡ Vite Config
├── docker-compose.yml            # 🐳 Orquestração
└── README.md                     # 📖 Este arquivo
```

---

## 🛠️ Desenvolvimento

### Backend

```bash
cd backend

# Testar agent framework
python agent_framework.py

# Rodar servidor com reload
uvicorn websocket_server:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Dev server com HMR
npm run dev

# Build para produção
npm run build

# Preview do build
npm run preview
```

---

## 🐛 Troubleshooting

### Backend não conecta ao Ollama

```bash
# Verificar se Ollama está rodando
curl http://localhost:11434/api/tags

# Se não estiver, inicie
ollama serve

# Verificar logs do container
docker logs arbiter-backend
```

### Frontend não conecta ao WebSocket

```bash
# Verificar se backend está rodando
curl http://localhost:8000/health

# Verificar console do browser (F12)
# Procure por erros de WebSocket
```

### Porta já em uso

```bash
# Encontrar processo usando porta 8000
lsof -ti:8000 | xargs kill -9

# Ou use porta diferente
docker run -p 8001:8000 arbiterai-backend
```

---

## 🎯 Roadmap

- [ ] Execução real de código (sandbox)
- [ ] Suporte a múltiplos modelos simultâneos
- [ ] Histórico de conversas persistente
- [ ] Exportar código gerado
- [ ] Integração com Git
- [ ] Plugins e extensões
- [ ] API REST além do WebSocket
- [ ] Autenticação e multi-usuário

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se livre para:

1. 🍴 Fork o projeto
2. 🌿 Criar uma branch (`git checkout -b feature/amazing`)
3. 💾 Commit suas mudanças (`git commit -m 'Add amazing feature'`)
4. 📤 Push para a branch (`git push origin feature/amazing`)
5. 🎉 Abrir um Pull Request

---

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

## 🙏 Agradecimentos

- **Ollama** - Por tornar LLMs locais acessíveis
- **FastAPI** - Framework web moderno e rápido
- **React** - Biblioteca UI poderosa
- **Antigravity** - Inspiração para o design do agente

---

<div align="center">

**Feito com 🦉 por [NoctuaCoder](https://github.com/NoctuaCoder)**

⭐ Se este projeto te ajudou, deixe uma estrela!

[Report Bug](https://github.com/NoctuaCoder/ArbiterAI/issues) • [Request Feature](https://github.com/NoctuaCoder/ArbiterAI/issues)

</div>

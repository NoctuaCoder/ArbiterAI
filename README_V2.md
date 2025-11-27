# 🦉 ArbiterAI 2.0 - The Executor

<div align="center">

![Version](https://img.shields.io/badge/version-2.0-blueviolet?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)
![Ollama](https://img.shields.io/badge/Ollama-Powered-000000?style=for-the-badge)

**Autonomous code agent that EXECUTES real tasks, FIXES its own errors, and BUILDS complete projects.**

[🚀 Quick Start](#-quick-start) | [⚡ What's New in 2.0](#-whats-new-in-20) | [📖 Docs](#-documentation)

</div>

---

## ⚡ What's New in 2.0

### 🔥 Real Execution
- **No more simulation** - Executes actual shell commands, creates real files
- **Toolbox System** - Shell executor, file manager, web fetcher
- **Safety First** - Whitelist/blacklist, workspace isolation, timeouts

### 🧠 Autonomous Reflection
- **Self-Correction** - Detects errors and generates correction plans
- **Retry Loop** - Automatically retries with improved approach (max 3 attempts)
- **Learning** - Maintains execution history and context

### 💾 Project Memory
- **Persistent Context** - Remembers all files in the project
- **Smart Editing** - Can modify existing files intelligently
- **Full State** - Tracks execution history, errors, and successes

---

## 🎯 Capabilities

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Task Planning | ✅ | ✅ |
| Code Generation | ✅ Simulated | ✅ **Real** |
| File Operations | ❌ | ✅ **Create/Edit/Delete** |
| Shell Commands | ❌ | ✅ **Execute** |
| Error Handling | ❌ | ✅ **Auto-Fix** |
| Project Memory | ❌ | ✅ **Full Context** |
| Web Requests | ❌ | ✅ **HTTP Client** |

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull DeepSeek Coder (recommended for code tasks)
ollama pull deepseek-coder

# Start Ollama
ollama serve
```

### Run ArbiterAI 2.0

```bash
# Clone repository
git clone https://github.com/NoctuaCoder/ArbiterAI.git
cd ArbiterAI

# Start backend (v2.0)
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python websocket_server_v2.py

# Start frontend (new terminal)
cd frontend
npm install
npm run dev
```

Access at **http://localhost:5173** 🎉

---

## 💡 Example Usage

### Simple Task
```
Task: "Create a Python hello world script"

Result:
✅ hello.py created
✅ Script tested and working
```

### Complex Task with Error Recovery
```
Task: "Create a React component with TypeScript"

Flow:
1. 🧠 Plans: Install deps → Create component → Test
2. ❌ Error: "npm not found"
3. 🤔 Reflects: Realizes Node.js needed
4. 🔧 Corrects: Install Node → Retry npm install
5. ✅ Success: Component created
```

### Multi-File Project
```
Task: "Build a FastAPI REST API with 3 endpoints"

Result:
📁 main.py (API routes)
📁 models.py (data models)
📁 requirements.txt (dependencies)
📁 README.md (documentation)
✅ All files created and tested
```

---

## 🏗️ Architecture

```
┌─────────────────┐      WebSocket      ┌──────────────────┐
│  React Frontend │ ◄─────────────────► │  FastAPI Backend │
│   (Port 5173)   │   Real-time Stream  │   (Port 8000)    │
└─────────────────┘                      └──────────────────┘
                                                  │
                                                  ▼
                                         ┌──────────────────┐
                                         │ AutonomousAgent  │
                                         │  - Tool Selection│
                                         │  - Execution     │
                                         │  - Reflection    │
                                         └──────────────────┘
                                                  │
                                    ┌─────────────┼─────────────┐
                                    ▼             ▼             ▼
                              ┌──────────┐  ┌──────────┐  ┌──────────┐
                              │  Shell   │  │   File   │  │   Web    │
                              │ Executor │  │ Manager  │  │ Fetcher  │
                              └──────────┘  └──────────┘  └──────────┘
                                    │             │             │
                                    └─────────────┴─────────────┘
                                              ▼
                                    /tmp/arbiter_workspace/
```

---

## 🛠️ Toolbox

### ShellExecutor
```python
# Executes real commands
toolbox.execute_tool("shell", command="python script.py")

# Safety features:
- Whitelist: npm, python, git, docker, etc.
- Blacklist: rm -rf /, fork bombs, etc.
- Timeout: 30 seconds max
- Workspace: Isolated directory
```

### FileManager
```python
# Create/edit/delete files
toolbox.execute_tool("write_file", 
    filepath="app.py",
    content="print('Hello')")

# Safety features:
- Path restriction: Only within workspace
- No path traversal (../ blocked)
- Automatic directory creation
```

### WebFetcher
```python
# HTTP requests
toolbox.execute_tool("web_fetch",
    url="https://api.github.com/repos/...",
    method="GET")

# Features:
- GET/POST support
- JSON handling
- Timeout protection
```

---

## 🔄 Reflection Loop

When an error occurs, ArbiterAI 2.0 doesn't give up:

```python
1. Execute step
2. Error detected? 
   → YES: 
     a. Analyze error
     b. Generate correction plan
     c. Retry with new approach
   → NO: Continue to next step
3. Max retries (3) reached?
   → Report partial completion
```

**Example**:
```
Original Plan:
1. npm install react
2. Create component.jsx

Error: "npm: command not found"

Reflection:
"npm is not installed. Need to install Node.js first."

Correction Plan:
1. Install Node.js
2. Verify npm is available
3. npm install react
4. Create component.jsx

Result: ✅ Success after reflection
```

---

## 🔒 Safety

### Workspace Isolation
- All operations restricted to `/tmp/arbiter_workspace`
- Cannot access system files
- Path traversal blocked

### Command Whitelist
```python
ALLOWED = [
    'npm', 'node', 'python', 'pip',
    'git', 'docker', 'ls', 'cat', 'mkdir'
]
```

### Resource Limits
- **Timeout**: 30s per command
- **Output**: 10KB max
- **Retries**: 3 attempts max

---

## 📊 Comparison

| Feature | Cursor | GitHub Copilot | **ArbiterAI 2.0** |
|---------|--------|----------------|-------------------|
| Code Suggestions | ✅ | ✅ | ✅ |
| Auto-completion | ✅ | ✅ | ❌ |
| **Real Execution** | ❌ | ❌ | ✅ |
| **Error Reflection** | ❌ | ❌ | ✅ |
| **Project Memory** | ❌ | ❌ | ✅ |
| **100% Local** | ❌ | ❌ | ✅ |
| **No API Costs** | ❌ | ❌ | ✅ |
| **No Censorship** | ❌ | ❌ | ✅ |

---

## 🎮 Usage

### Via Web Interface
1. Open `http://localhost:5173`
2. Enter task: "Create a Python web scraper"
3. Watch agent:
   - 🧠 Generate plan
   - ⚙️ Execute each step
   - ❌ Detect errors
   - 🤔 Reflect and correct
   - ✅ Complete task

### Via API (Coming Soon)
```python
import requests

response = requests.post("http://localhost:8000/api/execute", json={
    "task": "Create a REST API with FastAPI"
})
```

---

## 📁 Project Structure

```
ArbiterAI/
├── backend/
│   ├── toolbox.py                 # 🔧 Real execution tools
│   ├── agent_framework_v2.py      # 🧠 Autonomous agent
│   ├── websocket_server_v2.py     # 🌐 WebSocket + reflection loop
│   ├── agent_framework.py         # (v1.0 - deprecated)
│   └── websocket_server.py        # (v1.0 - deprecated)
├── frontend/                      # 💬 React UI
└── docker-compose.yml             # 🐳 Deployment
```

---

## 🚧 Roadmap

- [ ] **Sandbox Execution** - Docker-based isolation
- [ ] **Multi-Agent** - Parallel task execution
- [ ] **Git Integration** - Auto-commit changes
- [ ] **Plugin System** - Custom tools
- [ ] **API Mode** - REST API alongside WebSocket
- [ ] **Persistent Projects** - Save/load project state
- [ ] **Code Review** - AI-powered review before execution

---

## 🤝 Contributing

We welcome contributions! Areas of focus:
- Additional tools (database, cloud, etc.)
- Enhanced safety mechanisms
- Frontend improvements
- Test coverage
- Documentation

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

## 🙏 Credits

- **Ollama** - Local LLM infrastructure
- **DeepSeek Coder** - Specialized code model
- **FastAPI** - Modern web framework
- **React** - UI library

---

<div align="center">

**Built with 🦉 by [NoctuaCoder](https://github.com/NoctuaCoder)**

**ArbiterAI 2.0 - Where Code Meets Autonomy**

⭐ Star this repo if you believe in autonomous AI!

[Report Bug](https://github.com/NoctuaCoder/ArbiterAI/issues) • [Request Feature](https://github.com/NoctuaCoder/ArbiterAI/issues) • [Discussions](https://github.com/NoctuaCoder/ArbiterAI/discussions)

</div>

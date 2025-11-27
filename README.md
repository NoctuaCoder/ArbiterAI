# 🦉 ArbiterAI v4.0 - The Docker for AI Code Agents

<div align="center">

![Version](https://img.shields.io/badge/version-4.0-blueviolet?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Docker](https://img.shields.io/badge/Docker-Required-2496ED?style=for-the-badge&logo=docker)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production_Ready-success?style=for-the-badge)

**The ONLY platform combining real code execution, Docker isolation, plugin extensibility, and Git integration. 100% local, zero API costs.**

[🚀 Quick Start](#-quick-start) | [⚡ What Makes Us Unique](#-what-makes-us-unique) | [🔌 Plugin System](#-plugin-system) | [📖 Documentation](#-documentation)

</div>

---

> **⚠️ ORIGINAL PROJECT NOTICE**
> 
> **ArbiterAI** is an original work by [NoctuaCoder](https://github.com/NoctuaCoder)  
> **First Published**: November 27, 2025  
> **Original Repository**: https://github.com/NoctuaCoder/ArbiterAI  
> **Project ID**: ARBITER-2025-NOCTUACODER-PLATFORM
> 
> This project is protected under MIT License with attribution requirements.  
> Any use, modification, or distribution must credit the original author.  
> See [NOTICE](NOTICE) file for full copyright information.

---

## ⚡ What Makes Us Unique

**ArbiterAI is the ONLY platform that combines ALL of these:**

| Feature | GitHub Copilot | Cursor | Devin | **ArbiterAI** |
|---------|----------------|--------|-------|---------------|
| Code Suggestions | ✅ | ✅ | ✅ | ✅ |
| **Real Execution** | ❌ | ❌ | ✅ | ✅ |
| **Docker Isolation** | ❌ | ❌ | ❌ | **✅** |
| **Plugin System** | ❌ | ❌ | ❌ | **✅** |
| **100% Local** | ❌ | ❌ | ❌ | **✅** |
| **Git Integration** | ⚠️ | ⚠️ | ⚠️ | **✅** |
| **Zero API Cost** | ❌ | ❌ | ❌ | **✅** |
| **Open Source** | ❌ | ❌ | ❌ | **✅** |

**Tagline**: *"The Docker for AI Code Agents"*

---

## 🎯 Key Features

### 🐳 Docker Sandbox (Enterprise Security)
- **Container Isolation**: Every command runs in ephemeral Docker containers
- **Resource Limits**: CPU (1 core), Memory (512MB) enforced
- **Non-Root Execution**: UID 1000 for security
- **Network Isolation**: Disabled by default
- **Auto-Cleanup**: Containers removed after execution

### 🔌 Plugin System (Unlimited Extensibility)
- **Auto-Discovery**: Plugins loaded from `plugins/` directory
- **Dynamic Loading**: No core modifications needed
- **Permission System**: Filesystem, network, database, cloud, shell
- **Community-Ready**: Easy plugin development

### 🔄 Git Integration (Team Member Capabilities)
- **Local Operations**: init, status, add, commit, log, diff, branch, checkout
- **Remote Operations**: clone, push, pull, fetch, remote management
- **State Tracking**: Comprehensive repository awareness
- **Workflow Automation**: Complete Git workflow support

### 💾 Built-in Plugins
- **Shell Plugin**: Secure command execution (Docker-based)
- **Database Plugin**: SQLite operations with SQL injection prevention
- **Git Plugin**: Full version control integration

---

## 🚀 Quick Start

### Prerequisites

```bash
# 1. Install Docker
curl -fsSL https://get.docker.com | sh

# 2. Install Ollama (local LLM)
curl -fsSL https://ollama.com/install.sh | sh

# 3. Pull DeepSeek Coder model
ollama pull deepseek-coder

# 4. Start Ollama
ollama serve
```

### Installation

```bash
# Clone repository
git clone https://github.com/NoctuaCoder/ArbiterAI.git
cd ArbiterAI

# Build Docker sandbox image
cd backend
chmod +x build_sandbox.sh
./build_sandbox.sh

# Install Python dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start backend
python websocket_server_v2.py
```

### Frontend (Optional)

```bash
# In new terminal
cd frontend
npm install
npm run dev
```

Access at **http://localhost:5173** 🎉

---

## 💡 Example Usage

### Simple Task
```
User: "Create a Python hello world script"

Agent:
✅ Initialized workspace
✅ Created hello.py
✅ Executed script successfully
✅ Output: Hello, World!
```

### Git Workflow
```
User: "Clone repo, create feature branch, make changes, commit, and push"

Agent:
✅ Cloned repository
✅ Created branch: feature/new-feature
✅ Made changes to code
✅ Staged files
✅ Committed: "feat: implement new feature"
✅ Pushed to origin/feature/new-feature
```

### Database Operations
```
User: "Create users table and insert sample data"

Agent:
✅ Created database.db
✅ Executed: CREATE TABLE users (id, name, email)
✅ Inserted 3 sample users
✅ Query result:
   id | name  | email
   1  | Alice | alice@example.com
   2  | Bob   | bob@example.com
   3  | Carol | carol@example.com
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
                                         │  - Planning      │
                                         │  - Tool Selection│
                                         │  - Reflection    │
                                         └──────────────────┘
                                                  │
                                                  ▼
                                         ┌──────────────────┐
                                         │    Toolbox       │
                                         │  + PluginManager │
                                         └──────────────────┘
                                                  │
                                    ┌─────────────┼─────────────┐
                                    ▼             ▼             ▼
                              ┌──────────┐  ┌──────────┐  ┌──────────┐
                              │  Shell   │  │    Git   │  │ Database │
                              │  Plugin  │  │  Plugin  │  │  Plugin  │
                              └──────────┘  └──────────┘  └──────────┘
                                    │             │             │
                                    └─────────────┴─────────────┘
                                              ▼
                                    ┌──────────────────┐
                                    │  Docker Sandbox  │
                                    │  (Isolated Exec) │
                                    └──────────────────┘
```

---

## 🔌 Plugin System

### Creating a Plugin

```python
# plugins/my_plugin.py

from plugin_interface import ArbiterPlugin, PluginMetadata, PluginResult

class MyPlugin(ArbiterPlugin):
    @property
    def metadata(self):
        return PluginMetadata(
            name="my_plugin",
            version="1.0.0",
            author="Your Name",
            description="What your plugin does"
        )
    
    def execute(self, **kwargs):
        # Your logic here
        return PluginResult(
            success=True,
            output="Result"
        )
    
    def describe(self):
        return {
            "name": "my_plugin",
            "description": "Detailed description for LLM",
            "parameters": {"param1": "description"},
            "examples": ["Example usage"]
        }
```

**That's it!** Plugin is auto-discovered on next startup.

### Available Plugins

- **Shell Plugin**: Execute commands in Docker containers
- **Database Plugin**: SQLite operations
- **Git Plugin**: Version control operations

### Community Plugins (Coming Soon)

- Cloud Plugin (AWS S3, GCP, Azure)
- Testing Plugin (pytest, jest)
- CI/CD Plugin (GitHub Actions, GitLab CI)
- Monitoring Plugin (Prometheus, Grafana)

---

## 🔒 Security

### Docker Sandbox
- **Isolation**: Complete process/network/filesystem isolation
- **Resource Limits**: Prevents DoS attacks
- **Non-Root**: UID 1000 execution
- **Ephemeral**: Containers destroyed after use
- **Network**: Disabled by default

### Command Validation
- **Whitelist**: Only allowed commands execute
- **Blacklist**: Dangerous patterns blocked
- **Timeout**: 30s max per command
- **Workspace**: Path traversal prevented

### Plugin Security
- **Permission System**: Plugins declare required permissions
- **Input Validation**: All inputs validated
- **Sandboxing**: Plugins run in isolated environment

---

## 📊 Code Statistics

| Component | Lines of Code | Status |
|-----------|---------------|--------|
| Docker Sandbox | 350 | ✅ Production |
| Plugin System | 550 | ✅ Production |
| Database Plugin | 280 | ✅ Production |
| Shell Plugin | 215 | ✅ Production |
| Git Plugin | 800 | ✅ Production |
| **Total** | **~2,200** | **✅ Ready** |

---

## 🗺️ Roadmap

### ✅ Completed (v4.0)
- [x] Docker Sandbox (Enterprise security)
- [x] Plugin System (Unlimited extensibility)
- [x] Git Integration (Team member capabilities)
- [x] Database Plugin (SQLite operations)
- [x] Shell Plugin (Secure execution)

### 🎯 Next (v4.1)
- [ ] UX/Frontend Enhancement (file visualization, execution history)
- [ ] Plugin Documentation (developer guide, templates)
- [ ] Performance Optimization (caching, lazy loading)
- [ ] GitHub API Integration (PRs, issues)

### 🚀 Future (v5.0)
- [ ] Multi-Agent Orchestration
- [ ] Plugin Marketplace
- [ ] Enterprise Features (SSO, RBAC)
- [ ] Cloud Deployment Options

---

## 💰 Pricing (Planned)

### Free Tier (Open Source)
- ✅ Core platform
- ✅ Basic plugins
- ✅ Community support
- ✅ Self-hosted

### Pro Tier ($49/month)
- ✅ Advanced plugins (Cloud, Testing, CI/CD)
- ✅ Priority support
- ✅ Plugin marketplace access
- ✅ Multi-agent orchestration

### Enterprise ($499/month)
- ✅ On-premise deployment
- ✅ Custom plugin development
- ✅ SLA 99.9%
- ✅ Dedicated support
- ✅ Team collaboration
- ✅ SSO/SAML integration

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas of Focus
- Plugin development
- Frontend improvements
- Documentation
- Testing
- Performance optimization

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

**Attribution Required**: Any use must credit [NoctuaCoder](https://github.com/NoctuaCoder) and link to the original repository.

---

## 🙏 Credits

- **Ollama** - Local LLM infrastructure
- **DeepSeek Coder** - Specialized code model
- **Docker** - Container platform
- **FastAPI** - Modern web framework
- **React** - UI library

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/NoctuaCoder/ArbiterAI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/NoctuaCoder/ArbiterAI/discussions)
- **Email**: Contact through GitHub profile

---

<div align="center">

**Built with 🦉 by [NoctuaCoder](https://github.com/NoctuaCoder)**

**ArbiterAI v4.0 - Where Security Meets Extensibility**

⭐ Star this repo if you believe in secure, extensible AI agents!

[Report Bug](https://github.com/NoctuaCoder/ArbiterAI/issues) • [Request Feature](https://github.com/NoctuaCoder/ArbiterAI/issues) • [Discussions](https://github.com/NoctuaCoder/ArbiterAI/discussions)

---

**© 2025 NoctuaCoder. Original work protected under MIT License.**

**Project ID**: ARBITER-2025-NOCTUACODER-PLATFORM

</div>

# Docker Sandbox Setup Guide

## Prerequisites

- Docker 20.10+ installed
- User in docker group
- 2GB free disk space

## Quick Start

### 1. Build Sandbox Image

```bash
cd backend
./build_sandbox.sh
```

This will:
- Build the `arbiter-sandbox:latest` image
- Test Python and Node.js availability
- Verify the sandbox is working

### 2. Enable Docker Sandbox

```bash
# Set environment variable
export USE_DOCKER_SANDBOX=true

# Run ArbiterAI
python websocket_server_v2.py
```

### 3. Verify

Look for this message in the logs:
```
🐳 Docker sandbox enabled for shell execution
```

---

## Configuration

### Environment Variables

```bash
# Enable/disable Docker sandbox
export USE_DOCKER_SANDBOX=true   # Use Docker (default: false)

# Ollama configuration
export OLLAMA_URL=http://localhost:11434/api/generate
export OLLAMA_MODEL=deepseek-coder
```

### Resource Limits

Default limits (configurable in `sandbox_manager.py`):
- **CPU**: 1 core
- **Memory**: 512MB
- **Timeout**: 30 seconds per command
- **Network**: Disabled by default

---

## Docker Setup (Linux)

### Install Docker

```bash
# Arch Linux
sudo pacman -S docker
sudo systemctl start docker
sudo systemctl enable docker

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo systemctl enable docker
```

### Add User to Docker Group

```bash
sudo usermod -aG docker $USER
newgrp docker  # Activate group without logout

# Verify
docker ps
```

---

## Troubleshooting

### Error: "Cannot connect to Docker daemon"

**Solution**:
```bash
# Start Docker service
sudo systemctl start docker

# Check status
sudo systemctl status docker
```

### Error: "Permission denied"

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again, or:
newgrp docker
```

### Error: "Image not found"

**Solution**:
```bash
# Rebuild sandbox image
cd backend
./build_sandbox.sh
```

### Fallback to Direct Execution

If Docker fails, ArbiterAI automatically falls back to direct execution:
```
⚠️ Docker sandbox failed to initialize: ...
   Falling back to direct execution
```

This ensures the agent continues working even without Docker.

---

## Security Features

### Container Isolation
- Separate process namespace
- Separate network namespace  
- Separate filesystem

### Non-Root Execution
- User `arbiter` (UID 1000)
- No sudo access
- Limited capabilities

### Resource Limits
- CPU: 1 core maximum
- Memory: 512MB maximum
- Disk: Limited to workspace volume
- Network: Disabled by default

### Ephemeral Containers
- Created per execution
- Automatically destroyed after use
- No persistent state between runs

---

## Testing

### Manual Test

```bash
cd backend
python sandbox_manager.py
```

Expected output:
```
=== Test 1: Simple Command ===
Success: True
Output: Hello from Docker!

=== Test 2: Python Code ===
Success: True
Output: Python in Docker!

=== Test 3: File Operations ===
Success: True
Output: test content

=== Test 4: Health Check ===
Sandbox healthy: True
```

### Integration Test

```bash
# Enable Docker
export USE_DOCKER_SANDBOX=true

# Test with toolbox
python -c "
from toolbox import Toolbox
tb = Toolbox(use_docker=True)
result = tb.execute_tool('shell', command='python --version')
print(f'Success: {result.success}')
print(f'Output: {result.output}')
print(f'Sandbox: {result.data.get(\"sandbox\")}')
"
```

Expected:
```
🐳 Docker sandbox enabled for shell execution
Success: True
Output: Python 3.11.x
Sandbox: docker
```

---

## Performance

### Container Startup Time
- **Cold start**: ~2-3 seconds (first run)
- **Warm start**: ~0.5 seconds (image cached)

### Resource Overhead
- **Memory**: +50MB per container
- **CPU**: Minimal overhead
- **Disk**: +200MB for base image

### Optimization Tips
- Keep image minimal (current: ~200MB)
- Pre-pull image on startup
- Use Alpine-based images for smaller size

---

## Advanced Configuration

### Custom Resource Limits

Edit `sandbox_manager.py`:
```python
sandbox = DockerSandbox(
    workspace_path="/tmp/workspace",
    cpu_limit=2.0,        # 2 CPU cores
    memory_limit="1g",    # 1GB RAM
    enable_network=True   # Enable network
)
```

### Enable Network Access

```python
# In sandbox_manager.py
sandbox = DockerSandbox(
    workspace_path="/tmp/workspace",
    enable_network=True  # Allow network requests
)
```

**Warning**: Enabling network reduces isolation.

### Custom Docker Image

```bash
# Build custom image
docker build -f Dockerfile.custom -t my-sandbox:latest .

# Use custom image
sandbox = DockerSandbox(
    workspace_path="/tmp/workspace",
    image="my-sandbox:latest"
)
```

---

## Comparison: Docker vs Direct

| Feature | Direct Execution | Docker Sandbox |
|---------|------------------|----------------|
| Security | ⚠️ Whitelist only | ✅ Full isolation |
| Performance | ✅ Fast | ⚠️ +0.5-3s overhead |
| Setup | ✅ None | ⚠️ Requires Docker |
| Resource Limits | ❌ None | ✅ CPU/Memory/Disk |
| Network Isolation | ❌ No | ✅ Yes |
| Production Ready | ⚠️ Dev only | ✅ Enterprise-grade |

**Recommendation**: Use Docker for production, direct for development.

---

## Next Steps

1. ✅ Build sandbox image
2. ✅ Enable Docker sandbox
3. ✅ Test execution
4. 🔄 Deploy to production
5. 🔄 Monitor performance
6. 🔄 Tune resource limits

---

<div align="center">

**Docker Sandbox: Enterprise-Grade Security**

*Transforming ArbiterAI from prototype to production*

</div>

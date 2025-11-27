# Contributing to ArbiterAI

Thank you for your interest in contributing to ArbiterAI! 🦉

We welcome contributions from the community and are excited to see what you'll build!

## 🌟 Ways to Contribute

- **Report Bugs**: Use the bug report template
- **Request Features**: Use the feature request template
- **Submit Plugins**: Use the plugin submission template
- **Improve Documentation**: Fix typos, add examples, clarify instructions
- **Write Code**: Fix bugs, implement features, optimize performance
- **Share Feedback**: Tell us what you think!

## 🚀 Getting Started

### 1. Fork the Repository

Click the "Fork" button at the top right of the repository page.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/ArbiterAI.git
cd ArbiterAI
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 4. Make Your Changes

- Follow the existing code style
- Add tests if applicable
- Update documentation
- Test your changes thoroughly

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: add amazing feature"
```

**Commit Message Format**:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

### 6. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 7. Create a Pull Request

Go to the original repository and click "New Pull Request".

## 🔌 Plugin Development

### Plugin Structure

```python
from plugin_interface import ArbiterPlugin, PluginMetadata, PluginResult

class MyPlugin(ArbiterPlugin):
    @property
    def metadata(self):
        return PluginMetadata(
            name="my_plugin",
            version="1.0.0",
            author="Your Name",
            description="What your plugin does",
            permissions=["filesystem", "network"]  # Required permissions
        )
    
    def execute(self, **kwargs):
        # Your plugin logic here
        return PluginResult(
            success=True,
            output="Result message",
            data={"key": "value"}  # Optional
        )
    
    def describe(self):
        return {
            "name": "my_plugin",
            "description": "Detailed description for LLM",
            "parameters": {
                "param1": "Parameter description"
            },
            "examples": [
                "Example usage 1",
                "Example usage 2"
            ]
        }
```

### Plugin Guidelines

- **Single Responsibility**: Each plugin should do one thing well
- **Error Handling**: Always handle errors gracefully
- **Documentation**: Provide clear descriptions and examples
- **Testing**: Include tests for your plugin
- **Security**: Request only necessary permissions
- **Performance**: Optimize for speed and resource usage

## 📝 Code Style

### Python
- Follow PEP 8
- Use type hints where applicable
- Write docstrings for functions and classes
- Keep functions small and focused

### JavaScript/React
- Use ES6+ features
- Follow Airbnb style guide
- Use functional components with hooks
- Write meaningful variable names

## 🧪 Testing

Before submitting a PR:

```bash
# Run tests (when available)
pytest

# Test Docker sandbox
cd backend
./build_sandbox.sh
python websocket_server_v2.py

# Test frontend
cd frontend
npm run dev
```

## 📖 Documentation

- Update README.md if adding new features
- Add inline comments for complex logic
- Create examples for new plugins
- Update CHANGELOG.md

## 🐛 Reporting Bugs

Use the bug report template and include:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Error logs/screenshots

## 💡 Requesting Features

Use the feature request template and include:
- Clear description of the feature
- Use case and problem it solves
- Proposed solution
- Priority level

## 🎯 Pull Request Guidelines

### Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### PR Description Should Include
- What changes were made
- Why the changes were necessary
- How to test the changes
- Screenshots/GIFs if UI changes
- Related issues (if any)

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Thanked in the community

## 📞 Getting Help

- **GitHub Discussions**: Ask questions
- **GitHub Issues**: Report problems
- **Discord** (coming soon): Chat with the community

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## 🌟 Thank You!

Every contribution, no matter how small, makes ArbiterAI better for everyone. We appreciate your time and effort!

**Happy Coding!** 🦉✨

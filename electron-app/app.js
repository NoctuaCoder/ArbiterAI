const { ipcRenderer } = require('electron');

// WebSocket connection
let ws = null;
let reconnectInterval = null;

// DOM elements
const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');

// Window controls
document.getElementById('minimize-btn').addEventListener('click', () => {
    ipcRenderer.send('window-minimize');
});

document.getElementById('maximize-btn').addEventListener('click', () => {
    ipcRenderer.send('window-maximize');
});

document.getElementById('close-btn').addEventListener('click', () => {
    ipcRenderer.send('window-close');
});

// WebSocket connection
function connect() {
    const wsUrl = 'ws://localhost:8000/ws';

    try {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('Connected to ArbiterAI');
            updateStatus('connected', 'Connected');
            clearInterval(reconnectInterval);
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                handleMessage(data);
            } catch (error) {
                console.error('Error parsing message:', error);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateStatus('disconnected', 'Connection error');
        };

        ws.onclose = () => {
            console.log('Disconnected from ArbiterAI');
            updateStatus('disconnected', 'Disconnected');

            // Attempt to reconnect
            reconnectInterval = setInterval(() => {
                updateStatus('connecting', 'Reconnecting...');
                connect();
            }, 3000);
        };
    } catch (error) {
        console.error('Connection error:', error);
        updateStatus('disconnected', 'Failed to connect');
    }
}

// Update connection status
function updateStatus(status, text) {
    statusDot.className = `status-dot ${status}`;
    statusText.textContent = text;
}

// Handle incoming messages
function handleMessage(data) {
    const messageType = data.type;

    switch (messageType) {
        case 'status':
            addStatusMessage(data.content);
            break;
        case 'agent':
            addAgentMessage(data.content);
            break;
        case 'result':
            addResultMessage(data);
            break;
        case 'reflection':
            addReflectionMessage(data);
            break;
        case 'complete':
            addCompleteMessage(data);
            break;
        case 'pong':
            console.log('Pong received');
            break;
        default:
            console.log('Unknown message type:', messageType);
    }
}

// Add user message
function addUserMessage(content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.innerHTML = `<div class="message-content">${escapeHtml(content)}</div>`;
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Add agent message
function addAgentMessage(content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent';

    // Parse markdown-style formatting
    const formattedContent = formatContent(content);
    messageDiv.innerHTML = `<div class="message-content">${formattedContent}</div>`;

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Add status message
function addStatusMessage(content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message status';
    messageDiv.innerHTML = `<div class="message-content">Status: ${escapeHtml(content)}</div>`;
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Add result message
function addResultMessage(data) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${data.success ? 'agent' : 'error'}`;

    let content = `<strong>Step ${data.stepNumber}/${data.totalSteps}:</strong> ${escapeHtml(data.step)}<br>`;

    if (data.output) {
        content += `<div class="code-block">${escapeHtml(data.output)}</div>`;
    }

    if (data.error) {
        content += `<div style="color: #ef4444; margin-top: 8px;">❌ Error: ${escapeHtml(data.error)}</div>`;
    }

    messageDiv.innerHTML = `<div class="message-content">${content}</div>`;
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Add reflection message
function addReflectionMessage(data) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent';
    messageDiv.innerHTML = `<div class="message-content">${formatContent(data.content)}</div>`;
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Add completion message
function addCompleteMessage(data) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent';
    messageDiv.innerHTML = `<div class="message-content">${formatContent(data.content)}</div>`;
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Format content (basic markdown-style)
function formatContent(content) {
    let formatted = escapeHtml(content);

    // Bold
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Code blocks
    formatted = formatted.replace(/```([\s\S]*?)```/g, '<div class="code-block">$1</div>');

    // Inline code
    formatted = formatted.replace(/`(.*?)`/g, '<code style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px;">$1</code>');

    // Line breaks
    formatted = formatted.replace(/\n/g, '<br>');

    return formatted;
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Scroll to bottom
function scrollToBottom() {
    messagesContainer.parentElement.scrollTop = messagesContainer.parentElement.scrollHeight;
}

// Send message
function sendMessage() {
    const message = messageInput.value.trim();

    if (!message || !ws || ws.readyState !== WebSocket.OPEN) {
        return;
    }

    // Add user message to UI
    addUserMessage(message);

    // Send to backend
    ws.send(JSON.stringify({
        type: 'task',
        content: message
    }));

    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
}

// Event listeners
sendBtn.addEventListener('click', sendMessage);

messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Auto-resize textarea
messageInput.addEventListener('input', () => {
    messageInput.style.height = 'auto';
    messageInput.style.height = messageInput.scrollHeight + 'px';
});

// Initialize connection
connect();

// Send ping every 30 seconds to keep connection alive
setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
    }
}, 30000);

import React, { useState, useRef, useEffect } from 'react';
import { useAgent } from './AgentProvider';
import { Send, Loader2, CheckCircle2, Circle, Trash2 } from 'lucide-react';

const Home: React.FC = () => {
    const { status, messages, isConnected, sendPrompt, clearMessages } = useAgent();
    const [input, setInput] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (input.trim() && status === 'idle') {
            sendPrompt(input.trim());
            setInput('');
        }
    };

    const getStatusColor = () => {
        switch (status) {
            case 'planning':
                return 'bg-blue-500';
            case 'executing':
                return 'bg-yellow-500';
            case 'idle':
                return isConnected ? 'bg-green-500' : 'bg-red-500';
            default:
                return 'bg-gray-500';
        }
    };

    const getStatusText = () => {
        if (!isConnected) return 'Disconnected';
        switch (status) {
            case 'planning':
                return 'Planning...';
            case 'executing':
                return 'Executing...';
            case 'idle':
                return 'Ready';
            default:
                return 'Unknown';
        }
    };

    const formatContent = (content: string) => {
        // Simple markdown-like formatting
        return content
            .split('\n')
            .map((line, i) => {
                // Bold text
                line = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                return <div key={i} dangerouslySetInnerHTML={{ __html: line || '<br/>' }} />;
            });
    };

    return (
        <div className="flex flex-col h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
            {/* Header */}
            <header className="bg-gray-800/50 backdrop-blur-sm border-b border-gray-700 px-6 py-4">
                <div className="max-w-6xl mx-auto flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="text-3xl">🦉</div>
                        <div>
                            <h1 className="text-2xl font-bold text-white">Anti-C Code Agent</h1>
                            <p className="text-sm text-gray-400">Powered by Ollama LLM</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        {/* Status Indicator */}
                        <div className="flex items-center gap-2">
                            <div className={`w-3 h-3 rounded-full ${getStatusColor()} animate-pulse`} />
                            <span className="text-sm text-gray-300">{getStatusText()}</span>
                        </div>

                        {/* Clear Button */}
                        {messages.length > 0 && (
                            <button
                                onClick={clearMessages}
                                className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-gray-300 transition-colors"
                                title="Clear messages"
                            >
                                <Trash2 size={18} />
                            </button>
                        )}
                    </div>
                </div>
            </header>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto px-6 py-8">
                <div className="max-w-4xl mx-auto space-y-4">
                    {messages.length === 0 && (
                        <div className="text-center py-12">
                            <div className="text-6xl mb-4">🦉</div>
                            <h2 className="text-2xl font-bold text-white mb-2">Welcome to Anti-C</h2>
                            <p className="text-gray-400">
                                Enter a coding task below and I'll create a plan and execute it for you.
                            </p>
                            <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
                                <button
                                    onClick={() => setInput('Create a Python function to calculate fibonacci numbers')}
                                    className="p-4 bg-gray-800 hover:bg-gray-700 rounded-lg text-left transition-colors border border-gray-700"
                                >
                                    <div className="text-sm text-gray-400 mb-1">Example</div>
                                    <div className="text-white">Calculate Fibonacci numbers</div>
                                </button>
                                <button
                                    onClick={() => setInput('Build a REST API with FastAPI')}
                                    className="p-4 bg-gray-800 hover:bg-gray-700 rounded-lg text-left transition-colors border border-gray-700"
                                >
                                    <div className="text-sm text-gray-400 mb-1">Example</div>
                                    <div className="text-white">Build a REST API</div>
                                </button>
                            </div>
                        </div>
                    )}

                    {messages.map((message) => (
                        <div
                            key={message.id}
                            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div
                                className={`max-w-3xl rounded-lg px-4 py-3 ${message.type === 'user'
                                        ? 'bg-blue-600 text-white'
                                        : message.type === 'result'
                                            ? 'bg-gray-800 border border-gray-700 text-gray-100'
                                            : 'bg-gray-800 text-gray-100'
                                    }`}
                            >
                                {message.type === 'result' && (
                                    <div className="flex items-center gap-2 mb-2 text-sm text-gray-400">
                                        {message.success ? (
                                            <CheckCircle2 size={16} className="text-green-500" />
                                        ) : (
                                            <Circle size={16} className="text-gray-500" />
                                        )}
                                        {message.stepNumber && message.totalSteps && (
                                            <span>Step {message.stepNumber}/{message.totalSteps}</span>
                                        )}
                                    </div>
                                )}

                                <div className="whitespace-pre-wrap font-mono text-sm">
                                    {formatContent(message.content)}
                                </div>

                                <div className="text-xs text-gray-500 mt-2">
                                    {message.timestamp.toLocaleTimeString()}
                                </div>
                            </div>
                        </div>
                    ))}

                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input Area */}
            <div className="bg-gray-800/50 backdrop-blur-sm border-t border-gray-700 px-6 py-4">
                <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
                    <div className="flex gap-3">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder={
                                !isConnected
                                    ? 'Connecting to server...'
                                    : status !== 'idle'
                                        ? 'Agent is busy...'
                                        : 'Enter a coding task...'
                            }
                            disabled={!isConnected || status !== 'idle'}
                            className="flex-1 bg-gray-900 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed border border-gray-700"
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || !isConnected || status !== 'idle'}
                            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg px-6 py-3 flex items-center gap-2 transition-colors"
                        >
                            {status !== 'idle' ? (
                                <>
                                    <Loader2 size={20} className="animate-spin" />
                                    <span>Working...</span>
                                </>
                            ) : (
                                <>
                                    <Send size={20} />
                                    <span>Send</span>
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Home;

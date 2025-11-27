import React, { createContext, useContext, useEffect, useState, useRef, ReactNode } from 'react';

type AgentStatus = 'idle' | 'planning' | 'executing';

interface Message {
    id: string;
    type: 'user' | 'agent' | 'result';
    content: string;
    timestamp: Date;
    step?: string;
    success?: boolean;
    stepNumber?: number;
    totalSteps?: number;
}

interface AgentContextType {
    status: AgentStatus;
    messages: Message[];
    isConnected: boolean;
    sendPrompt: (prompt: string) => void;
    clearMessages: () => void;
}

const AgentContext = createContext<AgentContextType | undefined>(undefined);

export const useAgent = () => {
    const context = useContext(AgentContext);
    if (!context) {
        throw new Error('useAgent must be used within AgentProvider');
    }
    return context;
};

interface AgentProviderProps {
    children: ReactNode;
    wsUrl?: string;
}

export const AgentProvider: React.FC<AgentProviderProps> = ({
    children,
    wsUrl = 'ws://localhost:8000/ws'
}) => {
    const [status, setStatus] = useState<AgentStatus>('idle');
    const [messages, setMessages] = useState<Message[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
    const reconnectAttemptsRef = useRef(0);
    const maxReconnectAttempts = 5;

    const addMessage = (message: Omit<Message, 'id' | 'timestamp'>) => {
        setMessages(prev => [...prev, {
            ...message,
            id: Math.random().toString(36).substr(2, 9),
            timestamp: new Date(),
        }]);
    };

    const connect = () => {
        try {
            const ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                console.log('WebSocket connected');
                setIsConnected(true);
                reconnectAttemptsRef.current = 0;
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    switch (data.type) {
                        case 'status':
                            setStatus(data.content as AgentStatus);
                            break;

                        case 'agent':
                            addMessage({
                                type: 'agent',
                                content: data.content,
                            });
                            break;

                        case 'result':
                            addMessage({
                                type: 'result',
                                content: data.content,
                                step: data.step,
                                success: data.success,
                                stepNumber: data.stepNumber,
                                totalSteps: data.totalSteps,
                            });
                            break;

                        default:
                            console.log('Unknown message type:', data.type);
                    }
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            ws.onclose = () => {
                console.log('WebSocket disconnected');
                setIsConnected(false);
                wsRef.current = null;

                // Attempt to reconnect
                if (reconnectAttemptsRef.current < maxReconnectAttempts) {
                    const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000);
                    console.log(`Reconnecting in ${delay}ms... (attempt ${reconnectAttemptsRef.current + 1}/${maxReconnectAttempts})`);

                    reconnectTimeoutRef.current = setTimeout(() => {
                        reconnectAttemptsRef.current++;
                        connect();
                    }, delay);
                } else {
                    addMessage({
                        type: 'agent',
                        content: '❌ Connection lost. Please refresh the page to reconnect.',
                    });
                }
            };

            wsRef.current = ws;
        } catch (error) {
            console.error('Error creating WebSocket:', error);
        }
    };

    useEffect(() => {
        connect();

        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [wsUrl]);

    const sendPrompt = (prompt: string) => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            addMessage({
                type: 'agent',
                content: '❌ Not connected to server. Please wait for reconnection...',
            });
            return;
        }

        // Add user message
        addMessage({
            type: 'user',
            content: prompt,
        });

        // Send to server
        wsRef.current.send(JSON.stringify({
            type: 'prompt',
            content: prompt,
        }));
    };

    const clearMessages = () => {
        setMessages([]);
    };

    return (
        <AgentContext.Provider value={{ status, messages, isConnected, sendPrompt, clearMessages }}>
            {children}
        </AgentContext.Provider>
    );
};

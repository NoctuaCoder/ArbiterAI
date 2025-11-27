import React from 'react';
import { Route } from 'wouter';
import { AgentProvider } from './components/AgentProvider';
import Home from './components/Home';

function App() {
    return (
        <AgentProvider>
            <Route path="/" component={Home} />
            <Route path="/home" component={Home} />
        </AgentProvider>
    );
}

export default App;

"""
WebSocket Server with FastAPI - Integrates SimpleAgent for Real-Time Code Generation

This server provides a WebSocket endpoint that connects to the React frontend,
receives task prompts, generates plans using SimpleAgent, and streams execution
results back to the client in real-time.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from typing import Dict, Any
from agent_framework import SimpleAgent

app = FastAPI(title="Anti-C Code Agent Server")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_message(self, websocket: WebSocket, message: Dict[str, Any]):
        await websocket.send_json(message)


manager = ConnectionManager()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "online", "service": "Anti-C Code Agent"}


@app.get("/health")
async def health():
    """Health check for monitoring."""
    return {"status": "healthy"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time agent communication.
    
    Message format from client:
    {
        "type": "prompt",
        "content": "task description"
    }
    
    Message formats to client:
    {
        "type": "status",
        "content": "planning" | "executing" | "idle"
    }
    {
        "type": "agent",
        "content": "plan or message text"
    }
    {
        "type": "result",
        "content": "execution result",
        "step": "step description",
        "success": true/false
    }
    """
    await manager.connect(websocket)
    
    # Initialize the agent
    agent = SimpleAgent()
    
    try:
        # Send initial connection message
        await manager.send_message(websocket, {
            "type": "status",
            "content": "idle"
        })
        
        await manager.send_message(websocket, {
            "type": "agent",
            "content": "🦉 Agent connected and ready! Send me a task to get started."
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "prompt":
                task = message.get("content", "").strip()
                
                if not task:
                    await manager.send_message(websocket, {
                        "type": "agent",
                        "content": "⚠ Please provide a task description."
                    })
                    continue
                
                # Update status to planning
                await manager.send_message(websocket, {
                    "type": "status",
                    "content": "planning"
                })
                
                await manager.send_message(websocket, {
                    "type": "agent",
                    "content": f"🤔 Planning task: {task}"
                })
                
                # Generate plan using the agent
                try:
                    plan = agent.plan(task)
                    
                    # Send the plan to the client
                    plan_text = "📋 **Generated Plan:**\n\n"
                    for i, step in enumerate(plan, 1):
                        plan_text += f"{i}. {step}\n"
                    
                    await manager.send_message(websocket, {
                        "type": "agent",
                        "content": plan_text
                    })
                    
                    # Small delay before execution
                    await asyncio.sleep(0.5)
                    
                    # Update status to executing
                    await manager.send_message(websocket, {
                        "type": "status",
                        "content": "executing"
                    })
                    
                    await manager.send_message(websocket, {
                        "type": "agent",
                        "content": "⚙️ **Executing plan...**"
                    })
                    
                    # Execute each step and send results
                    context = {}
                    for i, step in enumerate(plan, 1):
                        # Send step start notification
                        await manager.send_message(websocket, {
                            "type": "agent",
                            "content": f"\n**[Step {i}/{len(plan)}]** {step}"
                        })
                        
                        # Execute the step
                        result = agent.execute_step(step, context)
                        context = result.get("context", {})
                        
                        # Send execution result
                        await manager.send_message(websocket, {
                            "type": "result",
                            "content": result.get("output", ""),
                            "step": step,
                            "success": result.get("success", True),
                            "stepNumber": i,
                            "totalSteps": len(plan)
                        })
                        
                        # Small delay between steps for better UX
                        await asyncio.sleep(0.3)
                    
                    # Send completion message
                    await manager.send_message(websocket, {
                        "type": "agent",
                        "content": f"✅ **Task completed!** All {len(plan)} steps executed successfully."
                    })
                    
                    # Reset agent context
                    agent.reset_context()
                    
                except Exception as e:
                    await manager.send_message(websocket, {
                        "type": "agent",
                        "content": f"❌ Error during planning/execution: {str(e)}"
                    })
                
                finally:
                    # Update status back to idle
                    await manager.send_message(websocket, {
                        "type": "status",
                        "content": "idle"
                    })
            
            elif message.get("type") == "ping":
                # Respond to ping for connection health check
                await manager.send_message(websocket, {
                    "type": "pong"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")
    
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        try:
            await manager.send_message(websocket, {
                "type": "agent",
                "content": f"❌ Server error: {str(e)}"
            })
        except:
            pass
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Anti-C Code Agent Server...")
    print("📡 WebSocket endpoint: ws://localhost:8000/ws")
    print("🌐 HTTP endpoint: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

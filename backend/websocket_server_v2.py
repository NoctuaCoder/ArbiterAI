"""
ArbiterAI 2.0 - WebSocket Server with Reflection Loop
Real-time autonomous code execution with error correction.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from typing import Dict, Any
from agent_framework_v2 import AutonomousAgent

app = FastAPI(title="ArbiterAI 2.0 - The Executor")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    return {"status": "online", "service": "ArbiterAI 2.0 - The Executor", "version": "2.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.0"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint with autonomous execution and reflection loop.
    
    Message format from client:
    {
        "type": "prompt",
        "content": "task description"
    }
    
    Message formats to client:
    - status: {"type": "status", "content": "planning|executing|reflecting|idle"}
    - agent: {"type": "agent", "content": "message"}
    - result: {"type": "result", "success": bool, "output": str, "step": str}
    - reflection: {"type": "reflection", "error": str, "correction_plan": [...]}
    - complete: {"type": "complete", "files": {...}}
    """
    await manager.connect(websocket)
    
    # Initialize agent
    agent = AutonomousAgent()
    
    try:
        await manager.send_message(websocket, {
            "type": "status",
            "content": "idle"
        })
        
        await manager.send_message(websocket, {
            "type": "agent",
            "content": "🦉 **ArbiterAI 2.0 ready!** I can execute real code, fix errors, and build projects."
        })
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "prompt":
                task = message.get("content", "").strip()
                
                if not task:
                    await manager.send_message(websocket, {
                        "type": "agent",
                        "content": "⚠️ Please provide a task description."
                    })
                    continue
                
                # Initialize context
                context = agent.initialize_context(task)
                
                # PLANNING PHASE
                await manager.send_message(websocket, {
                    "type": "status",
                    "content": "planning"
                })
                
                await manager.send_message(websocket, {
                    "type": "agent",
                    "content": f"🧠 **Planning:** {task}"
                })
                
                try:
                    plan = agent.plan(task, context)
                    
                    plan_text = "📋 **Execution Plan:**\n\n"
                    for i, step in enumerate(plan, 1):
                        plan_text += f"{i}. {step}\n"
                    
                    await manager.send_message(websocket, {
                        "type": "agent",
                        "content": plan_text
                    })
                    
                    await asyncio.sleep(0.5)
                    
                    # EXECUTION PHASE WITH REFLECTION LOOP
                    await manager.send_message(websocket, {
                        "type": "status",
                        "content": "executing"
                    })
                    
                    await manager.send_message(websocket, {
                        "type": "agent",
                        "content": "⚙️ **Executing plan...**"
                    })
                    
                    max_retries = 3
                    retry_count = 0
                    current_plan = plan
                    
                    while retry_count < max_retries:
                        all_success = True
                        
                        for i, step in enumerate(current_plan, 1):
                            # Send step start
                            await manager.send_message(websocket, {
                                "type": "agent",
                                "content": f"\n**[Step {i}/{len(current_plan)}]** {step}"
                            })
                            
                            # Execute step
                            result = agent.execute_step(step, context)
                            context = result['context']
                            
                            # Send result
                            await manager.send_message(websocket, {
                                "type": "result",
                                "success": result['success'],
                                "output": result['output'],
                                "error": result.get('error'),
                                "step": step,
                                "stepNumber": i,
                                "totalSteps": len(current_plan),
                                "tool_used": result.get('tool_used'),
                                "tool_args": result.get('tool_args')
                            })
                            
                            # Handle errors with REFLECTION
                            if not result['success']:
                                all_success = False
                                
                                await manager.send_message(websocket, {
                                    "type": "status",
                                    "content": "reflecting"
                                })
                                
                                await manager.send_message(websocket, {
                                    "type": "agent",
                                    "content": f"❌ **Error detected:** {result.get('error')}\n\n🤔 **Reflecting on error...**"
                                })
                                
                                # Generate correction plan
                                correction_plan = agent.reflect_on_error(
                                    original_task=task,
                                    failed_step=step,
                                    error=result.get('error', 'Unknown error'),
                                    context=context
                                )
                                
                                correction_text = "🔧 **Correction Plan:**\n\n"
                                for j, correction_step in enumerate(correction_plan, 1):
                                    correction_text += f"{j}. {correction_step}\n"
                                
                                await manager.send_message(websocket, {
                                    "type": "reflection",
                                    "error": result.get('error'),
                                    "correction_plan": correction_plan,
                                    "content": correction_text
                                })
                                
                                # Update plan and retry
                                current_plan = correction_plan
                                retry_count += 1
                                
                                await manager.send_message(websocket, {
                                    "type": "agent",
                                    "content": f"🔄 **Retry {retry_count}/{max_retries}** - Executing correction plan..."
                                })
                                
                                await manager.send_message(websocket, {
                                    "type": "status",
                                    "content": "executing"
                                })
                                
                                await asyncio.sleep(0.3)
                                break  # Restart with correction plan
                            
                            await asyncio.sleep(0.3)
                        
                        # If all steps succeeded, break the retry loop
                        if all_success:
                            break
                    
                    # COMPLETION
                    if all_success:
                        files_created = list(context.get('files', {}).keys())
                        completion_msg = f"✅ **Task completed successfully!**\n\n"
                        
                        if files_created:
                            completion_msg += f"📁 **Files created:**\n"
                            for file in files_created:
                                completion_msg += f"- {file}\n"
                        
                        completion_msg += f"\n📊 **Total steps executed:** {len(context.get('history', []))}"
                        
                        await manager.send_message(websocket, {
                            "type": "complete",
                            "content": completion_msg,
                            "files": context.get('files', {}),
                            "history": context.get('history', [])
                        })
                    else:
                        await manager.send_message(websocket, {
                            "type": "agent",
                            "content": f"⚠️ **Task partially completed** - Max retries ({max_retries}) reached."
                        })
                    
                except Exception as e:
                    await manager.send_message(websocket, {
                        "type": "agent",
                        "content": f"❌ **Fatal error:** {str(e)}"
                    })
                
                finally:
                    await manager.send_message(websocket, {
                        "type": "status",
                        "content": "idle"
                    })
            
            elif message.get("type") == "ping":
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
    print("🚀 Starting ArbiterAI 2.0 - The Executor")
    print("📡 WebSocket: ws://localhost:8000/ws")
    print("🌐 HTTP: http://localhost:8000")
    print("⚡ Features: Real execution | Error reflection | Project memory")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

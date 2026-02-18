from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database.db import engine, Base
from app.routers import auth, tokens, queues, analytics, healthcare, banking, admin
from app.services.websocket_manager import manager
from app.ai.predictor import WaitTimePredictor

# Initialize AI predictor
predictor = WaitTimePredictor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    predictor.train_initial_model()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="SmartQueue AI",
    description="AI-Powered Queue Management System for Healthcare & Banking",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tokens.router, prefix="/api/tokens", tags=["Tokens"])
app.include_router(queues.router, prefix="/api/queues", tags=["Queues"])
app.include_router(healthcare.router, prefix="/api/healthcare", tags=["Healthcare"])
app.include_router(banking.router, prefix="/api/banking", tags=["Banking"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

@app.get("/")
async def root():
    return {
        "message": "SmartQueue AI Backend",
        "version": "1.0.0",
        "status": "operational"
    }

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)

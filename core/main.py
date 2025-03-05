from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Agent of All Agents API", version="1.0.0")

# Base model for all API requests
class TextRequest(BaseModel):
    text: str

class FileRequest(BaseModel):
    file_path: str

class SuggestRequest(BaseModel):
    context: Optional[str] = None
    category: str

# ========== Writing Endpoints ==========
@app.post("/v1/write/{type}")
async def write_content(type: str, request: TextRequest):
    if type not in ["Sales pitch", "E-mail", "Tweet", "Website Content", "Technical Research", "Caption", "Article", "Poem", "Whitepaper", "Scenario", "Movie Script", "Song", "Newsletter"]:
        raise HTTPException(status_code=400, detail="Unsupported writing type")
    return {"type": type, "content": f"Generated {type} based on: {request.text}"}

# ========== Watching Endpoints ==========
@app.get("/v1/watch/{type}")
async def watch_content(type: str):
    if type not in ["Video", "Screen"]:
        raise HTTPException(status_code=400, detail="Unsupported watching type")
    return {"type": type, "content": f"Watching {type}"}

# ========== Listening Endpoints ==========
@app.get("/v1/listen/{type}")
async def listen_content(type: str):
    if type not in ["Audio", "Video", "Microphone"]:
        raise HTTPException(status_code=400, detail="Unsupported listening type")
    return {"type": type, "content": f"Listening to {type}"}

# ========== Talk Endpoints ==========
@app.post("/v1/talk/{type}")
async def talk_content(type: str, request: TextRequest):
    if type not in ["Chat", "Voice"]:
        raise HTTPException(status_code=400, detail="Unsupported talk type")
    return {"type": type, "content": f"Talking via {type} with message: {request.text}"}

# ========== Generate Endpoints ==========
@app.post("/v1/generate/{type}")
async def generate_content(type: str, request: TextRequest):
    if type not in ["Image", "Video", "Music"]:
        raise HTTPException(status_code=400, detail="Unsupported generate type")
    return {"type": type, "content": f"Generated {type} based on: {request.text}"}

# ========== Create Endpoints ==========
@app.post("/v1/create/{type}")
async def create_content(type: str, request: TextRequest):
    if type not in ["Website", "Screen", "Email List"]:
        raise HTTPException(status_code=400, detail="Unsupported create type")
    return {"type": type, "content": f"Created {type} based on: {request.text}"}

# ========== Suggest Endpoints ==========
@app.post("/v1/suggest/{category}")
async def suggest_content(category: str, request: SuggestRequest):
    if category not in ["Movies", "Ideas", "Travels", "Companies", "Health solutions"]:
        raise HTTPException(status_code=400, detail="Unsupported suggestion category")
    return {"category": category, "suggestions": [f"Suggested {category} based on: {request.context}"]}

# ========== Trade Endpoints ==========
@app.post("/v1/trade/{type}")
async def trade_assets(type: str, request: TextRequest):
    if type not in ["Crypto", "Stocks", "Forex"]:
        raise HTTPException(status_code=400, detail="Unsupported trade type")
    return {"type": type, "content": f"Trading {type} based on: {request.text}"}

# ========== Convert Endpoints ==========
@app.post("/v1/convert/{type}")
async def convert_file(type: str, request: FileRequest):
    if type not in ["File", "Dataset"]:
        raise HTTPException(status_code=400, detail="Unsupported convert type")
    return {"type": type, "content": f"Converted {type} from file: {request.file_path}"}

# ========== Health Check ==========
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


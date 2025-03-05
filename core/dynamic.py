import json
import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from importlib import import_module

app = FastAPI()

# Load URFN registry
URFN_REGISTRY_FILE = "urfn_Registry.json"

def load_urfn_registry():
    if not os.path.exists(URFN_REGISTRY_FILE):
        raise FileNotFoundError(f"{URFN_REGISTRY_FILE} not found.")
    with open(URFN_REGISTRY_FILE, "r") as f:
        return json.load(f)

urfn_registry = load_urfn_registry()

# Define request model
class RequestPayload(BaseModel):
    text: str

# Dynamic function loader based on URFN
def execute_urfn(urfn_name, text):
    urfn_data = urfn_registry.get(urfn_name)
    if not urfn_data:
        raise HTTPException(status_code=400, detail="Unsupported function")
    
    module_name = urfn_data.get("module")
    function_name = urfn_data.get("function")
    
    if not module_name or not function_name:
        raise HTTPException(status_code=500, detail="Invalid URFN configuration")
    
    # Dynamically import module and call the function
    try:
        module = import_module(f"addons.{module_name}")
        func = getattr(module, function_name)
        return func(text)
    except (ModuleNotFoundError, AttributeError) as e:
        raise HTTPException(status_code=500, detail=f"Function loading error: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Generate dynamic endpoints based on URFNs
for urfn_name in urfn_registry.keys():
    category, function = urfn_name.split("_", 1)
    endpoint = f"/v1/{category}/{function}"
    
    @app.post(endpoint)
    async def dynamic_endpoint(payload: RequestPayload, urfn_name=urfn_name):
        result = execute_urfn(urfn_name, payload.text)
        return {"result": result}

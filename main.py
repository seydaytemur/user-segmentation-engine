from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, Any

app = FastAPI()

# Custom exception handler to return 400 Bad Request for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)},
    )

# User Model
class User(BaseModel):
    id: str
    level: int = Field(ge=0)
    country: str = Field(min_length=1)
    first_session: int = Field(ge=0)
    last_session: int = Field(ge=0)
    purchase_amount: int = Field(ge=0)
    last_purchase_at: int = Field(ge=0)

# Request Model for POST /evaluate
class EvaluateRequest(BaseModel):
    user: User
    segments: Dict[str, str]

@app.get("/evaluate")
async def get_evaluate():
    return FileResponse("test.html")

import pandas as pd
import time
import re

@app.post("/evaluate")
async def post_evaluate(request: EvaluateRequest):
    # Convert user model to dictionary/DataFrame
    try:
        user_data = request.user.model_dump()
    except AttributeError:
        user_data = request.user.dict()
        
    df = pd.DataFrame([user_data])
    
    results = {}
    current_time = int(time.time())
    
    for name, rule in request.segments.items():
        # Replace _now() with current timestamp
        processed_rule = rule.replace("_now()", str(current_time))
        
        # SQL to Pandas syntax conversion
        # 1. Replace AND/OR (case-insensitive) with and/or
        processed_rule = re.sub(r'\bAND\b', 'and', processed_rule, flags=re.IGNORECASE)
        processed_rule = re.sub(r'\bOR\b', 'or', processed_rule, flags=re.IGNORECASE)
        
        # 2. Replace <> with != (ANSI SQL standard)
        processed_rule = processed_rule.replace("<>", "!=")
        
        # 3. Replace single = with == (for equality), ensuring we don't break >=, <=, ==, !=
        # Lookbehind matches position where previous char is NOT <, >, !, = 
        # Lookahead matches position where next char is NOT =
        processed_rule = re.sub(r'(?<![<>!=])=(?!=)', '==', processed_rule)
        
        try:
            # Pandas query logic
            subset = df.query(processed_rule)
            results[name] = not subset.empty
        except Exception as e:
            # Return 400 for any error during evaluation (syntax, unknown field, etc.)
            return JSONResponse(
                status_code=400,
                content={"error": f"Error in rule '{name}': {str(e)}"}
            )
            
    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)

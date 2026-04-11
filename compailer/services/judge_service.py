from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

# In a true microservice, this would have its own database connection.
# For our decomposed monolith, we import the shared data layers.
import main

router = APIRouter(prefix="/api/v1/judge", tags=["judge"])

class SubmitRequest(BaseModel):
    problem_id: str
    code: str
    language: str

@router.post("/execute")
async def execute_code(request: SubmitRequest, payload: dict = Depends(main.verify_jwt_token)):
    user_email = payload.get("email")
    user_id = payload.get("sub")
    
    if request.problem_id not in main.problems_db:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    valid_languages = ["python", "cpp", "java", "javascript", "python3"]
    if request.language not in valid_languages:
        raise HTTPException(status_code=400, detail="Invalid language")
        
    execution_result = await main.execute_with_judge0(
        language=request.language,
        code=request.code,
        problem_id=request.problem_id
    )

    return execution_result

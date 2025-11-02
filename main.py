"""
FastAPI backend for solver comparison project.
Provides endpoints for running classical and quantum solvers and comparing results.
"""

import uuid
import time
import json
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Add the parent directory to the path to import solver modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import solver functions - these will be replaced with actual implementations
try:
    from classical_solver import run_classical_solver
    from quantum_solver import run_quantum_solver
    from compare_results import compare_solvers
except ImportError:
    # Mock implementations if actual solvers are not available
    print("Warning: Actual solver modules not found, using mock implementations")
    
    def run_classical_solver(puzzle: List[List[int]]) -> Dict[str, Any]:
        """Mock classical solver - replace with actual implementation"""
        import time
        # Simulate solving time
        time.sleep(0.1)
        # Return a mock solution (dynamic size)
        grid_size = len(puzzle)
        # Create a simple mock solution for any grid size
        solution = []
        for i in range(grid_size):
            row = [(j + i) % grid_size + 1 for j in range(grid_size)]
            solution.append(row)
        return {"solution": solution, "time": 0.1}
    
    def run_quantum_solver(puzzle: List[List[int]]) -> Dict[str, Any]:
        """Mock quantum solver - replace with actual implementation"""
        import time
        import random
        # Simulate quantum computation time
        time.sleep(0.2)
        # Return mock quantum result with histogram (dynamic size)
        grid_size = len(puzzle)
        state_length = grid_size * grid_size
        state = ''.join([str(random.randint(0, 1)) for _ in range(state_length)])
        counts = {
            state: 45,
            state[:-1] + '0': 12,
            state[:-1] + '1': 8,
            state[:-2] + '00': 5,
            state[:-2] + '11': 3,
            state[:-2] + '01': 2
        }
        return {
            "state": state,
            "time": 0.2,
            "counts": counts
        }
    
    def compare_solvers(puzzle: List[List[int]]) -> Dict[str, Any]:
        """Mock comparison function - replace with actual implementation"""
        classical_result = run_classical_solver(puzzle)
        quantum_result = run_quantum_solver(puzzle)
        return {
            "classical": classical_result,
            "quantum": quantum_result,
            "comparison": {
                "classical_time": classical_result["time"],
                "quantum_time": quantum_result["time"],
                "time_difference": abs(classical_result["time"] - quantum_result["time"]),
                "both_solved": True  # Mock that both solved correctly
            }
        }

app = FastAPI(title="Solver Comparison API", version="1.0.0")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    message: str

class PuzzleRequest(BaseModel):
    puzzle: List[List[int]]

class SolverResponse(BaseModel):
    solution: Optional[List[List[int]]] = None
    state: Optional[str] = None
    time: float
    counts: Optional[Dict[str, int]] = None

class ComparisonResponse(BaseModel):
    classical: SolverResponse
    quantum: SolverResponse
    comparison: Dict[str, Any]

# In-memory storage for tokens (in production, use a proper database)
valid_tokens = set()

def verify_token(token: str) -> bool:
    """Verify if token is valid"""
    return token in valid_tokens

@app.get("/api/status")
async def get_status():
    """Health check endpoint"""
    return {"ok": True}

@app.post("/api/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Mock login endpoint - accepts any username/password"""
    # Generate a simple UUID token
    token = str(uuid.uuid4())
    valid_tokens.add(token)
    
    return LoginResponse(
        token=token,
        message=f"Login successful for user: {request.username}"
    )

@app.post("/api/run/classical", response_model=SolverResponse)
async def run_classical(puzzle_request: PuzzleRequest):
    """Run classical solver on the provided puzzle"""
    try:
        start_time = time.time()
        result = run_classical_solver(puzzle_request.puzzle)
        end_time = time.time()
        
        return SolverResponse(
            solution=result.get("solution"),
            time=end_time - start_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classical solver error: {str(e)}")

@app.post("/api/run/quantum", response_model=SolverResponse)
async def run_quantum(puzzle_request: PuzzleRequest):
    """Run quantum solver on the provided puzzle"""
    try:
        start_time = time.time()
        result = run_quantum_solver(puzzle_request.puzzle)
        end_time = time.time()
        
        return SolverResponse(
            state=result.get("state"),
            time=end_time - start_time,
            counts=result.get("counts")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quantum solver error: {str(e)}")

@app.post("/api/run/compare", response_model=ComparisonResponse)
async def run_compare(puzzle_request: PuzzleRequest):
    """Run both solvers and compare results"""
    try:
        start_time = time.time()
        result = compare_solvers(puzzle_request.puzzle)
        end_time = time.time()
        
        return ComparisonResponse(
            classical=SolverResponse(
                solution=result["classical"].get("solution"),
                time=result["classical"].get("time", 0)
            ),
            quantum=SolverResponse(
                state=result["quantum"].get("state"),
                time=result["quantum"].get("time", 0),
                counts=result["quantum"].get("counts")
            ),
            comparison=result.get("comparison", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


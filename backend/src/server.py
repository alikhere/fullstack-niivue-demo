from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import os
from pathlib import Path

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup directories
os.makedirs("data", exist_ok=True)
os.makedirs("static", exist_ok=True)

@app.get("/")
async def root():
    return JSONResponse(content={
        "message": "Niivue Backend with niimath",
        "endpoints": {
            "get_image": "/api/image",
            "threshold": "/api/threshold?min_val=100&max_val=500"
        }
    })

@app.get("/api/image")
async def get_image():
    file_path = Path("data/test.nii.gz")
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Download test image first: curl -L https://niivue.github.io/niivue-demo-images/mni152.nii.gz -o data/test.nii.gz"
        )
    return FileResponse(file_path)

@app.get("/api/threshold")
async def apply_threshold(
    min_val: float = Query(0, ge=0),
    max_val: float = Query(1000, ge=0)
):
    try:
        # Create static directory if missing
        Path("static").mkdir(exist_ok=True)
        
        # Correct niimath thresholding command
        cmd = [
            "niimath",
            "data/test.nii.gz",
            "-thr", str(min_val),    # Lower threshold
            "-uthr", str(max_val),   # Upper threshold
            "static/thresholded.nii.gz"
        ]
        
        # Run with full error capture
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Verify output was created
        if not Path("static/thresholded.nii.gz").exists():
            raise HTTPException(
                status_code=500,
                detail="Processing succeeded but no output file created"
            )
        
        return {"output": "/static/thresholded.nii.gz"}
    
    except subprocess.CalledProcessError as e:
        error_detail = f"niimath failed: {e.stderr}" if e.stderr else "niimath command failed"
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

app.mount("/static", StaticFiles(directory="static"), name="static")
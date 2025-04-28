from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import nibabel as nib
import numpy as np
import os
from pathlib import Path

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (adjust for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup directories
os.makedirs("data", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Root endpoint
@app.get("/")
async def root():
    return JSONResponse(content={
        "message": "Niivue Backend API",
        "endpoints": {
            "documentation": "/docs",
            "get_image": "/api/image",
            "apply_threshold": "/api/threshold?min_val=100&max_val=500"
        }
    })

# API Endpoints
@app.get("/api/image")
async def get_image(name: str = "test.nii.gz"):
    file_path = Path(f"data/{name}")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        # Validate it's a proper NIfTI file
        nib.load(file_path)
        return FileResponse(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid NIfTI file: {str(e)}"
        )

@app.get("/api/threshold")
async def apply_threshold(
    min_val: float = Query(0, ge=0),
    max_val: float = Query(1000, ge=0)
):
    try:
        input_path = Path("data/test.nii.gz")
        output_path = Path("static/thresholded.nii.gz")
        
        # Verify input exists
        if not input_path.exists():
            raise HTTPException(status_code=404, detail="Input image not found")
        
        # Verify file size
        if input_path.stat().st_size < 1024:
            raise HTTPException(status_code=422, detail="File too small to be valid")
            
        # Load and process image
        img = nib.load(input_path)
        data = img.get_fdata()
        
        # Apply threshold
        thresholded = np.where(
            (data >= min_val) & (data <= max_val),
            data, 
            0  # Set values outside range to 0
        )
        
        # Ensure output directory exists
        output_path.parent.mkdir(exist_ok=True)
        
        # Save with original header information
        nib.save(
            nib.Nifti1Image(thresholded, img.affine, img.header),
            output_path
        )
        
        return {"output": "/static/thresholded.nii.gz"}
    
    except nib.filebasedimages.ImageFileError as e:
        raise HTTPException(status_code=400, detail=f"Invalid NIfTI file: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Processing error: {str(e)}"
        )

# Mount static files (must be last)
app.mount("/static", StaticFiles(directory="static"), name="static")
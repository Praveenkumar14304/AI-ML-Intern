from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd
import json
import os
from typing import List, Optional
import uuid
import shutil
from services.data_processor import DataProcessor
from services.llm_service import LLMService
from services.ppt_generator import PPTGenerator
from utils.file_utils import save_upload_file, validate_csv_file

app = FastAPI(title="DataSlide API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
data_processor = DataProcessor()
llm_service = LLMService()
ppt_generator = PPTGenerator()

@app.get("/")
async def root():
    return {"message": "DataSlide API is running!"}

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload and validate CSV file"""
    if not validate_csv_file(file):
        raise HTTPException(status_code=400, detail="Invalid CSV file")

    session_id = str(uuid.uuid4())
    file_path = f"../data/uploads/{session_id}_{file.filename}"

    await save_upload_file(file, file_path)

    try:
        df = pd.read_csv(file_path)
        columns_info = data_processor.analyze_columns(df)

        return {
            "session_id": session_id,
            "filename": file.filename,
            "columns": columns_info,
            "shape": df.shape,
            "preview": df.head().to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

@app.post("/upload-template")
async def upload_template(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    """Upload PPT template"""
    if not file.filename.endswith('.pptx'):
        raise HTTPException(status_code=400, detail="Only .pptx files are allowed")

    template_path = f"../data/uploads/{session_id}_template.pptx"
    await save_upload_file(file, template_path)

    return {"message": "Template uploaded successfully", "template_path": template_path}

@app.post("/generate-presentation")
async def generate_presentation(
    session_id: str = Form(...),
    selected_columns: str = Form(...),
    use_template: bool = Form(False),
    theme: Optional[str] = Form("Corporate Blue")
):
    """Generate PowerPoint presentation"""
    try:
        columns = json.loads(selected_columns)

        csv_files = [f for f in os.listdir("../data/uploads") if f.startswith(session_id) and f.endswith('.csv')]
        if not csv_files:
            raise HTTPException(status_code=404, detail="CSV file not found")

        csv_path = f"../data/uploads/{csv_files[0]}"
        df = pd.read_csv(csv_path)

        df_filtered = df[columns] if columns else df

        analysis_results = data_processor.process_data(df_filtered, session_id)
        narrative = llm_service.generate_narrative(analysis_results)

        template_path = None
        if use_template:
            template_files = [f for f in os.listdir("../data/uploads") 
                            if f.startswith(session_id) and f.endswith('_template.pptx')]
            if template_files:
                template_path = f"../data/uploads/{template_files[0]}"

        output_path = ppt_generator.create_presentation(
            narrative, analysis_results, session_id, template_path, theme
        )

        return {"message": "Presentation generated successfully", "download_path": output_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating presentation: {str(e)}")

@app.get("/download/{session_id}")
async def download_presentation(session_id: str):
    """Download generated presentation"""
    output_files = [f for f in os.listdir("../data/outputs") if f.startswith(session_id)]
    if not output_files:
        raise HTTPException(status_code=404, detail="Presentation not found")

    file_path = f"../data/outputs/{output_files[0]}"
    return FileResponse(
        path=file_path,
        filename=f"DataSlide_Presentation_{session_id}.pptx",
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
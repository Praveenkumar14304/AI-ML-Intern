# Now let me create the complete project zip file with all necessary files

import zipfile
import os

# All the file contents that we need to include
all_files = {
    "requirements.txt": """streamlit==1.29.0
fastapi==0.104.1
uvicorn==0.24.0
pandas==2.1.3
numpy==1.25.2
matplotlib==3.8.2
seaborn==0.13.0
python-pptx==0.6.23
python-multipart==0.0.6
requests==2.31.0
transformers==4.36.0
torch==2.1.1
accelerate==0.25.0
scipy==1.11.4
scikit-learn==1.3.2
plotly==5.17.0
openpyxl==3.1.2
Pillow==10.1.0
aiofiles==23.2.1""",

    "backend/main.py": '''from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd
import json
import os
from typing import List, Optional
import uuid
from services.data_processor import DataProcessor
from services.llm_service import LLMService
from services.ppt_generator import PPTGenerator
from utils.file_utils import save_upload_file, validate_csv_file

app = FastAPI(title="DataSlide API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

data_processor = DataProcessor()
llm_service = LLMService()
ppt_generator = PPTGenerator()

@app.get("/")
async def root():
    return {"message": "DataSlide API is running!"}

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
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
async def upload_template(session_id: str = Form(...), file: UploadFile = File(...)):
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
    uvicorn.run(app, host="0.0.0.0", port=8000)''',

    "backend/services/data_processor.py": '''import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from sklearn.preprocessing import LabelEncoder
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class DataProcessor:
    def __init__(self):
        self.plot_dir = "../data/plots"
        os.makedirs(self.plot_dir, exist_ok=True)
        
    def analyze_columns(self, df):
        columns_info = []
        
        for col in df.columns:
            col_info = {
                "name": col,
                "type": str(df[col].dtype),
                "null_count": int(df[col].isnull().sum()),
                "unique_count": int(df[col].nunique()),
                "sample_values": df[col].dropna().head(3).tolist()
            }
            
            if df[col].dtype in ['int64', 'float64']:
                col_info["data_type"] = "numerical"
                col_info["stats"] = {
                    "mean": float(df[col].mean()) if not df[col].isnull().all() else None,
                    "std": float(df[col].std()) if not df[col].isnull().all() else None,
                    "min": float(df[col].min()) if not df[col].isnull().all() else None,
                    "max": float(df[col].max()) if not df[col].isnull().all() else None
                }
            elif df[col].dtype == 'object':
                if df[col].str.contains(r'\\d{4}-\\d{2}-\\d{2}|\\d{2}/\\d{2}/\\d{4}', na=False).any():
                    col_info["data_type"] = "datetime"
                else:
                    col_info["data_type"] = "categorical"
                    col_info["stats"] = {
                        "most_common": df[col].value_counts().head(3).to_dict()
                    }
            else:
                col_info["data_type"] = "other"
            
            columns_info.append(col_info)
            
        return columns_info
    
    def process_data(self, df, session_id):
        data_description = {
            "filename": f"session_{session_id}",
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum()
        }
        
        with open(f"../data/outputs/{session_id}_data_description.json", "w") as f:
            json.dump(data_description, f, indent=2)
        
        correlation_results = self._perform_correlation_analysis(df, session_id)
        insights = self._generate_feature_insights(df, session_id)
        
        return {
            "data_description": data_description,
            "correlation_analysis": correlation_results,
            "insights": insights,
            "session_id": session_id
        }
    
    def _perform_correlation_analysis(self, df, session_id):
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numerical_cols) < 2:
            return {"message": "Not enough numerical columns for correlation analysis"}
        
        correlation_matrix = df[numerical_cols].corr()
        
        corr_pairs = []
        for i in range(len(numerical_cols)):
            for j in range(i+1, len(numerical_cols)):
                corr_value = correlation_matrix.iloc[i, j]
                if not pd.isna(corr_value):
                    corr_pairs.append({
                        "feature1": numerical_cols[i],
                        "feature2": numerical_cols[j],
                        "correlation": float(corr_value),
                        "strength": self._correlation_strength(abs(corr_value))
                    })
        
        corr_pairs.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        
        correlation_results = {
            "top_correlations": corr_pairs[:10],
            "correlation_matrix": correlation_matrix.to_dict()
        }
        
        with open(f"../data/outputs/{session_id}_correlation_analysis.json", "w") as f:
            json.dump(correlation_results, f, indent=2)
        
        return correlation_results
    
    def _generate_feature_insights(self, df, session_id):
        insights = {}
        
        for column in df.columns:
            col_insights = self._analyze_single_feature(df, column, session_id)
            insights[column] = col_insights
        
        with open(f"../data/outputs/{session_id}_analysis_insights.json", "w") as f:
            json.dump(insights, f, indent=2)
        
        return insights
    
    def _analyze_single_feature(self, df, column, session_id):
        col_data = df[column].dropna()
        
        if len(col_data) == 0:
            return {
                "type": "empty",
                "statistics": {},
                "insight": f"{column} contains no valid data",
                "plot_path": None
            }
        
        if df[column].dtype in ['int64', 'float64']:
            return self._analyze_numerical_feature(col_data, column, session_id)
        elif df[column].dtype == 'object':
            return self._analyze_categorical_feature(col_data, column, session_id)
        else:
            return self._analyze_other_feature(col_data, column, session_id)
    
    def _analyze_numerical_feature(self, col_data, column, session_id):
        stats = {
            "mean": float(col_data.mean()),
            "median": float(col_data.median()),
            "std": float(col_data.std()),
            "min": float(col_data.min()),
            "max": float(col_data.max()),
            "skewness": float(col_data.skew()),
            "kurtosis": float(col_data.kurtosis())
        }
        
        plt.figure(figsize=(10, 6))
        plt.subplot(1, 2, 1)
        plt.hist(col_data, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title(f'Distribution of {column}')
        plt.xlabel(column)
        plt.ylabel('Frequency')
        
        plt.subplot(1, 2, 2)
        plt.boxplot(col_data)
        plt.title(f'Box Plot of {column}')
        plt.ylabel(column)
        
        plot_path = f"{self.plot_dir}/{session_id}_{column}_numerical.png"
        plt.tight_layout()
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        insight = f"{column} has a mean of {stats['mean']:.2f} with standard deviation {stats['std']:.2f}. "
        if abs(stats['skewness']) > 1:
            insight += f"The distribution is {'right' if stats['skewness'] > 0 else 'left'} skewed. "
        if stats['kurtosis'] > 3:
            insight += "The distribution has heavy tails indicating potential outliers."
        elif stats['kurtosis'] < 3:
            insight += "The distribution has light tails."
        
        return {
            "type": "numerical",
            "statistics": stats,
            "insight": insight,
            "plot_path": plot_path
        }
    
    def _analyze_categorical_feature(self, col_data, column, session_id):
        value_counts = col_data.value_counts()
        stats = {
            "unique_count": len(value_counts),
            "most_common": value_counts.head(5).to_dict(),
            "least_common": value_counts.tail(5).to_dict()
        }
        
        plt.figure(figsize=(12, 6))
        top_categories = value_counts.head(10)
        
        if len(top_categories) <= 6:
            plt.pie(top_categories.values, labels=top_categories.index, autopct='%1.1f%%')
            plt.title(f'Distribution of {column}')
        else:
            plt.bar(range(len(top_categories)), top_categories.values)
            plt.xticks(range(len(top_categories)), top_categories.index, rotation=45)
            plt.title(f'Top 10 Categories in {column}')
            plt.xlabel(column)
            plt.ylabel('Count')
        
        plot_path = f"{self.plot_dir}/{session_id}_{column}_categorical.png"
        plt.tight_layout()
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        most_common_val, most_common_count = value_counts.iloc[0], value_counts.iloc[0]
        percentage = (most_common_count / len(col_data)) * 100
        
        insight = f"{column} has {stats['unique_count']} unique categories. "
        insight += f"The most frequent category is '{most_common_val}' ({percentage:.1f}% of data). "
        
        if stats['unique_count'] > len(col_data) * 0.8:
            insight += "High cardinality suggests this might be an identifier column."
        
        return {
            "type": "categorical",
            "statistics": stats,
            "insight": insight,
            "plot_path": plot_path
        }
    
    def _analyze_other_feature(self, col_data, column, session_id):
        stats = {
            "count": len(col_data),
            "unique_count": col_data.nunique(),
            "sample_values": col_data.head(5).tolist()
        }
        
        insight = f"{column} contains {stats['count']} values with {stats['unique_count']} unique entries."
        
        return {
            "type": "other",
            "statistics": stats,
            "insight": insight,
            "plot_path": None
        }
    
    def _correlation_strength(self, corr_value):
        if corr_value >= 0.7:
            return "Strong"
        elif corr_value >= 0.3:
            return "Moderate"
        else:
            return "Weak"''',

    "backend/services/llm_service.py": '''from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import json
import os

class LLMService:
    def __init__(self):
        self.model_name = "mistralai/Mistral-7B-Instruct-v0.1"
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self._initialize_model()
    
    def _initialize_model(self):
        try:
            print("Loading Mistral 7B model...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Using device: {device}")
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map="auto" if device == "cuda" else None,
                trust_remote_code=True
            )
            
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_length=2048,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            print("Mistral 7B model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading Mistral 7B model: {e}")
            print("Using fallback text generation...")
            self.pipeline = None
    
    def generate_narrative(self, analysis_results):
        prompt = self._create_prompt(analysis_results)
        
        if self.pipeline is not None:
            try:
                response = self.pipeline(
                    prompt,
                    max_length=1500,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True
                )
                
                generated_text = response[0]['generated_text']
                narrative_text = generated_text[len(prompt):].strip()
                
                narrative = self._parse_narrative_response(narrative_text, analysis_results)
                
            except Exception as e:
                print(f"Error generating with Mistral 7B: {e}")
                narrative = self._generate_fallback_narrative(analysis_results)
        else:
            narrative = self._generate_fallback_narrative(analysis_results)
        
        session_id = analysis_results.get("session_id", "default")
        with open(f"../data/outputs/{session_id}_presentation_narrative.json", "w") as f:
            json.dump(narrative, f, indent=2)
        
        return narrative
    
    def _create_prompt(self, analysis_results):
        data_desc = analysis_results.get("data_description", {})
        correlations = analysis_results.get("correlation_analysis", {})
        insights = analysis_results.get("insights", {})
        
        prompt = f"""[INST]You are a professional data analyst creating a PowerPoint presentation. 
Based on the following data analysis results, create a structured presentation narrative.

DATA OVERVIEW:
- Dataset shape: {data_desc.get('shape', 'Unknown')}
- Columns: {', '.join(data_desc.get('columns', [])[:5])}
- Missing values: {sum(data_desc.get('missing_values', {}).values())} total

KEY INSIGHTS:
"""
        
        for col, insight_data in list(insights.items())[:3]:
            prompt += f"- {col}: {insight_data.get('insight', 'No insight available')}\\n"
        
        top_corr = correlations.get("top_correlations", [])[:2]
        if top_corr:
            prompt += "\\nTOP CORRELATIONS:\\n"
            for corr in top_corr:
                prompt += f"- {corr['feature1']} vs {corr['feature2']}: {corr['correlation']:.2f} ({corr['strength']})\\n"
        
        prompt += """
Please create a presentation structure with:
1. Title slide
2. Data overview slide  
3. Key findings slides (2-3 slides)
4. Conclusions slide

Respond in this JSON format:
{
  "slides": [
    {
      "title": "slide title",
      "content": ["bullet point 1", "bullet point 2"],
      "chart_references": ["chart_name_if_applicable"]
    }
  ]
}[/INST]"""
        
        return prompt
    
    def _parse_narrative_response(self, response_text, analysis_results):
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                parsed_response = json.loads(json_text)
                
                if "slides" in parsed_response:
                    return self._enhance_narrative(parsed_response, analysis_results)
            
            return self._create_structured_from_text(response_text, analysis_results)
            
        except Exception as e:
            print(f"Error parsing narrative response: {e}")
            return self._generate_fallback_narrative(analysis_results)
    
    def _enhance_narrative(self, narrative, analysis_results):
        insights = analysis_results.get("insights", {})
        
        for slide in narrative.get("slides", []):
            slide_title = slide.get("title", "").lower()
            
            for col, insight_data in insights.items():
                if insight_data.get("plot_path") and any(keyword in slide_title for keyword in [col.lower(), "finding", "analysis"]):
                    if "chart_references" not in slide:
                        slide["chart_references"] = []
                    slide["chart_references"].append(insight_data["plot_path"])
        
        return narrative
    
    def _create_structured_from_text(self, text, analysis_results):
        lines = [line.strip() for line in text.split('\\n') if line.strip()]
        
        slides = [
            {
                "title": "Data Analysis Overview",
                "content": lines[:3] if len(lines) >= 3 else lines,
                "chart_references": []
            }
        ]
        
        insights = analysis_results.get("insights", {})
        for i, (col, insight_data) in enumerate(list(insights.items())[:3]):
            slide = {
                "title": f"Analysis of {col}",
                "content": [
                    insight_data.get("insight", f"Analysis of {col}"),
                    f"Data type: {insight_data.get('type', 'unknown')}",
                    "Key statistical measures computed"
                ],
                "chart_references": [insight_data["plot_path"]] if insight_data.get("plot_path") else []
            }
            slides.append(slide)
        
        return {"slides": slides}
    
    def _generate_fallback_narrative(self, analysis_results):
        data_desc = analysis_results.get("data_description", {})
        insights = analysis_results.get("insights", {})
        correlations = analysis_results.get("correlation_analysis", {})
        
        slides = []
        
        slides.append({
            "title": "Data Analysis Report",
            "content": [
                f"Analysis of dataset with {data_desc.get('shape', [0, 0])[0]} rows and {data_desc.get('shape', [0, 0])[1]} columns",
                f"Generated on: {data_desc.get('filename', 'dataset')}",
                "Comprehensive statistical analysis and insights"
            ],
            "chart_references": []
        })
        
        slides.append({
            "title": "Dataset Overview",
            "content": [
                f"Total records: {data_desc.get('shape', [0, 0])[0]:,}",
                f"Total features: {data_desc.get('shape', [0, 0])[1]}",
                f"Missing values: {sum(data_desc.get('missing_values', {}).values())} across all columns",
                f"Key columns: {', '.join(data_desc.get('columns', [])[:5])}"
            ],
            "chart_references": []
        })
        
        for i, (col, insight_data) in enumerate(list(insights.items())[:3]):
            slide = {
                "title": f"Analysis: {col}",
                "content": [
                    insight_data.get("insight", f"Detailed analysis of {col}"),
                    f"Data type: {insight_data.get('type', 'unknown').title()}",
                    f"Statistical summary computed with {len(insight_data.get('statistics', {}))} metrics"
                ],
                "chart_references": [insight_data["plot_path"]] if insight_data.get("plot_path") else []
            }
            slides.append(slide)
        
        top_corr = correlations.get("top_correlations", [])[:3]
        if top_corr:
            slides.append({
                "title": "Key Relationships",
                "content": [
                    "Top correlations identified in the dataset:",
                    *[f"{corr['feature1']} and {corr['feature2']}: {corr['correlation']:.2f} ({corr['strength']} correlation)" 
                      for corr in top_corr]
                ],
                "chart_references": []
            })
        
        slides.append({
            "title": "Key Findings",
            "content": [
                f"Analyzed {len(insights)} features comprehensively",
                f"Generated {len([i for i in insights.values() if i.get('plot_path')])} visualizations",
                "Statistical insights reveal data patterns and distributions",
                "Ready for business decision making and further analysis"
            ],
            "chart_references": []
        })
        
        return {"slides": slides}''',

    # Continue creating more files...
}

# Continue with the rest of the files in the next part
print("Created file definitions for core backend services...")
print("Files included so far:")
for filename in all_files.keys():
    print(f"  ✅ {filename}")
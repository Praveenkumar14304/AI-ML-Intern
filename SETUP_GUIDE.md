# DataSlide - Complete Ready-to-Run Project

## 📦 What's Included

This zip file contains the complete DataSlide application - a CSV to PowerPoint converter with AI-powered insights using Mistral 7B.

## 🚀 Quick Setup & Run

### Step 1: Extract the Zip File
```bash
# Extract to your desired location
unzip DataSlide_Complete_Project.zip
cd DataSlide_Project
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

**Note**: First run will download Mistral 7B model (~13GB). Ensure:
- Stable internet connection
- At least 15GB free disk space  
- 8GB+ RAM recommended

### Step 3: Start the Application

**Option A: One Command (Recommended)**
```bash
python run.py
```

**Option B: Manual Start**
```bash
# Terminal 1 - Start Backend
cd backend
python main.py

# Terminal 2 - Start Frontend  
cd frontend
streamlit run app.py
```

### Step 4: Access the App
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000

## 📱 How to Use

1. **Upload CSV**: Drag & drop your CSV file
2. **Select Columns**: Choose which columns to analyze
3. **Pick Theme**: Select from 4 professional themes OR upload custom template
4. **Generate**: Click "Generate Presentation" 
5. **Download**: Get your professional PowerPoint!

## 🧪 Test with Sample Data

Use the included `sample_data.csv` to test the application immediately.

## 📊 Project Structure

```
DataSlide_Project/
├── frontend/
│   └── app.py                 # Streamlit UI
├── backend/
│   ├── main.py                # FastAPI server
│   ├── services/
│   │   ├── data_processor.py  # Data analysis
│   │   ├── llm_service.py     # Mistral 7B integration
│   │   └── ppt_generator.py   # PowerPoint creation
│   └── utils/
│       └── file_utils.py      # File handling
├── data/
│   ├── uploads/               # Uploaded files
│   ├── outputs/               # Generated presentations
│   └── plots/                 # Visualizations
├── requirements.txt           # Dependencies
├── run.py                     # One-click starter
├── sample_data.csv           # Test data
└── README.md                  # Full documentation
```

## 🛠 System Requirements

- **Python**: 3.8 or higher
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 15GB free space (for Mistral 7B model)
- **GPU**: Optional (CUDA-compatible for faster processing)

## 🔧 Troubleshooting

### Common Issues:

**1. Model Download Fails**
```bash
# Check internet connection and disk space
# Ensure at least 15GB free space
```

**2. Memory Issues**
- Use smaller CSV files for testing
- Close other applications
- Consider using CPU-only mode if GPU memory insufficient

**3. Port Conflicts**
- Backend uses port 8000
- Frontend uses port 8501
- Change in respective files if needed

**4. Installation Issues**
```bash
# Upgrade pip first
pip install --upgrade pip
pip install -r requirements.txt
```

## ⚡ Performance Tips

- **Large Files**: Select specific columns instead of all
- **Faster Processing**: Use datasets <10K rows for testing  
- **GPU Acceleration**: Automatically used if CUDA available
- **Custom Templates**: Upload your own .pptx templates for branding

## 🎯 Features

✅ **Modern UI** - Clean, professional interface  
✅ **AI-Powered** - Mistral 7B generates insights  
✅ **Data Analysis** - Comprehensive statistical analysis  
✅ **Visualizations** - Auto-generated charts and plots  
✅ **Professional Themes** - 4 built-in themes  
✅ **Custom Templates** - Upload your own PowerPoint templates  
✅ **Secure Processing** - All data processed locally  

## 💡 Next Steps

1. **Extract** the zip file
2. **Install** requirements: `pip install -r requirements.txt`  
3. **Run** the app: `python run.py`
4. **Open** http://localhost:8501 in your browser
5. **Upload** sample_data.csv to test
6. **Generate** your first presentation!

## 📞 Support

Check the detailed README.md file for comprehensive documentation, troubleshooting, and advanced configuration options.

---

**Ready to create professional presentations with AI! 🎯**
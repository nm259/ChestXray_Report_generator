# CheXagent AI - Chest X-Ray Analysis Web App

## 🏥 Overview
This is a Streamlit web application that uses AI to analyze chest X-rays and generate patient-friendly reports.

## 🚀 Installation

### Step 1: Clone or Download
Download all project files to a folder called `chexagent-webapp`

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv

# On Windows
venv\\Scripts\\activate

# On Mac/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up API Key
1. Get a Gemini API key from: https://makersuite.google.com/app/apikey
2. Create a `.env` file in the project root
3. Add your key: `GEMINI_API_KEY=your_key_here`

## 🎮 Running the App

### Option 1: With GPU (Recommended)
```bash
streamlit run app.py
```

### Option 2: CPU Only
```bash
streamlit run app.py
```
*Note: CPU mode is much slower (5-15 minutes per analysis)*

## 📝 How to Use

1. Open the app in your browser (usually http://localhost:8501)
2. Enter your Gemini API key in the sidebar
3. Upload a chest X-ray image (PNG or JPG)
4. Click "Analyze X-Ray"
5. Wait 30-60 seconds for results
6. Review the simplified report
7. Check accuracy metrics
8. Download reports if needed

## 🖥️ System Requirements

### Minimum (CPU):
- 8GB RAM
- Python 3.8+
- 10GB free disk space

### Recommended (GPU):
- NVIDIA GPU with 8GB+ VRAM
- 16GB RAM
- Python 3.8+
- CUDA 11.7+

## 📦 Project Structure
```
chexagent-webapp/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env                   # API keys (don't share!)
├── utils/
│   ├── __init__.py
│   └── model_loader.py   # Model loading utilities
└── README.md             # This file
```

## ⚠️ Important Notes

1. **Medical Disclaimer**: This tool is for educational purposes only. Always consult healthcare professionals.

2. **API Costs**: Gemini API has free tier limits. Check: https://ai.google.dev/pricing

3. **First Run**: The first time you run the app, it will download the 3B parameter model (~6GB). This takes 5-10 minutes.

4. **GPU vs CPU**: 
   - GPU: 30-60 seconds per analysis
   - CPU: 5-15 minutes per analysis

## 🐛 Troubleshooting

### "CUDA out of memory"
- Your GPU doesn't have enough VRAM
- Solution: Use CPU mode or a machine with more VRAM

### "Model download failed"
- Check your internet connection
- Try again (downloads can be interrupted)

### "API key invalid"
- Double-check your Gemini API key
- Make sure it's in the `.env` file correctly

### "Streamlit command not found"
- Make sure you activated the virtual environment
- Try: `python -m streamlit run app.py`

## 📧 Support
For issues, check:
- Streamlit docs: https://docs.streamlit.io
- CheXagent: https://github.com/Stanford-AIMI/CheXagent
- Gemini API: https://ai.google.dev/docs

## 📄 License
This project uses:
- CheXagent (Stanford AIMI)
- Google Gemini API
- Streamlit

Please review their respective licenses.
"""


# ============================================================
# FILE 7: .gitignore (Optional but recommended)
# ============================================================
"""
# Environment
venv/
env/
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Streamlit
.streamlit/

# Model cache
*.bin
*.pt
model_cache/

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
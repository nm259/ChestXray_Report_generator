import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
import google.generativeai as genai
from sentence_transformers import SentenceTransformer, util
import os
from dotenv import load_dotenv
import time
import re

load_dotenv()

st.set_page_config(
    page_title="CheXagent - AI Radiology Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state
if 'medical_report' not in st.session_state:
    st.session_state.medical_report = None
if 'layman_report' not in st.session_state:
    st.session_state.layman_report = None
if 'colab_connected' not in st.session_state:
    st.session_state.colab_connected = False
if 'analyzing' not in st.session_state:
    st.session_state.analyzing = False

# Custom CSS with Claude Sans font and animations
st.markdown("""
<style>
@import url('https://fonts.cdnfonts.com/css/claude-sans');

* {
    font-family: 'Claude Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.header-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 3rem 2rem;
    border-radius: 20px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    animation: slideDown 0.6s ease-out;
    position: relative;
    overflow: hidden;
}

.header-container::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: pulse 4s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.5; }
    50% { transform: translate(10px, 10px) scale(1.1); opacity: 0.8; }
}

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(30px); }
    to { opacity: 1; transform: translateX(0); }
}

.header-title {
    color: white;
    font-size: 3.5rem;
    font-weight: 700;
    text-align: center;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    position: relative;
    z-index: 1;
}

.header-subtitle {
    color: #E8EAF6;
    font-size: 1.3rem;
    text-align: center;
    margin-top: 0.5rem;
    position: relative;
    z-index: 1;
}

.report-card {
    background: white;
    padding: 2.5rem;
    border-radius: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    margin: 1.5rem 0;
    border-left: 6px solid #667eea;
    animation: fadeIn 0.6s ease-out;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.report-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
}

.medical-report-card {
    border-left: 6px solid #F44336;
}

.layman-report-card {
    border-left: 6px solid #4CAF50;
}

.comparison-card {
    border-left: 6px solid #FF9800;
}

.report-header {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    color: #1a1a1a;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.report-content {
    font-size: 1.05rem;
    line-height: 1.8;
    color: #333;
}

.report-content strong {
    color: #667eea;
    font-weight: 600;
}

.status-box {
    padding: 1.2rem;
    border-radius: 15px;
    margin: 1rem 0;
    text-align: center;
    font-weight: 600;
    font-size: 1.1rem;
    animation: fadeIn 0.5s ease-out;
    transition: all 0.3s ease;
}

.status-online {
    background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
    color: #2E7D32;
    border: 2px solid #4CAF50;
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2);
}

.status-offline {
    background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
    color: #C62828;
    border: 2px solid #F44336;
    box-shadow: 0 4px 15px rgba(244, 67, 54, 0.2);
}

.upload-section {
    animation: slideInLeft 0.6s ease-out;
}

.analysis-section {
    animation: slideInRight 0.6s ease-out;
}

.metric-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 20px;
    text-align: center;
    color: white;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    animation: fadeIn 0.8s ease-out;
}

.metric-value {
    font-size: 3.5rem;
    font-weight: 700;
    margin: 1rem 0;
}

.metric-label {
    font-size: 1.2rem;
    opacity: 0.9;
}

.section-divider {
    height: 3px;
    background: linear-gradient(90deg, transparent, #667eea, transparent);
    margin: 3rem 0;
    border-radius: 2px;
}

.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.8rem 2rem;
    font-size: 1.1rem;
    font-weight: 600;
    border-radius: 12px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 1rem;
}

.stTabs [data-baseweb="tab"] {
    padding: 1rem 2rem;
    font-size: 1.1rem;
    font-weight: 600;
    border-radius: 10px 10px 0 0;
}

.comparison-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin-top: 2rem;
}

@media (max-width: 768px) {
    .comparison-grid {
        grid-template-columns: 1fr;
    }
}

.accuracy-badge {
    display: inline-block;
    padding: 0.5rem 1.5rem;
    border-radius: 25px;
    font-weight: 600;
    font-size: 1rem;
    margin: 1rem 0;
}

.accuracy-high {
    background: #E8F5E9;
    color: #2E7D32;
    border: 2px solid #4CAF50;
}

.accuracy-moderate {
    background: #FFF3E0;
    color: #E65100;
    border: 2px solid #FF9800;
}

.accuracy-low {
    background: #FFEBEE;
    color: #C62828;
    border: 2px solid #F44336;
}

.loading-dots {
    display: inline-block;
    animation: loadingDots 1.5s infinite;
}

@keyframes loadingDots {
    0%, 20% { content: '.'; }
    40% { content: '..'; }
    60%, 100% { content: '...'; }
}

.image-container {
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    transition: transform 0.3s ease;
}

.image-container:hover {
    transform: scale(1.02);
}

.footer {
    text-align: center;
    color: #666;
    padding: 3rem 2rem;
    margin-top: 3rem;
    animation: fadeIn 1s ease-out;
}

.footer-title {
    font-size: 1.3rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.footer-tech {
    font-size: 1.1rem;
    margin: 0.5rem 0;
}

.footer-disclaimer {
    font-size: 0.9rem;
    opacity: 0.7;
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Helper function to convert markdown bold to HTML
def markdown_to_html(text):
    """Convert **bold** markdown to <strong>bold</strong> HTML"""
    # Replace **text** with <strong>text</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Replace newlines with <br>
    text = text.replace('\n', '<br>')
    return text

# ============================================================
# COLAB CONNECTION FUNCTIONS
# ============================================================

def test_colab_connection(url):
    """Test if Colab backend is reachable"""
    try:
        response = requests.get(url.replace('/analyze', '/'), timeout=5)
        return response.status_code == 200
    except:
        return False

def analyze_with_colab(image_file, colab_url):
    """Send image to Colab GPU for analysis"""
    
    # Convert image to base64
    buffered = BytesIO()
    image = Image.open(image_file)
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Call Colab API
    response = requests.post(
        colab_url,
        json={'image': img_str},
        timeout=120
    )
    
    result = response.json()
    
    if result.get('status') == 'success':
        return result['report']
    else:
        raise Exception(result.get('error', 'Unknown error'))

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("### 🔌 Colab GPU Connection")
    
    # Colab URL input
    colab_url = st.text_input(
        "Colab API URL",
        value=os.getenv("COLAB_API_URL", ""),
        placeholder="https://xxxx.ngrok-free.app/analyze",
        help="Paste the ngrok URL from your Colab notebook"
    )
    
    # Test connection
    if colab_url:
        if st.button("🔍 Test Connection"):
            with st.spinner("Testing..."):
                if test_colab_connection(colab_url):
                    st.session_state.colab_connected = True
                    st.success("✅ Connected to Colab GPU!")
                else:
                    st.session_state.colab_connected = False
                    st.error("❌ Cannot reach Colab backend")
        
        # Show status
        if st.session_state.colab_connected:
            st.markdown('<div class="status-box status-online">🟢 Colab GPU Online</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-box status-offline">🔴 Not Connected</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gemini API key
    st.markdown("### 🔑 Gemini API Key")
    api_key = st.text_input(
        "API Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="For translating to simple language"
    )
    
    if api_key:
        genai.configure(api_key=api_key)
        st.success("✅ API key configured")
    
    st.markdown("---")
    
    # Instructions
    st.markdown("### 📝 Setup Instructions")
    st.info("""
    **Step 1:** Open Google Colab
    
    **Step 2:** Upload `colab_backend.ipynb`
    
    **Step 3:** Enable GPU:
    - Runtime → Change runtime type
    - Hardware accelerator → GPU (T4)
    
    **Step 4:** Run all cells
    
    **Step 5:** Copy the ngrok URL
    
    **Step 6:** Paste URL above and click "Test Connection"
    
    **Step 7:** Upload X-ray and analyze!
    """)
    
    st.markdown("---")
    
    st.warning("""
    ⚠️ **Important:**
    - Keep Colab tab open while using
    - Free tier: 12 hour limit
    - URL changes each session
    """)

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="header-container">
    <h1 class="header-title">🏥 CheXagent AI</h1>
    <p class="header-subtitle">Advanced Chest X-Ray Analysis • Powered by Google Colab GPU</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# MAIN CONTENT - UPLOAD & ANALYZE
# ============================================================

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.markdown("### 📤 Upload X-Ray Image")
    
    uploaded_file = st.file_uploader(
        "Choose a chest X-ray image",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear chest X-ray image"
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        st.image(image, caption="Uploaded X-Ray", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.success(f"✅ Image uploaded: {image.size[0]} × {image.size[1]} pixels")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    st.markdown("### 🤖 Analysis")
    
    if uploaded_file is None:
        st.info("👈 Upload an X-ray image to begin")
    elif not colab_url:
        st.warning("⚠️ Configure Colab URL in sidebar first")
    elif not st.session_state.colab_connected:
        st.warning("⚠️ Test connection to Colab first")
    elif not api_key:
        st.warning("⚠️ Enter Gemini API key in sidebar")
    else:
        if st.button("🔍 Analyze X-Ray", use_container_width=True, type="primary"):
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Send to Colab GPU
                status_text.text("Step 1/3: Sending to Colab GPU...")
                progress_bar.progress(10)
                
                with st.spinner("🌐 Analyzing on Colab GPU (30-60 sec)..."):
                    medical_report = analyze_with_colab(uploaded_file, colab_url)
                    st.session_state.medical_report = medical_report
                
                progress_bar.progress(50)
                status_text.text("Step 2/3: Translating to simple language...")
                
                # Step 2: Translate
                with st.spinner("📝 Translating..."):
                    translation_model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    prompt = f"""You are a medical translator. Translate this medical report into simple, patient-friendly language that anyone can understand. Give direct response as you are actually giving the report.

Medical Report: {medical_report}

Provide a clear, layman translation:"""
                    
                    translation_response = translation_model.generate_content(prompt)
                    layman_report = translation_response.text
                    st.session_state.layman_report = layman_report
                
                progress_bar.progress(90)
                status_text.text("Step 3/3: Calculating accuracy...")
                
                # Step 3: Accuracy check
                time.sleep(1)
                
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                
                time.sleep(1)
                progress_bar.empty()
                status_text.empty()
                
                st.success("✅ Analysis complete!")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                progress_bar.empty()
                status_text.empty()
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# RESULTS SECTION (UPDATED WITH LLM-ONLY HALLUCINATION CHECK)
# ============================================================

if st.session_state.medical_report and st.session_state.layman_report:
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("## 📋 Analysis Results")
    
    # ------------------------------------------------------------
    # 1) Sentence Similarity Score (your current method)
    # ------------------------------------------------------------
    similarity_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    medical_embedding = similarity_model.encode(st.session_state.medical_report, convert_to_tensor=True)
    layman_embedding = similarity_model.encode(st.session_state.layman_report, convert_to_tensor=True)
    similarity_score = util.cos_sim(medical_embedding, layman_embedding).item()

    # ------------------------------------------------------------
    # 2) LLM-ONLY Hallucination / Difference Check
    # ------------------------------------------------------------
    with st.spinner("🔍 Checking report accuracy..."):
        analysis_model = genai.GenerativeModel('gemini-2.5-flash')

        comparison_prompt = f"""
You are a medical analysis expert LLM.

Two reports are provided:
- Report A = Original medical report  
- Report B = Layman translation generated by another LLM  

Your ONLY job:
- Decide if Report B contains *hallucinations* (incorrect additions NOT in Report A).  
- Normal explanation or simplification is allowed.  
- Only WRONG MEDICAL ADDITIONS count as hallucinations.

Return EXACTLY this format:

Hallucinated: YES or NO  
Difference: HIGH / MEDIUM / LOW  
Explanation: <short explanation>  
Hallucination Score: <0-100 number>

-----------------
Report A:
{st.session_state.medical_report}

Report B:
{st.session_state.layman_report}
"""

        analysis_response = analysis_model.generate_content(comparison_prompt)
        analysis_text = analysis_response.text

        # ---- PARSE OUTPUT ----
        hallucinated = "UNKNOWN"
        difference = "UNKNOWN"
        explanation = "No explanation found."
        hallucination_score = 0

        for line in analysis_text.split("\n"):
            line = line.strip()
            if line.lower().startswith("hallucinated:"):
                hallucinated = line.split(":")[1].strip()
            elif line.lower().startswith("difference:"):
                difference = line.split(":")[1].strip()
            elif line.lower().startswith("explanation:"):
                explanation = line.split(":", 1)[1].strip()
            elif "hallucination score" in line.lower():
                try:
                    hallucination_score = int(line.split(":")[1].strip())
                except:
                    hallucination_score = 0

    # ------------------------------------------------------------
    # MEDICAL REPORT CARD
    # ------------------------------------------------------------
    st.markdown("### 🔬 Medical Report")
    medical_html = markdown_to_html(st.session_state.medical_report)
    st.markdown(f"""
    <div class="report-card medical-report-card">
        <div class="report-header"><span>🔬</span> Technical Medical Analysis</div>
        <div class="report-content">{medical_html}</div>
    </div>
    """, unsafe_allow_html=True)

    st.download_button(
        label="📥 Download",
        data=st.session_state.medical_report,
        file_name="medical_report.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------------------
    # LAYMAN REPORT CARD
    # ------------------------------------------------------------
    st.markdown("### 📝 Patient-Friendly Report")
    layman_html = markdown_to_html(st.session_state.layman_report)
    st.markdown(f"""
    <div class="report-card layman-report-card">
        <div class="report-header"><span>📝</span> Simplified Explanation</div>
        <div class="report-content">{layman_html}</div>
    </div>
    """, unsafe_allow_html=True)

    st.download_button(
        label="📥 Download",
        data=st.session_state.layman_report,
        file_name="patient_report.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)



    # ------------------------------------------------------------
    # HALLUCINATION CHECK RESULTS (LLM ONLY)
    # ------------------------------------------------------------
    st.markdown("### 🤖 LLM Consistency & Hallucination Check")

    st.markdown(f"""
    <div class="report-card comparison-card">
        <div class="report-header"><span>🧠</span> AI Hallucination Analysis</div>
        <div class="report-content">
            <strong>Hallucinated:</strong> {hallucinated}<br>
            <strong>Difference:</strong> {difference}<br>
            <strong>Explanation:</strong> {explanation}<br><br>
            <strong>Hallucination Score:</strong> {hallucination_score} / 100
        </div>
    </div>
    """, unsafe_allow_html=True)

    if hallucination_score <= 20:
        hall_class = "accuracy-high"
        hall_text = "🟢 No significant hallucination"
    elif hallucination_score <= 50:
        hall_class = "accuracy-moderate"
        hall_text = "🟡 Minor hallucinations detected"
    else:
        hall_class = "accuracy-low"
        hall_text = "🔴 Significant hallucinations found"

    st.markdown(f"""
    <div style="text-align:center;">
        <span class="accuracy-badge {hall_class}">{hall_text}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)



# ============================================================
# FOOTER
# ============================================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <p class="footer-title"><strong>CheXagent AI - Chest X-Ray Analysis Assistant</strong></p>
    <p class="footer-tech">🖥️ Frontend: Local Streamlit | 🚀 Backend: Google Colab GPU | 🤖 AI: CheXagent-2-3b + Gemini</p>
    <p class="footer-disclaimer">⚠️ For educational and research purposes only • Not a substitute for professional medical advice</p>
</div>
""", unsafe_allow_html=True)
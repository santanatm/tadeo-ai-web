import streamlit as st
from groq import Groq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from fpdf import FPDF
import io

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Tadeo AI", page_icon="🤖", layout="centered")

# Premium CSS Customization
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {display: none !important;}
    header {display: none !important;}
    .block-container {padding-top: 1rem !important;}
    
    /* File Uploader Style */
    .stFileUploader section {
        border: 1px solid #bfa34b !important;
        border-radius: 5px;
    }
    /* PDF Download Button Style */
    .stDownloadButton > button {
        background-color: #333333 !important;
        color: #bfa34b !important;
        border: 1px solid #bfa34b !important;
        width: 100%;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INTERFACE: PHOTO AND TITLE
col_foto, col_titulo = st.columns([1, 5]) 
with col_foto:
    try:
        st.image("Tadeo_Santana.png", width=60) 
    except:
        st.write("🤖")
with col_titulo:
    st.markdown("<h1 style='margin-top: -10px;'>TADEO AI</h1>", unsafe_allow_html=True)

# 3. KEYS AND ENGINES CONFIGURATION
GROQ_KEY = st.secrets.get("GROQ_API_KEY")
TAVILY_KEY = st.secrets.get("TAVILY_API_KEY")

if not GROQ_KEY or not TAVILY_KEY:
    st.error("API Keys missing in Secrets.")
    st.stop()

try:
    client = Groq(api_key=GROQ_KEY)
    api_wrapper = TavilySearchAPIWrapper(tavily_api_key=TAVILY_KEY)
    search = TavilySearchResults(api_wrapper=api_wrapper)
except Exception as e:
    st.error(f"Initialization error: {e}")

# 4. PDF GENERATION FUNCTION
def crear_pdf(texto, consulta):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Tadeo AI Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.multi_cell(0, 10, txt=f"Analysis/Question: {consulta}")
    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    texto_seguro = texto.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=texto_seguro)
    return pdf.output(dest='S').encode('latin-1')

# 5. INPUT SECTION
# File uploader (Triggers script rerun on change)
archivo_subido = st.file_uploader("Upload a file to analyze", type=['pdf', 'txt', 'docx'])

# Text input (Triggers script rerun on Enter)
pregunta = st.text_input("", placeholder="What do you want to know?   (e.g. Who was Albert Einstein?)", key="user_input")

# 6. AUTOMATIC EXECUTION LOGIC
# Executes if there is a question OR if a file has just been uploaded
if pregunta or archivo_subido:
    with st.spinner("Tadeo is processing your request..."):
        try:
            # Process file context
            contenido_archivo = ""
            label_consulta = pregunta if pregunta else f"Automatic analysis of: {archivo_subido.name}"
            
            if archivo_subido:
                # Basic file info as context
                contenido_archivo = f"\n[Document attached for analysis: {archivo_subido.name}]"
            
            # Web search logic (only if there is a text query)
            try:
                if pregunta:
                    resultados_raw = search.run(pregunta)
                else:
                    resultados_raw = f"General analysis requested for file: {archivo_subido.name}"
                
                if "401" in str(resultados_raw) or "Unauthorized" in str(resultados_raw):
                    resultados_raw = "No recent web data available."
            except:
                resultados_raw = "No recent web data available."

            # AI Response Generation
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "You are Tadeo AI, an expert assistant. Respond in English. If a file is provided, prioritize its analysis. Ignore technical API errors."
                    },
                    {"role": "user", "content": f"Context: {resultados_raw}{contenido_archivo}\n\nTask/Question: {label_consulta}"}
                ],
                model="llama-3.3-70b-versatile",
            )
            
            respuesta_final = chat_completion.choices[0].message.content
            st.subheader("📝 Result:")
            st.write(respuesta_final)
            
            # PDF Download Button
            pdf_bytes = crear_pdf(respuesta_final, label_consulta)
            st.download_button(
                label="📥 Download report as PDF", 
                data=pdf_bytes, 
                file_name="Tadeo_AI_Report.pdf", 
                mime="application/pdf"
            )
            
        except Exception as e:
            st.error(f"An error occurred: {e}")

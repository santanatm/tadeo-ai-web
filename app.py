import streamlit as st
from groq import Groq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from fpdf import FPDF
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io
import base64

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Tadeo AI", page_icon="🤖", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {display: none !important;}
    header {display: none !important;}
    .block-container {padding-top: 1rem !important;}
    .stFileUploader section { border: 1px solid #bfa34b !important; border-radius: 5px; }
    .stDownloadButton > button { background-color: #333333 !important; color: #bfa34b !important; border: 1px solid #bfa34b !important; width: 100%; font-weight: bold; }
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

# 3. KEYS AND ENGINES
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

# 4. UTILITY FUNCTIONS
def crear_pdf(texto, consulta):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Tadeo AI Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.multi_cell(0, 10, txt=f"Question: {consulta}")
    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    texto_seguro = texto.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=texto_seguro)
    return pdf.output(dest='S').encode('latin-1')

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

# 5. MULTIMODAL INPUT
archivo_subido = st.file_uploader("Upload a file to analyze", type=['pdf', 'txt', 'docx'])

# Voice Dictation Column
col_text, col_mic = st.columns([0.9, 0.1])
with col_mic:
    st.write("") # Alignment
    audio_input = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='recorder')

# Text Input
input_text = ""
if audio_input:
    input_text = audio_input['text']

pregunta = st.text_input("", value=input_text, placeholder="What do you want to know? (e.g. Who was Albert Einstein?)", key="user_input")

# 6. EXECUTION LOGIC
if pregunta:
    with st.spinner("Tadeo is processing your request..."):
        try:
            contenido_archivo = f"\n[Attached document: {archivo_subido.name}]" if archivo_subido else ""
            
            try:
                resultados_raw = search.run(pregunta)
                if "401" in str(resultados_raw): resultados_raw = "No recent web data available."
            except:
                resultados_raw = "No recent web data available."

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are Tadeo AI. Respond in English. Analyze files if attached. Ignore API errors."},
                    {"role": "user", "content": f"Context: {resultados_raw}{contenido_archivo}\n\nQuestion: {pregunta}"}
                ],
                model="llama-3.3-70b-versatile",
            )
            
            respuesta_final = chat_completion.choices[0].message.content
            st.subheader("📝 Result:")
            st.write(respuesta_final)
            
            # Listen to the Answer
            if st.button("🔊 Listen to the answer"):
                audio_fp = text_to_speech(respuesta_final)
                st.audio(audio_fp, format='audio/mp3')
            
            # PDF Download
            pdf_bytes = crear_pdf(respuesta_final, pregunta)
            st.download_button(label="📥 Download report as PDF", data=pdf_bytes, file_name="Tadeo_AI_Report.pdf", mime="application/pdf")
            
        except Exception as e:
            st.error(f"An error occurred: {e}")

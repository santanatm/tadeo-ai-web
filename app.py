import streamlit as st
from groq import Groq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from fpdf import FPDF
import io

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tadeo AI", page_icon="🤖", layout="centered")

# Estilo CSS para personalización premium
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {display: none !important;}
    header {display: none !important;}
    .block-container {padding-top: 1rem !important;}
    
    /* Estilo para el área de carga de archivos y botones multimedia */
    .stFileUploader section {
        border: 1px solid #bfa34b !important;
        border-radius: 5px;
    }
    .stDownloadButton > button {
        background-color: #333333 !important;
        color: #bfa34b !important;
        border: 1px solid #bfa34b !important;
        width: 100%;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INTERFAZ: FOTO Y TÍTULO
col_foto, col_titulo = st.columns([1, 5]) 
with col_foto:
    try:
        st.image("Tadeo_Santana.png", width=60) 
    except:
        st.write("🤖")
with col_titulo:
    st.markdown("<h1 style='margin-top: -10px;'>TADEO AI</h1>", unsafe_allow_html=True)

# 3. CONFIGURACIÓN DE LLAVES Y MOTORES
GROQ_KEY = st.secrets.get("GROQ_API_KEY")
TAVILY_KEY = st.secrets.get("TAVILY_API_KEY")

if not GROQ_KEY or not TAVILY_KEY:
    st.error("Faltan llaves API en Secrets.")
    st.stop()

try:
    client = Groq(api_key=GROQ_KEY)
    api_wrapper = TavilySearchAPIWrapper(tavily_api_key=TAVILY_KEY)
    search = TavilySearchResults(api_wrapper=api_wrapper)
except Exception as e:
    st.error(f"Error de inicio: {e}")

# 4. FUNCIÓN PARA GENERAR PDF
def crear_pdf(texto, consulta):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Tadeo AI Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.multi_cell(0, 10, txt=f"Pregunta: {consulta}")
    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    texto_seguro = texto.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=texto_seguro)
    return pdf.output(dest='S').encode('latin-1')

# 5. ENTRADA MULTIMODAL
archivo_subido = st.file_uploader("", type=['pdf', 'txt', 'docx'])

# Al presionar ENTER en este campo, Streamlit recarga la página y 'pregunta' deja de estar vacía
pregunta = st.text_input("", placeholder="What do you want to know?   (e.g. Who was Albert Einstein?)", key="user_input")

# Botones visuales (decorativos o para funciones futuras)
col_v1, col_v2, col_v3 = st.columns([1, 1, 8])
with col_v1:
    st.button("🎤", help="Voice Dictation")
with col_v2:
    st.button("🔊", help="Listen to the answer")

# 6. LÓGICA DE EJECUCIÓN AUTOMÁTICA (Al detectar texto en 'pregunta')
if pregunta:
    with st.spinner("Tadeo is processing your request...."):
        try:
            # Procesar contexto de archivo si existe
            contenido_archivo = ""
            if archivo_subido:
                contenido_archivo = f"\n[Documento adjunto detectado: {archivo_subido.name}]"
            
            # Búsqueda web con protección contra errores 401
            try:
                resultados_raw = search.run(pregunta)
                if "401" in str(resultados_raw) or "Unauthorized" in str(resultados_raw):
                    resultados_raw = "No recent web data is available at the moment."
            except:
                resultados_raw = "No recent web data is available at the moment."

            # Generación de respuesta con Llama 3.3
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "Eres Tadeo AI. Responde en español de forma experta. Si hay un archivo adjunto, analízalo. Ignora errores técnicos de API."
                    },
                    {"role": "user", "content": f"Contexto: {resultados_raw}{contenido_archivo}\n\nPregunta: {pregunta}"}
                ],
                model="llama-3.3-70b-versatile",
            )
            
            respuesta_final = chat_completion.choices[0].message.content
            st.subheader("📝 Result found:")
            st.write(respuesta_final)
            
            # Botón de descarga PDF (aparece solo después del resultado)
            pdf_bytes = crear_pdf(respuesta_final, pregunta)
            st.download_button(
                label="📥 Download result as PDF", 
                data=pdf_bytes, 
                file_name="Tadeo_AI_Report.pdf", 
                mime="application/pdf"
            )
            
        except Exception as e:
            st.error(f"There was a problem.: {e}")
elif archivo_subido and not pregunta:
    st.info("Write a question about the file you uploaded and press ENTER.")

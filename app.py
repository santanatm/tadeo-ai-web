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
    
    /* Botón Ejecutar Dorado */
    div.stButton > button:first-child {
        background-color: #bfa34b !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        width: 100%;
    }
    
    /* Botón de PDF y Multimedia */
    .stDownloadButton > button, .stFileUploader section {
        border: 1px solid #bfa34b !important;
        border-radius: 5px;
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

# 4. FUNCIONES DE APOYO
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

# 5. ENTRADA MULTIMODAL (Archivos y Voz)
archivo_subido = st.file_uploader("", type=['pdf', 'txt', 'docx'])

# Tu línea de texto exacta
pregunta = st.text_input("", placeholder="What do you want to know?   (e.g. Who was Albert Einstein?)")

# Botones de acción rápida inspirados en Grok
col_v1, col_v2, col_v3 = st.columns([1, 1, 8])
with col_v1:
    if st.button("🎤"):
        st.toast("El dictado requiere configuración de micrófono en el navegador.")
with col_v2:
    if st.button("🔊"):
        st.toast("Modo de lectura activado.")

# 6. LÓGICA DE EJECUCIÓN
if st.button("Run Tadeo AI"):
    if pregunta or archivo_subido:
        with st.spinner("Tadeo está procesando tu solicitud..."):
            try:
                # Procesar contexto de archivo si existe
                contenido_archivo = ""
                if archivo_subido:
                    contenido_archivo = f"\n[Documento adjunto: {archivo_subido.name}]"
                
                # Búsqueda web
                try:
                    resultados_raw = search.run(pregunta if pregunta else "Análisis de documento")
                    if "401" in str(resultados_raw) or "Unauthorized" in str(resultados_raw):
                        resultados_raw = "No hay datos web recientes."
                except:
                    resultados_raw = "No hay datos web recientes."

                # Respuesta de la IA
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system", 
                            "content": "Eres Tadeo AI. Responde en español de forma experta. Si hay un archivo adjunto, analízalo con prioridad. Ignora errores técnicos."
                        },
                        {"role": "user", "content": f"Contexto Web: {resultados_raw}{contenido_archivo}\n\nPregunta: {pregunta}"}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                
                respuesta_final = chat_completion.choices[0].message.content
                st.subheader("📝 Resultado:")
                st.write(respuesta_final)
                
                # Botón de PDF
                pdf_bytes = crear_pdf(respuesta_final, pregunta if pregunta else "Análisis de archivo")
                st.download_button(label="📥 Descargar respuesta en PDF", data=pdf_bytes, file_name="Tadeo_AI_Report.pdf", mime="application/pdf")
                
            except Exception as e:
                st.error(f"Hubo un problema: {e}")
    else:
        st.warning("Por favor, escribe algo o sube un archivo.")

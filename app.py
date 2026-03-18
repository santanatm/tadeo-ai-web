import streamlit as st
from groq import Groq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tadeo AI", page_icon="🤖", layout="centered")

# Estilo CSS para limpieza visual y personalización de botones
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {display: none !important;}
    header {display: none !important;}
    .block-container {padding-top: 1rem !important;}
    
    /* Botón 'Ejecutar' Dorado */
    div.stButton > button:first-child {
        background-color: #bfa34b !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        width: 100%;
        border-radius: 5px;
    }
    
    /* Botón de PDF con estilo elegante */
    .stDownloadButton > button {
        background-color: #333333 !important;
        color: #bfa34b !important;
        border: 1px solid #bfa34b !important;
        width: 100%;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 TADEO AI")

# 2. EXTRACCIÓN DE LLAVES DESDE SECRETS
GROQ_KEY = st.secrets.get("GROQ_API_KEY")
TAVILY_KEY = st.secrets.get("TAVILY_API_KEY")

if not GROQ_KEY or not TAVILY_KEY:
    st.error("❌ Faltan llaves API en la configuración de Secrets.")
    st.stop()

# 3. FUNCIÓN PARA GENERAR EL PDF
def crear_pdf(texto, consulta):
    pdf = FPDF()
    pdf.add_page()
    # Encabezado
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Informe de Investigación - Tadeo AI", ln=True, align='C')
    pdf.ln(10)
    
    # Pregunta original
    pdf.set_font("Arial", 'B', 12)
    pdf.multi_cell(0, 10, txt=f"Pregunta: {consulta}")
    pdf.ln(5)
    
    # Respuesta (con limpieza de caracteres para evitar errores de codificación)
    pdf.set_font("Arial", size=11)
    texto_seguro = texto.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=texto_seguro)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(200, 10, txt="Generado por tadeosantana.com", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# 4. INICIALIZAR MOTORES
try:
    client = Groq(api_key=GROQ_KEY)
    api_wrapper = TavilySearchAPIWrapper(tavily_api_key=TAVILY_KEY)
    search = TavilySearchResults(api_wrapper=api_wrapper)
except Exception as e:
    st.error(f"Error de inicio: {e}")

# 5. INTERFAZ (Tu línea personalizada con el ejemplo)
pregunta = st.text_input("¿Qué quieres investigar hoy?", placeholder="Ej: ¿Quién fue Albert Einstein?")

if st.button("Ejecutar Tadeo AI"):
    if pregunta:
        with st.spinner("Investigando en tiempo real..."):
            try:
                # Paso 1: Búsqueda y control de errores del buscador
                try:
                    resultados_raw = search.run(pregunta)
                    error_tavily = False
                except Exception:
                    # Si falla el buscador (como el error 401), avisamos pero seguimos con la IA
                    st.error("⚠️ Error de conexión con el buscador (Tavily).")
                    st.info("La respuesta se basará en mi base de conocimientos interna.")
                    resultados_raw = "Error en el buscador. Responde con tu conocimiento general."
                    error_tavily = True

                # Paso 2: Generación con la IA
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "Eres Tadeo AI. Responde siempre en español. "
                                "Si recibes datos de búsqueda, úsalos para ser más preciso. "
                                "Si los datos indican un error técnico, ignóralo y responde con tu conocimiento."
                            )
                        },
                        {"role": "user", "content": f"Contexto: {resultados_raw}\n\nPregunta: {pregunta}"}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                
                respuesta_final = chat_completion.choices[0].message.content
                st.subheader("📝 Resultado:")
                st.write(respuesta_final)
                
                # --- BOTÓN DE DESCARGA PDF ---
                pdf_bytes = crear_pdf(respuesta_final, pregunta)
                st.download_button(
                    label="📥 Descargar esta respuesta en PDF",
                    data=pdf_bytes,
                    file_name="investigacion_tadeo_ai.pdf",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"Hubo un problema: {e}")
    else:
        st.warning("Por favor, escribe una pregunta primero.")

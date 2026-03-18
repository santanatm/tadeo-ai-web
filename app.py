import streamlit as st
from groq import Groq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tadeo AI", page_icon="🤖", layout="centered")

# Estilo CSS para limpieza y botones dorados
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {display: none !important;}
    header {display: none !important;}
    .block-container {padding-top: 1rem !important;}
    
    /* Botón principal dorado */
    div.stButton > button:first-child {
        background-color: #bfa34b !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        width: 100%;
    }
    
    /* Estilo para el botón de descarga (secundario) */
    .stDownloadButton > button {
        background-color: #333333 !important;
        color: #bfa34b !important;
        border: 1px solid #bfa34b !important;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 TADEO AI")

# 2. LLAVES API
GROQ_KEY = st.secrets.get("GROQ_API_KEY")
TAVILY_KEY = st.secrets.get("TAVILY_API_KEY")

if not GROQ_KEY or not TAVILY_KEY:
    st.error("❌ Faltan llaves API en los Secrets de Streamlit.")
    st.stop()

# 3. FUNCIÓN PARA GENERAR PDF
def generar_pdf(texto_respuesta, usuario_pregunta):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Informe de Tadeo AI", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.multi_cell(0, 10, txt=f"Pregunta: {usuario_pregunta}")
    pdf.ln(5)
    
    pdf.set_font("Arial", size=11)
    # Reemplazamos caracteres no compatibles con latin-1 para evitar errores
    texto_limpio = texto_respuesta.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=texto_limpio)
    
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

# 5. INTERFAZ DE USUARIO
pregunta = st.text_input("¿Qué quieres investigar hoy?", placeholder="Ej: ¿Quién fue Albert Einstein?")

if st.button("Ejecutar Tadeo AI"):
    if pregunta:
        with st.spinner("Investigando en tiempo real..."):
            try:
                # Paso 1: Búsqueda
                resultados_raw = search.run(pregunta)
                
                # Verificamos si la búsqueda falló por autenticación (Error 401)
                if "401" in str(resultados_raw) or "Unauthorized" in str(resultados_raw):
                    st.error("⚠️ Error de conexión con el buscador (Tavily).")
                    st.info("Tu API Key de Tavily parece no ser válida. Por favor, revísala en los Secrets.")
                    # Si falla la búsqueda, usamos conocimiento general de la IA sin confundirla
                    resultados_raw = "No se pudieron obtener datos actuales. Responde con tu base de conocimientos."

                # Paso 2: Generación con la IA
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system", 
                            "content": "Eres Tadeo AI. Responde de forma experta en español. Si recibes datos de búsqueda, úsalos. Ignora mensajes de error técnico en los datos."
                        },
                        {"role": "user", "content": f"Datos: {resultados_raw}\n\nPregunta: {pregunta}"}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                
                respuesta_final = chat_completion.choices[0].message.content
                st.subheader("📝 Resultado:")
                st.write(respuesta_final)
                
                # --- BOTÓN DE DESCARGA PDF ---
                pdf_bytes = generar_pdf(respuesta_final, pregunta)
                st.download_button(
                    label="📥 Descargar esta respuesta en PDF",
                    data=pdf_bytes,
                    file_name="respuesta_tadeo_ai.pdf",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"Error en la investigación: {e}")
    else:
        st.warning("Por favor, escribe una pregunta primero.")

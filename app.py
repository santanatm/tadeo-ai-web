import streamlit as st
from groq import Groq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tadeo AI", page_icon="🤖", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {display: none !important;}
    header {display: none !important;}
    .block-container {padding-top: 1rem !important;}
    div.stButton > button:first-child {
        background-color: #bfa34b !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        width: 100%;
    }
    .stDownloadButton > button {
        background-color: #333333 !important;
        color: #bfa34b !important;
        border: 1px solid #bfa34b !important;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

#st.title("🤖 TADEO AI")
# 4. INTERFAZ DE USUARIO personalizada
try:
    st.image("Tadeo_Santana.png", width=50) 
except:
    st.write("🤖") # Icono de respaldo si la foto no carga

st.title("TADEO AI")

# 2. LLAVES API
GROQ_KEY = st.secrets.get("GROQ_API_KEY")
TAVILY_KEY = st.secrets.get("TAVILY_API_KEY")

if not GROQ_KEY or not TAVILY_KEY:
    st.error("Faltan llaves API en Secrets.")
    st.stop()

# 3. FUNCIÓN PDF
def crear_pdf(texto, consulta):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Informe de Tadeo AI", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.multi_cell(0, 10, txt=f"Pregunta: {consulta}")
    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    texto_seguro = texto.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=texto_seguro)
    return pdf.output(dest='S').encode('latin-1')

# 4. INICIALIZAR
try:
    client = Groq(api_key=GROQ_KEY)
    api_wrapper = TavilySearchAPIWrapper(tavily_api_key=TAVILY_KEY)
    search = TavilySearchResults(api_wrapper=api_wrapper)
except Exception as e:
    st.error(f"Error de inicio: {e}")

# 5. INTERFAZ
pregunta = st.text_input("¿Qué quieres investigar hoy?", placeholder="Ej: ¿Quién fue Albert Einstein?")

if st.button("Ejecutar Tadeo AI"):
    if pregunta:
        with st.spinner("Investigando..."):
            try:
                # PASO 1: Búsqueda con filtro de error
                try:
                    resultados_raw = search.run(pregunta)
                    # Si el resultado contiene palabras de error, lo vaciamos
                    if "401" in str(resultados_raw) or "Unauthorized" in str(resultados_raw):
                        resultados_raw = "No hay datos recientes disponibles."
                except:
                    resultados_raw = "No hay datos recientes disponibles."

                # PASO 2: Respuesta de la IA
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system", 
                            "content": "Eres Tadeo AI. Responde en español de forma directa. IGNORA cualquier mensaje de error técnico. Si no tienes datos nuevos, usa tu conocimiento general sin mencionar fallos de API."
                        },
                        {"role": "user", "content": f"Contexto: {resultados_raw}\n\nPregunta: {pregunta}"}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                
                respuesta_final = chat_completion.choices[0].message.content
                st.subheader("📝 Resultado:")
                st.write(respuesta_final)
                
                # Botón de PDF
                pdf_bytes = crear_pdf(respuesta_final, pregunta)
                st.download_button(label="📥 Descargar respuesta en PDF", data=pdf_bytes, file_name="Tadeo_AI_Informe.pdf", mime="application/pdf")
                
            except Exception as e:
                st.error(f"Hubo un problema: {e}")
    else:
        st.warning("Escribe una pregunta primero.")



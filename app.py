import streamlit as st
from groq import Groq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from fpdf import FPDF

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tadeo AI", page_icon="🤖", layout="centered")

# Estilo CSS para limpieza y botón dorado
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
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 TADEO AI")

# 2. LLAVES API
GROQ_KEY = st.secrets.get("GROQ_API_KEY")
TAVILY_KEY = st.secrets.get("TAVILY_API_KEY")

if not GROQ_KEY or not TAVILY_KEY:
    st.error("Faltan llaves API en Secrets.")
    st.stop()

# 3. FUNCIÓN PARA GENERAR PDF
def generar_pdf(texto_respuesta, usuario_pregunta):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Informe de Tadeo AI", ln=True, align='C')
    pdf.ln(10)
    
    # Pregunta del usuario
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Pregunta: {usuario_pregunta}", ln=True)
    pdf.ln(5)
    
    # Respuesta
    pdf.set_font("Arial", size=11)
    # Multi_cell se encarga de que el texto no se salga de la hoja
    pdf.multi_cell(0, 10, txt=texto_respuesta)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(200, 10, txt="Generado por tadeosantana.com", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# 4. INICIALIZAR MOTORES
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
                resultados = search.run(pregunta)
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": f"Eres Tadeo AI. Responde en español usando estos datos: {resultados}"},
                        {"role": "user", "content": pregunta}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                
                respuesta_texto = chat_completion.choices[0].message.content
                st.subheader("📝 Resultado:")
                st.write(respuesta_texto)
                
                # --- BOTÓN DE DESCARGA PDF ---
                pdf_data = generar_pdf(respuesta_texto, pregunta)
                st.download_button(
                    label="📥 Descargar respuesta en PDF",
                    data=pdf_data,
                    file_name="respuesta_tadeo_ai.pdf",
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Por favor, escribe una pregunta primero.")

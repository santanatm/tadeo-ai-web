import streamlit as st
from groq import Groq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tadeo AI", page_icon="🤖", layout="centered")

# Estilo CSS para eliminar el espacio superior y preparar el recorte inferior
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {display: none !important;}
    header {display: none !important;}
    
    /* Eliminar el padding para que el contenido empiece desde arriba */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    
    /* Estilo del Botón Dorado */
    div.stButton > button:first-child {
        background-color: #bfa34b !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
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

# 3. INICIALIZAR
try:
    client = Groq(api_key=GROQ_KEY)
    api_wrapper = TavilySearchAPIWrapper(tavily_api_key=TAVILY_KEY)
    search = TavilySearchResults(api_wrapper=api_wrapper)
except Exception as e:
    st.error(f"Error: {e}")

# 4. INTERFAZ
pregunta = st.text_input("¿Qué quieres investigar hoy?", placeholder="Escribe aquí...")

if st.button("Ejecutar Tadeo AI"):
    if pregunta:
        with st.spinner("Investigando..."):
            try:
                resultados = search.run(pregunta)
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": f"Eres Tadeo AI. Responde usando estos datos: {resultados}"},
                        {"role": "user", "content": pregunta}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                st.subheader("📝 Resultado:")
                st.write(chat_completion.choices[0].message.content)
            except Exception as e:
                st.error(f"Error: {e}")

import streamlit as st
import google.generativeai as genai
from langchain_community.tools.tavily_search import TavilySearchResults
import os
import warnings

warnings.filterwarnings("ignore")

# --- CONFIGURACIÓN DE SEGURIDAD (OCULTANDO LLAVES) ---
# Streamlit leerá estas llaves desde su panel de configuración, no desde el código.
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)

if "TAVILY_API_KEY" in st.secrets:
    os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]

# --- INTERFAZ ---
st.set_page_config(page_title="Tadeo AI", page_icon="🤖")

st.title("🤖 TADEO AI")
st.markdown("### Tu Asistente de Investigación en tadeosantana.com")

# Inicializar herramientas
model = genai.GenerativeModel('gemini-2.0-flash')
search = TavilySearchResults(max_results=3)

pregunta = st.text_input("¿Qué quieres investigar hoy?", placeholder="Escribe aquí...")

if st.button("Ejecutar Tadeo AI"):
    if pregunta:
        with st.spinner("Buscando en tiempo real..."):
            try:
                # 1. Búsqueda con Tavily
                busqueda = search.run(pregunta)
                
                # 2. Procesamiento con Gemini
                prompt = f"Datos de internet: {busqueda}\nPregunta: {pregunta}"
                respuesta = model.generate_content(prompt)
                
                st.subheader("📝 Resultado:")
                st.write(respuesta.text)
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ Cupo diario agotado. Intenta de nuevo mañana.")
                else:
                    st.error(f"Error: {e}")

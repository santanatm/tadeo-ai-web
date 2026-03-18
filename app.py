import streamlit as st
import google.generativeai as genai
from langchain_community.tools.tavily_search import TavilySearchResults
import os

# 1. CARGAR SECRETOS PRIMERO (Antes de cualquier otra cosa)
# Esto evita el error de Pydantic
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

if "TAVILY_API_KEY" in st.secrets:
    # Esta línea es la que arregla el error que ves en pantalla
    os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]

# 2. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tadeo AI", page_icon="🤖")

st.title("🤖 TADEO AI")
st.markdown("### Tu Asistente en tadeosantana.com")

# 3. INICIALIZAR HERRAMIENTAS (Ahora con las llaves ya cargadas)
try:
    model = genai.GenerativeModel('gemini-2.0-flash')
    search = TavilySearchResults(max_results=3)
except Exception as e:
    st.error(f"Error al inicializar herramientas: {e}")

# INTERFAZ
pregunta = st.text_input("¿Qué quieres investigar hoy?", placeholder="Escribe aquí...")

if st.button("Ejecutar Tadeo AI"):
    if pregunta:
        with st.spinner("Buscando en tiempo real..."):
            try:
                busqueda = search.run(pregunta)
                prompt = f"Datos de internet: {busqueda}\nPregunta: {pregunta}"
                respuesta = model.generate_content(prompt)
                
                st.subheader("📝 Resultado:")
                st.write(respuesta.text)
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ Cupo diario agotado. Intenta de nuevo mañana.")
                else:
                    st.error(f"Error: {e}")
    else:
        st.warning("Por favor, escribe una pregunta.")

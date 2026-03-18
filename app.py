import streamlit as st
import google.generativeai as genai
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper

# CONFIGURACIÓN BÁSICA
st.set_page_config(page_title="Tadeo AI", layout="centered")
st.title("🤖 TADEO AI")

# LLAVES
GOOGLE_KEY = st.secrets.get("GOOGLE_API_KEY")
TAVILY_KEY = st.secrets.get("TAVILY_API_KEY")

if not GOOGLE_KEY or not TAVILY_KEY:
    st.error("Faltan las llaves API en Secrets.")
    st.stop()

try:
    # Volvemos a la configuración estándar
    genai.configure(api_key=GOOGLE_KEY)
    
    # IMPORTANTE: Usamos 'gemini-pro' que es el nombre más viejo y compatible
    # Esto evita el error 404 de "model not found"
    model = genai.GenerativeModel('gemini-pro')
    
    api_wrapper = TavilySearchAPIWrapper(tavily_api_key=TAVILY_KEY)
    search = TavilySearchResults(api_wrapper=api_wrapper)
    
    st.success("✅ Tadeo AI está listo.")
except Exception as e:
    st.error(f"Error de inicio: {e}")

# INTERFAZ
pregunta = st.text_input("¿Qué quieres investigar?")

if st.button("Ejecutar"):
    if pregunta:
        with st.spinner("Buscando..."):
            try:
                # 1. Buscar
                contexto = search.run(pregunta)
                # 2. Responder
                response = model.generate_content(f"Datos: {contexto}\nPregunta: {pregunta}")
                st.write(response.text)
            except Exception as e:
                # Aquí mostramos el error real sin mensajes de 'cupo agotado'
                st.error(f"Error: {e}")

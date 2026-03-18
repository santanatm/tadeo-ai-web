import streamlit as st
import google.generativeai as genai
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tadeo AI", page_icon="🤖")
st.title("🤖 TADEO AI")

# 2. EXTRACCIÓN SEGURA DE LLAVES
# Buscamos en Secrets (Streamlit Cloud) o en Variables de Entorno (Local)
GOOGLE_KEY = st.secrets.get("GOOGLE_API_KEY")
TAVILY_KEY = st.secrets.get("TAVILY_API_KEY")

# 3. VALIDACIÓN DE LLAVES
if not GOOGLE_KEY or not TAVILY_KEY:
    st.error("❌ ERROR: No se detectan las llaves API.")
    st.info("Asegúrate de haber guardado las llaves en 'Manage App' -> 'Settings' -> 'Secrets'.")
    st.stop() 

# 4. INICIALIZAR HERRAMIENTAS
try:
    # Configurar Google Gemini
    genai.configure(api_key=GOOGLE_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Configurar Tavily de forma blindada
    api_wrapper = TavilySearchAPIWrapper(tavily_api_key=TAVILY_KEY)
    search = TavilySearchResults(api_wrapper=api_wrapper)
    
    st.success("✅ Tadeo AI está en línea y vinculada a tadeosantana.com")

except Exception as e:
    st.error(f"Error crítico de conexión: {e}")

# --- INTERFAZ DE USUARIO ---
pregunta = st.text_input("¿Qué quieres investigar hoy?", placeholder="Ej: Precio del Bitcoin...")

if st.button("Ejecutar Tadeo AI"):
    if pregunta:
        with st.spinner("Investigando en tiempo real..."):
            try:
                # Ejecutar búsqueda
                busqueda = search.run(pregunta)
                
                # Generar respuesta con IA
                prompt = f"Eres un asistente experto. Datos actuales: {busqueda}\nPregunta: {pregunta}"
                respuesta = model.generate_content(prompt)
                
                st.subheader("📝 Resultado:")
                st.write(respuesta.text)
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ Cupo diario agotado. Google reiniciará tu acceso en unas horas.")
                else:
                    st.error(f"Error en la investigación: {e}")
    else:
        st.warning("Por favor, escribe una pregunta primero.")

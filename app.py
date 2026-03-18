st.write("¿Veo la llave de Google?:", "GOOGLE_API_KEY" in st.secrets)
st.write("¿Veo la llave de Tavily?:", "TAVILY_API_KEY" in st.secrets)

import streamlit as st
import google.generativeai as genai
from langchain_community.tools.tavily_search import TavilySearchResults
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tadeo AI", page_icon="🤖")

st.title("🤖 TADEO AI")
st.markdown("### Tu Asistente en tadeosantana.com")

# 2. CARGAR LLAVES DESDE SECRETS
# Extraemos las llaves primero para usarlas directamente
google_key = st.secrets.get("GOOGLE_API_KEY")
tavily_key = st.secrets.get("TAVILY_API_KEY")

# 3. INICIALIZAR HERRAMIENTAS
try:
    # Configuramos Google
    genai.configure(api_key=google_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Configuramos Tavily PASANDO LA LLAVE DIRECTAMENTE
    # Esto elimina el error de "Did not find tavily_api_key"
    search = TavilySearchResults(tavily_api_key=tavily_key, max_results=3)
    
    st.success("✅ Tadeo AI está lista para trabajar.")

except Exception as e:
    st.error(f"Error al inicializar herramientas: {e}")

# --- INTERFAZ ---
pregunta = st.text_input("¿Qué quieres investigar hoy?", placeholder="Escribe aquí...")

if st.button("Ejecutar Tadeo AI"):
    if pregunta:
        if not google_key or not tavily_key:
            st.error("Faltan las llaves de API en los Secrets de Streamlit.")
        else:
            with st.spinner("Buscando en tiempo real..."):
                try:
                    # Búsqueda
                    busqueda = search.run(pregunta)
                    
                    # Inteligencia
                    prompt = f"Datos de internet: {busqueda}\nPregunta: {pregunta}"
                    respuesta = model.generate_content(prompt)
                    
                    st.subheader("📝 Resultado:")
                    st.write(respuesta.text)
                except Exception as e:
                    if "429" in str(e):
                        st.error("⚠️ Cupo diario agotado. Intenta de nuevo mañana.")
                    else:
                        st.error(f"Error durante la ejecución: {e}")
    else:
        st.warning("Por favor, escribe una pregunta.")

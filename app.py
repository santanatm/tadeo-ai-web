import streamlit as st
import google.generativeai as genai
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tadeo AI", page_icon="🤖")
st.title("🤖 TADEO AI")

# 2. EXTRACCIÓN DE LLAVES
GOOGLE_KEY = st.secrets.get("GOOGLE_API_KEY")
TAVILY_KEY = st.secrets.get("TAVILY_API_KEY")

if not GOOGLE_KEY or not TAVILY_KEY:
    st.error("❌ ERROR: No se detectan las llaves API.")
    st.stop() 

# 3. INICIALIZAR HERRAMIENTAS
try:
    genai.configure(api_key=GOOGLE_KEY)
    # Volvemos a 'gemini-pro' para evitar el error 404 de modelos nuevos
    model = genai.GenerativeModel('gemini-pro')
    
    api_wrapper = TavilySearchAPIWrapper(tavily_api_key=TAVILY_KEY)
    search = TavilySearchResults(api_wrapper=api_wrapper)
    
    st.success("✅ Tadeo AI está listo.")

except Exception as e:
    st.error(f"Error de conexión: {e}")

# 4. INTERFAZ DE USUARIO
pregunta = st.text_input("¿Qué quieres investigar hoy?", placeholder="Ej: Precio del Bitcoin...")

if st.button("Ejecutar Tadeo AI"):
    if pregunta:
        with st.spinner("Investigando..."):
            try:
                # Ejecutar búsqueda
                busqueda = search.run(pregunta)
                
                # Generar respuesta
                prompt = f"Actúa como un experto. Datos actuales: {busqueda}\nPregunta: {pregunta}"
                respuesta = model.generate_content(prompt)
                
                st.subheader("📝 Resultado:")
                st.write(respuesta.text)
            except Exception as e:
                st.error(f"Error detectado: {e}")
    else:
        st.warning("Por favor, escribe una pregunta primero.")

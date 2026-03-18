import streamlit as st
import google.generativeai as genai
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper

# 1. CONFIGURACIÓN BÁSICA (Layout centrado para que se vea bien en WordPress)
st.set_page_config(page_title="Tadeo AI", layout="centered")
st.title("🤖 TADEO AI")

# 2. CARGA DE LLAVES DESDE SECRETS
GOOGLE_KEY = st.secrets.get("GOOGLE_API_KEY")
TAVILY_KEY = st.secrets.get("TAVILY_API_KEY")

if not GOOGLE_KEY or not TAVILY_KEY:
    st.error("Faltan llaves API en los Secrets de Streamlit.")
    st.stop()

# 3. CONFIGURACIÓN DE MODELOS (VERSIONES ESTABLES)
try:
    genai.configure(api_key=GOOGLE_KEY)
    
    # Usamos el modelo más básico y compatible para evitar el error 404
    model = genai.GenerativeModel('gemini-pro')
    
    # Configuración de búsqueda
    api_wrapper = TavilySearchAPIWrapper(tavily_api_key=TAVILY_KEY)
    search = TavilySearchResults(api_wrapper=api_wrapper)
    
    st.success("✅ Tadeo AI está listo.")
except Exception as e:
    st.error(f"Error al iniciar: {e}")

# 4. INTERFAZ Y LÓGICA
pregunta = st.text_input("¿Qué quieres investigar hoy?")

if st.button("Ejecutar Tadeo AI"):
    if pregunta:
        with st.spinner("Buscando información..."):
            try:
                # Paso 1: Buscar datos
                resultados = search.run(pregunta)
                
                # Paso 2: Generar respuesta
                prompt_final = f"Datos actuales: {resultados}\n\nPregunta: {pregunta}"
                respuesta = model.generate_content(prompt_final)
                
                st.subheader("📝 Resultado:")
                st.write(respuesta.text)
            except Exception as e:
                # Mostramos el error directo para saber qué pasa exactamente
                st.error(f"Hubo un problema: {e}")
    else:
        st.warning("Por favor, escribe algo primero.")

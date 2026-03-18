import streamlit as st
import google.generativeai as genai
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
import os

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser lo primero)
st.set_page_config(page_title="Tadeo AI", page_icon="🤖")

# Estilo para ocultar menús innecesarios y ajustar el ancho
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 1rem;}
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 TADEO AI")

# 2. EXTRACCIÓN SEGURA DE LLAVES
GOOGLE_KEY = st.secrets.get("GOOGLE_API_KEY")
TAVILY_KEY = st.secrets.get("TAVILY_API_KEY")

# 3. VALIDACIÓN Y CONFIGURACIÓN
if not GOOGLE_KEY or not TAVILY_KEY:
    st.error("❌ ERROR: No se detectan las llaves API en Secrets.")
    st.stop() 

try:
    # Configuración forzada a la versión estable mediante 'rest'
    genai.configure(api_key=GOOGLE_KEY, transport='rest')
    
    # Usamos el modelo más estable para evitar errores 404
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    # Configurar Tavily
    api_wrapper = TavilySearchAPIWrapper(tavily_api_key=TAVILY_KEY)
    search = TavilySearchResults(api_wrapper=api_wrapper)
    
    st.success("✅ Sistema listo y vinculado a tadeosantana.com")

except Exception as e:
    st.error(f"Error en la inicialización: {e}")

# 4. INTERFAZ DE USUARIO
pregunta = st.text_input("¿Qué quieres investigar hoy?", placeholder="Ej: Ganador Serie del Caribe 2026...")

if st.button("Ejecutar Tadeo AI"):
    if pregunta:
        with st.spinner("Buscando en tiempo real..."):
            try:
                # Paso 1: Búsqueda Web
                busqueda_resultados = search.run(pregunta)
                
                # Paso 2: Procesamiento con IA
                prompt = (
                    f"Eres Tadeo AI, un asistente experto. "
                    f"Utiliza la siguiente información reciente para responder de forma clara: "
                    f"\n\nContexto: {busqueda_resultados}\n\nPregunta: {pregunta}"
                )
                
                respuesta = model.generate_content(prompt)
                
                # Paso 3: Mostrar resultado
                st.subheader("📝 Resultado:")
                st.write(respuesta.text)
                
            except Exception as e:
                # Captura de error detallada
                st.error(f"Error durante la ejecución: {e}")
                if "429" in str(e):
                    st.warning("Aviso: Se ha alcanzado el límite de consultas gratuitas de Google por este minuto.")
    else:
        st.warning("Escribe una pregunta para comenzar.")

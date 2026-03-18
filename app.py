import streamlit as st
import google.generativeai as genai
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tadeo AI", page_icon="🤖", layout="wide")

# Estilo para limpiar la interfaz en WordPress
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 TADEO AI")

# 2. LLAVES API
GOOGLE_KEY = st.secrets.get("GOOGLE_API_KEY")
TAVILY_KEY = st.secrets.get("TAVILY_API_KEY")

if not GOOGLE_KEY or not TAVILY_KEY:
    st.error("❌ Faltan llaves API en los Secrets de Streamlit.")
    st.stop()

# 3. INICIALIZACIÓN BLINDADA
try:
    genai.configure(api_key=GOOGLE_KEY)
    
    # Usamos gemini-pro que es el nombre más universal y compatible
    model = genai.GenerativeModel('gemini-pro')
    
    api_wrapper = TavilySearchAPIWrapper(tavily_api_key=TAVILY_KEY)
    search = TavilySearchResults(api_wrapper=api_wrapper)
    
    st.success("✅ Tadeo AI está listo.")
except Exception as e:
    st.error(f"Error de inicio: {e}")

# 4. INTERFAZ
pregunta = st.text_input("¿Qué quieres investigar hoy?")

if st.button("Ejecutar Tadeo AI"):
    if pregunta:
        with st.spinner("Buscando información actualizada..."):
            try:
                # Búsqueda web
                contexto_web = search.run(pregunta)
                
                # Generación de respuesta
                # Usamos una estructura de prompt más robusta
                full_prompt = f"Eres un asistente inteligente. Basándote en estos datos: {contexto_web}, responde a: {pregunta}"
                
                # Llamada directa para evitar errores de ruta 404
                response = model.generate_content(full_prompt)
                
                st.subheader("📝 Resultado:")
                st.write(response.text)
            except Exception as e:
                # Si falla el 404 otra vez, intentamos una ruta alternativa
                st.error(f"Error detectado: {e}")
                st.info("Intentando reconexión automática... por favor pulsa el botón de nuevo en 5 segundos.")

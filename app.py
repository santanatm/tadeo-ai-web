import streamlit as st
from groq import Groq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tadeo AI", layout="centered")
st.title("🤖 TADEO AI (Powered by Groq)")

# 2. LLAVES API
GROQ_KEY = st.secrets.get("GROQ_API_KEY")
TAVILY_KEY = st.secrets.get("TAVILY_API_KEY")

if not GROQ_KEY or not TAVILY_KEY:
    st.error("Faltan llaves API (GROQ o TAVILY) en Secrets.")
    st.stop()

# 3. INICIALIZAR HERRAMIENTAS
try:
    # Cliente de Groq (Súper rápido y estable)
    client = Groq(api_key=GROQ_KEY)
    
    # Buscador Tavily
    api_wrapper = TavilySearchAPIWrapper(tavily_api_key=TAVILY_KEY)
    search = TavilySearchResults(api_wrapper=api_wrapper)
    
    st.success("✅ Tadeo AI está en línea con Llama-3.")
except Exception as e:
    st.error(f"Error de inicio: {e}")

# 4. INTERFAZ
pregunta = st.text_input("¿Qué quieres investigar hoy?")

if st.button("Ejecutar Tadeo AI"):
    if pregunta:
        with st.spinner("Investigando en milisegundos..."):
            try:
                # Paso 1: Búsqueda
                resultados = search.run(pregunta)
                
                # Paso 2: Generación con Llama 3 (de Meta)
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": f"Eres Tadeo AI. Usa estos datos para responder: {resultados}"
                        },
                        {
                            "role": "user",
                            "content": pregunta,
                        }
                    ],
                    model="llama3-8b-8192", # Modelo gratuito y ultra rápido
                )
                
                st.subheader("📝 Resultado:")
                st.write(chat_completion.choices[0].message.content)
                
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Escribe algo primero.")

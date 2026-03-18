import streamlit as st
from groq import Groq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tadeo AI", page_icon="🤖", layout="centered")

# Estilo CSS "Agresivo" para limpiar la interfaz al 100%
st.markdown("""
    <style>
    /* Ocultar menú, pie de página y cabecera estándar */
    #MainMenu {visibility: hidden;}
    footer {display: none !important;}
    header {display: none !important;}
    
    /* Ocultar la barra específica de 'Built with Streamlit' y el botón de Fullscreen */
    .stDeployButton {display:none !important;}
    div[data-testid="stStatusWidget"] {display:none !important;}
    div[data-testid="stDecoration"] {display:none !important;}
    
    /* Eliminar el espacio en blanco extra en la parte inferior */
    .main .block-container {
        padding-bottom: 0rem;
    }
    
    /* Estilizar el botón para que combine con tu web (Dorado/Negro) */
    div.stButton > button:first-child {
        background-color: #bfa34b;
        color: white;
        border: none;
    }
    div.stButton > button:first-child:hover {
        background-color: #000000;
        color: #bfa34b;
        border: 1px solid #bfa34b;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 TADEO AI")

# 2. EXTRACCIÓN DE LLAVES DESDE SECRETS
# Asegúrate de tener 'GROQ_API_KEY' y 'TAVILY_API_KEY' en los Secrets de Streamlit
GROQ_KEY = st.secrets.get("GROQ_API_KEY")
TAVILY_KEY = st.secrets.get("TAVILY_API_KEY")

if not GROQ_KEY or not TAVILY_KEY:
    st.error("❌ Faltan llaves API (GROQ o TAVILY) en la configuración de Secrets.")
    st.stop()

# 3. INICIALIZAR MOTORES
try:
    # Cliente de Groq (Ultra rápido)
    client = Groq(api_key=GROQ_KEY)
    
    # Buscador Tavily para datos en tiempo real
    api_wrapper = TavilySearchAPIWrapper(tavily_api_key=TAVILY_KEY)
    search = TavilySearchResults(api_wrapper=api_wrapper)
    
    st.success("✅ Tadeo AI está en línea y listo.")
except Exception as e:
    st.error(f"Error al iniciar los servicios: {e}")

# 4. INTERFAZ DE USUARIO
pregunta = st.text_input("¿Qué quieres investigar hoy?", placeholder="Ej: ¿Quién fue Albert Einstein?")

if st.button("Ejecutar Tadeo AI"):
    if pregunta:
        with st.spinner("Buscando información actualizada..."):
            try:
                # Paso 1: Búsqueda en la web
                resultados_busqueda = search.run(pregunta)
                
                # Paso 2: Procesamiento con Llama 3.3 (El modelo más potente de Groq)
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Eres Tadeo AI, un asistente experto y preciso. "
                                f"Utiliza estos datos de búsqueda para responder: {resultados_busqueda}. "
                                "Si los datos no contienen la respuesta, indícalo cortésmente."
                            )
                        },
                        {
                            "role": "user",
                            "content": pregunta,
                        }
                    ],
                    model="llama-3.3-70b-versatile", # Versión estable y actualizada
                )
                
                # Paso 3: Mostrar el resultado
                st.subheader("📝 Resultado:")
                st.write(chat_completion.choices[0].message.content)
                
            except Exception as e:
                st.error(f"Hubo un error durante la ejecución: {e}")
    else:
        st.warning("Por favor, escribe una pregunta primero.")

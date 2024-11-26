import streamlit as st
import os
from dotenv import load_dotenv
from generators.content_generator import ContentGenerator
from generators.prompt_manager import PromptManager

# Configuración de la página DEBE SER LO PRIMERO
st.set_page_config(
    page_title="Generador de Contenido Digital",
    page_icon="📝",
    layout="wide"
)

# Cargar variables de entorno
load_dotenv()

# Verificar API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ No se encontró la API key en las variables de entorno")
    st.stop()
elif not api_key.startswith("sk-"):
    st.error("❌ La API key no tiene el formato correcto. Debe comenzar con 'sk-'")
    st.stop()
elif len(api_key) < 20:
    st.error("❌ La API key parece ser demasiado corta")
    st.stop()

# Si llegamos aquí, la API key parece válida
st.sidebar.success("✅ API key configurada correctamente")

# Inicialización de clases
prompt_manager = PromptManager()

# Título y descripción
st.title("🚀 Generador de Contenido Digital")
st.markdown("""
    Genera contenido optimizado para diferentes plataformas sociales.
    Personaliza el mensaje según tu audiencia y tono deseado.
""")

# Sidebar para configuración
st.sidebar.header("⚙️ Configuración")

# Selección de plataforma
platform = st.sidebar.selectbox(
    "Selecciona la plataforma",
    prompt_manager.get_all_platforms()
)

# Configuración del contenido
st.header("📝 Detalles del Contenido")

col1, col2 = st.columns(2)

with col1:
    tema = st.text_area(
        "¿Sobre qué tema quieres generar contenido?",
        help="Describe el tema principal de tu contenido"
    )
    
    tono = st.selectbox(
        "Tono de comunicación",
        ["Profesional", "Casual", "Educativo", "Inspirador", "Humorístico"]
    )

with col2:
    audiencia = st.text_input(
        "Audiencia objetivo",
        help="Describe tu audiencia ideal (ej: profesionales de marketing, estudiantes...)"
    )

# Botón de generación
if st.button("🎯 Generar Contenido", type="primary"):
    if tema and audiencia:
        with st.spinner("✨ Generando contenido personalizado..."):
            try:
                generator = ContentGenerator(api_key=api_key)
                template_data = prompt_manager.get_template(platform)
                
                if template_data:
                    params = {
                        "tema": tema,
                        "audiencia": audiencia,
                        "tono": tono
                    }
                    
                    resultado = generator.generate_content(
                        template_data["template"],
                        params
                    )
                    
                    st.success("¡Contenido generado con éxito! 🎉")
                    st.header("📊 Contenido Generado")
                    st.markdown(resultado)
                    
                    st.download_button(
                        label="📥 Descargar Contenido",
                        data=resultado,
                        file_name=f"contenido_{platform.lower()}.txt",
                        mime="text/plain"
                    )
                else:
                    st.error(f"No se encontró template para la plataforma {platform}")
                    
            except Exception as e:
                st.error(f"Error inesperado: {str(e)}")
    else:
        st.warning("⚠️ Por favor, completa todos los campos requeridos.")

# Footer
st.markdown("---")
st.markdown("Desarrollado con ❤️ usando Streamlit y LangChain")
import streamlit as st
import os
from dotenv import load_dotenv
from generators.content_generator import ContentGenerator
from generators.prompt_manager import PromptManager

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="Generador de Contenido Digital",
    page_icon="📝",
    layout="wide"
)

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
                # Inicializar generador
                generator = ContentGenerator(api_key=os.getenv("OPENAI_API_KEY"))
                
                # Obtener template
                template_data = prompt_manager.get_template(platform)
                
                if template_data:
                    # Preparar parámetros
                    params = {
                        "tema": tema,
                        "audiencia": audiencia,
                        "tono": tono
                    }
                    
                    # Generar contenido
                    resultado = generator.generate_content(
                        template_data["template"],
                        params
                    )
                    
                    if resultado:
                        st.success("¡Contenido generado con éxito! 🎉")
                        
                        # Mostrar resultado
                        st.header("📊 Contenido Generado")
                        st.markdown(resultado)
                        
                        # Opciones adicionales
                        st.download_button(
                            label="📥 Descargar Contenido",
                            data=resultado,
                            file_name=f"contenido_{platform.lower()}.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("Error generando el contenido. Por favor, intenta de nuevo.")
                        
            except Exception as e:
                st.error(f"Ocurrió un error: {str(e)}")
    else:
        st.warning("⚠️ Por favor, completa todos los campos requeridos.")

# Footer
st.markdown("---")
st.markdown("Desarrollado con ❤️ usando Streamlit y LangChain")
import streamlit as st
from generators.prompt_manager import PromptManager
from generators.ollama_generator import OllamaGenerator
from generators.image_generator import ImageGenerator
from generators.llm_handler import LLMManager
from company_profile import ProfileManager, CompanyProfile
import os

# Configuración de la página
st.set_page_config(
    page_title="Generador de Contenido Digital",
    page_icon="📝",
    layout="wide"
)

# Inicialización de clases
prompt_manager = PromptManager()
llm_manager = LLMManager()
profile_manager = ProfileManager()

# Título y descripción
st.title("🚀 Generador de Contenido Digital")
st.markdown("""
    Genera contenido optimizado para diferentes plataformas sociales.
    Personaliza el mensaje según tu audiencia y tono deseado.
""")

# Sidebar para configuración
st.sidebar.header("⚙️ Configuración")

# Selección de provider LLM
available_providers = llm_manager.get_available_providers()
provider_names = [p[0] for p in available_providers]
provider_descriptions = {p[0]: p[1] for p in available_providers}

selected_provider = st.sidebar.selectbox(
    "Selecciona el proveedor LLM",
    provider_names,
    format_func=lambda x: f"{x} - {provider_descriptions[x]}"
)

# Selección de plataforma
platform = st.sidebar.selectbox(
    "Selecciona la plataforma",
    prompt_manager.get_all_platforms()
)

# Gestión de perfiles de empresa
st.sidebar.header("👥 Perfil de Empresa")
profiles = profile_manager.get_all_profiles()
selected_profile = st.sidebar.selectbox(
    "Selecciona un perfil",
    ["Ninguno"] + profiles,
    help="Selecciona un perfil de empresa existente o crea uno nuevo"
)

# Configuración del contenido
st.header("📝 Detalles del Contenido")

# Cargar perfil seleccionado
profile_data = None
if selected_profile != "Ninguno":
    profile_data = profile_manager.load_profile(selected_profile)

col1, col2 = st.columns(2)

with col1:
    tema = st.text_area(
        "¿Sobre qué tema quieres generar contenido?",
        help="Describe el tema principal de tu contenido"
    )
    
    tono = st.selectbox(
        "Tono de comunicación",
        ["Profesional", "Casual", "Educativo", "Inspirador", "Humorístico"],
        index=0 if not profile_data else ["Profesional", "Casual", "Educativo", "Inspirador", "Humorístico"].index(profile_data.tone_of_voice)
    )

with col2:
    audiencia = st.text_input(
        "Audiencia objetivo",
        value="" if not profile_data else ", ".join(profile_data.target_audience),
        help="Describe tu audiencia ideal (ej: profesionales de marketing, estudiantes...)"
    )
    
    generar_imagen = st.checkbox(
        "Generar imagen para el contenido",
        help="Genera una imagen relacionada con el contenido usando Stability AI"
    )

# Configuración de imagen
if generar_imagen and os.getenv("STABILITY_API_KEY"):
    image_dimensions = st.selectbox(
        "Dimensiones de la imagen",
        [
            "Cuadrada (512x512)",
            "Horizontal (768x512)",
            "Vertical (512x768)"
        ]
    )
    
    negative_prompt = st.text_input(
        "Prompt negativo (opcional)",
        help="Elementos que NO quieres que aparezcan en la imagen"
    )

# Botón de generación
if st.button("🎯 Generar Contenido", type="primary"):
    if tema and audiencia:
        with st.spinner("✨ Generando contenido personalizado..."):
            try:
                # Obtener el provider seleccionado
                provider = llm_manager.get_provider(selected_provider)
                if not provider:
                    st.error(f"Provider {selected_provider} no encontrado")
                    st.stop()
                
                template_data = prompt_manager.get_template(platform)
                
                if template_data:
                    # Preparar contexto del prompt
                    context = ""
                    if profile_data:
                        context = profile_data.get_prompt_context()
                    
                    params = {
                        "tema": tema,
                        "audiencia": audiencia,
                        "tono": tono,
                        "context": context
                    }
                    
                    # Generar contenido
                    llm = provider.get_llm()
                    resultado = llm.generate(template_data["template"].format(**params))
                    
                    st.success("¡Contenido generado con éxito! 🎉")
                    st.header("📊 Contenido Generado")
                    st.markdown(resultado)
                    
                    # Generar imagen si está seleccionado
                    if generar_imagen and os.getenv("STABILITY_API_KEY"):
                        image_gen = ImageGenerator(api_key=os.getenv("STABILITY_API_KEY"))
                        
                        # Configurar dimensiones
                        dimensions = {
                            "Cuadrada (512x512)": (512, 512),
                            "Horizontal (768x512)": (768, 512),
                            "Vertical (512x768)": (512, 768)
                        }[image_dimensions]
                        
                        # Generar imagen
                        image_prompt = f"Imagen para contenido sobre: {tema}"
                        image_base64 = image_gen.generate_image(
                            prompt=image_prompt,
                            dimensions=dimensions,
                            negative_prompt=negative_prompt
                        )
                        
                        if image_base64:
                            st.image(image_base64)
                            st.download_button(
                                label="📥 Descargar Imagen",
                                data=image_base64,
                                file_name="contenido_imagen.png",
                                mime="image/png"
                            )
                    
                    # Botón de descarga para el contenido
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
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🔧 Modelos Disponibles:**")
    for provider_name, description in provider_descriptions.items():
        st.markdown(f"- {provider_name}: {description}")

with col2:
    st.markdown("**📱 Plataformas Soportadas:**")
    for platform in prompt_manager.get_all_platforms():
        st.markdown(f"- {platform}")

with col3:
    st.markdown("**💡 Perfiles Disponibles:**")
    for profile in profiles:
        st.markdown(f"- {profile}")

st.markdown("Desarrollado con ❤️ usando Streamlit, LangChain y Stability AI")
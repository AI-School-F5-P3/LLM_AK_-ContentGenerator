import streamlit as st
from generators.ollama_generator import OllamaGenerator
from generators.image_generator import ImageGenerator
from utils.company_profile import ProfileManager, CompanyProfile
from utils.prompt_manager import PromptManager
import os
from dotenv import load_dotenv
import base64
from io import BytesIO
import zipfile

# Configuración de la página
st.set_page_config(
    page_title="Generador de Contenido Digital",
    page_icon="📝",
    layout="wide"
)

# Inicializar estados en session_state si no existen
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = None
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None
if 'profile_saved' not in st.session_state:
    st.session_state.profile_saved = False

# Cargar variables de entorno
load_dotenv()

# Inicialización de los managers
generator = OllamaGenerator()
profile_manager = ProfileManager()
prompt_manager = PromptManager()  # Inicializamos PromptManager

# Configuración de Stability AI
stability_api_key = os.getenv("STABILITY_API_KEY")
st.sidebar.write("STABILITY_API_KEY present:", "Yes" if stability_api_key else "No")
image_gen = ImageGenerator(api_key=stability_api_key) if stability_api_key else None

# Título y descripción
st.title("🚀 Generador de Contenido Digital")
st.markdown("""
    Genera contenido optimizado para diferentes plataformas sociales.
    Personaliza el mensaje según tu audiencia y tono deseado.
""")

# Sidebar para configuración
st.sidebar.header("⚙️ Configuración")

# Selección de modelo
model = st.sidebar.selectbox(
    "Selecciona el modelo",
    ["mistral", "llama2", "neural-chat"]
)

# Selección de plataforma
platforms = prompt_manager.get_all_platforms()
platform = st.sidebar.selectbox(
    "📱 Selecciona la plataforma",
    platforms
)



# Perfil de empresa
st.sidebar.header("🏢 Perfil de Empresa")
profiles = profile_manager.get_all_profiles()
selected_profile = st.sidebar.selectbox(
    "Seleccionar perfil",
    ["Ninguno"] + profiles
)

# Formulario para nuevo perfil
if st.sidebar.checkbox("Crear nuevo perfil"):
    with st.sidebar.form("new_profile"):
        company_name = st.text_input("Nombre de la empresa")
        company_description = st.text_area("Descripción")
        industry = st.text_input("Industria")
        tone = st.text_input("Tono de voz")
        target_audience = st.text_input("Audiencia objetivo (separada por comas)")
        key_values = st.text_input("Valores clave (separados por comas)")
        hashtags = st.text_input("Hashtags (separados por comas)")
        website = st.text_input("Sitio web (opcional)")

        if st.form_submit_button("Guardar perfil"):
            if company_name and company_description and industry and tone and target_audience and key_values:
                new_profile = CompanyProfile(
                    name=company_name,
                    description=company_description,
                    industry=industry,
                    tone_of_voice=tone,
                    target_audience=target_audience.split(','),
                    key_values=key_values.split(','),
                    hashtags=hashtags.split(','),
                    website=website
                )
                profile_manager.save_profile(new_profile)
                st.session_state.profile_saved = True
                st.experimental_rerun()
            else:
                st.error("Por favor complete todos los campos obligatorios")

# Mostrar mensaje de éxito después del rerun si el perfil se guardó
if st.session_state.profile_saved:
    st.sidebar.success("✅ Perfil guardado exitosamente")
    # Resetear el estado después de mostrar el mensaje
    st.session_state.profile_saved = False                

# Información del modelo seleccionado
st.sidebar.info(f"✨ Usando modelo: {model}")

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
    
    generar_imagen = st.checkbox(
        "Generar imagen para el contenido",
        help="Genera una imagen relacionada con el contenido"
    )

# Configuración adicional para la generación de imagen
if generar_imagen:
    image_dimensions = st.selectbox(
        "Dimensiones de la imagen",
        ["Cuadrada (512x512)", "Horizontal (768x512)", "Vertical (512x768)"]
    )
    
    negative_prompt = st.text_area(
        "Prompt negativo (opcional)",
        help="Describe lo que NO quieres que aparezca en la imagen"
    )

    dimensions_map = {
        "Cuadrada (512x512)": (512, 512),
        "Horizontal (768x512)": (768, 512),
        "Vertical (512x768)": (512, 768)
    }
    dimensions = dimensions_map[image_dimensions]

    if not stability_api_key:
        st.warning("⚠️ No se ha configurado la API key de Stability AI. La generación de imágenes no estará disponible.")
            
# Botón de generación
if st.button("🎯 Generar Contenido", type="primary"):
    if tema and audiencia:
        with st.spinner("✨ Generando contenido personalizado..."):
            try:
                # Actualizar el modelo del generador
                generator.model = model
                
                # Obtener el template para la plataforma seleccionada
                platform_template = prompt_manager.get_template(platform)
                
                if not platform_template:
                    st.error(f"No se encontró template para la plataforma {platform}")
                    st.stop()
                
                # Preparar los parámetros para el template
                template_params = {
                    "tema": tema,
                    "audiencia": audiencia,
                    "tono": tono
                }
                
                # Validar que tenemos todos los parámetros necesarios
                if generator.validate_params(platform_template["params"], template_params):
                    # Obtener el template y añadir contexto del perfil si existe
                    prompt_template = platform_template["template"]
                    
                    if selected_profile != "Ninguno":
                        profile = profile_manager.load_profile(selected_profile)
                        if profile:
                            prompt_template += f"\n\nContexto de la empresa:\n{profile.get_prompt_context()}"
                    
                    # Generar contenido
                    resultado = generator.generate_content(
                        prompt_template,
                        template_params
                    )
                    
                    if resultado:
                        st.success("¡Contenido generado con éxito! 🎉")
                        st.header(f"📊 Contenido para {platform}")
                        # Guardar el contenido en session_state
                        st.session_state.generated_content = resultado
                        st.markdown(resultado)
                
                    # Generar imagen si está seleccionado y configurado
                    if generar_imagen and image_gen:
                        try:
                            with st.spinner("🎨 Generando imagen..."):
                                image_prompt = f"Create a professional and modern image that represents: {tema}"
                                st.info("🔍 Prompt para la imagen: " + image_prompt)
                                
                                image_base64 = image_gen.generate_image(
                                    prompt=image_prompt.strip(),
                                    dimensions=dimensions,
                                    negative_prompt=negative_prompt
                                )
                                
                                if image_base64:
                                    st.success("✨ ¡Imagen generada exitosamente!")
                                    # Decodificar la imagen base64 y mostrarla
                                    try:
                                        image_data = base64.b64decode(image_base64)
                                        # Guardar la imagen en session_state
                                        st.session_state.generated_image = image_data
                                        st.image(BytesIO(image_data))
                                        
                                        # Crear un archivo ZIP con el contenido y la imagen
                                        zip_buffer = BytesIO()
                                        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                                            # Añadir el contenido de texto
                                            zip_file.writestr(
                                                f"contenido_{platform.lower()}.txt",
                                                st.session_state.generated_content
                                            )
                                            # Añadir la imagen
                                            zip_file.writestr(
                                                f"imagen_{platform.lower()}.png",
                                                st.session_state.generated_image

                                            )
                                        
                                        # Botón para descargar el ZIP
                                        st.download_button(
                                            label="📥 Descargar Contenido e Imagen",
                                            data=zip_buffer.getvalue(),
                                            file_name=f"contenido_{platform.lower()}_completo.zip",
                                            mime="application/zip"
                                        )
                                        
                                        # Botones individuales para descargar cada elemento
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.download_button(
                                                label="📝 Descargar solo Texto",
                                                data=st.session_state.generated_content,
                                                file_name=f"contenido_{platform.lower()}.txt",
                                                mime="text/plain"
                                            )
                                        with col2:
                                            st.download_button(
                                                label="🖼️ Descargar solo Imagen",
                                                data=st.session_state.generated_image,
                                                file_name=f"imagen_{platform.lower()}.png",
                                                mime="image/png"
                                            )
                                            
                                    except Exception as e:
                                        st.error(f"❌ Error al procesar la imagen: {str(e)}")
                                else:
                                    st.error("❌ No se pudo generar la imagen.")
                                    # Mostrar solo el botón de descarga de texto si la imagen falló
                                    st.download_button(
                                        label="📥 Descargar Contenido",
                                        data=st.session_state.generated_content,
                                        file_name=f"contenido_{platform.lower()}.txt",
                                        mime="text/plain"
                                    )
                        except Exception as e:
                            st.error(f"🚨 Error en la generación de imagen: {str(e)}")
                            # Mostrar solo el botón de descarga de texto si hubo error
                            st.download_button(
                                label="📥 Descargar Contenido",
                                data=st.session_state.generated_content,
                                file_name=f"contenido_{platform.lower()}.txt",
                                mime="text/plain"
                            )
                    else:
                        # Si no se solicitó imagen, mostrar solo el botón de descarga de texto
                        st.download_button(
                            label="📥 Descargar Contenido",
                            data=st.session_state.generated_content,
                            file_name=f"contenido_{platform.lower()}.txt",
                            mime="text/plain"
                        )
                else:
                    st.error("Faltan parámetros requeridos para la generación del contenido")
                    
            except Exception as e:
                st.error(f"Error generando contenido: {str(e)}")
    else:
        st.warning("⚠️ Por favor, completa todos los campos requeridos.")


# Mostrar contenido e imagen persistentes
if st.session_state.generated_content:
    st.markdown(st.session_state.generated_content)
    
if st.session_state.generated_image:
    st.image(BytesIO(st.session_state.generated_image))        

# Footer
st.markdown("---")
st.markdown("Desarrollado con ❤️ usando Streamlit y Ollama")
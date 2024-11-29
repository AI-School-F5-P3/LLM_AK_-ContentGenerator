import streamlit as st
from generators.ollama_generator import OllamaGenerator
from generators.image_generator import ImageGenerator
from utils.company_profile import ProfileManager, CompanyProfile
import os
from dotenv import load_dotenv
import base64
from io import BytesIO

# Configuración de la página - DEBE SER LA PRIMERA LLAMADA A STREAMLIT
st.set_page_config(
    page_title="Generador de Contenido Digital",
    page_icon="📝",
    layout="wide"
)

# Cargar variables de entorno
load_dotenv()

# Mostrar estado de STABILITY_API_KEY
stability_api_key = os.getenv("STABILITY_API_KEY")
st.sidebar.write("STABILITY_API_KEY present:", "Yes" if stability_api_key else "No")

# Inicialización del generador y profile manager
generator = OllamaGenerator()
profile_manager = ProfileManager()

# Inicializar el generador de imágenes si hay API key
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
            st.success("Perfil guardado exitosamente")
            st.experimental_rerun()

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
                
                # Preparar el prompt
                prompt_base = f"""
                Genera contenido sobre el tema: {tema}
                Para una audiencia de: {audiencia}
                Usando un tono: {tono}
                """
                
                # Añadir contexto del perfil de empresa si está seleccionado
                if selected_profile != "Ninguno":
                    profile = profile_manager.load_profile(selected_profile)
                    if profile:
                        prompt_base += f"\n{profile.get_prompt_context()}"
                
                # Generar contenido
                resultado = generator.generate_content(
                    prompt_base,
                    {"tema": tema, "audiencia": audiencia, "tono": tono}
                )
                
                if resultado:
                    st.success("¡Contenido generado con éxito! 🎉")
                    st.header("📊 Contenido Generado")
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
                                        image_bytes = BytesIO(image_data)
                                        st.image(image_bytes)
                                    except Exception as e:
                                        st.error(f"❌ Error al procesar la imagen: {str(e)}")
                                else:
                                    st.error("❌ No se pudo generar la imagen.")
                        except Exception as e:
                            st.error(f"🚨 Error en la generación de imagen: {str(e)}")
                    
                    # Botón de descarga
                    st.download_button(
                        label="📥 Descargar Contenido",
                        data=resultado,
                        file_name="contenido_generado.txt",
                        mime="text/plain"
                    )
                    
            except Exception as e:
                st.error(f"Error generando contenido: {str(e)}")
    else:
        st.warning("⚠️ Por favor, completa todos los campos requeridos.")

# Footer
st.markdown("---")
st.markdown("Desarrollado con ❤️ usando Streamlit y Ollama")
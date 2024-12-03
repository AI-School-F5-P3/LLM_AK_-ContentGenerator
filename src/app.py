import streamlit as st
from generators.ollama_generator import OllamaGenerator
from generators.image_generator import ImageGenerator
from utils.company_profile import ProfileManager, CompanyProfile
from utils.prompt_manager import PromptManager
from services.financial_news_service import FinancialNewsService
from services.scientific_content_service import ScientificContentService
from services.language_service import LanguageService
from trackers.langsmith_tracker import LangSmithTracker
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

# Initialize services
language_service = LanguageService()
financial_news_service = FinancialNewsService(os.getenv("ALPHA_VANTAGE_API_KEY"))
scientific_content_service = ScientificContentService(os.getenv("OPENAI_API_KEY"))
langsmith_tracker = LangSmithTracker(os.getenv("LANGSMITH_API_KEY"))


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

# Selector de idioma en el sidebar
st.sidebar.header("🌍 Idioma")
target_language = st.sidebar.selectbox(
    "Seleccionar idioma del contenido",
    options=list(language_service.SUPPORTED_LANGUAGES.keys()),
    format_func=lambda x: language_service.SUPPORTED_LANGUAGES[x]
)

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
            
if st.button("🎯 Generar Contenido", type="primary"):
    if tema and audiencia:
        with st.spinner("✨ Generando contenido personalizado..."):
            try:
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
                
                # Obtener el template y añadir contexto del perfil
                prompt_template = platform_template["template"]
                
                if selected_profile != "Ninguno":
                    profile = profile_manager.load_profile(selected_profile)
                    if profile:
                        prompt_template += f"\n\nContexto de la empresa:\n{profile.get_prompt_context()}"

                # Actualizar el modelo del generador
                generator.model = model

                # Iniciar tracking
                with langsmith_tracker.track_generation(
                    tema=tema,
                    platform=platform,
                    tono=tono,
                    audiencia=audiencia
                ):
                    # Validar que tenemos todos los parámetros necesarios
                    if generator.validate_params(platform_template["params"], template_params):
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


def add_language_selection():
    """Add to the sidebar in app.py"""
    st.sidebar.header("🌍 Language")
    target_language = st.sidebar.selectbox(
        "Select content language",
        options=list(LanguageService.SUPPORTED_LANGUAGES.values()),
        format_func=lambda x: LanguageService.SUPPORTED_LANGUAGES[x]
    )
    return target_language

def add_market_news_section():
    """Add as a new section in app.py"""
    st.header("📈 Market News")
    if st.button("Refresh Market Data"):
        with st.spinner("Fetching latest market data..."):
            news_data = FinancialNewsService.get_market_news()
            
            # Display market indices
            cols = st.columns(3)
            for i, (index, data) in enumerate(news_data["market_data"].items()):
                with cols[i]:
                    st.metric(
                        label=index,
                        value=f"${data['price']:.2f}",
                        delta=f"{data['change']:.2f}"
                    )
            
            # Display news
            st.subheader("Latest News")
            for article in news_data["news"]:
                st.write(f"**{article['title']}**")
                st.write(article['summary'])
                st.write(f"Source: {article['source']} | {article['time_published']}")
                st.markdown("---")

def add_scientific_content_section():
    """Add as a new section in app.py"""
    st.header("🔬 Scientific Content Generator")
    
    scientific_areas = [
        "Quantum Physics",
        "Artificial Intelligence",
        "Biomedicine",
        "Astrophysics",
        "Climate Science"
    ]
    
    selected_area = st.selectbox("Select Scientific Area", scientific_areas)
    specific_topic = st.text_input("Enter specific topic or question")
    
    if st.button("Generate Scientific Content"):
        with st.spinner("Researching and generating content..."):
            # Fetch relevant papers
            papers = ScientificContentService.fetch_arxiv_papers(
                query=f"{selected_area} {specific_topic}"
            )
            
            # Process documents and create vector store
            vectorstore = ScientificContentService.process_documents(papers)
            
            # Generate content
            content = ScientificContentService.generate_content(
                query=specific_topic,
                vectorstore=vectorstore
            )
            
            st.write(content)
            
            # Display sources
            st.subheader("Sources")
            for paper in papers:
                st.write(f"- [{paper.title}]({paper.entry_id})")            

# Sección de noticias financieras
st.header("📈 Noticias del Mercado")
if st.button("Actualizar Datos del Mercado"):
    with st.spinner("Obteniendo últimos datos del mercado..."):
        try:
            news_data = financial_news_service.get_market_news()
            
            # Mostrar índices de mercado
            cols = st.columns(3)
            if "market_data" in news_data:
                for i, (index, data) in enumerate(news_data["market_data"].items()):
                    with cols[i]:
                        st.metric(
                            label=index,
                            value=f"${data['price']:.2f}",
                            delta=f"{data['change']:.2f}%"
                        )
            
            # Mostrar noticias
            if "news" in news_data:
                st.subheader("Últimas Noticias")
                for article in news_data["news"]:
                    with st.expander(article['title']):
                        st.write(article['summary'])
                        st.write(f"Fuente: {article['source']} | {article['time_published']}")
        except Exception as e:
            st.error(f"Error al obtener datos del mercado: {str(e)}")

# Sección de contenido científico
st.header("🔬 Generador de Contenido Científico")

areas_cientificas = [
    "Física Cuántica",
    "Inteligencia Artificial",
    "Biomedicina",
    "Astrofísica",
    "Ciencia del Clima"
]

col1, col2 = st.columns(2)
with col1:
    area_seleccionada = st.selectbox("Seleccionar Área Científica", areas_cientificas)
with col2:
    tema_especifico = st.text_input("Ingrese tema o pregunta específica")

if st.button("Generar Contenido Científico"):
    with st.spinner("Investigando y generando contenido..."):
        try:
            # Obtener papers relevantes
            papers = scientific_content_service.fetch_arxiv_papers(
                query=f"{area_seleccionada} {tema_especifico}"
            )
            
            if papers:
                # Procesar documentos y crear vector store
                vectorstore = scientific_content_service.process_documents(papers)
                
                # Generar contenido
                contenido = scientific_content_service.generate_content(
                    query=tema_especifico,
                    vectorstore=vectorstore
                )
                
                st.write(contenido)
                
                # Mostrar fuentes
                st.subheader("Fuentes")
                for paper in papers:
                    st.write(f"- [{paper.title}]({paper.entry_id})")
            else:
                st.warning("No se encontraron papers relevantes para el tema especificado.")
        except Exception as e:
            st.error(f"Error al generar contenido científico: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Desarrollado con ❤️ usando Streamlit y Ollama")
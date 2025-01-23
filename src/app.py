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

# Page configuration
st.set_page_config(
    page_title="Digital Content Generator",
    page_icon="📝",
    layout="wide"
)

# Initialize session state if not exists
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = None
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None
if 'profile_saved' not in st.session_state:
    st.session_state.profile_saved = False

# Load environment variables
load_dotenv()

# Initialize managers
generator = OllamaGenerator()
profile_manager = ProfileManager()
prompt_manager = PromptManager()  # Initialize PromptManager

# Stability AI configuration
stability_api_key = os.getenv("STABILITY_API_KEY")
st.sidebar.write("STABILITY_API_KEY present:", "Yes" if stability_api_key else "No")
image_gen = ImageGenerator(api_key=stability_api_key) if stability_api_key else None

# Title and description
st.title("🚀 Digital Content Generator")
st.markdown("""
    Generate optimized content for different social platforms.
    Personalize the message according to your audience and desired tone.
""")

# Sidebar for configuration
st.sidebar.header("⚙️ Configuration")

# Model selection
model = st.sidebar.selectbox(
    "Select Model",
    ["mistral", "llama2", "neural-chat"]
)

# Platform selection
platforms = prompt_manager.get_all_platforms()
platform = st.sidebar.selectbox(
    "📱 Select Platform",
    platforms
)

# Company profile
st.sidebar.header("🏢 Company Profile")
profiles = profile_manager.get_all_profiles()
selected_profile = st.sidebar.selectbox(
    "Select Profile",
    ["None"] + profiles
)

# Form for new profile
if st.sidebar.checkbox("Create New Profile"):
    with st.sidebar.form("new_profile"):
        company_name = st.text_input("Company Name")
        company_description = st.text_area("Description")
        industry = st.text_input("Industry")
        tone = st.text_input("Voice Tone")
        target_audience = st.text_input("Target Audience (comma-separated)")
        key_values = st.text_input("Key Values (comma-separated)")
        hashtags = st.text_input("Hashtags (comma-separated)")
        website = st.text_input("Website (optional)")

        if st.form_submit_button("Save Profile"):
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
                st.error("Please complete all required fields")

# Show success message after rerun if profile was saved
if st.session_state.profile_saved:
    st.sidebar.success("✅ Profile saved successfully")
    # Reset state after showing message
    st.session_state.profile_saved = False                

# Selected model information
st.sidebar.info(f"✨ Using model: {model}")

# Content configuration
st.header("📝 Content Details")

col1, col2 = st.columns(2)

with col1:
    theme = st.text_area(
        "What topic do you want to generate content about?",
        help="Describe the main topic of your content"
    )
    
    tone = st.selectbox(
        "Communication Tone",
        ["Professional", "Casual", "Educational", "Inspiring", "Humorous"]
    )

with col2:
    audience = st.text_input(
        "Target Audience",
        help="Describe your ideal audience (e.g., marketing professionals, students...)"
    )
    
    generate_image = st.checkbox(
        "Generate image for content",
        help="Generate an image related to the content"
    )

# Additional configuration for image generation
if generate_image:
    image_dimensions = st.selectbox(
        "Image Dimensions",
        ["Square (512x512)", "Horizontal (768x512)", "Vertical (512x768)"]
    )
    
    negative_prompt = st.text_area(
        "Negative Prompt (optional)",
        help="Describe what you do NOT want to appear in the image"
    )

    dimensions_map = {
        "Square (512x512)": (512, 512),
        "Horizontal (768x512)": (768, 512),
        "Vertical (512x768)": (512, 768)
    }
    dimensions = dimensions_map[image_dimensions]

    if not stability_api_key:
        st.warning("⚠️ Stability AI API key not configured. Image generation will not be available.")
            
# Generation button
if st.button("🎯 Generate Content", type="primary"):
    if theme and audience:
        with st.spinner("✨ Generating personalized content..."):
            try:
                # Update generator model
                generator.model = model
                
                # Get template for selected platform
                platform_template = prompt_manager.get_template(platform)
                
                if not platform_template:
                    st.error(f"No template found for platform {platform}")
                    st.stop()
                
                # Prepare template parameters
                template_params = {
                    "tema": theme,
                    "audiencia": audience,
                    "tono": tone
                }
                
                # Validate required parameters
                if generator.validate_params(platform_template["params"], template_params):
                    # Get template and add profile context if exists
                    prompt_template = platform_template["template"]
                    
                    if selected_profile != "None":
                        profile = profile_manager.load_profile(selected_profile)
                        if profile:
                            prompt_template += f"\n\nCompany Context:\n{profile.get_prompt_context()}"
                    
                    # Generate content
                    result = generator.generate_content(
                        prompt_template,
                        template_params
                    )
                    
                    if result:
                        st.success("Content generated successfully! 🎉")
                        st.header(f"📊 Content for {platform}")
                        # Save content in session_state
                        st.session_state.generated_content = result
                        st.markdown(result)
                
                    # Generate image if selected and configured
                    if generate_image and image_gen:
                        try:
                            with st.spinner("🎨 Generating image..."):
                                image_prompt = f"Create a professional and modern image that represents: {theme}"
                                st.info("🔍 Image prompt: " + image_prompt)
                                
                                image_base64 = image_gen.generate_image(
                                    prompt=image_prompt.strip(),
                                    dimensions=dimensions,
                                    negative_prompt=negative_prompt
                                )
                                
                                if image_base64:
                                    st.success("✨ Image generated successfully!")
                                    # Decode base64 image
                                    try:
                                        image_data = base64.b64decode(image_base64)
                                        # Save image in session_state
                                        st.session_state.generated_image = image_data
                                        st.image(BytesIO(image_data))
                                        
                                        # Create ZIP file with content and image
                                        zip_buffer = BytesIO()
                                        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                                            # Add text content
                                            zip_file.writestr(
                                                f"content_{platform.lower()}.txt",
                                                st.session_state.generated_content
                                            )
                                            # Add image
                                            zip_file.writestr(
                                                f"image_{platform.lower()}.png",
                                                st.session_state.generated_image
                                            )
                                        
                                        # Download ZIP button
                                        st.download_button(
                                            label="📥 Download Content and Image",
                                            data=zip_buffer.getvalue(),
                                            file_name=f"content_{platform.lower()}_complete.zip",
                                            mime="application/zip"
                                        )
                                        
                                        # Individual download buttons
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.download_button(
                                                label="📝 Download Text Only",
                                                data=st.session_state.generated_content,
                                                file_name=f"content_{platform.lower()}.txt",
                                                mime="text/plain"
                                            )
                                        with col2:
                                            st.download_button(
                                                label="🖼️ Download Image Only",
                                                data=st.session_state.generated_image,
                                                file_name=f"image_{platform.lower()}.png",
                                                mime="image/png"
                                            )
                                            
                                    except Exception as e:
                                        st.error(f"❌ Error processing image: {str(e)}")
                                else:
                                    st.error("❌ Could not generate image.")
                                    # Show text download button if image failed
                                    st.download_button(
                                        label="📥 Download Content",
                                        data=st.session_state.generated_content,
                                        file_name=f"content_{platform.lower()}.txt",
                                        mime="text/plain"
                                    )
                        except Exception as e:
                            st.error(f"🚨 Image generation error: {str(e)}")
                            # Show text download button if error occurred
                            st.download_button(
                                label="📥 Download Content",
                                data=st.session_state.generated_content,
                                file_name=f"content_{platform.lower()}.txt",
                                mime="text/plain"
                            )
                    else:
                        # If image not requested, show text download button
                        st.download_button(
                            label="📥 Download Content",
                            data=st.session_state.generated_content,
                            file_name=f"content_{platform.lower()}.txt",
                            mime="text/plain"
                        )
                else:
                    st.error("Missing required parameters for content generation")
                    
            except Exception as e:
                st.error(f"Error generating content: {str(e)}")
    else:
        st.warning("⚠️ Please complete all required fields.")

# Display persistent content and image
if st.session_state.generated_content:
    st.markdown(st.session_state.generated_content)
    
if st.session_state.generated_image:
    st.image(BytesIO(st.session_state.generated_image))        

# Footer
st.markdown("---")
st.markdown("Developed with ❤️ using Streamlit and Ollama")
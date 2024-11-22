# 📱 Digital Content Generator

A powerful content generation system that creates platform-specific content using AI for blogs, social media, and professional networks.

## 🌟 Features

### Essential Level
- Multi-platform content generation (Blog, Twitter, LinkedIn, Instagram)
- Custom tone and audience targeting
- User-friendly web interface
- Downloadable content in text format
- Real-time content preview

### Medium Level
- Docker containerization
- Multiple LLM support (OpenAI, Mistral)
- AI-generated images integration
- Company profile management
- Enhanced content personalization

## 🛠️ Technologies Used

- Python 3.9+
- Streamlit
- LangChain
- OpenAI API
- Stability AI
- Docker

## 📋 Prerequisites

- Python 3.9 or higher
- Docker (for containerized deployment)
- OpenAI API key
- Stability AI API key (for image generation)

## 🚀 Quick Start

### Local Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/digital-content-generator.git
cd digital-content-generator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key
STABILITY_API_KEY=your_stability_api_key
```

5. Run the application:
```bash
streamlit run src/app.py
```

### Docker Installation

1. Build the Docker image:
```bash
docker build -t content-generator .
```

2. Run the container:
```bash
docker run -p 8501:8501 --env-file .env content-generator
```

## 💻 Usage

1. Access the application at `http://localhost:8501`
2. Select your target platform (Blog, Twitter, LinkedIn, or Instagram)
3. Enter your topic, target audience, and desired tone
4. Click "Generate Content" to create your content
5. Download or copy the generated content

## 📁 Project Structure

```
project_content/
├── src/
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── content_generator.py
│   │   ├── prompt_manager.py
│   │   ├── image_generator.py
│   │   └── llm_manager.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── constants.py
│   └── app.py
├── .env
├── Dockerfile
├── requirements.txt
└── README.md
```

## ⚙️ Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `STABILITY_API_KEY`: Your Stability AI API key
- `PORT`: Port for the Streamlit application (default: 8501)

### Supported Platforms

- Blog posts
- Twitter/X threads
- LinkedIn articles
- Instagram posts

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT models
- Stability AI for image generation capabilities
- LangChain for the LLM framework
- Streamlit for the web interface framework

## 📧 Contact

Your Name - your.email@example.com
Project Link: https://github.com/yourusername/digital-content-generator

## 🐛 Troubleshooting

### Common Issues

1. **API Key Issues**
   - Ensure all API keys are correctly set in the `.env` file
   - Check API key permissions and quotas

2. **Docker Issues**
   - Ensure Docker daemon is running
   - Check port availability
   - Verify environment variables are properly passed

3. **Content Generation Issues**
   - Check internet connectivity
   - Verify API quotas haven't been exceeded
   - Ensure input parameters are properly formatted
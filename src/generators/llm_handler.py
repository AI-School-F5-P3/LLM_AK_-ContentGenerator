from abc import ABC, abstractmethod
from langchain_community.llms import OpenAI
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.schema.language_model import BaseLLM
import ollama
import os
from typing import Optional, Dict
from langchain_community.llms import Groq
import os
from groq import Groq

class LLMProvider(ABC):
    """Clase base para providers de LLM"""
    
    @abstractmethod
    def get_llm(self) -> BaseLLM:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        pass


class GroqProvider(LLMProvider):
    """Provider for Groq LLM"""
    
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 model: str = "mixtral-8x7b-32768", 
                 temperature: float = 0.7):
        """
        Initialize Groq provider
        
        Args:
            api_key (str): Groq API key. Defaults to GROQ_API_KEY environment variable
            model (str): Groq model to use. Defaults to mixtral
            temperature (float): Sampling temperature for generation
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.temperature = temperature
    
    def get_llm(self) -> BaseLLM:
        if not self.api_key:
            raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable.")
        
        return Groq(
            groq_api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()]
        )
    
    def get_name(self) -> str:
        return f"Groq-{self.model.capitalize()}"
    
    def get_description(self) -> str:
        return f"Groq {self.model} (High-speed inference)"


class OpenAIProvider(LLMProvider):
    """Provider para OpenAI"""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", temperature: float = 0.7):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
    
    def get_llm(self) -> BaseLLM:
        return OpenAI(
            openai_api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()]
        )
    
    def get_name(self) -> str:
        return "OpenAI"
    
    def get_description(self) -> str:
        return f"OpenAI {self.model} (Balanced quality and speed)"

class OllamaProvider(LLMProvider):
    """Provider para modelos usando Ollama"""
    
    def __init__(self, model: str = "mistral"):
        self.model = model
    
    def get_llm(self) -> BaseLLM:
        return ollama.LLM(
            model=self.model,
            callbacks=[StreamingStdOutCallbackHandler()]
        )
    
    def get_name(self) -> str:
        return f"Ollama-{self.model.capitalize()}"
    
    def get_description(self) -> str:
        return f"{self.model.capitalize()} (Open source, runs locally)"

class LLMManager:
    """Gestor principal de LLMs"""
    
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self._initialize_default_providers()
    
    def _initialize_default_providers(self):
        """Inicializa los providers por defecto"""

        # Add Groq provider if API key is available
        if os.getenv("GROQ_API_KEY"):
            self.add_provider(GroqProvider())
            
        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            self.add_provider(OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY")))
        
        # Ollama providers
        try:
            import ollama
            # Añadir diferentes modelos de Ollama
            for model in ["mistral", "llama2", "neural-chat"]:
                self.add_provider(OllamaProvider(model=model))
        except ImportError:
            pass
    
    def add_provider(self, provider: LLMProvider):
        """Añade un nuevo provider"""
        self.providers[provider.get_name()] = provider
    
    def get_provider(self, name: str) -> Optional[LLMProvider]:
        """Obtiene un provider específico"""
        return self.providers.get(name)
    
    def get_available_providers(self) -> list:
        """Retorna lista de providers disponibles"""
        return [(name, provider.get_description()) 
                for name, provider in self.providers.items()]
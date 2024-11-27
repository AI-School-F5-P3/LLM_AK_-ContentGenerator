from abc import ABC, abstractmethod
from langchain.llms import OpenAI, BaseLLM
from langchain.callbacks import StreamingStdOutCallbackHandler
import ollama
import os
from typing import Optional, Dict

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

class MistralProvider(LLMProvider):
    """Provider para Mistral usando Ollama"""
    
    def __init__(self):
        self.model = "mistral"
    
    def get_llm(self) -> BaseLLM:
        return ollama.LLM(
            model=self.model,
            callbacks=[StreamingStdOutCallbackHandler()]
        )
    
    def get_name(self) -> str:
        return "Mistral"
    
    def get_description(self) -> str:
        return "Mistral (Open source, runs locally)"

class LLMManager:
    """Gestor principal de LLMs"""
    
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self._initialize_default_providers()
    
    def _initialize_default_providers(self):
        """Inicializa los providers por defecto"""
        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            self.add_provider(OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY")))
        
        # Mistral (si Ollama está instalado)
        try:
            import ollama
            self.add_provider(MistralProvider())
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
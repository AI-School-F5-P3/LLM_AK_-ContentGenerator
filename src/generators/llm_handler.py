from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Any
import os
from langchain_core.pydantic_v1 import BaseModel
from groq import Groq


class LLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    def get_llm(self):
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        pass


class GroqProvider(LLMProvider):
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 model: str = "mixtral-8x7b-32768",
                 temperature: float = 0.7):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.temperature = temperature
    
    def get_llm(self):
        if not self.api_key:
            raise ValueError("Groq API key required")
        
        client = Groq(api_key=self.api_key)

        class GroqLLM(BaseModel):
            client: Any
            model: str
            temperature: float
            
            def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=self.temperature,
                        stop=stop
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    raise ValueError(f"Groq API Error: {str(e)}")
            
            def validate_params(self, required_params: List[str], provided_params: Dict[str, str]) -> bool:
                return all(param in provided_params and provided_params[param].strip() for param in required_params)
            
            def generate_content(self, prompt_template: str, template_params: Dict[str, str]) -> str:
                formatted_prompt = prompt_template.format(**template_params)
                return self._call(formatted_prompt)

        return GroqLLM(client=client, model=self.model, temperature=self.temperature)
    
    def get_name(self) -> str:
        return "Groq-Mixtral-8x7b-32768"
    
    def get_description(self) -> str:
        return "Groq Mixtral 8x7B (High performance)"


class LLMManager:
    """Main LLM manager"""
    
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self._initialize_default_providers()
    
    def _initialize_default_providers(self):
        groq_api_key = os.getenv("GROQ_API_KEY")
        if groq_api_key:
            self.add_provider(GroqProvider(
                api_key=groq_api_key, 
                model="mixtral-8x7b-32768"
            ))
    
    def add_provider(self, provider: LLMProvider):
        """Add a new provider"""
        self.providers[provider.get_name()] = provider
    
    def get_provider(self, name: str) -> Optional[LLMProvider]:
        """Get a specific provider"""
        return self.providers.get(name)
    
    def get_available_providers(self) -> list:
        """Return list of available providers"""
        return [(name, provider.get_description()) 
                for name, provider in self.providers.items()]
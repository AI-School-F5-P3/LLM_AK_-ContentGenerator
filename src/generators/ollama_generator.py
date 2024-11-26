from typing import Dict, Optional
import requests

class OllamaGenerator:
    """Clase para generar contenido usando Ollama API"""
    
    def __init__(self, model: str = "mistral", temperature: float = 0.7):
        """
        Inicializa el generador de contenido con Ollama
        
        Args:
            model (str): Nombre del modelo de Ollama a utilizar
            temperature (float): Temperatura para la generación (0.0 - 1.0)
        """
        self.base_url = "http://localhost:11434/api/generate"
        self.model = model
        self.temperature = temperature
    
    def generate_content(self, 
                        template: str, 
                        params: Dict[str, str]) -> Optional[str]:
        """
        Genera contenido usando Ollama API
        
        Args:
            template (str): Template de prompt a utilizar
            params (dict): Parámetros para el template
            
        Returns:
            str: Contenido generado
        """
        try:
            # Validar parámetros
            if not template or not params:
                raise ValueError("Template y parámetros son requeridos")
            
            # Reemplazar los placeholders en el template
            prompt = template.format(**params)
            
            # Preparar la solicitud para Ollama
            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": self.temperature,
                "stream": False
            }
            
            # Realizar la solicitud
            response = requests.post(self.base_url, json=payload)
            
            if response.status_code != 200:
                raise ValueError(f"Error en la API de Ollama: {response.text}")
            
            # Extraer el texto generado
            result = response.json()
            return result.get('response', '')
            
        except Exception as e:
            print(f"Error generando contenido: {str(e)}")
            raise Exception(f"Error en la generación de contenido: {str(e)}")

    def validate_params(self, required_params: list, provided_params: Dict) -> bool:
        """
        Valida que todos los parámetros requeridos estén presentes
        """
        return all(param in provided_params for param in required_params)
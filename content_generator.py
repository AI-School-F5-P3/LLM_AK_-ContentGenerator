from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import Dict, Optional

class ContentGenerator:
    """Clase principal para la generación de contenido"""
    
    def __init__(self, api_key: str, temperature: float = 0.7):
        """
        Inicializa el generador de contenido
        
        Args:
            api_key (str): API key para el modelo de lenguaje
            temperature (float): Temperatura para la generación (0.0 - 1.0)
        """
        self.llm = OpenAI(api_key=api_key, temperature=temperature)
    
    def generate_content(self, 
                        template: str, 
                        params: Dict[str, str]) -> Optional[str]:
        """
        Genera contenido basado en un template y parámetros
        
        Args:
            template (str): Template de prompt a utilizar
            params (dict): Parámetros para el template
            
        Returns:
            str: Contenido generado
        """
        try:
            # Crear el prompt
            prompt = PromptTemplate(
                input_variables=list(params.keys()),
                template=template
            )
            
            # Crear y ejecutar la chain
            chain = LLMChain(llm=self.llm, prompt=prompt)
            return chain.run(params)
            
        except Exception as e:
            print(f"Error generando contenido: {str(e)}")
            return None
    
    def validate_params(self, required_params: list, provided_params: Dict) -> bool:
        """
        Valida que todos los parámetros requeridos estén presentes
        
        Args:
            required_params (list): Lista de parámetros requeridos
            provided_params (dict): Parámetros proporcionados
            
        Returns:
            bool: True si todos los parámetros requeridos están presentes
        """
        return all(param in provided_params for param in required_params)
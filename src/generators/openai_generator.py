from typing import Dict, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class ContentGenerator:
    """Clase principal para la generación de contenido"""
    
    def __init__(self, api_key: str, temperature: float = 0.7):
        """
        Inicializa el generador de contenido
        
        Args:
            api_key (str): API key para el modelo de lenguaje
            temperature (float): Temperatura para la generación (0.0 - 1.0)
        """
        if not api_key:
            raise ValueError("API key no puede estar vacía")
            
        # Usando ChatOpenAI con gpt-3.5-turbo
        self.llm = ChatOpenAI(
            api_key=api_key,  # Cambio de openai_api_key a api_key
            model="gpt-3.5-turbo",  # Cambio de model_name a model
            temperature=temperature
        )
    
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
            # Validar parámetros
            if not template or not params:
                raise ValueError("Template y parámetros son requeridos")
                
            # Crear el prompt
            prompt = PromptTemplate(
                input_variables=list(params.keys()),
                template=template
            )
            
            # Crear y ejecutar la chain
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.invoke(params)  # Cambio de run a invoke
            
            if not result or not result.get('text'):
                raise ValueError("No se pudo generar contenido")
                
            return result.get('text')
            
        except Exception as e:
            print(f"Error generando contenido: {str(e)}")
            raise Exception(f"Error en la generación de contenido: {str(e)}")

    def validate_params(self, required_params: list, provided_params: Dict) -> bool:
        """
        Valida que todos los parámetros requeridos estén presentes
        """
        return all(param in provided_params for param in required_params)
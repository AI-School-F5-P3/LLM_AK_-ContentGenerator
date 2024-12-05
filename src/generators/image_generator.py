import base64
import requests
import logging
from typing import Tuple, Optional

class ImageGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_host = "https://api.stability.ai"
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _translate_prompt(self, prompt: str) -> str:
        """
        Traduce el prompt al inglés o ajusta el texto para que sea compatible con la API.
        """
        # Mapeo básico de términos comunes
        translations = {
            "Crear una imagen": "Create an image",
            "profesional": "professional",
            "atractiva": "attractive",
            "que represente": "representing",
            "Estilo": "Style",
            "moderno": "modern",
            "imagen para": "image for",
            "profesional y": "professional and",
        }
        
        translated_prompt = prompt.lower()
        for esp, eng in translations.items():
            translated_prompt = translated_prompt.replace(esp.lower(), eng)
        
        # Asegurarse de que el prompt comience con un prefijo en inglés
        if not any(translated_prompt.lower().startswith(prefix) for prefix in ["create", "generate", "make"]):
            translated_prompt = f"Create a professional image of {translated_prompt}"
            
        self.logger.info(f"Prompt traducido: {translated_prompt}")
        return translated_prompt

    def generate_image(
        self, 
        prompt: str, 
        dimensions: Tuple[int, int] = (512, 512),
        negative_prompt: str = ""
    ) -> Optional[str]:
        """
        Genera una imagen utilizando la API de Stability AI.
        
        Args:
            prompt (str): Descripción de la imagen a generar
            dimensions (Tuple[int, int]): Dimensiones de la imagen (ancho, alto)
            negative_prompt (str): Prompt negativo para la generación
            
        Returns:
            Optional[str]: Imagen en formato base64 si es exitoso, None si falla
        """
        try:
            self.logger.info(f"Prompt original: {prompt}")
            
            # Traducir el prompt al inglés
            english_prompt = self._translate_prompt(prompt)
            self.logger.info(f"Prompt en inglés: {english_prompt}")
            
            # Traducir el prompt negativo si existe
            english_negative_prompt = self._translate_prompt(negative_prompt) if negative_prompt else ""
            
            # Validar dimensiones permitidas
            if dimensions not in [(512, 512), (768, 512), (512, 768)]:
                raise ValueError("Dimensiones no válidas")

            engine_id = "stable-diffusion-v1-6"
            api_url = f"{self.api_host}/v1/generation/{engine_id}/text-to-image"

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "text_prompts": [
                    {
                        "text": english_prompt,
                        "weight": 1
                    }
                ],
                "cfg_scale": 7,
                "height": dimensions[1],
                "width": dimensions[0],
                "samples": 1,
                "steps": 30,
            }

            # Agregar prompt negativo si existe
            if english_negative_prompt:
                payload["text_prompts"].append({
                    "text": english_negative_prompt,
                    "weight": -1
                })

            self.logger.info("Enviando solicitud a la API...")
            response = requests.post(api_url, headers=headers, json=payload)
            
            if response.status_code != 200:
                self.logger.error(f"Error en la API: {response.status_code} - {response.text}")
                return None

            data = response.json()
            
            if not data.get('artifacts'):
                self.logger.error("No se encontraron artefactos en la respuesta")
                return None

            # Obtener la imagen en base64
            image_base64 = data['artifacts'][0]['base64']
            self.logger.info("Imagen generada exitosamente")
            
            return image_base64

        except Exception as e:
            self.logger.error(f"Error durante la generación de imagen: {str(e)}")
            raise e
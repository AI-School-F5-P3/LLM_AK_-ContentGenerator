import requests
from PIL import Image
from io import BytesIO
import os
from typing import Optional, Tuple
import base64

class ImageGenerator:
    """Clase para generar imágenes usando Stability AI"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_host = "https://api.stability.ai"
        self.engine_id = "stable-diffusion-v1-5"
    
    def generate_image(self, 
                      prompt: str,
                      dimensions: Tuple[int, int] = (512, 512),
                      negative_prompt: str = "") -> Optional[str]:
        """
        Genera una imagen basada en el prompt
        
        Args:
            prompt (str): Descripción de la imagen a generar
            dimensions (tuple): Dimensiones de la imagen (ancho, alto)
            negative_prompt (str): Prompt negativo para excluir elementos
            
        Returns:
            str: Base64 de la imagen generada o None si hay error
        """
        try:
            response = requests.post(
                f"{self.api_host}/v1/generation/{self.engine_id}/text-to-image",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "text_prompts": [
                        {
                            "text": prompt,
                            "weight": 1
                        },
                        {
                            "text": negative_prompt,
                            "weight": -1
                        }
                    ],
                    "cfg_scale": 7,
                    "height": dimensions[1],
                    "width": dimensions[0],
                    "samples": 1,
                    "steps": 30,
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"API error: {response.text}")
            
            # Obtener imagen base64 de la respuesta
            data = response.json()
            if data and "artifacts" in data and len(data["artifacts"]) > 0:
                image_base64 = data["artifacts"][0]["base64"]
                return image_base64
                
            return None
            
        except Exception as e:
            print(f"Error generando imagen: {str(e)}")
            return None
    
    def save_image(self, image_base64: str, path: str) -> bool:
        """Guarda una imagen base64 en un archivo"""
        try:
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))
            image.save(path)
            return True
        except Exception as e:
            print(f"Error guardando imagen: {str(e)}")
            return False
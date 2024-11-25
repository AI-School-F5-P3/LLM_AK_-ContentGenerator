from typing import Dict, Optional

class PromptManager:
    """Gestiona los templates de prompts para diferentes plataformas"""
    
    def __init__(self):
        self.templates = {
            "Blog": {
                "template": """Crea un artículo de blog profesional sobre {tema}.
                Audiencia: {audiencia}
                Tono: {tono}
                
                Estructura requerida:
                1. Título llamativo y SEO friendly
                2. Introducción que enganche (2-3 párrafos)
                3. Desarrollo del contenido (3-4 secciones principales)
                4. Conclusión impactante
                5. Call to action
                
                Requisitos adicionales:
                - Usa un lenguaje adaptado a la audiencia especificada
                - Incluye subtítulos relevantes
                - Longitud aproximada: 800-1000 palabras
                - Incluye 2-3 bullet points donde sea relevante
                """,
                "params": ["tema", "audiencia", "tono"]
            },
            
            "Twitter": {
                "template": """Genera un hilo de Twitter efectivo sobre {tema}.
                Audiencia: {audiencia}
                Tono: {tono}
                
                Estructura:
                1. Tweet principal que enganche
                2. 4-5 tweets de desarrollo
                3. Tweet final con call to action
                
                Requisitos:
                - Máximo 280 caracteres por tweet
                - Usa hashtags relevantes (máximo 2-3 por tweet)
                - Incluye emojis apropiados
                - Mantén un hilo coherente y progresivo
                """,
                "params": ["tema", "audiencia", "tono"]
            },
            
            "LinkedIn": {
                "template": """Crea una publicación profesional de LinkedIn sobre {tema}.
                Audiencia: {audiencia}
                Tono: {tono}
                
                Estructura:
                1. Primer párrafo impactante
                2. Desarrollo de la idea principal
                3. Experiencia personal o caso de estudio
                4. Conclusión con llamada a la acción
                
                Requisitos:
                - Mantén un tono profesional pero cercano
                - Incluye espaciado para mejor legibilidad
                - Usa emojis profesionales estratégicamente
                - Añade 3-5 hashtags relevantes al final
                """,
                "params": ["tema", "audiencia", "tono"]
            },
            
            "Instagram": {
                "template": """Genera una publicación de Instagram sobre {tema}.
                Audiencia: {audiencia}
                Tono: {tono}
                
                Estructura:
                1. Primer párrafo que capture la atención
                2. Desarrollo conciso del mensaje principal
                3. Call to action engagement-focused
                4. Hashtags relevantes
                
                Requisitos:
                - Texto conciso y visualmente espaciado
                - Emojis relevantes
                - 8-10 hashtags estratégicos
                - Tono conversacional y auténtico
                """,
                "params": ["tema", "audiencia", "tono"]
            }
        }
    
    def get_template(self, platform: str) -> Optional[Dict]:
        """Obtiene el template para una plataforma específica"""
        return self.templates.get(platform)
    
    def get_all_platforms(self) -> list:
        """Retorna lista de todas las plataformas disponibles"""
        return list(self.templates.keys())
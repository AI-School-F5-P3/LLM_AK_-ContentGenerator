from typing import Dict, Optional

class PromptManager:
    """Manages prompt templates for different platforms"""
    
    def __init__(self):
        self.templates = {
            "Blog": {
                "template": """Create a professional blog article about {tema}.
                Audience: {audiencia}
                Tone: {tono}
                
                Required Structure:
                1. Catchy and SEO-friendly title
                2. Engaging introduction (2-3 paragraphs)
                3. Content development (3-4 main sections)
                4. Impactful conclusion
                5. Call to action
                
                Additional Requirements:
                - Use language adapted to the specified audience
                - Include relevant subtitles
                - Approximate length: 800-1000 words
                - Include 2-3 bullet points where relevant
                """,
                "params": ["tema", "audiencia", "tono"]
            },
            
            "Twitter": {
                "template": """Generate an effective Twitter thread about {tema}.
                Audience: {audiencia}
                Tone: {tono}
                
                Structure:
                1. Main tweet that captures attention
                2. 4-5 development tweets
                3. Final tweet with call to action
                
                Requirements:
                - Maximum 280 characters per tweet
                - Use relevant hashtags (maximum 2-3 per tweet)
                - Include appropriate emojis
                - Maintain a coherent and progressive thread
                """,
                "params": ["tema", "audiencia", "tono"]
            },
            
            "LinkedIn": {
                "template": """Create a professional LinkedIn post about {tema}.
                Audience: {audiencia}
                Tone: {tono}
                
                Structure:
                1. Impactful first paragraph
                2. Main idea development
                3. Personal experience or case study
                4. Conclusion with call to action
                
                Requirements:
                - Maintain a professional yet close tone
                - Include spacing for better readability
                - Strategically use professional emojis
                - Add 3-5 relevant hashtags at the end
                """,
                "params": ["tema", "audiencia", "tono"]
            },
            
            "Instagram": {
                "template": """Generate an Instagram post about {tema}.
                Audience: {audiencia}
                Tone: {tono}
                
                Structure:
                1. First paragraph that captures attention
                2. Concise development of the main message
                3. Engagement-focused call to action
                4. Relevant hashtags
                
                Requirements:
                - Concise and visually spaced text
                - Relevant emojis
                - 8-10 strategic hashtags
                - Conversational and authentic tone
                """,
                "params": ["tema", "audiencia", "tono"]
            }
        }
    
    def get_template(self, platform: str) -> Optional[Dict]:
        """Gets template for a specific platform"""
        return self.templates.get(platform)
    
    def get_all_platforms(self) -> list:
        """Returns list of all available platforms"""
        return list(self.templates.keys())
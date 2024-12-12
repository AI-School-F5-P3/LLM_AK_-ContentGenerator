from dataclasses import dataclass
from typing import List, Optional
import json
import os

@dataclass
class CompanyProfile:
    """Clase para manejar perfiles de empresa"""
    name: str
    description: str
    industry: str
    tone_of_voice: str
    target_audience: List[str]
    key_values: List[str]
    hashtags: List[str]
    website: Optional[str] = None
    
    @classmethod
    def load_from_json(cls, file_path: str) -> 'CompanyProfile':
        """Carga un perfil desde un archivo JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return cls(**data)
    
    def save_to_json(self, file_path: str):
        """Guarda el perfil en un archivo JSON"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.__dict__, f, indent=4)
    
    def get_prompt_context(self) -> str:
        """Genera contexto para el prompt basado en el perfil"""
        return f"""
        Company Context:
        - Company Name: {self.name}
        - Description: {self.description}
        - Industry: {self.industry}
        - Brand Voice: {self.tone_of_voice}
        - Target Audience: {', '.join(self.target_audience)}
        - Key Values: {', '.join(self.key_values)}
        - Preferred Hashtags: {' '.join(self.hashtags)}
        """

class ProfileManager:
    """Gestor de perfiles de empresa"""
    
    def __init__(self, profiles_dir: str = "profiles"):
        self.profiles_dir = profiles_dir
        os.makedirs(profiles_dir, exist_ok=True)
    
    def save_profile(self, profile: CompanyProfile):
        """Guarda un perfil"""
        file_path = os.path.join(self.profiles_dir, f"{profile.name}.json")
        profile.save_to_json(file_path)
    
    def load_profile(self, name: str) -> Optional[CompanyProfile]:
        """Carga un perfil por nombre"""
        file_path = os.path.join(self.profiles_dir, f"{name}.json")
        if os.path.exists(file_path):
            return CompanyProfile.load_from_json(file_path)
        return None
    
    def get_all_profiles(self) -> List[str]:
        """Obtiene lista de todos los perfiles disponibles"""
        profiles = []
        for file in os.listdir(self.profiles_dir):
            if file.endswith('.json'):
                profiles.append(file[:-5])  # Remove .json extension
        return profiles
import re
from typing import Dict, List

class ContentSafetyValidator:
    HARMFUL_KEYWORDS = [
        # Severe violent content
        'kill', 'murder', 'decapitate', 'torture', 
        'genocide', 'terrorism',
        
        # Explicit sexual content
        'rape', 'sexual abuse', 'pedophilia',
        
        # Extreme hate speech
        'supremacy', 'ethnic cleansing', 
        
        # Severe self-harm
        'suicide methods', 'ways to die',
        
        # Serious illegal activities
        'create explosives', 'manufacture drugs', 
        'human trafficking'
    ]

    DANGEROUS_THEMES = [
        'bomb making',
        'weapon manufacturing',
        'detailed suicide instructions',
        'child exploitation'
    ]

    @classmethod
    def validate_content(cls, theme: str, content: str) -> Dict[str, bool]:
        """
        Validate content against multiple risk categories
        """
        results = {
            'is_safe': True,
            'violent_content': False,
            'sexual_content': False,
            'hate_speech': False,
            'self_harm': False,
            'illegal_activities': False
        }

        # Normalize text for searching
        check_text = (theme + " " + content).lower()

        # Comprehensive safety checks
        for category, keywords in {
            'violent_content': ['kill', 'murder', 'violence', 'torture'],
            'sexual_content': ['rape', 'sexual', 'abuse'],
            'hate_speech': ['supremacy', 'racist', 'discrimination'],
            'self_harm': ['suicide', 'self-harm', 'die'],
            'illegal_activities': ['drugs', 'weapon', 'explosive', 'trafficking']
        }.items():
            if any(keyword in check_text for keyword in keywords):
                results[category] = True
                results['is_safe'] = False

        # Strict keyword check
        if any(keyword.lower() in check_text for keyword in cls.HARMFUL_KEYWORDS):
            results['is_safe'] = False

        # Dangerous themes check
        if any(theme.lower() in dangerous_theme for dangerous_theme in cls.DANGEROUS_THEMES):
            results['is_safe'] = False

        return results

def safety_check_middleware(theme: str, platform: str, content: str) -> Dict:
    """
    Safety middleware for content validation
    """
    safety_result = ContentSafetyValidator.validate_content(theme, content)
    
    if not safety_result['is_safe']:
        risk_messages = []
        if safety_result['violent_content']:
            risk_messages.append("Violent content")
        if safety_result['sexual_content']:
            risk_messages.append("Inappropriate sexual content")
        if safety_result['hate_speech']:
            risk_messages.append("Hate speech")
        if safety_result['self_harm']:
            risk_messages.append("Self-harm content")
        if safety_result['illegal_activities']:
            risk_messages.append("Illegal activities")
        
        return {
            'is_safe': False,
            'message': f"⚠️ Potentially dangerous content detected:\n" + 
                       "\n".join(f"- {msg}" for msg in risk_messages) +
                       "\n\nPlease modify your request to ensure safe and ethical content."
        }
    
    return {'is_safe': True, 'message': None}
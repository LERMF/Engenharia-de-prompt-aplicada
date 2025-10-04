"""
Gemini 1.5 Flash 8B Configuration
Master LLM driver for LUIX-SMOLPHI-ELEN
"""

import os
from typing import Optional, Dict, Any
import json

class GeminiConfig:
    """Configuration for Gemini 1.5 Flash 8B API"""
    
    # API Configuration
    API_KEY = "AIzaSyCayJJLAYpk6DMFd41gZG_F5rAP7KBc8pE"
    MODEL = "gemini-1.5-flash-8b-exp-1003"
    MAX_TOKENS = 1_000_000  # 1M context window
    
    # Performance Targets
    TARGET_QUOTA_USAGE = 0.50  # <50% of quota
    MAX_TOKENS_PER_REQUEST = 8192
    TEMPERATURE = 0.7
    TOP_P = 0.95
    TOP_K = 40
    
    # Safety Settings
    SAFETY_SETTINGS = {
        "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE"
    }
    
    # System Prompts
    SYSTEM_PROMPT = """You are SmolΦ-ELEN-Titan, an advanced AI assistant running on a minimal Linux system.
Your role:
- Optimize for <5s boot, <200MB idle RAM
- Maintain zero CVEs
- Coordinate with SmolLM-135M auxiliary brain
- Generate high-quality responses within quota limits
- Assist with system evolution and self-optimization
"""
    
    # Distillation Settings
    DISTILLATION_INTERVAL = 10_000  # Steps between distillation
    DISTILLATION_TARGET = "SmolLM-135M-q2_k"
    DISTILLATION_TEMPERATURE = 2.0
    
    @classmethod
    def get_generation_config(cls) -> Dict[str, Any]:
        """Get generation configuration for API calls"""
        return {
            "temperature": cls.TEMPERATURE,
            "top_p": cls.TOP_P,
            "top_k": cls.TOP_K,
            "max_output_tokens": cls.MAX_TOKENS_PER_REQUEST,
        }
    
    @classmethod
    def get_api_url(cls) -> str:
        """Get Gemini API URL"""
        return f"https://generativelanguage.googleapis.com/v1beta/models/{cls.MODEL}:generateContent"
    
    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        """Get API request headers"""
        return {
            "Content-Type": "application/json",
            "x-goog-api-key": cls.API_KEY
        }
    
    @classmethod
    def estimate_quota_usage(cls, tokens_used: int) -> float:
        """Estimate quota usage percentage"""
        # Gemini 1.5 Flash has generous quotas
        # Assuming 1M tokens per day free tier
        daily_limit = 1_000_000
        return (tokens_used / daily_limit) * 100
    
    @classmethod
    def should_use_auxiliary_brain(cls, quota_usage: float) -> bool:
        """Decide whether to fallback to SmolLM"""
        return quota_usage > (cls.TARGET_QUOTA_USAGE * 100)
    
    @classmethod
    def save_config(cls, path: str = "/etc/luix/gemini.json"):
        """Save configuration to file"""
        config = {
            "model": cls.MODEL,
            "api_key": cls.API_KEY[:10] + "..." + cls.API_KEY[-4:],  # Partially masked
            "max_tokens": cls.MAX_TOKENS,
            "generation_config": cls.get_generation_config(),
            "distillation": {
                "interval": cls.DISTILLATION_INTERVAL,
                "target": cls.DISTILLATION_TARGET,
                "temperature": cls.DISTILLATION_TEMPERATURE
            }
        }
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration saved to {path}")
    
    @classmethod
    def validate_api_key(cls) -> bool:
        """Validate API key format"""
        if not cls.API_KEY or len(cls.API_KEY) < 30:
            return False
        if not cls.API_KEY.startswith("AIza"):
            return False
        return True


if __name__ == "__main__":
    # Validate configuration
    print("🔧 Gemini Configuration")
    print(f"Model: {GeminiConfig.MODEL}")
    print(f"Context Window: {GeminiConfig.MAX_TOKENS:,} tokens")
    print(f"Target Quota Usage: {GeminiConfig.TARGET_QUOTA_USAGE*100}%")
    print(f"API Key Valid: {GeminiConfig.validate_api_key()}")
    
    # Save configuration
    GeminiConfig.save_config()

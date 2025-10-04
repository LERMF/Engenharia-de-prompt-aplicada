#!/usr/bin/env python3
"""
Gemini 1.5 Flash 8B Driver
High-performance async driver with automatic quota management
"""

import asyncio
import aiohttp
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import json
import sys
import os

# Add config to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'config'))
from gemini_config import GeminiConfig


@dataclass
class GeminiRequest:
    """Gemini API request"""
    prompt: str
    context: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


@dataclass
class GeminiResponse:
    """Gemini API response"""
    text: str
    tokens_used: int
    latency_ms: float
    finish_reason: str
    quota_remaining: float


class GeminiDriver:
    """Async Gemini API driver with quota management"""
    
    def __init__(self):
        self.config = GeminiConfig
        self.session: Optional[aiohttp.ClientSession] = None
        self.total_tokens_used = 0
        self.request_count = 0
        self.avg_latency_ms = 0.0
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers=self.config.get_headers(),
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _build_request_payload(self, request: GeminiRequest) -> Dict[str, Any]:
        """Build API request payload"""
        # Construct full prompt with system + user
        full_prompt = self.config.SYSTEM_PROMPT + "\n\n"
        if request.context:
            full_prompt += f"Context: {request.context}\n\n"
        full_prompt += f"User: {request.prompt}"
        
        return {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": request.temperature or self.config.TEMPERATURE,
                "topP": self.config.TOP_P,
                "topK": self.config.TOP_K,
                "maxOutputTokens": request.max_tokens or self.config.MAX_TOKENS_PER_REQUEST,
            },
            "safetySettings": [
                {"category": category, "threshold": threshold}
                for category, threshold in self.config.SAFETY_SETTINGS.items()
            ]
        }
    
    async def generate(self, request: GeminiRequest) -> GeminiResponse:
        """Generate response from Gemini"""
        if not self.session:
            raise RuntimeError("Driver not initialized. Use async with context manager.")
        
        start_time = time.perf_counter()
        
        # Build request
        payload = self._build_request_payload(request)
        url = self.config.get_api_url()
        
        try:
            # Make API call
            async with self.session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"Gemini API error {response.status}: {error_text}")
                
                data = await response.json()
                
                # Extract response
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                finish_reason = data["candidates"][0]["finishReason"]
                
                # Estimate tokens (rough approximation: 1 token ≈ 4 chars)
                tokens_used = len(request.prompt + text) // 4
                
                # Calculate latency
                latency_ms = (time.perf_counter() - start_time) * 1000
                
                # Update stats
                self.total_tokens_used += tokens_used
                self.request_count += 1
                self.avg_latency_ms = (
                    (self.avg_latency_ms * (self.request_count - 1) + latency_ms) 
                    / self.request_count
                )
                
                # Calculate quota
                quota_usage = self.config.estimate_quota_usage(self.total_tokens_used)
                quota_remaining = 100 - quota_usage
                
                return GeminiResponse(
                    text=text,
                    tokens_used=tokens_used,
                    latency_ms=latency_ms,
                    finish_reason=finish_reason,
                    quota_remaining=quota_remaining
                )
                
        except asyncio.TimeoutError:
            raise RuntimeError("Gemini API timeout")
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}")
    
    async def batch_generate(self, requests: List[GeminiRequest]) -> List[GeminiResponse]:
        """Generate multiple responses concurrently"""
        tasks = [self.generate(req) for req in requests]
        return await asyncio.gather(*tasks)
    
    def should_fallback_to_smollm(self) -> bool:
        """Check if we should use SmolLM due to quota"""
        quota_usage = self.config.estimate_quota_usage(self.total_tokens_used)
        return self.config.should_use_auxiliary_brain(quota_usage)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get driver statistics"""
        quota_usage = self.config.estimate_quota_usage(self.total_tokens_used)
        return {
            "total_requests": self.request_count,
            "total_tokens": self.total_tokens_used,
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "quota_usage_percent": round(quota_usage, 2),
            "quota_remaining_percent": round(100 - quota_usage, 2),
            "should_use_smollm": self.should_fallback_to_smollm()
        }


async def main():
    """Test the Gemini driver"""
    print("🧠 Testing Gemini 1.5 Flash 8B Driver\n")
    
    async with GeminiDriver() as driver:
        # Test request
        request = GeminiRequest(
            prompt="Explain how to optimize Linux boot time to under 5 seconds. Be concise.",
            context="Building LUIX-SMOLPHI-ELEN minimal Linux distribution"
        )
        
        print("📤 Sending request...")
        response = await driver.generate(request)
        
        print(f"\n✅ Response received:")
        print(f"   Latency: {response.latency_ms:.1f}ms")
        print(f"   Tokens: {response.tokens_used}")
        print(f"   Quota Remaining: {response.quota_remaining:.1f}%")
        print(f"\n📝 Response:\n{response.text}\n")
        
        # Show stats
        stats = driver.get_stats()
        print(f"📊 Driver Stats:")
        for key, value in stats.items():
            print(f"   {key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())

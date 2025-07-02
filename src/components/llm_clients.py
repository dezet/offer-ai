from abc import ABC, abstractmethod
import json
import logging
from typing import Dict, Optional
import os

from openai import OpenAI
import anthropic
import google.generativeai as genai

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    @abstractmethod
    def get_structured_offer(self, prompt: str) -> dict:
        raise NotImplementedError


class OpenAIClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = "gpt-4-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        logger.info(f"Initialized OpenAI client with model: {model}")
    
    def get_structured_offer(self, prompt: str) -> dict:
        """Call OpenAI API and return structured response"""
        logger.info("Calling OpenAI API...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for more consistent extraction
                response_format={"type": "json_object"}  # Force JSON response
            )
            
            result = response.choices[0].message.content
            logger.debug(f"Received response from OpenAI")
            
            # Parse JSON response
            return json.loads(result)
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise


class ClaudeClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        logger.info(f"Initialized Claude client with model: {model}")
    
    def get_structured_offer(self, prompt: str) -> dict:
        """Call Claude API and return structured response"""
        logger.info("Calling Claude API...")
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response.content[0].text
            logger.debug(f"Received response from Claude")
            
            # Parse JSON response
            return json.loads(result)
            
        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            raise


class GeminiClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        logger.info(f"Initialized Gemini client with model: {model}")
    
    def get_structured_offer(self, prompt: str) -> dict:
        """Call Gemini API and return structured response"""
        logger.info("Calling Gemini API...")
        
        try:
            # Configure generation parameters for JSON output
            generation_config = genai.GenerationConfig(
                temperature=0.1,
                candidate_count=1,
            )
            
            # The prompt already contains all instructions from prompt_template.md
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            result = response.text
            logger.debug(f"Received response from Gemini")
            
            # Clean up response if needed (Gemini sometimes adds markdown)
            if result.startswith("```json"):
                result = result[7:]  # Remove ```json
            if result.endswith("```"):
                result = result[:-3]  # Remove ```
            
            # Parse JSON response
            return json.loads(result.strip())
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            raise


class LLMClientFactory:
    """Factory for creating LLM clients"""
    
    @staticmethod
    def create_client(provider: str, api_key: Optional[str] = None) -> BaseLLMClient:
        """Create an LLM client based on provider name"""
        
        # Get API key from environment if not provided
        if not api_key:
            if provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
            elif provider == "claude":
                api_key = os.getenv("ANTHROPIC_API_KEY")
            elif provider == "gemini":
                api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError(f"API key not provided for {provider}")
        
        if provider == "openai":
            return OpenAIClient(api_key)
        elif provider == "claude":
            return ClaudeClient(api_key)
        elif provider == "gemini":
            return GeminiClient(api_key)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
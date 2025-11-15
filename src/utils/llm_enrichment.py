"""
LLM integration utilities for game data enrichment.
Supports multiple LLM providers with fallback and rate limiting.
"""

import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LLMConfig:
    """Configuration for LLM providers."""
    
    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        max_retries: int = 3,
        timeout: int = 30,
        rate_limit_delay: float = 1.0
    ):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.max_retries = max_retries
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay


class GameEnrichmentExtractor:
    """Extract structured insights from game data using LLMs."""
    
    PROMPT_VERSION = "v1.0"
    
    SYSTEM_PROMPT = """You are an expert game analyst. Extract structured 
information from game descriptions and metadata. Be precise and concise."""
    
    EXTRACTION_PROMPT = """Analyze the following game and extract:
1. Game Mechanics: List 3-8 core gameplay mechanics
2. Themes: List 2-5 main themes
3. Features: List 3-10 key features or functionality

Game Name: {name}
Developer: {developer}
Description: {description}
Short Description: {short_description}

Respond ONLY with valid JSON in this exact format:
{{
    "mechanics": ["mechanic1", "mechanic2", ...],
    "themes": ["theme1", "theme2", ...],
    "features": ["feature1", "feature2", ...],
    "confidence": 0.85
}}"""
    
    SENTIMENT_PROMPT = """Analyze player sentiment for this game based on 
available reviews:

Game: {name}
Reviews: {reviews_summary}

Provide:
1. Overall sentiment score (-1.0 to 1.0, where -1 is very negative, 
   0 is neutral, 1 is very positive)
2. Brief summary (2-3 sentences) of common themes in player feedback

Respond ONLY with valid JSON:
{{
    "sentiment_score": 0.75,
    "summary": "Brief summary here",
    "confidence": 0.90
}}"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._last_request_time = 0
    
    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.config.rate_limit_delay:
            time.sleep(self.config.rate_limit_delay - elapsed)
        self._last_request_time = time.time()
    
    def _call_llm(self, prompt: str, system_prompt: str) -> str:
        """
        Call the configured LLM provider.
        This is a placeholder - implement actual API calls.
        """
        self._rate_limit()
        
        # TODO: Implement actual LLM API calls based on provider
        if self.config.provider == "openai":
            return self._call_openai(prompt, system_prompt)
        elif self.config.provider == "anthropic":
            return self._call_anthropic(prompt, system_prompt)
        elif self.config.provider == "local":
            return self._call_local_model(prompt, system_prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")
    
    def _call_openai(self, prompt: str, system_prompt: str) -> str:
        """Call OpenAI API."""
        # Placeholder for OpenAI integration
        # Requires: pip install openai
        logger.warning(
            "OpenAI integration not implemented. "
            "Install openai package and implement this method."
        )
        raise NotImplementedError("OpenAI integration pending")
    
    def _call_anthropic(self, prompt: str, system_prompt: str) -> str:
        """Call Anthropic Claude API."""
        # Placeholder for Anthropic integration
        # Requires: pip install anthropic
        logger.warning(
            "Anthropic integration not implemented. "
            "Install anthropic package and implement this method."
        )
        raise NotImplementedError("Anthropic integration pending")
    
    def _call_local_model(self, prompt: str, system_prompt: str) -> str:
        """Call local LLM model (e.g., via Ollama)."""
        # Placeholder for local model integration
        # Requires: ollama or similar
        logger.warning(
            "Local model integration not implemented. "
            "Install ollama or similar and implement this method."
        )
        raise NotImplementedError("Local model integration pending")
    
    def extract_game_features(
        self,
        game_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract mechanics, themes, and features from game data.
        
        Args:
            game_data: Dictionary with game information
            
        Returns:
            Dictionary with extracted features and metadata
        """
        start_time = time.time()
        
        try:
            prompt = self.EXTRACTION_PROMPT.format(
                name=game_data.get('name', 'Unknown'),
                developer=game_data.get('developer', 'Unknown'),
                description=game_data.get('description', '')[:2000],
                short_description=game_data.get('short_description', '')
            )
            
            response = self._call_llm(prompt, self.SYSTEM_PROMPT)
            extracted = json.loads(response)
            
            processing_time = time.time() - start_time
            
            return {
                'mechanics': extracted.get('mechanics', []),
                'themes': extracted.get('themes', []),
                'features': extracted.get('features', []),
                'confidence_score': extracted.get('confidence', 0.0),
                'processing_time_seconds': processing_time,
                'llm_model': f"{self.config.provider}:{self.config.model}",
                'prompt_version': self.PROMPT_VERSION,
                'error_message': None
            }
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return {
                'mechanics': [],
                'themes': [],
                'features': [],
                'confidence_score': 0.0,
                'processing_time_seconds': time.time() - start_time,
                'llm_model': f"{self.config.provider}:{self.config.model}",
                'prompt_version': self.PROMPT_VERSION,
                'error_message': str(e)
            }
    
    def analyze_sentiment(
        self,
        game_data: Dict[str, Any],
        reviews_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze player sentiment from reviews.
        
        Args:
            game_data: Dictionary with game information
            reviews_data: List of review dictionaries
            
        Returns:
            Dictionary with sentiment analysis results
        """
        if not reviews_data:
            return {
                'sentiment_score': 0.0,
                'sentiment_summary': 'No reviews available',
                'confidence_score': 0.0
            }
        
        try:
            # Prepare reviews summary
            reviews_summary = self._prepare_reviews_summary(reviews_data)
            
            prompt = self.SENTIMENT_PROMPT.format(
                name=game_data.get('name', 'Unknown'),
                reviews_summary=reviews_summary
            )
            
            response = self._call_llm(prompt, self.SYSTEM_PROMPT)
            sentiment = json.loads(response)
            
            return {
                'sentiment_score': sentiment.get('sentiment_score', 0.0),
                'sentiment_summary': sentiment.get('summary', ''),
                'confidence_score': sentiment.get('confidence', 0.0)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            # Fallback to simple positive/negative ratio
            positive_count = sum(
                1 for r in reviews_data if r.get('is_positive', False)
            )
            total = len(reviews_data)
            ratio = positive_count / total if total > 0 else 0.5
            
            return {
                'sentiment_score': (ratio - 0.5) * 2,  # Scale to -1 to 1
                'sentiment_summary': (
                    f"Based on {total} reviews: "
                    f"{positive_count} positive, "
                    f"{total - positive_count} negative"
                ),
                'confidence_score': 0.5
            }
    
    def _prepare_reviews_summary(
        self,
        reviews_data: List[Dict[str, Any]],
        max_reviews: int = 20
    ) -> str:
        """Prepare a summary of reviews for sentiment analysis."""
        summaries = []
        for review in reviews_data[:max_reviews]:
            sentiment = "Positive" if review.get('is_positive') else "Negative"
            text = review.get('review_text', '')[:200]
            summaries.append(f"[{sentiment}] {text}")
        
        return "\n".join(summaries)


def create_default_extractor() -> GameEnrichmentExtractor:
    """Create a default extractor with mock implementation."""
    config = LLMConfig(
        provider="local",  # Use local by default to avoid API costs
        model="mock",
        rate_limit_delay=0.5
    )
    return GameEnrichmentExtractor(config)

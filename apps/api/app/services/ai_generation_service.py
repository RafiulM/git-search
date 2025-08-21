"""
Unified AI Generation Service that supports multiple providers and models
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union

from app.models.ai_config import (
    AIProvider,
    AIConfig,
    AIModelConfig,
    GenerationRequest,
    GenerationResponse,
    RepositorySummaryConfig,
    ShortDescriptionConfig,
    ContentExtractionConfig,
    DEFAULT_OPENAI_CONFIG,
    DEFAULT_GEMINI_CONFIG,
    REPOSITORY_SUMMARY_CONFIGS,
    SHORT_DESCRIPTION_CONFIGS,
    CONTENT_EXTRACTION_CONFIGS,
)
from app.services.openai_service import OpenAIService
from app.services.gemini_ai import GeminiAIService

logger = logging.getLogger(__name__)


class AIGenerationService:
    """Unified service for AI generation across multiple providers"""

    def __init__(self):
        """Initialize the generation service"""
        self._openai_service: Optional[OpenAIService] = None
        self._gemini_service: Optional[GeminiAIService] = None

    def _get_openai_service(self, api_key: Optional[str] = None) -> OpenAIService:
        """Get or create OpenAI service instance"""
        if self._openai_service is None or api_key is not None:
            self._openai_service = OpenAIService(api_key=api_key)
        return self._openai_service

    def _get_gemini_service(self, api_key: Optional[str] = None) -> GeminiAIService:
        """Get or create Gemini service instance"""
        if self._gemini_service is None or api_key is not None:
            self._gemini_service = GeminiAIService(api_key=api_key)
        return self._gemini_service

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """
        Generate content using the specified AI provider and model

        Args:
            request: Generation request with prompt, config, and optional context

        Returns:
            GenerationResponse with the generated content and metadata
        """
        start_time = time.time()

        try:
            logger.info(
                f"Generating content using {request.ai_config.provider} ({request.ai_config.model})"
            )

            if request.ai_config.provider == AIProvider.OPENAI:
                return await self._generate_openai(request, start_time)
            elif request.ai_config.provider == AIProvider.GOOGLE:
                return await self._generate_gemini(request, start_time)
            else:
                return GenerationResponse(
                    success=False,
                    error=f"Unsupported AI provider: {request.ai_config.provider}",
                    provider=str(request.ai_config.provider),
                    model=str(request.ai_config.model),
                    processing_time=time.time() - start_time,
                )

        except Exception as e:
            logger.error(f"Error in AI generation: {str(e)}")
            return GenerationResponse(
                success=False,
                error=str(e),
                provider=str(request.ai_config.provider),
                model=str(request.ai_config.model),
                processing_time=time.time() - start_time,
            )

    async def _generate_openai(
        self, request: GenerationRequest, start_time: float
    ) -> GenerationResponse:
        """Generate content using OpenAI"""
        try:
            service = self._get_openai_service(request.ai_config.api_key)

            # Prepare messages
            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            messages.append({"role": "user", "content": request.prompt})

            # Prepare generation parameters
            generation_params = {
                "model": str(request.ai_config.model),
                "messages": messages,
                "temperature": request.ai_config.config.temperature,
            }

            # Add optional parameters
            if request.ai_config.config.max_tokens:
                generation_params["max_tokens"] = request.ai_config.config.max_tokens
            if request.ai_config.config.max_completion_tokens:
                generation_params["max_completion_tokens"] = (
                    request.ai_config.config.max_completion_tokens
                )
            if request.ai_config.config.top_p is not None:
                generation_params["top_p"] = request.ai_config.config.top_p
            if request.ai_config.config.frequency_penalty is not None:
                generation_params["frequency_penalty"] = (
                    request.ai_config.config.frequency_penalty
                )
            if request.ai_config.config.presence_penalty is not None:
                generation_params["presence_penalty"] = (
                    request.ai_config.config.presence_penalty
                )

            # Make the API call
            response = await service.client.chat.completions.create(**generation_params)

            if not response.choices or not response.choices[0].message.content:
                return GenerationResponse(
                    success=False,
                    error="No content generated",
                    provider=str(request.ai_config.provider),
                    model=str(request.ai_config.model),
                    processing_time=time.time() - start_time,
                )

            tokens_used = None
            if hasattr(response, "usage") and response.usage:
                tokens_used = response.usage.total_tokens

            return GenerationResponse(
                success=True,
                content=response.choices[0].message.content,
                provider=str(request.ai_config.provider),
                model=str(request.ai_config.model),
                tokens_used=tokens_used,
                processing_time=time.time() - start_time,
                metadata={"finish_reason": response.choices[0].finish_reason},
            )

        except Exception as e:
            logger.error(f"OpenAI generation error: {str(e)}")
            return GenerationResponse(
                success=False,
                error=str(e),
                provider=str(request.ai_config.provider),
                model=str(request.ai_config.model),
                processing_time=time.time() - start_time,
            )

    async def _generate_gemini(
        self, request: GenerationRequest, start_time: float
    ) -> GenerationResponse:
        """Generate content using Gemini"""
        try:
            service = self._get_gemini_service(request.ai_config.api_key)

            # Prepare the full prompt
            full_prompt = request.prompt
            if request.system_prompt:
                full_prompt = f"{request.system_prompt}\n\n{request.prompt}"

            # Create generation config
            from google.genai import types

            generation_config = types.GenerateContentConfig()

            # Make the API call
            response = await asyncio.to_thread(
                service.client.models.generate_content,
                model=str(request.ai_config.model),
                contents=full_prompt,
                config=generation_config,
            )

            if not response or not response.text:
                return GenerationResponse(
                    success=False,
                    error="No content generated",
                    provider=str(request.ai_config.provider),
                    model=str(request.ai_config.model),
                    processing_time=time.time() - start_time,
                )

            return GenerationResponse(
                success=True,
                content=response.text,
                provider=str(request.ai_config.provider),
                model=str(request.ai_config.model),
                processing_time=time.time() - start_time,
                metadata={"response_type": "gemini_generate_content"},
            )

        except Exception as e:
            logger.error(f"Gemini generation error: {str(e)}")
            return GenerationResponse(
                success=False,
                error=str(e),
                provider=str(request.ai_config.provider),
                model=str(request.ai_config.model),
                processing_time=time.time() - start_time,
            )

    async def generate_repository_summary(
        self,
        full_text: str,
        repository_info: Dict[str, Any],
        config: Optional[RepositorySummaryConfig] = None,
        provider: Optional[AIProvider] = None,
    ) -> Dict[str, Any]:
        """
        Generate a repository summary using configurable AI provider

        Args:
            full_text: Full repository text content
            repository_info: Repository metadata and statistics
            config: Optional configuration for the summary generation
            provider: Optional provider override (defaults to OpenAI)

        Returns:
            Dictionary with summary results and metadata
        """
        try:
            # Use provided config or create default
            if config is None:
                provider = provider or AIProvider.OPENAI
                ai_config = REPOSITORY_SUMMARY_CONFIGS[provider]
                config = RepositorySummaryConfig(ai_config=ai_config)

            logger.info(
                f"Generating repository summary with {config.ai_config.provider}"
            )

            # Use the provider-specific service directly for complex operations
            if config.ai_config.provider == AIProvider.OPENAI:
                service = self._get_openai_service(config.ai_config.api_key)
                return await service.generate_repository_summary(
                    full_text, repository_info, None  # Let service get its own prompt
                )
            elif config.ai_config.provider == AIProvider.GOOGLE:
                service = self._get_gemini_service(config.ai_config.api_key)
                return await service.generate_repository_summary(
                    full_text, repository_info, None  # Let service get its own prompt
                )
            else:
                return {
                    "success": False,
                    "error": f"Unsupported provider for repository summary: {config.ai_config.provider}",
                    "summary": None,
                }

        except Exception as e:
            logger.error(f"Error generating repository summary: {str(e)}")
            return {"success": False, "error": str(e), "summary": None}

    async def generate_short_description(
        self,
        summary: str,
        repository_info: Optional[Dict[str, Any]] = None,
        config: Optional[ShortDescriptionConfig] = None,
        provider: Optional[AIProvider] = None,
    ) -> Dict[str, Any]:
        """
        Generate a short description from a repository summary

        Args:
            summary: The full repository summary to condense
            repository_info: Optional repository context information
            config: Optional configuration for the description generation
            provider: Optional provider override (defaults to OpenAI)

        Returns:
            Dictionary with short description results and metadata
        """
        try:
            # Use provided config or create default
            if config is None:
                provider = provider or AIProvider.OPENAI
                ai_config = SHORT_DESCRIPTION_CONFIGS[provider]
                config = ShortDescriptionConfig(ai_config=ai_config)

            logger.info(
                f"Generating short description with {config.ai_config.provider}"
            )

            # Use the provider-specific service directly
            if config.ai_config.provider == AIProvider.OPENAI:
                service = self._get_openai_service(config.ai_config.api_key)
                return await service.generate_short_description(
                    summary, repository_info, config.max_length
                )
            elif config.ai_config.provider == AIProvider.GOOGLE:
                service = self._get_gemini_service(config.ai_config.api_key)
                return await service.generate_short_description(
                    summary, repository_info, config.max_length
                )
            else:
                return {
                    "success": False,
                    "error": f"Unsupported provider for short description: {config.ai_config.provider}",
                    "short_description": None,
                }

        except Exception as e:
            logger.error(f"Error generating short description: {str(e)}")
            return {"success": False, "error": str(e), "short_description": None}

    async def extract_repositories_from_content(
        self,
        content: str,
        website_url: str,
        config: Optional[ContentExtractionConfig] = None,
        provider: Optional[AIProvider] = None,
    ) -> Dict[str, Any]:
        """
        Extract repository information from website content

        Args:
            content: Scraped website content (markdown format)
            website_url: Original website URL for context
            config: Optional configuration for the extraction
            provider: Optional provider override (defaults to Gemini for structured output)

        Returns:
            Dictionary containing extracted repositories and metadata
        """
        try:
            # Use provided config or create default (prefer Gemini for structured output)
            if config is None:
                provider = provider or AIProvider.GOOGLE
                ai_config = CONTENT_EXTRACTION_CONFIGS[provider]
                config = ContentExtractionConfig(
                    ai_config=ai_config, extraction_type="repositories"
                )

            logger.info(f"Extracting repositories with {config.ai_config.provider}")

            # Use the provider-specific service directly
            if config.ai_config.provider == AIProvider.OPENAI:
                service = self._get_openai_service(config.ai_config.api_key)
                return await service.extract_repositories_from_content(
                    content, website_url
                )
            elif config.ai_config.provider == AIProvider.GOOGLE:
                service = self._get_gemini_service(config.ai_config.api_key)
                return await service.extract_repositories_from_content(
                    content, website_url
                )
            else:
                return {
                    "success": False,
                    "error": f"Unsupported provider for content extraction: {config.ai_config.provider}",
                    "extracted_data": None,
                }

        except Exception as e:
            logger.error(f"Error extracting repositories: {str(e)}")
            return {"success": False, "error": str(e), "extracted_data": None}

    def get_default_config(self, provider: AIProvider) -> AIConfig:
        """Get default configuration for a provider"""
        if provider == AIProvider.OPENAI:
            return DEFAULT_OPENAI_CONFIG
        elif provider == AIProvider.GOOGLE:
            return DEFAULT_GEMINI_CONFIG
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def get_task_config(self, task_type: str, provider: AIProvider) -> AIConfig:
        """Get task-specific configuration for a provider"""
        config_map = {
            "repository_summary": REPOSITORY_SUMMARY_CONFIGS,
            "short_description": SHORT_DESCRIPTION_CONFIGS,
            "content_extraction": CONTENT_EXTRACTION_CONFIGS,
        }

        if task_type not in config_map:
            raise ValueError(f"Unsupported task type: {task_type}")

        if provider not in config_map[task_type]:
            raise ValueError(f"No config for task {task_type} with provider {provider}")

        return config_map[task_type][provider]

    async def health_check(self) -> Dict[str, Any]:
        """Check the health of all AI services"""
        health_status = {
            "openai": {"available": False, "error": None},
            "gemini": {"available": False, "error": None},
        }

        # Test OpenAI
        try:
            test_request = GenerationRequest(
                prompt="Hello",
                ai_config=AIConfig(
                    provider=AIProvider.OPENAI,
                    model="o4-mini",
                    config=AIModelConfig(temperature=0.1, max_tokens=5),
                ),
            )
            response = await self.generate(test_request)
            health_status["openai"]["available"] = response.success
            if not response.success:
                health_status["openai"]["error"] = response.error
        except Exception as e:
            health_status["openai"]["error"] = str(e)

        # Test Gemini
        try:
            test_request = GenerationRequest(
                prompt="Hello",
                ai_config=AIConfig(
                    provider=AIProvider.GOOGLE, model="gemini-2.0-flash"
                ),
            )
            response = await self.generate(test_request)
            health_status["gemini"]["available"] = response.success
            if not response.success:
                health_status["gemini"]["error"] = response.error
        except Exception as e:
            health_status["gemini"]["error"] = str(e)

        return health_status


# Create a singleton instance
ai_generation_service = AIGenerationService()

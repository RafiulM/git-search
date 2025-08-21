"""
AI Configuration Models for provider and model selection
"""

from enum import Enum
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class AIProvider(str, Enum):
    """Supported AI providers"""

    OPENAI = "openai"
    GOOGLE = "google"


class OpenAIModel(str, Enum):
    """OpenAI model options"""

    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_41 = "gpt-4.1"
    O4_MINI = "o4-mini"


class GeminiModel(str, Enum):
    """Gemini model options"""

    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_2_5_PRO = "gemini-2.5-pro"
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"


class AIModelConfig(BaseModel):
    """Configuration for AI model parameters"""

    temperature: float = Field(
        default=1, ge=0.0, le=2.0, description="Model temperature"
    )
    max_tokens: Optional[int] = Field(
        default=None, ge=1, description="Maximum tokens to generate"
    )
    max_completion_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum completion tokens to generate, for thinking models",
    )
    top_p: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Top-p sampling parameter"
    )
    frequency_penalty: Optional[float] = Field(
        default=None, ge=-2.0, le=2.0, description="Frequency penalty"
    )
    presence_penalty: Optional[float] = Field(
        default=None, ge=-2.0, le=2.0, description="Presence penalty"
    )


class AIConfig(BaseModel):
    """Main AI configuration for generation requests"""

    provider: AIProvider = Field(description="AI provider to use")
    model: Union[OpenAIModel, GeminiModel, str] = Field(
        description="Specific model to use"
    )
    config: AIModelConfig = Field(
        default_factory=AIModelConfig, description="Model configuration parameters"
    )

    # Provider-specific settings
    api_key: Optional[str] = Field(
        default=None, description="Override API key (if not using environment)"
    )

    class Config:
        use_enum_values = True


class GenerationRequest(BaseModel):
    """Request model for AI generation"""

    prompt: str = Field(description="The main prompt for generation")
    system_prompt: Optional[str] = Field(
        default=None, description="System prompt to set context"
    )
    ai_config: AIConfig = Field(description="AI configuration for this request")

    # Context data for specific use cases
    context_data: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional context data"
    )


class GenerationResponse(BaseModel):
    """Response model for AI generation"""

    success: bool = Field(description="Whether the generation was successful")
    content: Optional[str] = Field(default=None, description="Generated content")
    error: Optional[str] = Field(
        default=None, description="Error message if generation failed"
    )

    # Metadata
    provider: str = Field(description="AI provider used")
    model: str = Field(description="Specific model used")
    tokens_used: Optional[int] = Field(
        default=None, description="Number of tokens used"
    )
    processing_time: Optional[float] = Field(
        default=None, description="Processing time in seconds"
    )

    # Additional metadata
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional response metadata"
    )


class ChunkProcessingConfig(BaseModel):
    """Configuration for processing large content in chunks"""

    max_chars_per_chunk: int = Field(
        default=1500000, description="Maximum characters per chunk"
    )
    chunk_overlap: int = Field(
        default=0, description="Character overlap between chunks"
    )
    parallel_processing: bool = Field(
        default=True, description="Whether to process chunks in parallel"
    )
    max_concurrent_chunks: int = Field(
        default=5, description="Maximum concurrent chunk processing"
    )


class RepositorySummaryConfig(BaseModel):
    """Configuration for repository summary generation"""

    ai_config: AIConfig = Field(description="AI configuration")
    chunk_config: ChunkProcessingConfig = Field(default_factory=ChunkProcessingConfig)
    prompt_type: str = Field(
        default="repository_summary", description="Type of prompt to use"
    )
    prompt_name: str = Field(default="default", description="Specific prompt name")
    include_chunk_summaries: bool = Field(
        default=True, description="Whether to include individual chunk summaries"
    )


class ShortDescriptionConfig(BaseModel):
    """Configuration for short description generation"""

    ai_config: AIConfig = Field(description="AI configuration")
    max_length: int = Field(default=150, description="Maximum length of description")
    style: str = Field(
        default="technical",
        description="Style of description (technical, marketing, etc.)",
    )


class ContentExtractionConfig(BaseModel):
    """Configuration for content extraction tasks"""

    ai_config: AIConfig = Field(description="AI configuration")
    extraction_type: str = Field(
        description="Type of extraction (repositories, features, etc.)"
    )
    output_format: str = Field(
        default="json", description="Output format (json, structured, etc.)"
    )
    confidence_threshold: float = Field(
        default=0.5, description="Minimum confidence score for results"
    )


# Default configurations for different use cases
DEFAULT_OPENAI_CONFIG = AIConfig(
    provider=AIProvider.OPENAI,
    model=OpenAIModel.GPT_4O,
    config=AIModelConfig(temperature=0.3, max_tokens=4000),
)

DEFAULT_GEMINI_CONFIG = AIConfig(
    provider=AIProvider.GOOGLE,
    model=GeminiModel.GEMINI_2_0_FLASH,
    config=AIModelConfig(temperature=0.3),
)

# Task-specific default configurations
REPOSITORY_SUMMARY_CONFIGS = {
    AIProvider.OPENAI: AIConfig(
        provider=AIProvider.OPENAI,
        model=OpenAIModel.GPT_4O,
        config=AIModelConfig(temperature=0.3, max_tokens=8000),
    ),
    AIProvider.GOOGLE: AIConfig(
        provider=AIProvider.GOOGLE,
        model=GeminiModel.GEMINI_2_5_FLASH,
        config=AIModelConfig(temperature=0.3),
    ),
}

SHORT_DESCRIPTION_CONFIGS = {
    AIProvider.OPENAI: AIConfig(
        provider=AIProvider.OPENAI,
        model=OpenAIModel.GPT_4O,
        config=AIModelConfig(temperature=0.3, max_tokens=100),
    ),
    AIProvider.GOOGLE: AIConfig(
        provider=AIProvider.GOOGLE,
        model=GeminiModel.GEMINI_2_5_PRO,
        config=AIModelConfig(temperature=0.3),
    ),
}

CONTENT_EXTRACTION_CONFIGS = {
    AIProvider.OPENAI: AIConfig(
        provider=AIProvider.OPENAI,
        model=OpenAIModel.GPT_4O,
        config=AIModelConfig(temperature=0.1, max_tokens=4000),
    ),
    AIProvider.GOOGLE: AIConfig(
        provider=AIProvider.GOOGLE,
        model=GeminiModel.GEMINI_2_0_FLASH,
        config=AIModelConfig(temperature=0.1),
    ),
}

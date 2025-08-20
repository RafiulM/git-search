"""
Google Gemini AI Service for repository analysis and summarization
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from google import genai
from google.genai import types
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Import database service
from app.services.database import db_service


class GeminiAIService:
    """Service for interacting with Google Gemini AI models"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini AI service"""
        self.api_key = api_key or os.getenv("GOOGLE_AI_API_KEY")
        if not self.api_key:
            raise ValueError("Google AI API key is required")

        # Initialize the Gemini client
        self.client = genai.Client(api_key=self.api_key)

        # Model names
        self.chunk_model = "gemini-2.0-flash"
        self.summary_model = "gemini-2.5-flash"

        # Generation config for different use cases
        self.chunk_config = types.GenerateContentConfig()
        self.summary_config = types.GenerateContentConfig()
        self.extraction_config = types.GenerateContentConfig()

    async def get_system_prompt(
        self, prompt_type: str, prompt_name: str = "default"
    ) -> Optional[str]:
        """
        Get system prompt from database or return default prompt

        Args:
            prompt_type: Type of prompt (e.g., "repository_summary", "code_review")
            prompt_name: Name of prompt (default: "default")

        Returns:
            Prompt content as string or None if not found
        """
        try:
            # Try to get prompt from database
            prompt_content = await db_service.get_system_prompt(
                prompt_type, prompt_name
            )

            if prompt_content:
                return prompt_content

            # Return default prompts based on type
            default_prompts = {
                "repository_summary": """You are an expert code reviewer and software architect. 
                Analyze the provided repository content and create a comprehensive summary that helps developers understand:
                1. What this codebase does (purpose and functionality)
                2. Key architecture and technology choices
                3. Main components and how they interact
                4. Notable patterns, configurations, or design decisions
                5. Overall code structure and organization
                
                Make your summary clear, technical, and actionable for developers who need to understand or work with this codebase.""",
                "code_review": """You are an expert software engineer conducting a thorough code review. 
                Analyze the provided code and provide feedback on:
                1. Code quality and best practices
                2. Potential bugs or issues
                3. Performance optimizations
                4. Security considerations
                5. Maintainability and readability
                6. Architecture and design patterns
                
                Provide specific, actionable feedback with examples where possible.""",
                "architecture_analysis": """You are a senior software architect. 
                Analyze the provided repository and provide a detailed architecture analysis covering:
                1. System architecture and components
                2. Technology stack and framework choices
                3. Data flow and communication patterns
                4. Scalability and performance considerations
                5. Security architecture
                6. Deployment and infrastructure
                7. Potential improvements or concerns
                
                Provide a comprehensive technical analysis with specific examples from the codebase.""",
                "documentation_generation": """You are a technical documentation specialist. 
                Create clear, comprehensive documentation based on the provided codebase:
                1. API documentation (if applicable)
                2. Installation and setup instructions
                3. Configuration guide
                4. Usage examples
                5. Architecture overview
                6. Troubleshooting guide
                
                Make the documentation accessible to both technical and non-technical users where appropriate.""",
            }

            return default_prompts.get(prompt_type)

        except Exception as e:
            logger.warning(
                f"Error getting system prompt for {prompt_type}/{prompt_name}: {str(e)}"
            )
            return None

    def chunk_text(self, text: str, max_chars_per_chunk: int = 1500000) -> List[str]:
        """
        Split text into chunks by character count with smart breaking points
        Based on the TypeScript reference implementation
        """
        if len(text) <= max_chars_per_chunk:
            return [text]

        chunks = []
        current_index = 0

        while current_index < len(text):
            end_index = current_index + max_chars_per_chunk

            # If we're not at the end of the text, try to find a good breaking point
            if end_index < len(text):
                # Look for natural breaking points within the last 10% of the chunk
                search_start = end_index - int(max_chars_per_chunk * 0.1)
                break_point = end_index

                # Try to find a good breaking point (in order of preference)
                break_patterns = [
                    "\n\n",  # Double newlines (paragraph breaks)
                    "\n=",  # Section headers with equals
                    "\n-",  # Section headers with dashes
                    "\nFILE:",  # File boundaries in repo2text output
                    "\nclass ",
                    "\nfunction ",
                    "\nexport ",
                    "\nimport ",  # Code structure breaks
                    "\n}",  # End of code blocks
                    "\n",  # Any newline
                    ". ",  # Sentence endings
                    " ",  # Word boundaries
                ]

                for pattern in break_patterns:
                    # Find the last occurrence of the pattern in the search area
                    search_text = text[search_start:end_index]
                    last_occurrence = search_text.rfind(pattern)

                    if last_occurrence != -1:
                        break_point = search_start + last_occurrence + len(pattern)
                        break

                end_index = break_point

            chunks.append(text[current_index:end_index])
            current_index = end_index

        return chunks

    async def generate_chunk_summary(
        self,
        chunk: str,
        chunk_index: int,
        total_chunks: int,
        repository_context: str,
        system_prompt: str,
    ) -> Dict[str, Any]:
        """Generate summary for a single chunk of repository content"""
        try:
            # Prepare the chunk with context
            chunk_with_context = (
                repository_context
                + f"\nCHUNK {chunk_index + 1}/{total_chunks} CONTENT:\n"
                + chunk
            )

            # Create the full prompt
            full_prompt = f"""{system_prompt}

You are analyzing chunk {chunk_index + 1} of {total_chunks} from a repository. 
The repository overview, statistics, and structure are provided for context.
Focus on the key components, functionality, and structure in this specific chunk.
Keep your summary comprehensive but concise, and relate it to the overall repository structure when relevant.

{chunk_with_context}"""

            # Generate summary using Gemini
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.chunk_model,
                contents=full_prompt,
                config=self.chunk_config,
            )

            return {
                "chunk_index": chunk_index + 1,
                "total_chunks": total_chunks,
                "summary": response.text,
                "character_count": len(chunk),
                "success": True,
                "error": None,
            }

        except Exception as e:
            logger.error(f"Error processing chunk {chunk_index + 1}: {str(e)}")

            fallback_summary = (
                f"Chunk {chunk_index + 1} processing failed ({str(e)}). "
                f"This chunk contained {len(chunk):,} characters of repository content "
                f"that could not be analyzed automatically."
            )

            return {
                "chunk_index": chunk_index + 1,
                "total_chunks": total_chunks,
                "summary": fallback_summary,
                "character_count": len(chunk),
                "success": False,
                "error": str(e),
            }

    async def generate_repository_summary(
        self,
        full_text: str,
        repository_info: Dict[str, Any],
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive repository summary by processing in chunks
        """
        try:
            # Get system prompt from database if not provided
            if not system_prompt:
                system_prompt = await self.get_system_prompt("repository_summary")

            # If still no system prompt, use a basic default
            if not system_prompt:
                system_prompt = """You are an expert code reviewer and software architect. 
                Analyze the provided repository content and create a comprehensive summary that helps developers understand:
                1. What this codebase does (purpose and functionality)
                2. Key architecture and technology choices
                3. Main components and how they interact
                4. Notable patterns, configurations, or design decisions
                5. Overall code structure and organization
                
                Make your summary clear, technical, and actionable for developers who need to understand or work with this codebase."""

            # Create repository context
            stats = repository_info.get("statistics", {})
            structure = repository_info.get("structure", {})

            repository_context = f"""
REPOSITORY OVERVIEW:
URL: {repository_info.get('repository_url', 'Unknown')}

STATISTICS:
- Files processed: {stats.get('files_processed', 0)}
- Binary files skipped: {stats.get('binary_files_skipped', 0)}
- Large files skipped: {stats.get('large_files_skipped', 0)}
- Encoding errors: {stats.get('encoding_errors', 0)}
- Total characters: {stats.get('total_characters', 0):,}
- Total lines: {stats.get('total_lines', 0):,}
- Total files found: {stats.get('total_files_found', 0)}
- Total directories: {stats.get('total_directories', 0)}

REPOSITORY STRUCTURE:
- Total files in structure: {structure.get('total_files', 0)}
- Total directories in structure: {structure.get('total_dirs', 0)}

{f"DIRECTORY TREE:\n{structure.get('tree', 'Not available')}" if structure.get('tree') else "DIRECTORY TREE: Not available"}

---
"""

            # Split text into chunks
            chunks = self.chunk_text(full_text, 1200000)  # 1.2M chars per chunk
            logger.info(f"Processing {len(chunks)} chunks of repository data")

            # Process chunks in parallel
            chunk_tasks = [
                self.generate_chunk_summary(
                    chunk, index, len(chunks), repository_context, system_prompt
                )
                for index, chunk in enumerate(chunks)
            ]

            chunk_summaries = await asyncio.gather(*chunk_tasks)

            # Separate successful and failed chunks
            successful_chunks = [c for c in chunk_summaries if c["success"]]
            failed_chunks = [c for c in chunk_summaries if not c["success"]]

            logger.info(
                f"Chunk processing complete: {len(successful_chunks)} successful, "
                f"{len(failed_chunks)} failed out of {len(chunks)} total"
            )

            if failed_chunks:
                logger.warning(
                    f"Failed chunks: {[c['chunk_index'] for c in failed_chunks]}"
                )

                # Only fail if ALL chunks failed
                if len(failed_chunks) == len(chunks):
                    raise Exception("All repository chunks failed to process")

            # Combine chunk summaries for final summary
            combined_summaries = "\n\n".join(
                [
                    f"--- Chunk {c['chunk_index']}/{c['total_chunks']} "
                    f"({c['character_count']:,} chars) ---\n{c['summary']}"
                    for c in chunk_summaries
                ]
            )

            # Create processing status message
            processing_status = ""
            if failed_chunks:
                processing_status = (
                    f"\n\nIMPORTANT: {len(failed_chunks)} out of {len(chunks)} chunks "
                    f"failed to process due to errors. The analysis below is based on "
                    f"{len(successful_chunks)} successfully processed chunks. "
                    f"Please note this limitation in your summary."
                )
            else:
                processing_status = (
                    f"\n\nAll {len(chunks)} chunks were successfully processed."
                )

            # Create final summary prompt
            final_summary_prompt = f"""You are creating a comprehensive summary of a repository that was analyzed in {len(chunks)} chunks. 

Below are the individual summaries for each chunk. Your task is to create a unified, comprehensive summary that:
1. Captures the overall purpose and functionality of the repository
2. Highlights the main components and their relationships
3. Describes the technology stack and architecture
4. Notes any important patterns, configurations, or notable features
5. Provides a clear understanding of what this codebase does and how it's structured
6. If some chunks failed to process, acknowledge this limitation but provide the best analysis possible from available data

Repository Information:
- URL: {repository_info.get('repository_url', 'Unknown')}
- Files processed: {stats.get('files_processed', 0)}
- Total characters: {stats.get('total_characters', 0):,}
- Total lines: {stats.get('total_lines', 0):,}
- Total files in structure: {structure.get('total_files', 0)}
- Total directories: {structure.get('total_dirs', 0)}
- Chunks analyzed: {len(chunks)}
- Successful chunks: {len(successful_chunks)}
- Failed chunks: {len(failed_chunks)}

Repository Structure:
{structure.get('tree', 'Detailed structure not available')}{processing_status}

Individual Chunk Summaries:
{combined_summaries}"""

            # Limit prompt size if too large
            max_summary_length = 1600000
            if len(final_summary_prompt) > max_summary_length:
                logger.warning(
                    f"Final summary prompt too long ({len(final_summary_prompt):,} chars), "
                    f"truncating to {max_summary_length:,} characters"
                )
                final_summary_prompt = final_summary_prompt[:max_summary_length]

            # Generate final summary
            final_response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.summary_model,
                contents=f"{system_prompt}\n\n{final_summary_prompt}",
                config=self.summary_config,
            )

            return {
                "success": True,
                "summary": final_response.text,
                "chunks_processed": len(chunks),
                "successful_chunks": len(successful_chunks),
                "failed_chunks": len(failed_chunks),
                "chunk_summaries": chunk_summaries,
                "processing_stats": {
                    "total_chunks": len(chunks),
                    "successful_chunks": len(successful_chunks),
                    "failed_chunks": len(failed_chunks),
                    "total_characters": len(full_text),
                    "final_prompt_length": len(final_summary_prompt),
                },
            }

        except Exception as e:
            logger.error(f"Error generating repository summary: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "summary": None,
                "chunks_processed": 0,
                "successful_chunks": 0,
                "failed_chunks": 0,
                "chunk_summaries": [],
                "processing_stats": {},
            }

    async def generate_short_description(
        self,
        summary: str,
        repository_info: Optional[Dict[str, Any]] = None,
        max_length: int = 150,
    ) -> Dict[str, Any]:
        """
        Generate a short description from a repository summary using gemini-2.5-pro

        Args:
            summary: The full repository summary to condense
            repository_info: Optional repository context information
            max_length: Maximum length of the short description (default: 150 chars)

        Returns:
            Dictionary with success status, short description, and metadata
        """
        try:
            logger.info(
                f"Generating short description from summary ({len(summary)} chars)"
            )

            # Create system prompt for short description generation
            system_prompt = f"""You are an expert at creating concise, compelling descriptions from technical content.

Your task is to create a short description (maximum {max_length} characters) from a detailed repository summary.

Requirements:
1. Keep it under {max_length} characters
2. Focus on what the project DOES, not how it's built
3. Make it engaging and clear for developers
4. Use active voice and present tense
5. No technical jargon unless essential
6. Start with a strong verb or "A tool/library/framework that..."

Examples of good short descriptions:
- "A modern REST API for managing GitHub repositories with AI-powered analysis"
- "Real-time chat application built with WebSocket and Redis"
- "CLI tool that converts Markdown files to beautiful PDFs"

Create a short, engaging description that would make a developer want to learn more."""

            # Prepare the user content with repository context
            user_content = f"""REPOSITORY SUMMARY TO CONDENSE:
{summary}
"""

            # Add repository context if available
            if repository_info:
                repo_name = repository_info.get("name", "Unknown")
                repo_author = repository_info.get("author", "Unknown")
                repo_url = repository_info.get("repository_url", "")

                user_content = f"""REPOSITORY CONTEXT:
Name: {repo_name}
Author: {repo_author}
URL: {repo_url}

{user_content}

Focus on creating a description that represents what "{repo_name}" does in a compelling way."""

            # Generate short description using gemini-2.5-pro
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.5-pro",
                contents=system_prompt + "\n\n" + user_content,
                config=self.summary_config,
            )

            if not response or not response.text:
                return {
                    "success": False,
                    "error": "No response from Gemini API",
                    "short_description": None,
                    "length": 0,
                    "model_used": "gemini-2.5-pro",
                }

            short_description = response.text.strip()

            # Remove quotes if they wrap the entire description
            if (
                short_description.startswith('"') and short_description.endswith('"')
            ) or (
                short_description.startswith("'") and short_description.endswith("'")
            ):
                short_description = short_description[1:-1]

            # Check length and truncate if needed
            if len(short_description) > max_length:
                logger.warning(
                    f"Generated description ({len(short_description)} chars) exceeds max length ({max_length}), truncating"
                )
                short_description = short_description[: max_length - 3] + "..."

            logger.info(
                f"Successfully generated short description: {len(short_description)} characters"
            )

            return {
                "success": True,
                "short_description": short_description,
                "length": len(short_description),
                "original_summary_length": len(summary),
                "model_used": "gemini-2.5-pro",
                "max_length": max_length,
            }

        except Exception as e:
            logger.error(f"Error generating short description: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "short_description": None,
                "length": 0,
                "model_used": "gemini-2.5-pro",
            }

    async def extract_repositories_from_content(
        self, content: str, website_url: str
    ) -> Dict[str, Any]:
        """
        Extract repository information from website content using structured output

        Args:
            content: Scraped website content (markdown format)
            website_url: Original website URL for context
            schema_class: Pydantic schema class for structured output

        Returns:
            Dictionary containing extracted repositories and metadata
        """
        try:
            logger.info(
                f"Extracting repositories from content ({len(content)} chars) from {website_url}"
            )

            # Create the extraction prompt
            extraction_prompt = f"""You are an expert at extracting repository information from website content. 
Your task is to analyze the provided website content and extract ALL Git repository URLs along with any available metadata.

IMPORTANT INSTRUCTIONS:
1. Look for ANY Git repository URLs (GitHub, GitLab, Bitbucket, etc.)
2. Extract as much metadata as possible for each repository (name, author, description)
3. Only include VALID repository URLs that point to actual code repositories
4. If no repositories are found, return an empty list
5. Provide a confidence score between 0.0 and 1.0 for each repository

SOURCE WEBSITE: {website_url}

WEBSITE CONTENT TO ANALYZE:
{content[:100000]}{"... [content truncated]" if len(content) > 100000 else ""}"""

            # Import the ExtractedRepoInfo model for structured output
            from app.models.simple_scraping import ExtractedRepoInfo

            # Generate structured output using Gemini with Pydantic model
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model="gemini-2.0-flash",
                contents=extraction_prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": list[ExtractedRepoInfo],
                },
            )

            # Access the parsed response directly
            if not response.parsed:
                raise Exception("No response parsed from Gemini")

            extracted_data = response.parsed
            if not isinstance(extracted_data, list):
                raise Exception("Response is not a list")

            logger.info(f"Successfully extracted repository data from {website_url}")

            return {
                "success": True,
                "extracted_data": extracted_data,
                "content_length": len(content),
                "website_url": website_url,
                "model_used": "gemini-2.0-flash",
                "error": None,
            }

        except Exception as e:
            logger.error(f"Error extracting repositories from {website_url}: {str(e)}")
            return {
                "success": False,
                "extracted_data": None,
                "content_length": len(content) if content else 0,
                "website_url": website_url,
                "model_used": "gemini-2.0-flash",
                "error": str(e),
            }


# Create a singleton instance
gemini_service = GeminiAIService()

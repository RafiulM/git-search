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
        self.chunk_model = "gemini-2.0-flash-lite"
        self.summary_model = "gemini-2.5-flash"
        
        # Generation config for different use cases
        self.chunk_config = types.GenerateContentConfig(
            max_output_tokens=4000,
            temperature=0.7,
            top_p=0.9,
            top_k=40,
            thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disable thinking
        )
        
        self.summary_config = types.GenerateContentConfig(
            max_output_tokens=8000,
            temperature=0.7,
            top_p=0.9,
            top_k=40,
            thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disable thinking
        )

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
                    '\n\n',  # Double newlines (paragraph breaks)
                    '\n=',   # Section headers with equals
                    '\n-',   # Section headers with dashes
                    '\nFILE:', # File boundaries in repo2text output
                    '\nclass ', '\nfunction ', '\nexport ', '\nimport ',  # Code structure breaks
                    '\n}',   # End of code blocks
                    '\n',    # Any newline
                    '. ',    # Sentence endings
                    ' '      # Word boundaries
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
        system_prompt: str
    ) -> Dict[str, Any]:
        """Generate summary for a single chunk of repository content"""
        try:
            # Prepare the chunk with context
            chunk_with_context = (
                repository_context + 
                f"\nCHUNK {chunk_index + 1}/{total_chunks} CONTENT:\n" + 
                chunk
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
                config=self.chunk_config
            )
            
            return {
                "chunk_index": chunk_index + 1,
                "total_chunks": total_chunks,
                "summary": response.text,
                "character_count": len(chunk),
                "success": True,
                "error": None
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
                "error": str(e)
            }

    async def generate_repository_summary(
        self,
        full_text: str,
        repository_info: Dict[str, Any],
        system_prompt: str
    ) -> Dict[str, Any]:
        """
        Generate comprehensive repository summary by processing in chunks
        """
        try:
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
            chunks = self.chunk_text(full_text, 1500000)  # 1.5M chars per chunk
            logger.info(f"Processing {len(chunks)} chunks of repository data")
            
            # Process chunks in parallel
            chunk_tasks = [
                self.generate_chunk_summary(
                    chunk, 
                    index, 
                    len(chunks),
                    repository_context,
                    system_prompt
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
                logger.warning(f"Failed chunks: {[c['chunk_index'] for c in failed_chunks]}")
                
                # Only fail if ALL chunks failed
                if len(failed_chunks) == len(chunks):
                    raise Exception("All repository chunks failed to process")
            
            # Combine chunk summaries for final summary
            combined_summaries = "\n\n".join([
                f"--- Chunk {c['chunk_index']}/{c['total_chunks']} "
                f"({c['character_count']:,} chars) ---\n{c['summary']}"
                for c in chunk_summaries
            ])
            
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
                processing_status = f"\n\nAll {len(chunks)} chunks were successfully processed."
            
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
                config=self.summary_config
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
                    "final_prompt_length": len(final_summary_prompt)
                }
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
                "processing_stats": {}
            }

# Create a singleton instance
gemini_service = GeminiAIService()
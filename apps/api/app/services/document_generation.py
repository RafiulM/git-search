import asyncio
import logging
from typing import Dict, List, Optional, Any
from uuid import UUID

from app.services.database import db_service
from app.services.gemini_ai import gemini_service
from app.models import DocumentInsert, Document

logger = logging.getLogger(__name__)


class DocumentGenerationService:
    """Service for generating various types of documents from repository analysis"""

    # Default document types
    DEFAULT_DOCUMENT_TYPES = [
        "project_requirements_document",
        "app_flow_document",
        "tech_stack_document",
    ]

    async def generate_document_from_summary(
        self,
        repository_id: UUID,
        document_type: str,
        repository_summary: str,
        repository_info: Dict[str, Any],
        analysis_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[Document]:
        """
        Generate a single document of specified type for a repository using the AI summary as input

        Args:
            repository_id: ID of the repository
            document_type: Type of document to generate
            repository_summary: AI-generated repository summary
            repository_info: Repository metadata and statistics
            analysis_data: Optional analysis data from repo2text

        Returns:
            Generated Document object or None if failed
        """
        try:
            logger.info(
                f"Generating {document_type} for repository {repository_id} using summary"
            )

            # Get the prompt for this document type
            prompt_name = f"{document_type}_generation"
            system_prompt = await gemini_service.get_system_prompt(
                "documentation_generation", prompt_name
            )

            # If no specific prompt found, use a default one based on document type
            if not system_prompt:
                system_prompt = self._get_default_prompt_for_type(document_type)

            # Prepare context for the AI using the summary
            context = self._prepare_document_context_from_summary(
                document_type, repository_summary, repository_info, analysis_data
            )

            # Generate document content using Gemini
            response = await asyncio.to_thread(
                gemini_service.client.models.generate_content,
                model=gemini_service.summary_model,
                contents=f"{system_prompt}\n\n{context}",
                config=gemini_service.summary_config,
            )

            if not response or not response.candidates:
                raise Exception("Invalid response from Gemini AI")

            candidate = response.candidates[0]
            if not candidate.content or not candidate.content.parts:
                raise Exception("Invalid response content from Gemini AI")

            document_content = candidate.content.parts[0].text

            if not document_content:
                raise Exception("No document content generated from Gemini AI")

            # Create document in database
            doc_data = DocumentInsert(
                repository_id=repository_id,
                title=self._generate_document_title(document_type, repository_info),
                content=document_content,
                document_type=document_type,
                description=self._generate_document_description(document_type),
                version=1,
                is_current=True,
                generated_by="gemini-2.5-pro",
                model_used=gemini_service.summary_model,
                metadata={
                    "source": "ai_generated_from_summary",
                    "document_type": document_type,
                    "generation_stats": {
                        "content_length": len(repository_summary),
                        "prompt_type": "documentation_generation",
                        "prompt_name": prompt_name,
                    },
                },
            )

            document = await db_service.create_document(doc_data)
            logger.info(
                f"Successfully generated {document_type} for repository {repository_id}: {document.id}"
            )

            return document

        except Exception as e:
            logger.error(
                f"Error generating {document_type} for repository {repository_id}: {str(e)}"
            )
            return None

    async def generate_multiple_documents_from_summary(
        self,
        repository_id: UUID,
        document_types: List[str],
        repository_summary: str,
        repository_info: Dict[str, Any],
        analysis_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Optional[Document]]:
        """
        Generate multiple documents for a repository using the AI summary as input

        Args:
            repository_id: ID of the repository
            document_types: List of document types to generate
            repository_summary: AI-generated repository summary
            repository_info: Repository metadata and statistics
            analysis_data: Optional analysis data from repo2text

        Returns:
            Dictionary mapping document types to generated Document objects (None if failed)
        """
        logger.info(
            f"Generating {len(document_types)} documents for repository {repository_id} using summary"
        )

        # Mark previous documents of these types as not current
        for doc_type in document_types:
            try:
                await db_service.mark_previous_documents_not_current(
                    repository_id, doc_type
                )
            except Exception as e:
                logger.warning(
                    f"Failed to mark previous documents as not current for {doc_type}: {str(e)}"
                )

        # Generate documents concurrently
        tasks = [
            self.generate_document_from_summary(
                repository_id,
                doc_type,
                repository_summary,
                repository_info,
                analysis_data,
            )
            for doc_type in document_types
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Map results to document types
        document_results = {}
        for i, doc_type in enumerate(document_types):
            result = results[i]
            if isinstance(result, Exception):
                logger.error(f"Exception generating {doc_type}: {str(result)}")
                document_results[doc_type] = None
            else:
                document_results[doc_type] = result

        logger.info(f"Completed document generation for repository {repository_id}")
        return document_results

    def _prepare_document_context_from_summary(
        self,
        document_type: str,
        repository_summary: str,
        repository_info: Dict[str, Any],
        analysis_data: Optional[Dict[str, Any]],
    ) -> str:
        """Prepare context for document generation based on document type using summary as input"""

        stats = repository_info.get("statistics", {})
        repository_url = repository_info.get("repository_url", "Unknown")

        context = f"""
REPOSITORY INFORMATION:
URL: {repository_url}
Name: {repository_info.get('name', 'Unknown')}
Author: {repository_info.get('author', 'Unknown')}

REPOSITORY STATISTICS:
- Files processed: {stats.get('files_processed', 0)}
- Binary files skipped: {stats.get('binary_files_skipped', 0)}
- Large files skipped: {stats.get('large_files_skipped', 0)}
- Encoding errors: {stats.get('encoding_errors', 0)}
- Total characters: {stats.get('total_characters', 0):,}
- Total lines: {stats.get('total_lines', 0):,}
- Total files found: {stats.get('total_files_found', 0)}
- Total directories: {stats.get('total_directories', 0)}
"""

        if analysis_data:
            context += f"""
ANALYSIS DATA:
{analysis_data.get('tree_structure', 'No tree structure available')}
"""

        # Add the AI summary as the main content
        context += f"\nREPOSITORY AI SUMMARY:\n{repository_summary}"

        return context

    def _get_default_prompt_for_type(self, document_type: str) -> str:
        """Get default prompt based on document type"""

        prompts = {
            "project_requirements_document": """You are a technical documentation specialist. 
            Create a comprehensive project requirements document based on the repository content that includes:
            1. Project Overview and Objectives
            2. Functional Requirements
            3. Non-functional Requirements
            4. Technical Requirements
            5. Dependencies and Prerequisites
            6. Assumptions and Constraints
            7. Success Criteria
            
            Make the document clear, structured, and actionable for project managers and developers.""",
            "app_flow_document": """You are a software architect and technical documentation specialist. 
            Analyze the repository and create a detailed application flow document that includes:
            1. High-level Architecture Overview
            2. Component Interaction Diagram (text-based)
            3. Data Flow Description
            4. User Journey/Workflow
            5. API Endpoints and Interactions
            6. Database Schema Overview
            7. External Service Integrations
            8. Error Handling and Fallbacks
            
            Focus on how data and control flow through the application. Be specific and technical.""",
            "tech_stack_document": """You are a technical lead and documentation specialist. 
            Create a comprehensive technology stack document based on the repository that includes:
            1. Programming Languages and Versions
            2. Frameworks and Libraries (with versions)
            3. Database Technologies
            4. Infrastructure and Deployment Tools
            5. Development and Build Tools
            6. Testing Frameworks and Tools
            7. Monitoring and Observability Tools
            8. Third-party Services and APIs
            9. Security Tools and Practices
            10. DevOps and CI/CD Tools
            
            Include version information where available and explain the purpose of each technology.""",
        }

        # If we have a predefined prompt for this document type, use it
        if document_type in prompts:
            return prompts[document_type]

        # Otherwise, generate a generic prompt with proper document type formatting
        words = document_type.split("_")
        formatted_words = []
        for word in words:
            # Handle common acronyms that should be uppercase
            if word.lower() in [
                "api",
                "url",
                "id",
                "http",
                "https",
                "ui",
                "ux",
                "html",
                "css",
                "js",
                "json",
                "xml",
            ]:
                formatted_words.append(word.upper())
            else:
                formatted_words.append(word.capitalize())

        document_name = " ".join(formatted_words)

        return f"""You are a technical documentation specialist. 
        Create a comprehensive {document_name.lower()} based on the repository content.
        Make the document clear, structured, and actionable for developers and stakeholders."""

    def _generate_document_title(
        self, document_type: str, repository_info: Dict[str, Any]
    ) -> str:
        """Generate document title based on document type and repository info"""

        # Convert snake_case to Title Case
        words = document_type.split("_")
        title_case = " ".join(word.capitalize() for word in words)

        return title_case

    def _generate_document_description(self, document_type: str) -> str:
        """Generate document description based on document type"""

        descriptions = {
            "project_requirements_document": "Comprehensive project requirements document generated from codebase analysis",
            "app_flow_document": "Detailed application flow and architecture document generated from codebase analysis",
            "tech_stack_document": "Complete technology stack documentation generated from codebase analysis",
        }

        # If we have a predefined description for this document type, use it
        if document_type in descriptions:
            return descriptions[document_type]

        # Otherwise, generate a properly formatted description from the document type
        # Convert snake_case to readable format
        words = document_type.split("_")
        formatted_words = []
        for word in words:
            # Handle common acronyms that should be uppercase
            if word.lower() in [
                "api",
                "url",
                "id",
                "http",
                "https",
                "ui",
                "ux",
                "html",
                "css",
                "js",
                "json",
                "xml",
            ]:
                formatted_words.append(word.upper())
            else:
                formatted_words.append(word.capitalize())

        document_name = " ".join(formatted_words)
        return f"AI-generated {document_name.lower()} document"


# Global instance
document_generation_service = DocumentGenerationService()

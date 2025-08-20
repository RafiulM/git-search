import os
import logging
from typing import Dict, Any, Optional, List
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)


class FirecrawlService:
    """Service for scraping websites using Firecrawl"""

    def __init__(self):
        self.api_key = os.getenv("FIRECRAWL_API_KEY")

        if not self.api_key:
            logger.warning("FIRECRAWL_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = FirecrawlApp(api_key=self.api_key)

    async def scrape_website(
        self, url: str, include_links: bool = True
    ) -> Dict[str, Any]:
        """
        Scrape a single website and return the content

        Args:
            url: Website URL to scrape
            include_links: Whether to include links from the page

        Returns:
            Dictionary containing scraped content and metadata
        """
        if not self.client:
            raise Exception("Firecrawl API key not configured")

        try:
            logger.info(f"Scraping website: {url}")

            # Configure scraping options
            scrape_options = {
                "formats": ["markdown", "html"],
                "includeTags": ["a"] if include_links else [],
                "excludeTags": ["script", "style", "nav", "footer"],
                "waitFor": 2000,  # Wait 2 seconds for dynamic content
                "timeout": 30000,  # 30 second timeout
            }

            # Scrape the website
            result = self.client.scrape_url(url, scrape_options)

            # Check if we have markdown content (handle both nested and flat structures)
            markdown_content = result.get("markdown") or result.get("data", {}).get(
                "markdown"
            )
            if not markdown_content:
                logger.error(f"Firecrawl result structure: {result}")
                raise Exception(
                    f"Firecrawl scraping failed: {result.get('error', 'No markdown content found')}"
                )

            # Extract content and metadata
            # Handle both nested and flat result structures
            data = result.get("data", result)
            metadata = data.get("metadata", {})

            content_data = {
                "url": url,
                "title": metadata.get("title", ""),
                "description": metadata.get("description", ""),
                "markdown": data.get("markdown", ""),
                "html": data.get("html", ""),
                "links": data.get("links", []),
                "metadata": metadata,
                "screenshot": data.get("screenshot"),
                "status_code": data.get("statusCode"),
                "success": True,
            }

            logger.info(
                f"Successfully scraped {url}: {len(content_data['markdown'])} chars"
            )
            return content_data

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to scrape {url}: {error_msg}")
            # Log additional debug info if available
            if hasattr(e, "response"):
                logger.error(f"Response details: {e.response}")
            return {
                "url": url,
                "success": False,
                "error": error_msg,
                "title": "",
                "description": "",
                "markdown": "",
                "html": "",
                "links": [],
                "metadata": {},
                "screenshot": None,
                "status_code": None,
            }

    async def crawl_website(
        self, url: str, max_pages: int = 10, include_subdomains: bool = False
    ) -> Dict[str, Any]:
        """
        Crawl a website and return content from multiple pages

        Args:
            url: Website URL to crawl
            max_pages: Maximum number of pages to crawl
            include_subdomains: Whether to include subdomains in crawling

        Returns:
            Dictionary containing crawled content from multiple pages
        """
        if not self.client:
            raise Exception("Firecrawl API key not configured")

        try:
            logger.info(f"Crawling website: {url} (max {max_pages} pages)")

            # Configure crawling options
            crawl_options = {
                "formats": ["markdown"],
                "limit": max_pages,
                "excludeTags": ["script", "style", "nav", "footer"],
                "includeSubdomains": include_subdomains,
                "maxDepth": 3,
                "timeout": 60000,  # 60 second timeout
            }

            # Start crawling
            result = self.client.crawl_url(url, crawl_options)

            if not result.get("success", False):
                raise Exception(
                    f"Firecrawl crawling failed: {result.get('error', 'Unknown error')}"
                )

            # Extract pages data
            pages = result.get("data", [])

            crawl_data = {
                "url": url,
                "total_pages": len(pages),
                "pages": [],
                "combined_content": "",
                "all_links": [],
                "success": True,
            }

            # Process each page
            for page in pages:
                page_data = {
                    "url": page.get("metadata", {}).get("sourceURL", ""),
                    "title": page.get("metadata", {}).get("title", ""),
                    "description": page.get("metadata", {}).get("description", ""),
                    "markdown": page.get("markdown", ""),
                    "metadata": page.get("metadata", {}),
                }

                crawl_data["pages"].append(page_data)
                crawl_data[
                    "combined_content"
                ] += f"\n\n--- Page: {page_data['title']} ---\n{page_data['markdown']}"

                # Extract links from this page
                if "links" in page:
                    crawl_data["all_links"].extend(page["links"])

            # Remove duplicates from links
            crawl_data["all_links"] = list(set(crawl_data["all_links"]))

            logger.info(
                f"Successfully crawled {url}: {len(pages)} pages, {len(crawl_data['combined_content'])} chars"
            )
            return crawl_data

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to crawl {url}: {error_msg}")
            return {
                "url": url,
                "success": False,
                "error": error_msg,
                "total_pages": 0,
                "pages": [],
                "combined_content": "",
                "all_links": [],
            }

    def extract_links_from_content(
        self, content: str, filter_domains: Optional[List[str]] = None
    ) -> List[str]:
        """
        Extract URLs from scraped content

        Args:
            content: Content to extract links from
            filter_domains: List of domains to filter for (e.g., ['github.com'])

        Returns:
            List of extracted URLs
        """
        import re

        # Regex pattern to match URLs
        url_pattern = r"https?://[^\s\)\]\}]+"
        urls = re.findall(url_pattern, content)

        # Filter by domains if specified
        if filter_domains:
            filtered_urls = []
            for url in urls:
                for domain in filter_domains:
                    if domain in url:
                        filtered_urls.append(url)
                        break
            urls = filtered_urls

        # Remove duplicates and return
        return list(set(urls))

    def is_configured(self) -> bool:
        """Check if Firecrawl service is properly configured"""
        return self.client is not None


# Global firecrawl service instance
firecrawl_service = FirecrawlService()

"""
Simple GitHub README screenshot service
Takes a direct screenshot of the GitHub repository page
"""
import os
import logging
from typing import Optional
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


async def screenshot_github_readme(
    repo_owner: str, 
    repo_name: str, 
    output_path: str,
    width: int = 1200,
    wait_time: int = 3000,
    square: bool = False,
    top_section_only: bool = False
) -> bool:
    """
    Take a screenshot of a GitHub repository's README section
    
    Args:
        repo_owner: GitHub repository owner
        repo_name: GitHub repository name
        output_path: Path where the PNG should be saved
        width: Width of the browser viewport (default: 1200)
        wait_time: Time to wait for page load in ms (default: 3000)
        square: Whether to make the image square (default: False)
        top_section_only: Whether to capture only the top section (default: False)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        github_url = f"https://github.com/{repo_owner}/{repo_name}"
        logger.info(f"Taking screenshot of GitHub README: {github_url}")
        
        async with async_playwright() as p:
            # Launch browser with emoji font support
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--font-render-hinting=none",
                    "--disable-font-subpixel-positioning",
                    "--force-color-profile=srgb"
                ]
            )
            page = await browser.new_page()
            
            # Set viewport - make it large enough for square screenshots
            viewport_height = width if (square or top_section_only) else 800
            await page.set_viewport_size({"width": width, "height": viewport_height})
            logger.info(f"Set viewport: {width}x{viewport_height}")
            
            # Set user agent to avoid being blocked
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # Navigate to GitHub repository
            logger.info(f"Navigating to: {github_url}")
            try:
                await page.goto(github_url, wait_until="domcontentloaded", timeout=45000)
                # Wait a bit more for dynamic content
                await page.wait_for_timeout(2000)
            except Exception as nav_error:
                logger.warning(f"Navigation timeout, trying with load event: {nav_error}")
                # Try again with just 'load' 
                await page.goto(github_url, wait_until="load", timeout=30000)
            
            # Wait for page to fully load
            await page.wait_for_timeout(wait_time)
            
            # Wait for README content to load - try multiple selectors
            readme_selectors = [
                '[data-testid="readme"]',
                '#readme',
                '.Box.md',
                '.repository-content .Box',
                'article',
                '[data-target="readme-toc.content"]'
            ]
            
            readme_element = None
            for selector in readme_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    readme_element = await page.query_selector(selector)
                    if readme_element:
                        logger.info(f"README section found with selector: {selector}")
                        break
                except Exception:
                    continue
            
            if not readme_element:
                logger.warning("README section not found with any selector, taking full page screenshot")
            
            # Determine screenshot area
            screenshot_area = None
            
            if top_section_only or square:
                # For top section or square, start from top of page
                if square:
                    # Always make square if requested
                    screenshot_height = width
                    description = f"square ({width}x{width})"
                else:
                    # Just top section, not square
                    screenshot_height = min(800, width)
                    description = f"top section ({width}x{screenshot_height})"
                
                screenshot_area = {
                    "x": 0,
                    "y": 0,
                    "width": width,
                    "height": screenshot_height
                }
                
                logger.info(f"Taking {description} screenshot")
                await page.screenshot(path=output_path, clip=screenshot_area)
                
            else:
                # Original behavior - try to capture README section
                try:
                    if readme_element:
                        # Get bounding box of README section
                        bbox = await readme_element.bounding_box()
                        if bbox:
                            # Add some padding around README
                            padding = 20
                            screenshot_area = {
                                "x": max(0, bbox["x"] - padding),
                                "y": max(0, bbox["y"] - padding), 
                                "width": bbox["width"] + 2 * padding,
                                "height": bbox["height"] + 2 * padding
                            }
                            
                            # Make square if requested
                            if square:
                                size = max(screenshot_area["width"], screenshot_area["height"])
                                screenshot_area = {
                                    "x": screenshot_area["x"],
                                    "y": screenshot_area["y"],
                                    "width": size,
                                    "height": size
                                }
                            
                            logger.info(f"Taking README screenshot: {screenshot_area['width']}x{screenshot_area['height']}")
                            await page.screenshot(path=output_path, clip=screenshot_area)
                        else:
                            logger.warning("Could not get README bounding box, taking full page")
                            await page.screenshot(path=output_path, full_page=True)
                    else:
                        logger.warning("README element not found, taking full page")
                        await page.screenshot(path=output_path, full_page=True)
                except Exception as e:
                    logger.warning(f"Error capturing README section: {e}, taking full page")
                    await page.screenshot(path=output_path, full_page=True)
            
            await browser.close()
        
        # Verify file was created
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            logger.info(f"Screenshot saved successfully: {output_path} ({file_size} bytes)")
            return True
        else:
            logger.error("Screenshot file was not created")
            return False
            
    except Exception as e:
        logger.error(f"Error taking GitHub screenshot: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def screenshot_github_readme_sync(
    repo_owner: str,
    repo_name: str, 
    output_path: str,
    width: int = 1200,
    wait_time: int = 3000,
    square: bool = False,
    top_section_only: bool = False
) -> bool:
    """
    Synchronous wrapper for screenshot_github_readme
    """
    import asyncio
    import threading
    from concurrent.futures import ThreadPoolExecutor
    
    def run_async_code():
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                screenshot_github_readme(repo_owner, repo_name, output_path, width, wait_time, square, top_section_only)
            )
        finally:
            loop.close()
    
    # Run the async code in a separate thread
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(run_async_code)
        return future.result()


async def screenshot_github_readme_smart(
    repo_owner: str,
    repo_name: str,
    output_path: str,
    fallback_to_markdown: bool = True,
    square: bool = False,
    top_section_only: bool = False
) -> bool:
    """
    Smart README screenshot that tries GitHub page first, falls back to markdown rendering
    
    Args:
        repo_owner: GitHub repository owner
        repo_name: GitHub repository name
        output_path: Path where the PNG should be saved
        fallback_to_markdown: Whether to fallback to markdown rendering if GitHub fails
        square: Whether to make the image square
        top_section_only: Whether to capture only the top section
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # First try direct GitHub screenshot
        success = await screenshot_github_readme(repo_owner, repo_name, output_path, square=square, top_section_only=top_section_only)
        
        if success:
            logger.info("GitHub screenshot successful")
            return True
        
        if fallback_to_markdown:
            logger.info("GitHub screenshot failed, falling back to markdown rendering")
            # Import here to avoid circular dependencies
            from app.services.background_tasks import get_github_readme
            from app.services.simple_markdown_to_image import simple_markdown_to_image_sync, get_default_branch
            
            # Get README content and convert using markdown approach
            readme_content = get_github_readme(repo_owner, repo_name)
            if readme_content:
                default_branch = get_default_branch(repo_owner, repo_name)
                return simple_markdown_to_image_sync(
                    readme_content, 
                    output_path, 
                    repo_owner, 
                    repo_name, 
                    default_branch
                )
            else:
                logger.error("No README content found for fallback")
                return False
        else:
            logger.error("GitHub screenshot failed and fallback disabled")
            return False
            
    except Exception as e:
        logger.error(f"Error in smart README screenshot: {str(e)}")
        return False


def screenshot_github_readme_smart_sync(
    repo_owner: str,
    repo_name: str,
    output_path: str,
    fallback_to_markdown: bool = True,
    square: bool = False,
    top_section_only: bool = False
) -> bool:
    """
    Synchronous wrapper for screenshot_github_readme_smart
    """
    import asyncio
    import threading
    from concurrent.futures import ThreadPoolExecutor
    
    def run_async_code():
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                screenshot_github_readme_smart(repo_owner, repo_name, output_path, fallback_to_markdown, square, top_section_only)
            )
        finally:
            loop.close()
    
    # Run the async code in a separate thread
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(run_async_code)
        return future.result()
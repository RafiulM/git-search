"""
README blob screenshot service
Takes screenshots from the /blob/main/README.md page with scrolling
"""
import os
import logging
from typing import Optional
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


async def screenshot_readme_blob(
    repo_owner: str, 
    repo_name: str, 
    output_path: str,
    width: int = 850,
    scroll_pixels: int = 50,
    wait_time: int = 3000,
    default_branch: str = "main"
) -> bool:
    """
    Take a screenshot of a GitHub repository's README blob page with scrolling
    
    Args:
        repo_owner: GitHub repository owner
        repo_name: GitHub repository name
        output_path: Path where the PNG should be saved
        width: Width of the browser viewport (default: 1200)
        scroll_pixels: How much to scroll down in pixels (default: 200)
        wait_time: Time to wait for page load in ms (default: 3000)
        default_branch: Git branch to use (default: "main")
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Build URL to README blob page
        github_url = f"https://github.com/{repo_owner}/{repo_name}/blob/{default_branch}/README.md"
        logger.info(f"Taking screenshot of README blob: {github_url}")
        
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
            
            # Set viewport
            await page.set_viewport_size({"width": width, "height": 800})
            logger.info(f"Set viewport: {width}x800")
            
            # Set user agent to avoid being blocked
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # Navigate to README blob page
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
            
            # Hide GitHub header and navigation elements for cleaner screenshot
            await page.evaluate("""
                // Hide the top GitHub header
                const header = document.querySelector('header[role="banner"]');
                if (header) header.style.display = 'none';
                
                // Hide the file navigation
                const fileNav = document.querySelector('[data-testid="breadcrumb"]');
                if (fileNav) fileNav.style.display = 'none';
                
                // Hide the file actions bar
                const fileActions = document.querySelector('.file-actions');
                if (fileActions) fileActions.style.display = 'none';
                
                // Hide blame/edit buttons
                const blameButton = document.querySelector('.btn-group');
                if (blameButton) blameButton.style.display = 'none';
            """)
            
            # Try to find the README content area with better selectors
            readme_selectors = [
                'article.markdown-body',  # Most specific for README content
                '[data-testid="readme"] article',
                '.Box.md article',
                '.file-content article',
                '[data-testid="readme"]',
                '.Box.md'
            ]
            
            readme_element = None
            for selector in readme_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    readme_element = await page.query_selector(selector)
                    if readme_element:
                        logger.info(f"README content found with selector: {selector}")
                        break
                except Exception:
                    continue
            
            # Scroll down a bit to get past any headers/navigation
            if scroll_pixels > 0:
                logger.info(f"Scrolling down {scroll_pixels} pixels")
                await page.evaluate(f"window.scrollBy(0, {scroll_pixels})")
                # Wait for scroll to complete
                await page.wait_for_timeout(1000)
            
            # Take full page screenshot to avoid cropping sides
            logger.info("Taking full page screenshot to preserve full width")
            await page.screenshot(path=output_path, full_page=True)
            
            await browser.close()
        
        # Verify file was created
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            logger.info(f"README blob screenshot saved: {output_path} ({file_size} bytes)")
            return True
        else:
            logger.error("Screenshot file was not created")
            return False
            
    except Exception as e:
        logger.error(f"Error taking README blob screenshot: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def screenshot_readme_blob_with_branch_detection(
    repo_owner: str,
    repo_name: str,
    output_path: str,
    width: int = 850,
    scroll_pixels: int = 50,
    wait_time: int = 3000
) -> bool:
    """
    Screenshot README blob with automatic branch detection (main/master)
    """
    # Try main first, then master
    branches = ["main", "master"]
    
    for branch in branches:
        try:
            logger.info(f"Trying branch: {branch}")
            success = await screenshot_readme_blob(
                repo_owner, repo_name, output_path, width, scroll_pixels, wait_time, branch
            )
            if success:
                logger.info(f"Successfully captured README from '{branch}' branch")
                return True
        except Exception as e:
            logger.warning(f"Failed with branch '{branch}': {e}")
            continue
    
    logger.error(f"Failed to capture README from any branch")
    return False


def screenshot_readme_blob_sync(
    repo_owner: str,
    repo_name: str,
    output_path: str,
    width: int = 850,
    scroll_pixels: int = 50,
    wait_time: int = 3000,
    auto_detect_branch: bool = True
) -> bool:
    """
    Synchronous wrapper for README blob screenshot
    """
    import asyncio
    import threading
    from concurrent.futures import ThreadPoolExecutor
    
    def run_async_code():
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            if auto_detect_branch:
                return loop.run_until_complete(
                    screenshot_readme_blob_with_branch_detection(
                        repo_owner, repo_name, output_path, width, scroll_pixels, wait_time
                    )
                )
            else:
                return loop.run_until_complete(
                    screenshot_readme_blob(
                        repo_owner, repo_name, output_path, width, scroll_pixels, wait_time
                    )
                )
        finally:
            loop.close()
    
    # Run the async code in a separate thread
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(run_async_code)
        return future.result()
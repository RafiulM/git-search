"""
Simple and reliable markdown to image converter
Uses server-side markdown processing and better image handling
"""
import os
import tempfile
import logging
import re
import requests
from typing import Optional
from playwright.async_api import async_playwright

# Try to import markdown library, use fallback if not available
try:
    import markdown
    from markdown.extensions import codehilite, tables, fenced_code
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False
    logger = logging.getLogger(__name__)
    logger.warning("markdown library not available, using client-side fallback")

logger = logging.getLogger(__name__)


def get_default_branch(repo_owner: str, repo_name: str) -> str:
    """Get the default branch for a repository (main or master)"""
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    try:
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            default_branch = data.get("default_branch", "main")
            logger.info(f"Default branch for {repo_owner}/{repo_name}: {default_branch}")
            return default_branch
    except Exception as e:
        logger.warning(f"Could not get default branch for {repo_owner}/{repo_name}: {e}")
    
    # Default fallback
    return "main"


def fix_github_shields(markdown_content: str) -> str:
    """
    Fix GitHub shields and badges that might not be rendering properly
    """
    # Convert reference-style image links to inline links for better processing
    # Pattern: [![alt][ref]][link] where [ref]: url
    
    # First, find all reference definitions
    import re
    ref_pattern = r'^\[([^\]]+)\]:\s*(.+)$'
    references = {}
    
    for line in markdown_content.split('\n'):
        match = re.match(ref_pattern, line.strip())
        if match:
            ref_name = match.group(1)
            ref_url = match.group(2).strip()
            references[ref_name] = ref_url
    
    # Replace reference-style images with inline images
    # Pattern: [![alt][ref]]
    ref_image_pattern = r'!\[([^\]]*)\]\[([^\]]+)\]'
    
    def replace_ref_image(match):
        alt_text = match.group(1)
        ref_name = match.group(2)
        if ref_name in references:
            return f'![{alt_text}]({references[ref_name]})'
        return match.group(0)  # Return original if reference not found
    
    # Replace reference-style images
    processed_content = re.sub(ref_image_pattern, replace_ref_image, markdown_content)
    
    # Also handle linked images: [![alt][ref]][link]
    linked_image_pattern = r'(\!\[[^\]]*\]\[[^\]]+\])\[([^\]]+)\]'
    
    def replace_linked_image(match):
        image_part = match.group(1)
        link_ref = match.group(2)
        # First process the image part
        processed_image = re.sub(ref_image_pattern, replace_ref_image, image_part)
        if link_ref in references:
            # Wrap in a link if we have the reference
            return f'[{processed_image}]({references[link_ref]})'
        return processed_image  # Just return the image if no link reference
    
    processed_content = re.sub(linked_image_pattern, replace_linked_image, processed_content)
    
    logger.info(f"GitHub shields processing: found {len(references)} references")
    for ref_name, ref_url in references.items():
        if any(domain in ref_url for domain in ['shields.io', 'img.shields.io', 'badge', 'travis-ci', 'codecov']):
            logger.info(f"  Badge reference: {ref_name} -> {ref_url}")
    
    return processed_content


def process_markdown_images(markdown_content: str, repo_owner: str = None, repo_name: str = None, default_branch: str = "main") -> str:
    """
    Pre-process markdown content to convert relative image URLs to absolute URLs
    """
    if not repo_owner or not repo_name:
        return markdown_content
    
    logger.info(f"Processing images for {repo_owner}/{repo_name} (branch: {default_branch})")
    
    # Find all markdown images
    image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    images = re.findall(image_pattern, markdown_content)
    
    if images:
        logger.info(f"Found {len(images)} images to process")
        for i, (alt, src) in enumerate(images):
            logger.info(f"  Image {i+1}: {alt} -> {src}")
    
    def replace_relative_url(match):
        alt_text = match.group(1)
        url = match.group(2)
        
        # Skip if already absolute URL or data URL
        if url.startswith(('http://', 'https://', 'data:', '/')):
            return match.group(0)
        
        # Remove leading ./ if present
        if url.startswith('./'):
            url = url[2:]
        
        # Convert to absolute GitHub raw URL
        absolute_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{default_branch}/{url}"
        logger.info(f"Converting relative URL: {url} -> {absolute_url}")
        
        return f"![{alt_text}]({absolute_url})"
    
    # Replace relative URLs
    processed_content = re.sub(image_pattern, replace_relative_url, markdown_content)
    
    # Also handle HTML img tags
    html_img_pattern = r'<img([^>]*?)src=["\']([^"\']+)["\']([^>]*?)>'
    
    def replace_html_img(match):
        before_src = match.group(1)
        url = match.group(2)
        after_src = match.group(3)
        
        # Skip if already absolute URL or data URL
        if url.startswith(('http://', 'https://', 'data:', '/')):
            return match.group(0)
        
        # Remove leading ./ if present
        if url.startswith('./'):
            url = url[2:]
        
        # Convert to absolute GitHub raw URL
        absolute_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{default_branch}/{url}"
        logger.info(f"Converting HTML img URL: {url} -> {absolute_url}")
        
        return f'<img{before_src}src="{absolute_url}"{after_src}>'
    
    processed_content = re.sub(html_img_pattern, replace_html_img, processed_content)
    
    return processed_content


def markdown_to_html(markdown_content: str) -> str:
    """
    Convert markdown to HTML using the markdown library or client-side fallback
    """
    if HAS_MARKDOWN:
        # Use server-side markdown processing (preferred)
        md = markdown.Markdown(
            extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.tables',
                'markdown.extensions.toc',
                'markdown.extensions.nl2br',
                'markdown.extensions.sane_lists',
                'markdown.extensions.attr_list',  # For attribute lists
                'markdown.extensions.def_list'    # For definition lists
            ],
            extension_configs={
                'markdown.extensions.fenced_code': {
                    'lang_prefix': 'language-'
                }
            }
        )
        
        html_content = md.convert(markdown_content)
        return html_content
    else:
        # Return the raw markdown content - it will be processed client-side
        return markdown_content


async def simple_markdown_to_image(
    markdown_content: str, 
    output_path: str, 
    repo_owner: str = None, 
    repo_name: str = None,
    default_branch: str = "main",
    width: int = 1200,
    max_height: int = 8000,
    dark_mode: bool = False
) -> bool:
    """
    Convert markdown content to PNG image using a simpler, more reliable approach
    
    Args:
        markdown_content: The markdown content to convert
        output_path: Path where the PNG should be saved
        repo_owner: GitHub repository owner (for image URL conversion)
        repo_name: GitHub repository name (for image URL conversion)
        default_branch: Git branch to use for image URLs (default: "main")
        width: Width of the rendered image (default: 1200)
        max_height: Maximum height before scrolling (default: 8000)
        dark_mode: Whether to use dark mode styling (default: False)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Converting markdown to image: {repo_owner}/{repo_name if repo_name else 'unknown'}")
        
        # Step 1: Fix GitHub shields and badges
        processed_markdown = fix_github_shields(markdown_content)
        
        # Step 2: Process relative image URLs
        processed_markdown = process_markdown_images(processed_markdown, repo_owner, repo_name, default_branch)
        
        # Step 3: Prepare content and scripts based on available libraries
        if HAS_MARKDOWN:
            # Server-side processing: convert markdown to HTML
            html_body = markdown_to_html(processed_markdown)
            client_side_script = '''
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                console.log('Content already processed server-side');
                window.contentParsed = true;
            });
        </script>'''
        else:
            # Client-side processing: keep as raw markdown for client-side conversion
            html_body = processed_markdown  # Keep as raw markdown
            client_side_script = '''
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                console.log('Starting client-side markdown processing');
                const contentDiv = document.getElementById('content');
                const markdownContent = contentDiv.textContent;
                console.log('Markdown content length:', markdownContent.length);
                const htmlContent = marked.parse(markdownContent);
                console.log('Converted HTML length:', htmlContent.length);
                contentDiv.innerHTML = htmlContent;
                
                // Signal that content is ready
                window.contentParsed = true;
                console.log('Client-side processing complete');
            });
        </script>'''
        
        # Step 4: Create complete HTML document
        
        # Define CSS variables for light and dark modes
        if dark_mode:
            css_variables = """
            :root {
                --bg-color: #0d1117;
                --text-color: #e6edf3;
                --border-color: #30363d;
                --code-bg: #161b22;
                --link-color: #4493f8;
                --link-hover: #58a6ff;
                --heading-border: #21262d;
                --blockquote-color: #8b949e;
                --table-header-bg: #161b22;
                --table-row-even: #161b22;
                --table-row-odd: #0d1117;
            }
            """
        else:
            css_variables = """
            :root {
                --bg-color: #ffffff;
                --text-color: #24292f;
                --border-color: #d0d7de;
                --code-bg: #f6f8fa;
                --link-color: #0969da;
                --link-hover: #0969da;
                --heading-border: #d0d7de;
                --blockquote-color: #656d76;
                --table-header-bg: #f6f8fa;
                --table-row-even: #f6f8fa;
                --table-row-odd: #ffffff;
            }
            """
        
        html_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>README</title>
    <style>
        {css_variables}
        
        body {{
            font-family: 'Noto Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji';
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
            max-width: {width - 80}px;
            margin: 0 auto;
            padding: 40px;
            box-sizing: border-box;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }}
        
        h1 {{ font-size: 2em; border-bottom: 1px solid var(--heading-border); padding-bottom: 0.3em; }}
        h2 {{ font-size: 1.5em; border-bottom: 1px solid var(--heading-border); padding-bottom: 0.3em; }}
        h3 {{ font-size: 1.25em; }}
        h4 {{ font-size: 1em; }}
        h5 {{ font-size: 0.875em; }}
        h6 {{ font-size: 0.85em; color: var(--blockquote-color); }}
        
        p {{ margin-bottom: 16px; }}
        
        img {{
            max-width: 100%;
            height: auto;
            border-style: none;
            background-color: var(--bg-color);
        }}
        
        code {{
            padding: 0.2em 0.4em;
            margin: 0;
            font-size: 85%;
            background-color: var(--code-bg);
            border-radius: 6px;
            font-family: 'Noto Sans Mono', ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace;
        }}
        
        pre {{
            padding: 16px;
            overflow: auto;
            font-size: 85%;
            line-height: 1.45;
            background-color: var(--code-bg);
            border-radius: 6px;
            margin-bottom: 16px;
        }}
        
        pre code {{
            background: transparent;
            border: 0;
            padding: 0;
            font-size: 100%;
            font-family: 'Noto Sans Mono', ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace;
        }}
        
        blockquote {{
            padding: 0 1em;
            color: var(--blockquote-color);
            border-left: 0.25em solid var(--border-color);
            margin: 0 0 16px 0;
        }}
        
        table {{
            border-spacing: 0;
            border-collapse: collapse;
            display: block;
            width: max-content;
            max-width: 100%;
            overflow: auto;
            margin-bottom: 16px;
        }}
        
        table th, table td {{
            padding: 6px 13px;
            border: 1px solid var(--border-color);
        }}
        
        table tr {{
            background-color: var(--table-row-odd);
            border-top: 1px solid var(--border-color);
        }}
        
        table tr:nth-child(2n) {{
            background-color: var(--table-row-even);
        }}
        
        table th {{
            font-weight: 600;
            background-color: var(--table-header-bg);
        }}
        
        ul, ol {{
            margin-bottom: 16px;
            padding-left: 2em;
        }}
        
        li {{
            margin-bottom: 0.25em;
        }}
        
        a {{
            color: var(--link-color);
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        hr {{
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            background-color: var(--border-color);
            border: 0;
        }}
    </style>
    {client_side_script}
</head>
<body>
    <div id="content">{html_body}</div>
</body>
</html>"""
        
        # Step 5: Use Playwright to render and capture
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--font-render-hinting=none",
                    "--disable-font-subpixel-positioning",
                    "--force-color-profile=srgb"
                ]
            )
            page = await browser.new_page()
            
            # Set up console logging to see what's happening in the browser
            def log_console_message(msg):
                logger.info(f"Browser console [{msg.type}]: {msg.text}")
            
            page.on("console", log_console_message)
            
            # Set viewport
            await page.set_viewport_size({"width": width, "height": 800})
            
            # Load the HTML content
            logger.info(f"Loading HTML content (length: {len(html_document)})")
            await page.set_content(html_document, wait_until="domcontentloaded")
            
            # Check if content is visible
            content_text = await page.evaluate("document.body.innerText")
            logger.info(f"Page content preview: {content_text[:200]}...")
            
            # Wait for content to be processed (either server-side or client-side)
            try:
                await page.wait_for_function("window.contentParsed === true", timeout=10000)
                logger.info("Content processed successfully")
            except Exception as e:
                logger.warning(f"Timeout waiting for content processing: {e}")
            
            # Wait a bit for any images to start loading
            await page.wait_for_timeout(2000)
            
            # Wait for all images to load or fail (with timeout)
            try:
                await page.wait_for_function("""
                    () => {
                        const images = Array.from(document.querySelectorAll('img'));
                        return images.length === 0 || images.every(img => img.complete);
                    }
                """, timeout=15000)
                logger.info("All images loaded successfully")
            except Exception as e:
                logger.warning(f"Timeout waiting for images to load: {e}")
                # Continue anyway
            
            # Get the full page height
            page_height = await page.evaluate("document.body.scrollHeight")
            actual_height = min(page_height + 40, max_height)  # Add some padding, but cap at max_height
            
            logger.info(f"Page dimensions: {width}x{actual_height}")
            
            # Set final viewport and take screenshot
            await page.set_viewport_size({"width": width, "height": actual_height})
            await page.screenshot(path=output_path, full_page=True)
            
            await browser.close()
        
        # Verify the file was created
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            logger.info(f"Successfully created image: {output_path} ({file_size} bytes)")
            return True
        else:
            logger.error("Image file was not created")
            return False
            
    except Exception as e:
        logger.error(f"Error converting markdown to image: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# Synchronous wrapper
def simple_markdown_to_image_sync(
    markdown_content: str, 
    output_path: str, 
    repo_owner: str = None, 
    repo_name: str = None,
    default_branch: str = "main",
    dark_mode: bool = False
) -> bool:
    """
    Synchronous wrapper for simple_markdown_to_image
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
                simple_markdown_to_image(markdown_content, output_path, repo_owner, repo_name, default_branch, dark_mode=dark_mode)
            )
        finally:
            loop.close()
    
    # Run the async code in a separate thread
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(run_async_code)
        return future.result()
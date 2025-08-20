#!/usr/bin/env python3
"""
Debug script to see what's happening with markdown rendering
"""
import os
import tempfile
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Simple test markdown
simple_markdown = """# Hello World

This is a **simple** test with some content:

- Item 1
- Item 2
- Item 3

## Code Example

```python
print("Hello, World!")
```

That's it!
"""

async def debug_rendering():
    """Debug the rendering process step by step"""
    try:
        from app.services.simple_markdown_to_image import (
            process_markdown_images, 
            markdown_to_html, 
            HAS_MARKDOWN
        )
        
        logger.info(f"Markdown library available: {HAS_MARKDOWN}")
        
        # Step 1: Test image processing
        logger.info("=== Step 1: Testing image processing ===")
        processed_content = process_markdown_images(simple_markdown, "test", "repo")
        logger.info(f"Processed content:\n{processed_content}")
        
        # Step 2: Test HTML conversion
        logger.info("=== Step 2: Testing HTML conversion ===")
        html_content = markdown_to_html(processed_content)
        logger.info(f"HTML content:\n{html_content}")
        
        # Step 3: Test full HTML document generation
        logger.info("=== Step 3: Testing full document generation ===")
        
        # Simulate the client-side script logic
        if not HAS_MARKDOWN:
            client_side_script = '''
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                console.log('DOM loaded');
                const contentDiv = document.getElementById('content');
                const markdownContent = contentDiv.textContent;
                console.log('Original markdown:', markdownContent);
                contentDiv.innerHTML = marked.parse(markdownContent);
                console.log('Converted to HTML');
                window.contentParsed = true;
            });
        </script>'''
        else:
            client_side_script = '''
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                console.log('DOM loaded - content already processed server-side');
                window.contentParsed = true;
            });
        </script>'''
        
        html_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>README</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
            background-color: #f0f0f0;
            color: #333;
        }}
        h1 {{ color: #0066cc; }}
        code {{ background-color: #f4f4f4; padding: 2px 4px; }}
        pre {{ background-color: #f4f4f4; padding: 10px; }}
    </style>
    {client_side_script}
</head>
<body>
    <div id="content">{html_content}</div>
</body>
</html>"""
        
        # Save the HTML to a file for inspection
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_document)
            html_file = f.name
        
        logger.info(f"HTML document saved to: {html_file}")
        logger.info("=== HTML Document Preview ===")
        print(html_document[:1000] + "..." if len(html_document) > 1000 else html_document)
        
        # Step 4: Test actual image generation
        logger.info("=== Step 4: Testing image generation ===")
        from app.services.simple_markdown_to_image import simple_markdown_to_image_sync
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            png_file = f.name
        
        success = simple_markdown_to_image_sync(
            simple_markdown,
            png_file,
            "test",
            "repo"
        )
        
        if success:
            file_size = os.path.getsize(png_file)
            logger.info(f"✅ PNG generated successfully: {png_file} ({file_size} bytes)")
        else:
            logger.error("❌ PNG generation failed")
            
        return success
        
    except Exception as e:
        logger.error(f"Error during debugging: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    logger.info("Starting markdown rendering debug...")
    success = asyncio.run(debug_rendering())
    logger.info(f"Debug completed. Success: {success}")
"""
Simple image cropping utility to make images square
"""

import os
import logging
from typing import Optional
from PIL import Image

logger = logging.getLogger(__name__)


def crop_to_square(
    input_path: str, output_path: str | None = None, size: int = 800
) -> bool:
    """
    Crop an image to a square format

    Args:
        input_path: Path to the input image
        output_path: Path for the output image (if None, overwrites input)
        size: Target square size (default: 800x800)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if output_path is None:
            output_path = input_path

        logger.info(f"Cropping image to {size}x{size} square: {input_path}")

        with Image.open(input_path) as img:
            original_width, original_height = img.size
            logger.info(f"Original image size: {original_width}x{original_height}")

            # Determine crop area to make it square
            if original_width > original_height:
                # Wide image - crop from sides
                crop_size = original_height
                left = (original_width - crop_size) // 2
                top = 0
                right = left + crop_size
                bottom = crop_size
            else:
                # Tall image - crop from top/bottom (prefer top content)
                crop_size = original_width
                left = 0
                top = 0  # Start from top to keep header content
                right = crop_size
                bottom = crop_size

            # Crop to square
            cropped = img.crop((left, top, right, bottom))
            logger.info(f"Cropped to: {cropped.size[0]}x{cropped.size[1]}")

            # Resize to target size if needed
            if cropped.size[0] != size:
                resized = cropped.resize((size, size), Image.Resampling.LANCZOS)
                logger.info(f"Resized to: {size}x{size}")
                resized.save(output_path, "PNG", optimize=True)
            else:
                cropped.save(output_path, "PNG", optimize=True)

            # Verify output
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"Square image saved: {output_path} ({file_size} bytes)")
                return True
            else:
                logger.error("Output file was not created")
                return False

    except Exception as e:
        logger.error(f"Error cropping image: {str(e)}")
        return False


def crop_to_square_from_top(
    input_path: str, output_path: str | None = None, size: int = 800
) -> bool:
    """
    Crop an image to square format, always taking from the top
    With narrower browser width, we can simply take the top square portion

    Args:
        input_path: Path to the input image
        output_path: Path for the output image (if None, overwrites input)
        size: Target square size (default: 800x800)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if output_path is None:
            output_path = input_path

        logger.info(f"Cropping image from top to {size}x{size} square: {input_path}")

        with Image.open(input_path) as img:
            original_width, original_height = img.size
            logger.info(f"Original image size: {original_width}x{original_height}")

            # With narrower browser width (~850px), we can take a square from the top
            # Use the original width as our square dimension (should be close to 850x850)
            crop_size = min(original_width, original_height)

            # Take square from top-left
            left = 0
            top = 0
            right = crop_size
            bottom = crop_size

            # Crop to square
            cropped = img.crop((left, top, right, bottom))
            logger.info(
                f"Cropped to: {cropped.size[0]}x{cropped.size[1]} (square from top)"
            )

            # Resize to target size if needed
            if cropped.size[0] != size:
                resized = cropped.resize((size, size), Image.Resampling.LANCZOS)
                resized.save(output_path, "PNG", optimize=True)
                logger.info(f"Resized to target: {size}x{size}")
            else:
                cropped.save(output_path, "PNG", optimize=True)

            # Verify output
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"Square image saved: {output_path} ({file_size} bytes)")
                return True
            else:
                logger.error("Output file was not created")
                return False

    except Exception as e:
        logger.error(f"Error cropping image from top: {str(e)}")
        return False


def crop_top_and_crop_to_size(
    input_path: str, output_path: str | None = None, top_crop: int = 200, size: tuple = (800, 800)
) -> bool:
    """
    Crop an image by removing pixels from the top and then crop to specific dimensions from top-left

    Args:
        input_path: Path to the input image
        output_path: Path for the output image (if None, overwrites input)
        top_crop: Number of pixels to crop from the top (default: 200)
        size: Target dimensions (width, height) (default: (800, 800))

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if output_path is None:
            output_path = input_path

        logger.info(f"Cropping image by {top_crop}px from top and then to {size[0]}x{size[1]} from top-left: {input_path}")

        with Image.open(input_path) as img:
            original_width, original_height = img.size
            logger.info(f"Original image size: {original_width}x{original_height}")

            # Check if we have enough height after cropping
            if original_height <= top_crop:
                logger.error("Image height is less than or equal to top crop value")
                return False

            # Crop from top
            left = 0
            top = top_crop
            right = original_width
            bottom = original_height

            cropped_from_top = img.crop((left, top, right, bottom))
            logger.info(f"Cropped from top by {top_crop}px: {cropped_from_top.size[0]}x{cropped_from_top.size[1]}")

            # Now crop to target dimensions from top-left
            target_width, target_height = size
            
            # Take the target area from top-left (0,0) of the cropped image
            left = 0
            top = 0
            right = min(target_width, cropped_from_top.size[0])
            bottom = min(target_height, cropped_from_top.size[1])

            # Final crop to target dimensions
            final_cropped = cropped_from_top.crop((left, top, right, bottom))
            logger.info(f"Final cropped to: {final_cropped.size[0]}x{final_cropped.size[1]}")

            # Save the result
            final_cropped.save(output_path, "PNG", optimize=True)
            logger.info(f"Final image saved: {output_path}")

            # Verify output
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"Processed image saved: {output_path} ({file_size} bytes)")
                return True
            else:
                logger.error("Output file was not created")
                return False

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return False

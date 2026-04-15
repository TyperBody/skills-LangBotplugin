from __future__ import annotations

import logging
from typing import Optional

from ..vision import ANALYZE_IMAGE_PROMPT, InvokeVision, encode_image_base64, sanitize_vision_text

logger = logging.getLogger(__name__)


async def parse_image(
    file_bytes: bytes,
    filename: str,
    invoke_vision: Optional[InvokeVision] = None,
) -> tuple[str, dict]:
    """Parse a direct image upload via the configured vision model."""
    logger.info(f'Parsing image file: {filename}')

    extra_metadata = {
        'has_images': True,
        'images_count': 1,
        'vision_used': False,
    }

    if invoke_vision is None:
        return f'[图片文件: {filename}]', extra_metadata

    image_b64 = encode_image_base64(file_bytes)
    vision_text = sanitize_vision_text(await invoke_vision(image_b64, ANALYZE_IMAGE_PROMPT))
    extra_metadata['vision_used'] = bool(vision_text)
    extra_metadata['vision_tasks_count'] = 1
    extra_metadata['vision_images_described_count'] = 1 if vision_text else 0

    if not vision_text:
        return f'[图片文件: {filename}]', extra_metadata

    return vision_text, extra_metadata

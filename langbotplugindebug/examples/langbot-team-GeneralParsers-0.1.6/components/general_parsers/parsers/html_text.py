from __future__ import annotations

import re
import logging
from typing import Optional

import markdown
from bs4 import BeautifulSoup

from ..utils import decode_text, run_sync
from ..vision import ANALYZE_IMAGE_PROMPT, InvokeVision, sanitize_vision_text

logger = logging.getLogger(__name__)


async def parse_txt(file_bytes: bytes, filename: str) -> str:
    logger.info(f'Parsing TXT file: {filename}')
    return decode_text(file_bytes)


async def parse_md(
    file_bytes: bytes,
    filename: str,
    invoke_vision: Optional[InvokeVision] = None,
) -> tuple[str, dict]:
    logger.info(f'Parsing Markdown file: {filename}')

    def _sync():
        md_content = file_bytes.decode('utf-8', errors='ignore')
        html_content = markdown.markdown(
            md_content, extensions=['extra', 'codehilite', 'tables', 'toc', 'fenced_code']
        )
        soup = BeautifulSoup(html_content, 'html.parser')
        vision_tasks, image_count = _prepare_inline_images(soup, enable_vision=invoke_vision is not None)
        text_parts = []
        for element in soup.children:
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(element.name[1])
                text_parts.append('#' * level + ' ' + element.get_text().strip())
            elif element.name == 'p':
                text = element.get_text().strip()
                if text:
                    text_parts.append(text)
            elif element.name in ['ul', 'ol']:
                for li in element.find_all('li'):
                    text_parts.append(f'* {li.get_text().strip()}')
            elif element.name == 'pre':
                code_block = element.get_text().strip()
                if code_block:
                    text_parts.append(f'```\n{code_block}\n```')
            elif element.name == 'table':
                table_str = _extract_table(element)
                if table_str:
                    text_parts.append(table_str)
            elif element.name:
                text = element.get_text(separator=' ', strip=True)
                if text:
                    text_parts.append(text)
        full_text = re.sub(r'\n\s*\n', '\n\n', '\n'.join(text_parts)).strip()
        metadata = {
            'has_images': image_count > 0,
        }
        if image_count:
            metadata['images_count'] = image_count
        return full_text, metadata, vision_tasks

    full_text, extra_metadata, vision_tasks = await run_sync(_sync)
    full_text, vision_stats = await _apply_inline_image_vision(full_text, vision_tasks, invoke_vision)
    extra_metadata.update(vision_stats)
    return full_text, extra_metadata


async def parse_html(
    file_bytes: bytes,
    filename: str,
    invoke_vision: Optional[InvokeVision] = None,
) -> tuple[str, dict]:
    logger.info(f'Parsing HTML file: {filename}')

    def _sync():
        html_content = file_bytes.decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html_content, 'html.parser')
        for s in soup(['script', 'style']):
            s.decompose()
        vision_tasks, image_count = _prepare_inline_images(soup, enable_vision=invoke_vision is not None)
        text_parts = []
        container = soup.body if soup.body else soup
        for element in container.children:
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(element.name[1])
                text_parts.append('#' * level + ' ' + element.get_text().strip())
            elif element.name == 'p':
                text = element.get_text().strip()
                if text:
                    text_parts.append(text)
            elif element.name in ['ul', 'ol']:
                for li in element.find_all('li'):
                    text = li.get_text().strip()
                    if text:
                        text_parts.append(f'* {text}')
            elif element.name == 'table':
                table_str = _extract_table(element)
                if table_str:
                    text_parts.append(table_str)
            elif element.name:
                text = element.get_text(separator=' ', strip=True)
                if text:
                    text_parts.append(text)
        full_text = re.sub(r'\n\s*\n', '\n\n', '\n'.join(text_parts)).strip()
        metadata = {
            'has_images': image_count > 0,
        }
        if image_count:
            metadata['images_count'] = image_count
        return full_text, metadata, vision_tasks

    full_text, extra_metadata, vision_tasks = await run_sync(_sync)
    full_text, vision_stats = await _apply_inline_image_vision(full_text, vision_tasks, invoke_vision)
    extra_metadata.update(vision_stats)
    return full_text, extra_metadata


def _prepare_inline_images(soup: BeautifulSoup, enable_vision: bool) -> tuple[list[dict], int]:
    vision_tasks = []
    images = soup.find_all('img')
    for idx, img in enumerate(images, start=1):
        src = (img.get('src') or '').strip()
        alt = (img.get('alt') or '').strip()
        placeholder = f'[图片: HTML图片{idx}]'
        replacement = placeholder if not alt else f'{placeholder} {alt}'
        if enable_vision and src.startswith('data:image/') and ',' in src:
            image_b64 = src.split(',', 1)[1].strip()
            if image_b64:
                vision_tasks.append({
                    'placeholder': placeholder,
                    'image_b64': image_b64,
                })
        img.replace_with(replacement)
    return vision_tasks, len(images)


async def _apply_inline_image_vision(
    full_text: str,
    vision_tasks: list[dict],
    invoke_vision: Optional[InvokeVision],
) -> tuple[str, dict]:
    if invoke_vision is None:
        return full_text, {}

    described_count = 0
    for task in vision_tasks:
        vision_text = sanitize_vision_text(
            await invoke_vision(task['image_b64'], ANALYZE_IMAGE_PROMPT)
        )
        if not vision_text:
            continue
        full_text = full_text.replace(task['placeholder'], f'[图片描述: {vision_text}]', 1)
        described_count += 1

    return full_text, {
        'vision_used': described_count > 0,
        'vision_tasks_count': len(vision_tasks),
        'vision_images_described_count': described_count,
    }


def _extract_table(table_element) -> str:
    """Convert a BeautifulSoup table element into a Markdown table string."""
    headers = [th.get_text().strip() for th in table_element.find_all('th')]
    rows = []
    for tr in table_element.find_all('tr'):
        cells = [td.get_text().strip() for td in tr.find_all('td')]
        if cells:
            rows.append(cells)

    if not headers and not rows:
        return ''

    lines = []
    if headers:
        lines.append(' | '.join(headers))
        lines.append(' | '.join(['---'] * len(headers)))

    for row_cells in rows:
        padded = row_cells + [''] * (len(headers) - len(row_cells)) if headers else row_cells
        lines.append(' | '.join(padded))

    return '\n'.join(lines)

from __future__ import annotations

import asyncio
import logging
import statistics
from collections import Counter
from typing import Optional

import fitz

from ..utils import run_sync
from ..vision import (
    ANALYZE_IMAGE_PROMPT,
    OCR_PAGE_PROMPT,
    InvokeVision,
    encode_image_base64,
    sanitize_vision_text,
)

logger = logging.getLogger(__name__)

# B4: Font-size heading thresholds (ratio relative to median font size)
_HEADING_RATIO_H1 = 2.0
_HEADING_RATIO_H2 = 1.6
_HEADING_RATIO_H3 = 1.3
_HEADING_MAX_LINE_LEN = 100  # lines longer than this are unlikely headings


async def parse_pdf(
    file_bytes: bytes,
    filename: str,
    invoke_vision: Optional[InvokeVision] = None,
) -> tuple[str, dict]:
    """Parse PDF using PyMuPDF with table extraction, image extraction, and position-aware text.

    Enhancements over the basic version:
    - B1: Improved scanned page detection (text amount + image area ratio + text density)
    - B2: Header/footer detection and filtering
    - B3: Vision call statistics in metadata
    - B4: Font-size based heading heuristics (injects Markdown ``#`` markers)

    Args:
        file_bytes: Raw PDF bytes.
        filename: Original filename.
        invoke_vision: Optional async callable ``(image_base64, prompt) -> str``.
            When provided, scanned pages are OCR'd and embedded images are described
            via a vision-capable LLM.

    Returns:
        A tuple of (text, extra_metadata) where extra_metadata contains extracted images.
    """
    logger.info(f'Parsing PDF file: {filename}')

    def _sync():
        doc = fitz.open(stream=file_bytes, filetype='pdf')
        page_count = len(doc)
        page_texts = []
        images = []
        scanned_pages = []
        total_word_count = 0
        has_tables = False

        # Vision tasks collected during sync phase
        vision_tasks: list[dict] = []

        # B4: Collect all font sizes across the document for median computation
        all_font_sizes: list[float] = []

        # B2: Collect candidate header/footer texts per page
        # Structure: { text: count }
        top_texts: Counter = Counter()
        bottom_texts: Counter = Counter()
        page_top_bottom: list[tuple[list[str], list[str]]] = []

        # --- First pass: collect font sizes and header/footer candidates ---
        for page in doc:
            page_rect = page.rect
            page_height = page_rect.height
            top_threshold = page_rect.y0 + page_height * 0.05
            bottom_threshold = page_rect.y1 - page_height * 0.05

            text_dict = page.get_text('dict', flags=fitz.TEXT_PRESERVE_WHITESPACE)
            page_top: list[str] = []
            page_bottom: list[str] = []

            for block in text_dict.get('blocks', []):
                if block['type'] != 0:
                    continue
                for line in block.get('lines', []):
                    for span in line.get('spans', []):
                        size = span.get('size', 0)
                        if size > 0:
                            all_font_sizes.append(size)

                    # B2: Check if line is in top or bottom margin
                    line_bbox = line.get('bbox', (0, 0, 0, 0))
                    line_y_center = (line_bbox[1] + line_bbox[3]) / 2
                    line_text = ''.join(
                        span['text'] for span in line.get('spans', [])
                    ).strip()

                    if line_text and len(line_text) < 80:
                        if line_y_center < top_threshold:
                            page_top.append(line_text)
                            top_texts[line_text] += 1
                        elif line_y_center > bottom_threshold:
                            page_bottom.append(line_text)
                            bottom_texts[line_text] += 1

            page_top_bottom.append((page_top, page_bottom))

        # B4: Compute baseline (median) font size
        baseline_font_size = statistics.median(all_font_sizes) if all_font_sizes else 12.0

        # B2: Determine header/footer patterns (appear on > 50% of pages)
        min_occurrences = max(2, page_count * 0.5)
        header_patterns: set[str] = set()
        footer_patterns: set[str] = set()
        for text, count in top_texts.items():
            if count >= min_occurrences:
                header_patterns.add(text)
        for text, count in bottom_texts.items():
            if count >= min_occurrences:
                footer_patterns.add(text)

        headers_footers_removed = bool(header_patterns or footer_patterns)
        if headers_footers_removed:
            logger.info(
                f'Detected {len(header_patterns)} header and '
                f'{len(footer_patterns)} footer patterns to filter'
            )

        # --- Second pass: extract content per page ---
        for page_idx, page in enumerate(doc):
            page_num = page_idx + 1
            page_rect = page.rect
            page_height = page_rect.height
            page_width = page_rect.width
            page_area = page_height * page_width

            # B2: Get this page's header/footer texts to filter
            page_header_texts, page_footer_texts = page_top_bottom[page_idx]
            filter_texts = set()
            for t in page_header_texts:
                if t in header_patterns:
                    filter_texts.add(t)
            for t in page_footer_texts:
                if t in footer_patterns:
                    filter_texts.add(t)

            # --- Collect table regions to avoid duplicating table text ---
            tables = page.find_tables()
            if tables:
                has_tables = True
            table_rects = []
            table_entries = []  # (y0, x0, markdown_str)
            for table in tables:
                bbox = fitz.Rect(table.bbox)
                table_rects.append(bbox)
                md = _pymupdf_table_to_markdown(table)
                if md:
                    table_entries.append((bbox.y0, bbox.x0, md))

            # --- Extract text blocks with position info ---
            text_dict = page.get_text('dict', flags=fitz.TEXT_PRESERVE_WHITESPACE)
            text_entries = []  # (y0, x0, text_str)
            for block in text_dict.get('blocks', []):
                if block['type'] != 0:  # skip image blocks
                    continue
                block_rect = fitz.Rect(block['bbox'])

                # Skip text blocks that overlap significantly with a table region
                in_table = False
                for tr in table_rects:
                    overlap = block_rect & tr  # intersection
                    if not overlap.is_empty and overlap.height > block_rect.height * 0.5:
                        in_table = True
                        break
                if in_table:
                    continue

                lines_text = []
                for line in block.get('lines', []):
                    spans_text = ''.join(span['text'] for span in line.get('spans', []))
                    stripped = spans_text.strip()
                    if not stripped:
                        continue

                    # B2: Skip header/footer text
                    if stripped in filter_texts:
                        continue

                    # B4: Font-size heading heuristics
                    if len(stripped) < _HEADING_MAX_LINE_LEN:
                        line_sizes = [
                            span['size'] for span in line.get('spans', [])
                            if span.get('size', 0) > 0
                        ]
                        if line_sizes:
                            avg_size = sum(line_sizes) / len(line_sizes)
                            ratio = avg_size / baseline_font_size if baseline_font_size > 0 else 1.0
                            if ratio >= _HEADING_RATIO_H1:
                                stripped = f'# {stripped}'
                            elif ratio >= _HEADING_RATIO_H2:
                                stripped = f'## {stripped}'
                            elif ratio >= _HEADING_RATIO_H3:
                                stripped = f'### {stripped}'

                    lines_text.append(stripped)
                if lines_text:
                    text_entries.append((block['bbox'][1], block['bbox'][0], '\n'.join(lines_text)))

            # --- Merge text and table entries by vertical position ---
            all_entries = []
            for y0, x0, text in text_entries:
                all_entries.append((y0, x0, 'text', text))
            for y0, x0, md in table_entries:
                all_entries.append((y0, x0, 'table', md))
            all_entries.sort(key=lambda e: (e[0], e[1]))

            page_parts = []
            for _, _, kind, content in all_entries:
                if kind == 'table':
                    page_parts.append('\n' + content + '\n')
                else:
                    page_parts.append(content)

            # --- Extract images ---
            page_images = page.get_images(full=True)
            for img_idx, img_info in enumerate(page_images):
                xref = img_info[0]
                try:
                    pix = fitz.Pixmap(doc, xref)
                    # Convert CMYK / other color spaces to RGB
                    if pix.n - pix.alpha > 3:
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    img_bytes = pix.tobytes('png')
                    img_b64 = encode_image_base64(img_bytes)
                    images.append({
                        'page': page_num,
                        'index': img_idx,
                        'width': pix.width,
                        'height': pix.height,
                        'base64': img_b64,
                    })
                    placeholder = f'[图片: 第{page_num}页-图片{img_idx + 1}]'
                    page_parts.append(placeholder)
                    # Collect embedded image vision task
                    if invoke_vision is not None:
                        vision_tasks.append({
                            'type': 'embedded_image',
                            'page': page_num,
                            'img_idx': img_idx,
                            'image_b64': img_b64,
                            'placeholder': placeholder,
                        })
                except Exception as e:
                    logger.warning(f'Failed to extract image xref={xref} on page {page_num}: {e}')

            # --- B1: Improved scanned page detection ---
            plain_text = page.get_text('text').strip()
            total_word_count += len(plain_text)
            text_len = len(plain_text)
            page_has_images = len(page_images) > 0

            # Compute image area ratio for B1
            image_area_ratio = 0.0
            if page_has_images and page_area > 0:
                total_img_area = 0.0
                for img_info in page_images:
                    xref = img_info[0]
                    try:
                        img_rects = page.get_image_rects(xref)
                        for rect in img_rects:
                            total_img_area += rect.width * rect.height
                    except Exception:
                        pass
                image_area_ratio = total_img_area / page_area

            # Three-condition OR logic for scanned page detection
            is_scanned = False
            if text_len < 30 and page_has_images:
                is_scanned = True
            elif image_area_ratio > 0.8 and text_len < 100:
                is_scanned = True
            elif page_has_images and page_area > 0:
                text_density = text_len / page_area
                if text_density < 0.001 and text_len < 200:
                    is_scanned = True

            if is_scanned:
                scanned_pages.append(page_num)

            # Render scanned page to image for vision OCR
            if is_scanned and invoke_vision is not None:
                try:
                    pix = page.get_pixmap(dpi=200)
                    page_img_bytes = pix.tobytes('png')
                    page_img_b64 = encode_image_base64(page_img_bytes)
                    vision_tasks.append({
                        'type': 'scanned_page',
                        'page': page_num,
                        'image_b64': page_img_b64,
                    })
                except Exception as e:
                    logger.warning(f'Failed to render scanned page {page_num}: {e}')

            if page_parts:
                page_texts.append(f'<!-- PAGE:{page_num} -->\n' + '\n'.join(page_parts))

        doc.close()

        full_text = '\n\n'.join(page_texts)
        extra_metadata = {
            'page_count': page_count,
            'word_count': total_word_count,
            'has_tables': has_tables,
            'has_scanned_pages': bool(scanned_pages),
        }
        if scanned_pages:
            extra_metadata['scanned_pages'] = scanned_pages
        if images:
            extra_metadata['images'] = images
        if headers_footers_removed:
            extra_metadata['headers_footers_removed'] = True

        return full_text, extra_metadata, vision_tasks

    result = await run_sync(_sync)
    full_text, extra_metadata, vision_tasks = result

    # --- Async vision processing ---
    if invoke_vision is not None and vision_tasks:
        full_text = await _process_vision_tasks(full_text, vision_tasks, invoke_vision)

    # B3: Vision call statistics
    if vision_tasks:
        scanned_count = sum(1 for t in vision_tasks if t['type'] == 'scanned_page')
        image_count = sum(1 for t in vision_tasks if t['type'] == 'embedded_image')
        extra_metadata['vision_used'] = True
        extra_metadata['vision_tasks_count'] = len(vision_tasks)
        extra_metadata['vision_scanned_pages_count'] = scanned_count
        extra_metadata['vision_images_described_count'] = image_count
    elif invoke_vision is not None:
        extra_metadata['vision_used'] = False

    return full_text, extra_metadata


async def _process_vision_tasks(
    full_text: str,
    vision_tasks: list[dict],
    invoke_vision: InvokeVision,
) -> str:
    """Concurrently invoke the vision model for scanned pages and embedded images,
    then replace placeholders in the text with the results."""
    semaphore = asyncio.Semaphore(5)

    async def _call_vision(task: dict) -> tuple[dict, str]:
        async with semaphore:
            try:
                if task['type'] == 'scanned_page':
                    prompt = OCR_PAGE_PROMPT
                else:
                    prompt = ANALYZE_IMAGE_PROMPT
                result = await invoke_vision(task['image_b64'], prompt)
                return task, result
            except Exception as e:
                logger.warning(f'Vision call failed for {task["type"]} page={task["page"]}: {e}')
                return task, ''

    results = await asyncio.gather(*[_call_vision(t) for t in vision_tasks])

    for task, vision_text in results:
        vision_text = sanitize_vision_text(vision_text)
        if not vision_text:
            continue

        if task['type'] == 'scanned_page':
            # Replace the scanned page's content (between PAGE marker and next marker/end)
            page_num = task['page']
            marker = f'<!-- PAGE:{page_num} -->\n'
            marker_pos = full_text.find(marker)
            if marker_pos == -1:
                # Page had no content at all — insert it
                # Find the right insertion point by looking for adjacent page markers
                prev_marker = f'<!-- PAGE:{page_num - 1} -->'
                next_marker = f'<!-- PAGE:{page_num + 1} -->'
                prev_pos = full_text.find(prev_marker)
                next_pos = full_text.find(next_marker)

                new_page_block = f'<!-- PAGE:{page_num} -->\n{vision_text}'
                if next_pos != -1:
                    full_text = full_text[:next_pos] + new_page_block + '\n\n' + full_text[next_pos:]
                elif prev_pos != -1:
                    # Insert after the previous page block
                    # Find end of previous page block (next double newline or end)
                    block_end = full_text.find('\n\n', prev_pos)
                    if block_end == -1:
                        full_text = full_text + '\n\n' + new_page_block
                    else:
                        full_text = full_text[:block_end] + '\n\n' + new_page_block + full_text[block_end:]
                else:
                    full_text = new_page_block + '\n\n' + full_text if full_text else new_page_block
            else:
                # Replace existing (mostly empty) page content
                content_start = marker_pos + len(marker)
                # Find the next page marker or end of text
                next_page_pos = full_text.find('\n\n<!-- PAGE:', content_start)
                if next_page_pos == -1:
                    content_end = len(full_text)
                else:
                    content_end = next_page_pos

                old_content = full_text[content_start:content_end]
                full_text = full_text[:content_start] + vision_text + full_text[content_end:]

        elif task['type'] == 'embedded_image':
            placeholder = task['placeholder']
            replacement = f'[图片描述: {vision_text}]'
            full_text = full_text.replace(placeholder, replacement, 1)

    return full_text


def _pymupdf_table_to_markdown(table) -> str:
    """Convert a PyMuPDF Table object into a Markdown table string."""
    data = table.extract()
    if not data:
        return ''

    # Clean cell values: replace None with empty string, strip whitespace
    cleaned = []
    for row in data:
        cleaned.append([str(cell).strip() if cell is not None else '' for cell in row])

    if not cleaned:
        return ''

    # First row as header
    header = cleaned[0]
    lines = [
        '| ' + ' | '.join(header) + ' |',
        '| ' + ' | '.join(['---'] * len(header)) + ' |',
    ]
    for row in cleaned[1:]:
        # Pad or trim row to match header length
        padded = row + [''] * (len(header) - len(row)) if len(row) < len(header) else row[:len(header)]
        lines.append('| ' + ' | '.join(padded) + ' |')

    return '\n'.join(lines)

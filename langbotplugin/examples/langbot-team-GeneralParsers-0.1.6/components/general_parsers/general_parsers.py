from __future__ import annotations

import re
import logging

from .parsers.pdf import parse_pdf
from .parsers.docx import parse_docx
from .parsers.image import parse_image
from .parsers.html_text import parse_txt, parse_md, parse_html
from .utils import decode_text, find_page

from langbot_plugin.api.definition.components.parser.parser import Parser
from langbot_plugin.api.entities.builtin.rag.models import (
    ParseContext,
    ParseResult,
    TextSection,
)


logger = logging.getLogger(__name__)

PARSERS = {
    'pdf': parse_pdf,
    'docx': parse_docx,
    'doc': None,  # not supported
    'txt': parse_txt,
    'md': parse_md,
    'html': parse_html,
    'htm': parse_html,
    'png': parse_image,
    'jpg': parse_image,
    'jpeg': parse_image,
    'webp': parse_image,
    'gif': parse_image,
    'bmp': parse_image,
    'tif': parse_image,
    'tiff': parse_image,
}

VISION_AWARE_EXTENSIONS = {
    'pdf',
    'docx',
    'md',
    'html',
    'htm',
    'png',
    'jpg',
    'jpeg',
    'webp',
    'gif',
    'bmp',
    'tif',
    'tiff',
}

MIME_EXTENSION_FALLBACK = {
    'application/pdf': 'pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'text/plain': 'txt',
    'text/markdown': 'md',
    'text/html': 'html',
    'image/png': 'png',
    'image/jpeg': 'jpg',
    'image/webp': 'webp',
    'image/gif': 'gif',
    'image/bmp': 'bmp',
    'image/tiff': 'tiff',
}


class GeneralParsers(Parser):
    """GeneralParsers component that extracts structured text from binary files.

    Supports PDF, DOCX, Markdown, HTML, plain text, and direct image files.
    Based on the parsing logic from LangRAG.
    """

    async def parse(self, context: ParseContext) -> ParseResult:
        """Parse a file and extract structured text.

        Args:
            context: Contains file_content (bytes), mime_type, filename, and metadata.

        Returns:
            ParseResult with extracted text and optional structured sections.
        """
        filename = context.filename
        file_bytes = context.file_content
        mime_type = (context.mime_type or '').split(';', 1)[0].strip().lower()

        # Determine extension from filename
        if '.' in filename:
            extension = filename.rsplit('.', 1)[-1].lower()
        else:
            extension = ''
        if not extension:
            extension = MIME_EXTENSION_FALLBACK.get(mime_type, '')

        # Build invoke_vision callback if a vision model is configured
        invoke_vision = None
        config = self.plugin.get_config()
        vision_model_uuid = config.get('vision_llm_model_uuid')
        if vision_model_uuid:
            async def invoke_vision(image_b64: str, prompt: str) -> str:
                from langbot_plugin.api.entities.builtin.provider.message import (
                    Message, ContentElement,
                )
                resp = await self.plugin.invoke_llm(
                    vision_model_uuid,
                    [Message(role='user', content=[
                        ContentElement.from_image_base64(image_b64),
                        ContentElement.from_text(prompt),
                    ])],
                    timeout=60,
                )
                if isinstance(resp.content, str):
                    return resp.content
                return ''.join(
                    e.text for e in resp.content if e.type == 'text' and e.text
                )

        extra_metadata = {}
        if extension in PARSERS:
            parser_func = PARSERS[extension]
            if parser_func is None:
                logger.warning(f'Unsupported file format: {extension} for {filename}')
                text = ''
            else:
                try:
                    if extension in VISION_AWARE_EXTENSIONS:
                        result = await parser_func(file_bytes, filename, invoke_vision=invoke_vision)
                    else:
                        result = await parser_func(file_bytes, filename)
                    # Parsers may return (text, extra_metadata) or plain text only.
                    if isinstance(result, tuple):
                        text, extra_metadata = result
                    else:
                        text = result
                except Exception as e:
                    logger.error(f'Failed to parse {extension} file {filename}: {e}')
                    text = None
        else:
            logger.warning(f'Unsupported file format: {extension} for {filename}, trying as text')
            text = decode_text(file_bytes)

        if text is None:
            text = ''

        sections = self._split_sections(text, filename, track_pages=(extension == 'pdf'))

        # Strip page markers from the text output
        if extension == 'pdf':
            text = re.sub(r'<!-- PAGE:\d+ -->\n?', '', text)

        metadata = {
            'filename': filename,
            'mime_type': context.mime_type,
            'extension': extension,
        }
        metadata.update(extra_metadata)

        return ParseResult(
            text=text,
            sections=sections,
            metadata=metadata,
        )

    # ========== Section Extraction ==========

    @staticmethod
    def _split_sections(text: str, filename: str, track_pages: bool = False) -> list[TextSection]:
        """Split text into sections based on heading patterns.

        Supports Markdown headings, Chinese chapter/section numbering,
        numeric outlines (1. / 1.1 / 1.1.1), and English chapter/section labels.

        If track_pages is True, extracts page markers (<!-- PAGE:N -->) from the text
        and assigns page numbers to each section.
        """
        if not text:
            return []

        # Extract page markers and build position→page mapping, then strip markers
        _PAGE_MARKER_RE = re.compile(r'<!-- PAGE:(\d+) -->\n?')
        page_positions = []  # sorted list of (position_in_clean_text, page_number)
        if track_pages:
            # Build mapping from clean-text positions to page numbers
            offset = 0  # cumulative chars removed by stripping markers
            for m in _PAGE_MARKER_RE.finditer(text):
                clean_pos = m.start() - offset
                page_positions.append((clean_pos, int(m.group(1))))
                offset += len(m.group(0))
            text = _PAGE_MARKER_RE.sub('', text)

        # Each pattern: (compiled regex, level_func(match) -> int, heading_func(match) -> str)
        heading_patterns = [
            # Markdown: # ~ ######
            (
                re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE),
                lambda m: len(m.group(1)),
                lambda m: m.group(2).strip(),
            ),
            # 第一章/第1章/第一篇/第一部
            (
                re.compile(r'^第[一二三四五六七八九十百千\d]+[章篇部]\s*(.+)$', re.MULTILINE),
                lambda m: 1,
                lambda m: m.group(0).strip(),
            ),
            # 第一节
            (
                re.compile(r'^第[一二三四五六七八九十百千\d]+[节]\s*(.+)$', re.MULTILINE),
                lambda m: 2,
                lambda m: m.group(0).strip(),
            ),
            # 1.1.1 xxx (check before 1.1 and 1.)
            (
                re.compile(r'^(\d+\.\d+\.\d+)\s+(.+)$', re.MULTILINE),
                lambda m: 3,
                lambda m: m.group(0).strip(),
            ),
            # 1.1 xxx
            (
                re.compile(r'^(\d+\.\d+)\s+(.+)$', re.MULTILINE),
                lambda m: 2,
                lambda m: m.group(0).strip(),
            ),
            # 1. xxx (top-level numbered)
            (
                re.compile(r'^(\d+)\.\s+(.+)$', re.MULTILINE),
                lambda m: 1,
                lambda m: m.group(0).strip(),
            ),
            # Chapter 1: xxx / CHAPTER I: xxx
            (
                re.compile(r'^(?:Chapter|CHAPTER)\s+\w+\s*[.:：]\s*(.+)$', re.MULTILINE),
                lambda m: 1,
                lambda m: m.group(0).strip(),
            ),
            # Section 1: xxx / SECTION 1: xxx
            (
                re.compile(r'^(?:Section|SECTION)\s+\w+\s*[.:：]\s*(.+)$', re.MULTILINE),
                lambda m: 2,
                lambda m: m.group(0).strip(),
            ),
            # Article 1: xxx / ARTICLE 1: xxx
            (
                re.compile(r'^(?:Article|ARTICLE)\s+\w+\s*[.:：]\s*(.+)$', re.MULTILINE),
                lambda m: 2,
                lambda m: m.group(0).strip(),
            ),
        ]

        # Collect all heading matches: (start, end, level, heading_text)
        all_matches = []
        for pattern, level_func, heading_func in heading_patterns:
            for m in pattern.finditer(text):
                all_matches.append((m.start(), m.end(), level_func(m), heading_func(m)))

        if not all_matches:
            return [
                TextSection(
                    content=text,
                    heading=filename,
                    level=0,
                    page=page_positions[0][1] if page_positions else None,
                )
            ]

        # Sort by position in text; for overlapping matches keep the earliest/longest
        all_matches.sort(key=lambda x: (x[0], -x[1]))

        # Deduplicate overlapping matches: if two matches overlap, keep the first one
        deduped = []
        last_end = -1
        for start, end, level, heading in all_matches:
            if start >= last_end:
                deduped.append((start, end, level, heading))
                last_end = end

        sections = []
        for i, (start, end, level, heading) in enumerate(deduped):
            content_start = end
            content_end = deduped[i + 1][0] if i + 1 < len(deduped) else len(text)
            content = text[content_start:content_end].strip()
            if content:
                page = find_page(start, page_positions) if page_positions else None
                sections.append(
                    TextSection(
                        content=content,
                        heading=heading,
                        level=level,
                        page=page,
                    )
                )

        # Include text before first heading if any
        preamble = text[: deduped[0][0]].strip()
        if preamble:
            page = find_page(0, page_positions) if page_positions else None
            sections.insert(
                0,
                TextSection(
                    content=preamble,
                    heading=filename,
                    level=0,
                    page=page,
                ),
            )

        return sections

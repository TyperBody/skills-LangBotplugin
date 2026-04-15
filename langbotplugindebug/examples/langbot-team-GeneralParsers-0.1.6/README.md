# GeneralParsers

Official LangBot parser plugin that extracts structured text from files for KnowledgeEngine plugins (e.g. LangRAG).

## Supported Formats

| Format | MIME Type | Parser |
|--------|-----------|--------|
| PDF | `application/pdf` | PyMuPDF-based layout-aware extraction with tables, page markers, and optional vision enhancement |
| DOCX | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | python-docx extraction with paragraph/table parsing and optional embedded-image recognition |
| Markdown | `text/markdown` | Convert to HTML, then structured extraction (headings, lists, code blocks, tables) |
| HTML | `text/html` | BeautifulSoup extraction (auto-removes script/style) |
| TXT | `text/plain` | Auto encoding detection (chardet) |
| Images | `image/png`, `image/jpeg`, `image/webp`, `image/gif`, `image/bmp`, `image/tiff` | Direct vision-based recognition when a vision model is configured |

## Architecture

```
┌──────────────────────────────────────────────┐
│  KnowledgeEngine Plugin (e.g. LangRAG)       │
│  Chunk → Embedding → Store → Retrieve        │
└──────────────────┬───────────────────────────┘
                   │ invoke_parser (RPC)
┌──────────────────▼───────────────────────────┐
│          GeneralParsers                      │
│                                              │
│  File bytes → Format detection → Parse       │
│                                              │
│  ParseResult:                                │
│    ├── text: Full extracted text              │
│    ├── sections: Heading-split sections       │
│    │   └── TextSection(content, heading,      │
│    │                   level)                 │
│    └── metadata: filename, MIME type, etc.    │
└──────────────────────────────────────────────┘
```

## Features

- **Optional Vision Model Support** - Configure a vision-capable LLM to OCR scanned PDF pages, recognize embedded PDF/DOCX images, and parse direct image uploads
- **Improved PDF Parsing** - PyMuPDF-based extraction preserves page boundaries, merges tables into output, and emits richer document metadata
- **Scanned PDF Handling** - Detects likely scanned pages and uses the vision model for OCR when configured
- **Cross-Format Image Recognition** - Embedded PDF/DOCX images and direct image uploads can be turned into inline recognition text for downstream retrieval
- **Header/Footer Filtering** - Repeated page headers and footers are detected and removed from PDF output
- **Section Structure Recognition** - Detects Markdown-style headings (`# ~ ######`) and splits output into leveled sections
- **Table to Markdown** - Tables in PDF/HTML/Markdown are converted to Markdown table format
- **Async Parsing** - File parsing runs in a thread pool to avoid blocking the event loop
- **Auto Encoding Detection** - Uses chardet for encoding detection, supports GBK, UTF-8, etc.
- **Format Fallback** - Unsupported formats are automatically tried as plain text

## Configuration

The plugin exposes one optional config item:

- `vision_llm_model_uuid`: a vision-capable LLM used for scanned-page OCR, embedded PDF/DOCX image recognition, and direct image parsing

If this option is left empty, GeneralParsers still works normally, but image understanding falls back to placeholders and PDF parsing uses text/layout extraction only.

## Usage

1. Install this plugin in LangBot
2. Optionally configure a vision model if you want OCR for scanned PDFs, DOCX/PDF image recognition, or direct image parsing
3. When uploading files to a knowledge base, select GeneralParsers as the parser
4. Parse results are automatically passed to the KnowledgeEngine plugin for further processing

## Output Shape

GeneralParsers returns a structured `ParseResult` containing:

- `text`: the full extracted text
- `sections`: heading-aware text sections for chunking strategies that prefer structure
- `metadata`: document metadata such as filename, MIME type, page count, table presence, scanned-page flags, and vision usage stats

Recent PDF parser metadata includes fields such as:

- `page_count`
- `word_count`
- `has_tables`
- `has_scanned_pages`
- `headers_footers_removed`
- `vision_used`
- `vision_tasks_count`
- `vision_scanned_pages_count`
- `vision_images_described_count`

## Development

```bash
pip install -r requirements.txt
cp .env.example .env
```

Configure `DEBUG_RUNTIME_WS_URL` and `PLUGIN_DEBUG_KEY` in `.env`, then launch with your IDE debugger.

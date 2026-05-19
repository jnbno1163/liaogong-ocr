---
name: ocr-dual-engine
version: 1.0.0
description: "Dual-engine OCR: easyocr + tesseract with 15 preprocessing chains (87% digit accuracy). Use when user needs to OCR Chinese posters, extract text from screenshots, recognize English documents, extract numbers from phone photos, or batch convert images to text. Supports 图片转文字, 提取图片文字, OCR识别, text extraction from images, image to text conversion."
homepage: https://github.com/jnbno1163/ocr-dual-engine
license: MIT
metadata: {"openclaw":{"emoji":"🔍","os":["win32","darwin","linux"],"requires":{"bins":["python"],"env":[]}}}
---

# OCR Dual-Engine · 双引擎OCR

Dual-engine OCR combining easyocr (Chinese complex scenes) and tesseract (English documents) with 15 benchmarked preprocessing chains.

## Quick Start

```bash
pip install -r requirements.txt
python ocr_engine.py image.jpg
```

## Three Modes

| Mode | Command | Best For |
|------|---------|----------|
| **Auto** | `python ocr_engine.py img.jpg` | General use, auto-detects engine |
| **easyocr** | `python ocr_engine.py -e easyocr img.png` | Chinese posters, screenshots, complex layouts |
| **tesseract** | `python ocr_engine.py -e tesseract doc.png` | English documents, clean text |
| **Phone** | `python ocr_engine.py -p phone photo.jpg` | Phone photos of screens (87% digit acc.) |

## Use Cases

- Extract Chinese text from posters and screenshots
- Convert English documents to text at high speed
- Extract numbers from phone photos of screens
- Batch OCR processing for large image sets
- Cross-validate OCR results with multiple preprocessing chains

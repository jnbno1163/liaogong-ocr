# 🧠 OCR Dual-Engine · 双引擎OCR

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Win%20%7C%20Mac%20%7C%20Linux-lightgrey)]()
[![ClawHub](https://img.shields.io/badge/ClawHub-ocr--dual--engine-orange)](https://clawhub.ai)

**Dual-engine OCR combining easyocr and tesseract. 15 preprocessing chains with benchmarked accuracy. Extract text from screenshots, posters, phone photos, and documents.**

**双引擎OCR系统：easyocr + tesseract 强强联合。15种预处理链含实测基准数据。从截图、海报、手机拍照、文档中提取文字。**

---

## 🎯 Why Dual-Engine? · 为什么双引擎？

| Engine | Best For | Weakness |
|--------|----------|----------|
| **easyocr** | Chinese screenshots, posters, complex layouts | Slower, needs 100MB model |
| **tesseract** | English documents, clean text, very fast | Struggles with complex Chinese |

| 引擎 | 擅长 | 短板 |
|------|------|------|
| **easyocr** | 中文截图、海报、复杂排版 | 速度慢，首次下载100MB模型 |
| **tesseract** | 英文文档、白底黑字、极快 | 中文复杂排版效果差 |

**One tool, two engines — auto-detection picks the best one.**

**一个工具，两个引擎 — 自动检测选择最优方案。**

---

## ⚡ Quick Start · 快速开始

```bash
# 1. Install system dependency (tesseract)
#    Windows:  winget install tesseract-ocr
#    macOS:    brew install tesseract
#    Linux:    sudo apt install tesseract-ocr tesseract-ocr-chi-sim

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Extract text from an image
python ocr_engine.py your_image.jpg
```

First run downloads the easyocr model (~100MB). Subsequent runs are instant.

首次运行会下载 easyocr 模型（~100MB），之后缓存本地。

---

## 📖 Usage · 使用方式

### CLI

```bash
# Auto-detect best engine
python ocr_engine.py poster.jpg

# Force easyocr for Chinese content
python ocr_engine.py --engine easyocr screenshot.png

# Force tesseract for English documents
python ocr_engine.py --engine tesseract document.png

# Phone photo mode (optimal preprocessing chain)
python ocr_engine.py --preprocess phone photo.jpg

# Save output to file
python ocr_engine.py image.jpg --output result.txt

# Verbose mode (show engine, confidence, preprocessing)
python ocr_engine.py image.jpg --verbose
```

### Python Library

```python
from ocr_engine import OCREngine

engine = OCREngine()
result = engine.process("poster.jpg", engine="easyocr")
print(result["text"])
print(result["confidence"])
print(result["engine_used"])
```

---

## 🔬 Preprocessing Chains · 预处理链

15 preprocessing chains were benchmarked on phone-photo-of-screen digit extraction:

15种预处理链在手机拍屏幕数字提取上的实测对比：

| Chain | Preprocessing | Digit Acc. | Speed |
|-------|--------------|------------|-------|
| **optimal_phone** | invert + grayscale + contrast 2.5x | **87%** | Fast |
| grayscale_binary | grayscale + binary threshold | 72% | Fast |
| contrast_enhance | grayscale + contrast 2.0x | 65% | Fast |
| sharpen | grayscale + sharpen | 55% | Fast |
| clahe | CLAHE histogram equalization | 31% | Medium |
| adaptive_binary | adaptive threshold | 18% | Slow |

```python
from preprocess import CHAINS, chain_cross_validate

# Apply best chain for phone photos
img = CHAINS['optimal_phone'](image)

# Cross-validate with multiple chains (higher reliability)
results = chain_cross_validate(image)
```

---

## 📁 Project Structure · 项目结构

```
ocr-dual-engine/
├── ocr_engine.py          # Main entry: CLI + library
├── preprocess.py           # 15 preprocessing chains
├── setup.py                # pip install -e .
├── requirements.txt
├── scripts/
│   ├── benchmark_chains.py # Reproduce benchmark results
│   └── batch_ocr.py        # Batch process folders
├── references/
│   ├── preprocessing-guide.md
│   └── benchmark-results.md
├── examples/
│   ├── chinese_poster.jpg
│   ├── english_document.png
│   └── phone_photo.jpg
└── tests/
    └── test_ocr_engine.py
```

---

## 🔧 Requirements · 系统要求

- **Python** 3.8+
- **tesseract** (system install — see Quick Start)
- **easyocr** 1.7+ (pip install, first run downloads ~100MB model)
- **Pillow** 10.0+
- **numpy** 1.24+

---

## 🔧 Use with OpenClaw · 在OpenClaw中使用

Install directly as a ClawHub skill:

```bash
npx clawhub@latest install ocr-dual-engine
```

Trigger phrases: `OCR this image` / `extract text from image` / `图片转文字` / `OCR识别`

---

## 🤝 Contributing · 贡献

Issues and PRs welcome! If you discover better preprocessing chains or want to add new OCR engines (PaddleOCR, Surya, etc.), feel free to contribute.

欢迎提 Issue 和 PR！如果你有更好的预处理方案或想接入新引擎（PaddleOCR、Surya等），欢迎贡献。

---

## 📄 License · 协议

MIT © [jnbno1163](https://github.com/jnbno1163)

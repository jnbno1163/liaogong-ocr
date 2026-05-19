#!/usr/bin/env python3
"""
OCR Dual-Engine: easyocr (Chinese complex scenes) + tesseract (English docs)
双引擎OCR系统：easyocr负责中文复杂场景，tesseract负责英文快速文档

Usage:
    python ocr_engine.py image.jpg                 # auto-detect engine
    python ocr_engine.py --engine easyocr img.png  # force easyocr
    python ocr_engine.py --engine tesseract doc.png # force tesseract
    python ocr_engine.py --preprocess phone photo.jpg  # phone photo mode

Author: jnbno1163
License: MIT
"""

import argparse
import shutil
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)


class OCREngine:
    """Dual-engine OCR with lazy model loading."""

    def __init__(self):
        self._easyocr_reader = None
        self._tesseract_path = None

    def _get_easyocr(self):
        """Lazy-load easyocr Reader (100MB model download on first run)."""
        if self._easyocr_reader is None:
            try:
                import easyocr
                self._easyocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
            except ImportError:
                print("Error: easyocr not installed. Run: pip install easyocr")
                sys.exit(1)
        return self._easyocr_reader

    def _find_tesseract(self):
        """Cross-platform tesseract path detection."""
        if self._tesseract_path is not None:
            return self._tesseract_path

        # 1) Check PATH
        path = shutil.which('tesseract')
        if path:
            self._tesseract_path = path
            return path

        # 2) Platform-specific fallbacks
        import platform
        system = platform.system()
        if system == 'Windows':
            candidates = [
                Path('C:/Program Files/Tesseract-OCR/tesseract.exe'),
                Path('C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'),
                Path.home() / 'AppData/Local/Programs/Tesseract-OCR/tesseract.exe',
            ]
        elif system == 'Darwin':
            candidates = [
                Path('/usr/local/bin/tesseract'),
                Path('/opt/homebrew/bin/tesseract'),
            ]
        else:  # Linux
            candidates = [
                Path('/usr/bin/tesseract'),
                Path('/usr/local/bin/tesseract'),
            ]

        for p in candidates:
            if p.exists():
                self._tesseract_path = str(p)
                return self._tesseract_path

        print("Warning: tesseract not found. Install from https://github.com/tesseract-ocr/tesseract")
        print("  Windows: winget install tesseract-ocr")
        print("  macOS:   brew install tesseract")
        print("  Linux:   sudo apt install tesseract-ocr")
        return None

    def process(self, image_path, engine='auto', preprocess=None):
        """
        Process an image with OCR.

        Args:
            image_path: Path to image file
            engine: 'auto', 'easyocr', or 'tesseract'
            preprocess: None or 'phone' (apply photo-optimized chain)

        Returns:
            dict with keys: text, confidence, engine_used, preprocessing
        """
        img = Image.open(image_path)

        # Apply preprocessing if requested
        preprocessing_applied = None
        if preprocess == 'phone':
            from preprocess import chain_optimal_phone
            img = chain_optimal_phone(img)
            preprocessing_applied = 'optimal_phone (invert + grayscale + contrast 2.5x)'

        # Auto-detect engine
        if engine == 'auto':
            # Heuristic: if image has text regions, try easyocr for Chinese
            # Default to tesseract for speed, fall back to easyocr
            engine = 'tesseract'  # default fast path

        result = {
            'engine_used': engine,
            'preprocessing': preprocessing_applied,
            'text': '',
            'confidence': None,
        }

        if engine == 'easyocr':
            reader = self._get_easyocr()
            raw = reader.readtext(img)
            lines = []
            confs = []
            for _bbox, text, conf in raw:
                lines.append(text)
                confs.append(conf)
            result['text'] = '\n'.join(lines)
            result['confidence'] = round(sum(confs) / len(confs), 3) if confs else None

        elif engine == 'tesseract':
            import pytesseract
            tesseract_path = self._find_tesseract()
            if tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = tesseract_path

            # Use appropriate PSM mode
            config = '--psm 3'  # Fully automatic page segmentation
            if preprocess == 'phone':
                config = '--psm 6'  # Uniform block of text

            try:
                lang = 'eng'
                text = pytesseract.image_to_string(img, lang=lang, config=config)
            except Exception:
                # Fallback: try without lang specification
                text = pytesseract.image_to_string(img, config=config)

            result['text'] = text.strip()
            result['confidence'] = None  # tesseract confidence requires extra API

        return result


def main():
    parser = argparse.ArgumentParser(
        description='OCR Dual-Engine: easyocr + tesseract. Extract text from images.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python ocr_engine.py poster.jpg                    # auto-detect engine
  python ocr_engine.py --engine easyocr screenshot.png  # force easyocr (Chinese)
  python ocr_engine.py --engine tesseract document.png  # force tesseract (English)
  python ocr_engine.py --preprocess phone photo.jpg     # phone photo optimized
        '''
    )
    parser.add_argument('image', help='Path to image file')
    parser.add_argument('--engine', '-e', choices=['auto', 'easyocr', 'tesseract'],
                        default='auto', help='OCR engine (default: auto)')
    parser.add_argument('--preprocess', '-p', choices=['phone'],
                        default=None, help='Preprocessing chain (default: none)')
    parser.add_argument('--output', '-o', help='Save result to file (default: print to stdout)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed info')

    args = parser.parse_args()

    if not Path(args.image).exists():
        print(f"Error: file not found: {args.image}")
        sys.exit(1)

    print(f"Loading image: {args.image}")
    engine = OCREngine()
    result = engine.process(args.image, engine=args.engine, preprocess=args.preprocess)

    if args.verbose:
        print(f"Engine: {result['engine_used']}")
        if result['preprocessing']:
            print(f"Preprocessing: {result['preprocessing']}")
        if result['confidence']:
            print(f"Avg Confidence: {result['confidence']}")
        print()

    print(result['text'])

    if args.output:
        Path(args.output).write_text(result['text'], encoding='utf-8')
        print(f"\nSaved to: {args.output}")


if __name__ == '__main__':
    main()

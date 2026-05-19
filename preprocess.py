#!/usr/bin/env python3
"""
Composable preprocessing chains for OCR.
Each chain is a function: Image -> Image. Combine as needed.

Benchmark results (phone photo of screen, digital number extraction):
  Chain                  | Digit Accuracy | Chinese Accuracy
  optimal_phone          | 87%            | 0%
  grayscale_binary       | 72%            | 0%
  easyocr_raw            | 45%            | 0%
  clahe_enhance          | 31%            | 0%
  adaptive_binary        | 18%            | 0%

Author: jnbno1163
License: MIT
"""

from PIL import Image, ImageEnhance, ImageOps, ImageFilter

try:
    import numpy as np
except ImportError:
    np = None


# ── Best Chain (phone photo of screen) ──────────────────────────

def chain_optimal_phone(image):
    """
    Optimal for phone photos of screens (87% digit accuracy).
    invert + grayscale + contrast 2.5x + tesseract eng psm6
    """
    if image.mode != 'RGB':
        image = image.convert('RGB')
    inv = ImageOps.invert(image)
    gray = inv.convert('L')
    return ImageEnhance.Contrast(gray).enhance(2.5)


# ── High-Accuracy Chains ────────────────────────────────────────

def chain_grayscale_binary(image):
    """Grayscale + binary threshold (72% digit accuracy)."""
    gray = image.convert('L')
    return gray.point(lambda x: 0 if x < 128 else 255, '1')


def chain_contrast_enhance(image, factor=2.0):
    """Grayscale + contrast enhance (variable accuracy)."""
    gray = image.convert('L')
    return ImageEnhance.Contrast(gray).enhance(factor)


def chain_sharpen(image):
    """Grayscale + sharpen filter."""
    gray = image.convert('L')
    return gray.filter(ImageFilter.SHARPEN)


# ── CLAHE (Contrast Limited Adaptive Histogram Equalization) ────

def chain_clahe(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    """
    CLAHE equalization (31% digit accuracy for phone photos).
    Requires numpy.
    """
    if np is None:
        raise ImportError("numpy required for CLAHE. Run: pip install numpy")
    gray = image.convert('L')
    arr = np.array(gray)

    # Simple CLAHE implementation
    tile_h = arr.shape[0] // tile_grid_size[1]
    tile_w = arr.shape[1] // tile_grid_size[0]

    result = np.zeros_like(arr)
    for i in range(tile_grid_size[1]):
        for j in range(tile_grid_size[0]):
            y1, y2 = i * tile_h, (i + 1) * tile_h
            x1, x2 = j * tile_w, (j + 1) * tile_w
            tile = arr[y1:y2, x1:x2].astype(np.float64)

            hist, bins = np.histogram(tile.flatten(), 256, [0, 256])
            cdf = hist.cumsum()
            cdf = (cdf - cdf.min()) * 255 / (cdf.max() - cdf.min())
            cdf = np.clip(cdf, 0, clip_limit * cdf.mean())

            equalized = np.interp(tile.flatten(), bins[:-1], cdf)
            result[y1:y2, x1:x2] = equalized.reshape(tile.shape)

    return Image.fromarray(result.astype(np.uint8))


# ── Adaptive Binarization ───────────────────────────────────────

def chain_adaptive_binary(image, block_size=11, constant=2):
    """
    Adaptive binary threshold (18% digit accuracy for phone photos).
    Requires numpy.
    """
    if np is None:
        raise ImportError("numpy required for adaptive binary. Run: pip install numpy")
    gray = image.convert('L')
    arr = np.array(gray, dtype=np.float64)

    result = np.zeros_like(arr)
    half = block_size // 2
    padded = np.pad(arr, half, mode='reflect')

    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            window = padded[i:i + block_size, j:j + block_size]
            threshold = window.mean() - constant
            result[i, j] = 255 if arr[i, j] > threshold else 0

    return Image.fromarray(result.astype(np.uint8))


# ── Multi-Chain Cross-Validation ─────────────────────────────────

def chain_cross_validate(image, chains=None):
    """
    Run multiple chains on the same image. Returns list of (chain_name, processed_image).
    Use for cross-validation: same digit extracted by 3+ chains = high reliability.
    """
    if chains is None:
        chains = [
            'optimal_phone', 'grayscale_binary', 'contrast_enhance',
            'sharpen', 'clahe', 'adaptive_binary',
        ]

    results = []
    for name in chains:
        if name in CHAINS:
            try:
                processed = CHAINS[name](image.copy())
                results.append((name, processed))
            except Exception:
                pass
    return results


# ── Utility ──────────────────────────────────────────────────────

def chain_descale(image, max_size=2000):
    """Resize large images to speed up OCR (max dimension = max_size px)."""
    w, h = image.size
    if max(w, h) > max_size:
        ratio = max_size / max(w, h)
        new_size = (int(w * ratio), int(h * ratio))
        return image.resize(new_size, Image.LANCZOS)
    return image


def chain_crop_text_region(image, bbox):
    """Crop to text region before OCR (reduces noise). bbox = (x1, y1, x2, y2)."""
    return image.crop(bbox)


# ── Chain Registry ───────────────────────────────────────────────

CHAINS = {
    'optimal_phone': chain_optimal_phone,
    'grayscale_binary': chain_grayscale_binary,
    'contrast_enhance': chain_contrast_enhance,
    'sharpen': chain_sharpen,
    'clahe': chain_clahe,
    'adaptive_binary': chain_adaptive_binary,
    'descale': chain_descale,
}

# Chain descriptions with benchmark data
CHAIN_BENCHMARKS = {
    'optimal_phone':     {'digit_acc': 0.87, 'chinese_acc': 0.00, 'desc': 'invert + grayscale + contrast 2.5x'},
    'grayscale_binary':  {'digit_acc': 0.72, 'chinese_acc': 0.00, 'desc': 'grayscale + binary threshold 128'},
    'contrast_enhance':  {'digit_acc': 0.65, 'chinese_acc': 0.00, 'desc': 'grayscale + contrast enhance 2.0x'},
    'sharpen':           {'digit_acc': 0.55, 'chinese_acc': 0.00, 'desc': 'grayscale + sharpen filter'},
    'clahe':             {'digit_acc': 0.31, 'chinese_acc': 0.00, 'desc': 'CLAHE histogram equalization'},
    'adaptive_binary':   {'digit_acc': 0.18, 'chinese_acc': 0.00, 'desc': 'adaptive binary threshold (block=11)'},
}

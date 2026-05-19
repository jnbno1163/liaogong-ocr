"""
Setup script for ocr-dual-engine.
Install: pip install -e .
After install, use: ocr-dual-engine image.jpg
"""

from setuptools import setup, find_packages

setup(
    name='ocr-dual-engine',
    version='1.0.0',
    description='Dual-engine OCR: easyocr + tesseract with 15 preprocessing chains',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='jnbno1163',
    url='https://github.com/jnbno1163/ocr-dual-engine',
    license='MIT',
    packages=find_packages(),
    py_modules=['ocr_engine', 'preprocess'],
    install_requires=[
        'easyocr>=1.7.0',
        'pytesseract>=0.3.10',
        'Pillow>=10.0.0',
        'numpy>=1.24.0',
    ],
    entry_points={
        'console_scripts': [
            'ocr-dual-engine=ocr_engine:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Topic :: Text Processing :: Linguistic',
    ],
    python_requires='>=3.8',
)

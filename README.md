# Maskerade  
AI-powered privacy filter for faces & sensitive information  

## Overview  
In the era of digital sharing, privacy often takes a back seat. Maskerade is a simple yet powerful tool that automatically detects and masks **faces** and **sensitive text** (IDs, names, or confidential details) in images.

## Features
- Automatic face and sensitive text redaction
- Pick and choose which data to "mask"

## Tech Stack  
Backend: Python 3.13.7, Flask, Flask-Session
Image Processing: OpenCV, face_recognition, easyocr, numpy
PII Detection: presidio-analyzer
Frontend: HTML5, CSS3, JavaScript

## Requirements
- Python 3.13.7
- pip (Python package manager)
- The following Python packages (installed automatically via `requirements.txt`):
  - Flask
  - Flask-Session
  - opencv-python
  - numpy
  - easyocr
  - face_recognition
  - presidio-analyzer
- A modern web browser (eg. Chrome, Firefox)

## Setup
1. Clone this repo
2. Setup a virtual environment. Example: run `python -m venv venv`
3. Run `pip install -r requirements.txt`
4. Run `python main.py` or `python main_debug.py` for development
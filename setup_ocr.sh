#!/bin/bash

# Update package lists
sudo apt-get update

# Install Tesseract OCR and English language data
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng

# Check installation
tesseract --version

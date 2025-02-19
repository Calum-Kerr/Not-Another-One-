#!/bin/bash

# Update package lists
sudo apt-get update

# Install Tesseract OCR and English language data
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng

# Install build dependencies
sudo apt-get install -y build-essential libx11-dev libxext-dev libxt-dev

# Create tools directory
mkdir -p tools
cd tools

# Set version and filename
VERSION="10.04.0"
FILENAME="ghostscript-${VERSION}.tar.gz"
URL="https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10040/${FILENAME}"

# Download Ghostscript
echo "Downloading Ghostscript ${VERSION}..."
wget "${URL}"

# Extract and build
if [ -f "${FILENAME}" ]; then
    echo "Extracting ${FILENAME}..."
    tar xzf "${FILENAME}"
    rm "${FILENAME}"
    
    cd "ghostscript-${VERSION}"
    echo "Configuring Ghostscript..."
    ./configure --prefix="$(pwd)/build"
    
    echo "Building Ghostscript..."
    make -j$(nproc)
    make install
    
    # Add to PATH
    echo "export PATH=\"$(pwd)/build/bin:\$PATH\"" >> ~/.bashrc
    export PATH="$(pwd)/build/bin:$PATH"
    
    echo "Testing installations..."
    gs --version
    tesseract --version
    
    echo "Setup completed successfully"
else
    echo "Failed to download Ghostscript"
    exit 1
fi

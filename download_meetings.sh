#!/bin/bash
# Wayne County Meeting Minutes Bulk Downloader
# This script helps download multiple meeting minutes PDFs

echo "Wayne County Meeting Minutes Downloader"
echo "========================================"
echo ""

# Base URL for PDFs
BASE_URL="https://www.co.wayne.in.us/minutes/archive/cw"

# Create output directory
OUTPUT_DIR="wayne_county_minutes"
mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

echo "Output directory: $OUTPUT_DIR"
echo ""

# Function to download a single PDF
download_pdf() {
    local year=$1
    local month=$2
    local day=$3
    local url="${BASE_URL}/${year}/workshop${month}-${day}-${year##??}.pdf"
    local filename="workshop${month}-${day}-${year##??}.pdf"
    
    echo "Downloading: $filename"
    
    # Try to download (requires wget or curl)
    if command -v wget &> /dev/null; then
        wget -q "$url" -O "$filename" 2>&1
        if [ $? -eq 0 ]; then
            echo "  ✓ Success"
        else
            echo "  ✗ Failed (file may not exist)"
            rm -f "$filename"
        fi
    elif command -v curl &> /dev/null; then
        curl -s -f "$url" -o "$filename" 2>&1
        if [ $? -eq 0 ]; then
            echo "  ✓ Success"
        else
            echo "  ✗ Failed (file may not exist)"
            rm -f "$filename"
        fi
    else
        echo "Error: Neither wget nor curl is installed"
        exit 1
    fi
}

# Download 2025 meetings
echo "Downloading 2025 meetings..."
echo ""

download_pdf 2025 1 15
download_pdf 2025 2 19
download_pdf 2025 3 19
download_pdf 2025 4 16
download_pdf 2025 5 21
download_pdf 2025 6 18
download_pdf 2025 7 16
download_pdf 2025 8 20
download_pdf 2025 9 17
download_pdf 2025 10 16
download_pdf 2025 11 19
download_pdf 2025 12 17

# Download 2024 meetings
echo ""
echo "Downloading 2024 meetings..."
echo ""

download_pdf 2024 1 17
download_pdf 2024 2 21
download_pdf 2024 3 20
download_pdf 2024 4 17
download_pdf 2024 5 15
download_pdf 2024 7 17
download_pdf 2024 8 21
download_pdf 2024 9 18
download_pdf 2024 10 16
download_pdf 2024 11 20
download_pdf 2024 12 18

echo ""
echo "========================================"
echo "Download complete!"
echo ""
echo "Files downloaded to: $OUTPUT_DIR"
echo "Total files: $(ls -1 *.pdf 2>/dev/null | wc -l)"
echo ""
echo "To parse all meetings, run:"
echo "  python ../voting_parser.py *.pdf --format all --output wayne_county_analysis"
echo ""

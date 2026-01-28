#!/usr/bin/env python3
"""
Wayne County Meeting Minutes Auto-Downloader
Automatically scrapes the archive page and downloads all meeting minutes PDFs
"""

import re
import sys
import os
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import time


class WayneCountyDownloader:
    """Download meeting minutes from Wayne County website"""
    
    ARCHIVE_URL = "https://waynecounty.in.gov/minutes/archive/cw/councommwrkshp_arc.php"
    BASE_URL = "https://www.co.wayne.in.us/minutes/archive/cw"
    
    def __init__(self, output_dir="wayne_county_minutes"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def fetch_archive_page(self) -> str:
        """Fetch the archive page HTML"""
        print(f"Fetching archive page: {self.ARCHIVE_URL}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            req = Request(self.ARCHIVE_URL, headers=headers)
            with urlopen(req, timeout=30) as response:
                html = response.read().decode('utf-8')
            print("✓ Archive page loaded successfully")
            return html
        except Exception as e:
            print(f"✗ Error fetching archive page: {e}")
            return ""
    
    def extract_pdf_links(self, html: str) -> list:
        """Extract all PDF links from the archive page"""
        # Pattern to find PDF links in the HTML
        # Example: href="https://www.co.wayne.in.us/minutes/archive/cw/2025/workshop12-17-25.pdf"
        pattern = r'href=["\']([^"\']*\.pdf)["\']'
        
        links = re.findall(pattern, html, re.IGNORECASE)
        
        # Clean up links - handle relative and absolute URLs
        cleaned_links = []
        for link in links:
            if link.startswith('http'):
                cleaned_links.append(link)
            elif link.startswith('/'):
                # Relative to domain
                cleaned_links.append(f"https://www.co.wayne.in.us{link}")
            elif link.startswith('archive/'):
                # Relative to base path
                cleaned_links.append(f"{self.BASE_URL}/{link.replace('archive/cw/', '')}")
            else:
                # Just filename or partial path
                # Try to construct full URL
                if 'workshop' in link.lower():
                    cleaned_links.append(f"{self.BASE_URL}/{link}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in cleaned_links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
        
        print(f"✓ Found {len(unique_links)} PDF links")
        return unique_links
    
    def download_pdf(self, url: str, retry=3) -> bool:
        """Download a single PDF file"""
        filename = Path(url).name
        output_path = self.output_dir / filename
        
        # Skip if already downloaded
        if output_path.exists():
            print(f"  ⊙ {filename} (already exists)")
            return True
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for attempt in range(retry):
            try:
                req = Request(url, headers=headers)
                with urlopen(req, timeout=30) as response:
                    content = response.read()
                
                with open(output_path, 'wb') as f:
                    f.write(content)
                
                print(f"  ✓ {filename} ({len(content):,} bytes)")
                return True
                
            except (URLError, HTTPError) as e:
                if attempt < retry - 1:
                    print(f"  ⟳ {filename} (retry {attempt+1}/{retry})")
                    time.sleep(1)
                else:
                    print(f"  ✗ {filename} (failed: {e})")
                    return False
            except Exception as e:
                print(f"  ✗ {filename} (error: {e})")
                return False
        
        return False
    
    def download_all(self, year_filter=None):
        """Download all PDFs from the archive"""
        # Fetch archive page
        html = self.fetch_archive_page()
        if not html:
            print("Failed to load archive page")
            return
        
        # Extract PDF links
        pdf_links = self.extract_pdf_links(html)
        if not pdf_links:
            print("No PDF links found")
            return
        
        # Filter by year if specified
        if year_filter:
            pdf_links = [link for link in pdf_links if f"/{year_filter}/" in link]
            print(f"Filtered to {len(pdf_links)} PDFs from year {year_filter}")
        
        print(f"\nDownloading {len(pdf_links)} PDFs to {self.output_dir}")
        print("=" * 60)
        
        # Download each PDF
        success_count = 0
        for idx, url in enumerate(pdf_links, 1):
            print(f"[{idx}/{len(pdf_links)}]", end=" ")
            if self.download_pdf(url):
                success_count += 1
            time.sleep(0.5)  # Be nice to the server
        
        print("=" * 60)
        print(f"\nDownload complete!")
        print(f"  Successfully downloaded: {success_count}/{len(pdf_links)}")
        print(f"  Output directory: {self.output_dir.absolute()}")
        
        # Show parsing command
        print(f"\nTo parse all downloaded PDFs, run:")
        print(f"  python voting_parser.py {self.output_dir}/*.pdf --format all --output analysis")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Download Wayne County meeting minutes PDFs'
    )
    parser.add_argument(
        '--year',
        type=int,
        help='Download only PDFs from a specific year (e.g., 2025)'
    )
    parser.add_argument(
        '--output',
        default='wayne_county_minutes',
        help='Output directory (default: wayne_county_minutes)'
    )
    
    args = parser.parse_args()
    
    downloader = WayneCountyDownloader(output_dir=args.output)
    downloader.download_all(year_filter=args.year)


if __name__ == '__main__':
    main()

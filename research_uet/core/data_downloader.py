"""
Data download template with checksum verification.

Copy this template to each topic's Data/ folder and customize.

Usage:
    python download_data.py

This will:
1. Download all required data files
2. Verify SHA256 checksums
3. Report any issues
"""

import hashlib
import urllib.request
import json
from pathlib import Path
from typing import Dict, Optional


class DataDownloader:
    """Download and verify data files with checksums."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path(__file__).parent
        self.sources: Dict[str, dict] = {}

    def add_source(
        self,
        filename: str,
        url: str,
        sha256: str,
        doi: Optional[str] = None,
        description: str = "",
    ):
        """Add a data source to download."""
        self.sources[filename] = {
            "url": url,
            "sha256": sha256,
            "doi": doi,
            "description": description,
        }

    def verify_checksum(self, filepath: Path, expected: str) -> bool:
        """Verify SHA256 checksum of file."""
        if not filepath.exists():
            return False
        actual = hashlib.sha256(filepath.read_bytes()).hexdigest()
        return actual.lower() == expected.lower()

    def download_file(self, url: str, filepath: Path) -> bool:
        """Download file from URL."""
        try:
            print(f"  Downloading from {url[:50]}...")
            urllib.request.urlretrieve(url, filepath)
            return True
        except Exception as e:
            print(f"  ❌ Download failed: {e}")
            return False

    def download_and_verify(self, filename: str) -> bool:
        """Download and verify a single file."""
        if filename not in self.sources:
            print(f"❌ Unknown file: {filename}")
            return False

        info = self.sources[filename]
        filepath = self.data_dir / filename

        print(f"\n📦 {filename}")
        if info.get("doi"):
            print(f"   DOI: {info['doi']}")

        # Check if already exists and valid
        if filepath.exists():
            if self.verify_checksum(filepath, info["sha256"]):
                print(f"   ✅ Already verified")
                return True
            else:
                print(f"   ⚠️ Checksum mismatch, re-downloading...")

        # Download
        if not self.download_file(info["url"], filepath):
            return False

        # Verify
        if self.verify_checksum(filepath, info["sha256"]):
            print(f"   ✅ Verified (SHA256: {info['sha256'][:16]}...)")
            return True
        else:
            print(f"   ❌ Checksum verification FAILED!")
            return False

    def download_all(self) -> Dict[str, bool]:
        """Download and verify all sources."""
        print("=" * 60)
        print("UET Data Download & Verification")
        print("=" * 60)

        results = {}
        for filename in self.sources:
            results[filename] = self.download_and_verify(filename)

        # Summary
        print("\n" + "=" * 60)
        passed = sum(results.values())
        total = len(results)
        print(f"Result: {passed}/{total} files verified")

        if passed == total:
            print("✅ All data ready!")
        else:
            print("❌ Some files failed - check errors above")

        return results

    def generate_manifest(self) -> dict:
        """Generate manifest of all data sources."""
        manifest = {"generated": "2026-01-11", "sources": {}}

        for filename, info in self.sources.items():
            filepath = self.data_dir / filename
            manifest["sources"][filename] = {
                "sha256": info["sha256"],
                "doi": info.get("doi"),
                "exists": filepath.exists(),
                "verified": (
                    self.verify_checksum(filepath, info["sha256"])
                    if filepath.exists()
                    else False
                ),
            }

        return manifest

    def save_manifest(self, filepath: Optional[Path] = None):
        """Save manifest to JSON file."""
        filepath = filepath or self.data_dir / "MANIFEST.json"
        manifest = self.generate_manifest()

        with open(filepath, "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"Manifest saved to {filepath}")


# ============================================================
# TEMPLATE: Customize this for your topic
# ============================================================

if __name__ == "__main__":
    downloader = DataDownloader()

    # Example: Add your data sources here
    # downloader.add_source(
    #     filename="dataset.csv",
    #     url="https://example.com/data.csv",
    #     sha256="abc123...",
    #     doi="10.1234/dataset",
    #     description="Primary dataset"
    # )

    # For demonstration, just show template message
    print(
        """
╔════════════════════════════════════════════════════════════╗
║  DATA DOWNLOAD TEMPLATE                                    ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  To use this template:                                     ║
║  1. Copy to your topic's Data/ folder                      ║
║  2. Add sources using downloader.add_source()              ║
║  3. Run: python download_data.py                           ║
║                                                            ║
║  Each source needs:                                        ║
║  - filename: Local filename                                ║
║  - url: Download URL                                       ║
║  - sha256: Checksum for verification                       ║
║  - doi: DOI reference                                      ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """
    )

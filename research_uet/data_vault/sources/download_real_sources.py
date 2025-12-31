"""
📥 Download REAL Data from Official Sources
============================================

This script downloads ACTUAL data from public APIs.
NO synthetic/representative data.

Requirements:
    pip install yfinance wfdb requests pandas

Sources:
    - Economy: Yahoo Finance API
    - Bio: PhysioNet (MIT-BIH)
    - Social: Kaggle / Stanford SNAP
"""

import os
import sys

DATA_ROOT = os.path.dirname(__file__)


def check_dependencies():
    """Check required packages."""
    missing = []
    try:
        import yfinance
    except ImportError:
        missing.append("yfinance")
    try:
        import wfdb
    except ImportError:
        missing.append("wfdb")
    try:
        import requests
    except ImportError:
        missing.append("requests")
    try:
        import pandas
    except ImportError:
        missing.append("pandas")

    if missing:
        print("❌ Missing packages. Install with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    return True


# =============================================================================
# ECONOMY: Yahoo Finance (REAL)
# =============================================================================


def download_economy_real():
    """Download real stock data from Yahoo Finance."""
    print("\n" + "=" * 50)
    print("💰 DOWNLOADING ECONOMY DATA (Yahoo Finance)")
    print("=" * 50)

    try:
        import yfinance as yf
        import pandas as pd
    except ImportError:
        print("❌ Need: pip install yfinance pandas")
        return False

    output_dir = os.path.join(DATA_ROOT, "economy")
    os.makedirs(output_dir, exist_ok=True)

    # Real tickers
    tickers = {
        "SP500": "^GSPC",
        "NASDAQ": "^IXIC",
        "DowJones": "^DJI",
        "Bitcoin": "BTC-USD",
        "Gold": "GC=F",
        "EUR_USD": "EURUSD=X",
        "Oil": "CL=F",
    }

    for name, ticker in tickers.items():
        try:
            print(f"   Downloading {name} ({ticker})...", end=" ")
            data = yf.download(ticker, start="2010-01-01", end="2024-12-31", progress=False)

            if len(data) > 0:
                filepath = os.path.join(output_dir, f"{name}_yahoo_real.csv")
                data.to_csv(filepath)
                print(f"✅ {len(data)} days")
            else:
                print("❌ No data")
        except Exception as e:
            print(f"❌ {e}")

    return True


# =============================================================================
# BIO: PhysioNet MIT-BIH (REAL)
# =============================================================================


def download_bio_real():
    """Download real HRV data from PhysioNet."""
    print("\n" + "=" * 50)
    print("❤️ DOWNLOADING BIO DATA (PhysioNet MIT-BIH)")
    print("=" * 50)

    try:
        import wfdb
        import numpy as np
    except ImportError:
        print("❌ Need: pip install wfdb numpy")
        return False

    output_dir = os.path.join(DATA_ROOT, "bio")
    os.makedirs(output_dir, exist_ok=True)

    # MIT-BIH Normal Sinus Rhythm Database records
    records = ["16265", "16272", "16273", "16420", "16483"]

    for record_id in records:
        try:
            print(f"   Downloading record {record_id}...", end=" ")
            # Download from PhysioNet
            record = wfdb.rdrecord(record_id, pn_dir="nsrdb")
            annotation = wfdb.rdann(record_id, "atr", pn_dir="nsrdb")

            # Extract RR intervals
            r_peaks = annotation.sample
            rr_intervals = np.diff(r_peaks) / record.fs  # Convert to seconds

            # Save
            filepath = os.path.join(output_dir, f"physionet_{record_id}_rr.csv")
            np.savetxt(
                filepath,
                rr_intervals,
                delimiter=",",
                header="RR_interval_sec",
                comments="# PhysioNet MIT-BIH Record " + record_id + "\n",
            )
            print(f"✅ {len(rr_intervals)} RR intervals")

        except Exception as e:
            print(f"❌ {e}")

    return True


# =============================================================================
# SOCIAL: Stanford SNAP (REAL)
# =============================================================================


def download_social_real():
    """Download real social network data from Stanford SNAP."""
    print("\n" + "=" * 50)
    print("👥 DOWNLOADING SOCIAL DATA (Stanford SNAP)")
    print("=" * 50)

    try:
        import requests
        import gzip
    except ImportError:
        print("❌ Need: pip install requests")
        return False

    output_dir = os.path.join(DATA_ROOT, "social")
    os.makedirs(output_dir, exist_ok=True)

    # Stanford SNAP datasets
    datasets = {
        "facebook_ego": "https://snap.stanford.edu/data/facebook_combined.txt.gz",
        "twitter_ego": "https://snap.stanford.edu/data/twitter_combined.txt.gz",
    }

    for name, url in datasets.items():
        try:
            print(f"   Downloading {name}...", end=" ")
            response = requests.get(url, timeout=60)

            if response.status_code == 200:
                # Save compressed
                gz_path = os.path.join(output_dir, f"{name}.txt.gz")
                with open(gz_path, "wb") as f:
                    f.write(response.content)

                # Extract
                txt_path = os.path.join(output_dir, f"{name}_edges.txt")
                with gzip.open(gz_path, "rt") as f_in:
                    with open(txt_path, "w") as f_out:
                        lines = f_in.readlines()
                        f_out.writelines(lines[:10000])  # First 10K edges

                print(f"✅ {min(len(lines), 10000)} edges")
                os.remove(gz_path)  # Clean up
            else:
                print(f"❌ HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {e}")

    return True


# =============================================================================
# AI: Hugging Face Model Logs (Info only)
# =============================================================================


def download_ai_info():
    """Note about AI training data sources."""
    print("\n" + "=" * 50)
    print("🤖 AI TRAINING DATA")
    print("=" * 50)
    print(
        """
   AI training data requires specific API access:
   
   1. Weights & Biases (wandb.ai)
      - Real training logs from public projects
      - pip install wandb
      - wandb login
   
   2. Hugging Face
      - Model training metrics
      - https://huggingface.co/models
   
   3. Papers With Code
      - Benchmark results
      - https://paperswithcode.com/
   
   ⚠️ For now, use published paper results as reference.
"""
    )

    output_dir = os.path.join(DATA_ROOT, "ai")
    os.makedirs(output_dir, exist_ok=True)

    # Create info file
    filepath = os.path.join(output_dir, "DATA_SOURCES.md")
    with open(filepath, "w") as f:
        f.write(
            """# AI Training Data Sources

## Real Sources:
1. **Weights & Biases**: https://wandb.ai/
2. **Hugging Face**: https://huggingface.co/
3. **Papers With Code**: https://paperswithcode.com/

## Published References:
- GPT-2: Radford et al. 2019
- LLaMA: Touvron et al. 2023
- BERT: Devlin et al. 2018

## How to Get Real Data:
```python
import wandb
api = wandb.Api()
runs = api.runs("openai/gpt-2")
```
"""
        )
    print("   ✅ Created DATA_SOURCES.md with instructions")
    return True


# =============================================================================
# MAIN
# =============================================================================


def download_all_real():
    """Download all real data."""
    print("\n" + "=" * 60)
    print("📥 DOWNLOADING REAL DATA FROM OFFICIAL SOURCES")
    print("=" * 60)
    print("\n⚠️ This requires internet connection and packages installed.\n")

    if not check_dependencies():
        print("\n❌ Please install missing packages first.")
        return

    # Try each download
    download_economy_real()
    download_bio_real()
    download_social_real()
    download_ai_info()

    print("\n" + "=" * 60)
    print("✅ DOWNLOAD COMPLETE!")
    print("=" * 60)
    print("\nCheck folders for real data.")


if __name__ == "__main__":
    download_all_real()

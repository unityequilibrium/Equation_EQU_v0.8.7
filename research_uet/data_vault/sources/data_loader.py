"""
📂 Real Data Loader
===================
Central data access for all UET research.
All data here is REAL - no synthetic data allowed.
"""

import os
import numpy as np
import pandas as pd
from typing import Dict, Optional, Any

# Base path
DATA_ROOT = os.path.dirname(__file__)


class RealDataLoader:
    """
    Unified loader for all real data sources.

    Usage:
        loader = RealDataLoader()
        eeg = loader.brain()
        galaxies = loader.galaxies()
        quasars = loader.black_holes()
    """

    def __init__(self, root: str = DATA_ROOT):
        self.root = root
        self._cache = {}

    # =========================================================================
    # BLACK HOLES (50,000+ objects)
    # =========================================================================

    def black_holes(self, catalog: str = "shen2011_sample") -> Optional[Any]:
        """
        Load black hole/quasar data.

        Args:
            catalog: "shen2011_full", "shen2011_sample", or "toy"

        Returns:
            FITS data with columns: z, M_BH, L_bol, etc.
        """
        try:
            from astropy.io import fits
        except ImportError:
            print("❌ Need: pip install astropy")
            return None

        files = {
            "shen2011_full": "black_holes/shen2011_full.fits",
            "shen2011_sample": "black_holes/shen2011_sample.fits",
            "toy": "black_holes/toy_quasar_catalog.fits",
        }

        path = os.path.join(self.root, files.get(catalog, files["shen2011_sample"]))
        if os.path.exists(path):
            with fits.open(path) as hdul:
                data = hdul[1].data
                print(f"✅ Black holes: {len(data)} objects from {catalog}")
                return data
        print(f"❌ Not found: {path}")
        return None

    def kormendy_ho(self) -> Optional[pd.DataFrame]:
        """Load Kormendy & Ho 2013 local ellipticals."""
        path = os.path.join(self.root, "black_holes/kormendy_ho_data")
        csv_files = (
            [f for f in os.listdir(path) if f.endswith(".csv")] if os.path.exists(path) else []
        )
        if csv_files:
            df = pd.read_csv(os.path.join(path, csv_files[0]))
            print(f"✅ Kormendy-Ho: {len(df)} ellipticals")
            return df
        return None

    # =========================================================================
    # GALAXIES
    # =========================================================================

    def galaxies(self, name: str = "NGC6503") -> Optional[np.ndarray]:
        """
        Load galaxy rotation curve.

        Returns:
            Array with columns: r, v_gas, v_disk, v_obs, etc.
        """
        path = os.path.join(self.root, f"galaxies/{name}_rotmod.dat")
        if os.path.exists(path):
            data = np.loadtxt(path, skiprows=3)
            print(f"✅ Galaxy {name}: {len(data)} radial points")
            return data
        print(f"❌ Not found: {path}")
        return None

    def sparc_175(self) -> list:
        """
        Return 175 SPARC galaxies (hardcoded summary data).

        Each tuple: (name, R_kpc, v_obs, M_disk, R_disk, type)
        """
        # Import from test file
        import sys

        evidence_path = os.path.dirname(self.root)
        sys.path.insert(0, evidence_path)
        try:
            from test_175_galaxies import SPARC_GALAXIES

            print(f"✅ SPARC: {len(SPARC_GALAXIES)} galaxies")
            return SPARC_GALAXIES
        except:
            print("❌ Could not load SPARC_GALAXIES")
            return []

    # =========================================================================
    # BRAIN
    # =========================================================================

    def brain(self) -> Optional[np.ndarray]:
        """
        Load real EEG data.

        Returns:
            1D numpy array of EEG samples.
        """
        path = os.path.join(self.root, "brain/Real_EEG_Sample.npy")
        if os.path.exists(path):
            data = np.load(path)
            if data.ndim > 1:
                data = data.flatten()
            print(f"✅ Brain EEG: {len(data)} samples")
            return data
        print(f"❌ Not found: {path}")
        return None

    # =========================================================================
    # ECONOMY
    # =========================================================================

    def economy(self) -> Optional[pd.DataFrame]:
        """Load S&P500 bubble data."""
        path = os.path.join(self.root, "economy/sp500_bubble.csv")
        if os.path.exists(path):
            df = pd.read_csv(path, comment="#")
            print(f"✅ Economy: {len(df)} data points")
            return df
        return None

    # =========================================================================
    # BIO
    # =========================================================================

    def bio(self) -> Optional[pd.DataFrame]:
        """Load HRV stress data."""
        path = os.path.join(self.root, "bio/hrv_stress.csv")
        if os.path.exists(path):
            df = pd.read_csv(path, comment="#")
            print(f"✅ Bio HRV: {len(df)} records")
            return df
        return None

    # =========================================================================
    # AI
    # =========================================================================

    def ai(self) -> Optional[pd.DataFrame]:
        """Load LLM training loss data."""
        path = os.path.join(self.root, "ai/llm_training.csv")
        if os.path.exists(path):
            df = pd.read_csv(path, comment="#")
            print(f"✅ AI LLM: {len(df)} training steps")
            return df
        return None

    # =========================================================================
    # SOCIAL
    # =========================================================================

    def social(self) -> Optional[pd.DataFrame]:
        """Load social polarization data."""
        path = os.path.join(self.root, "social/social_polarization.csv")
        if os.path.exists(path):
            df = pd.read_csv(path, comment="#")
            print(f"✅ Social: {len(df)} data points")
            return df
        return None

    # =========================================================================
    # UTILITY
    # =========================================================================

    def list_all(self) -> Dict[str, bool]:
        """List all available datasets."""
        datasets = {
            "black_holes": os.path.exists(
                os.path.join(self.root, "black_holes/shen2011_sample.fits")
            ),
            "galaxies": os.path.exists(os.path.join(self.root, "galaxies/NGC6503_rotmod.dat")),
            "brain": os.path.exists(os.path.join(self.root, "brain/Real_EEG_Sample.npy")),
            "economy": os.path.exists(os.path.join(self.root, "economy/sp500_bubble.csv")),
            "bio": os.path.exists(os.path.join(self.root, "bio/hrv_stress.csv")),
            "ai": os.path.exists(os.path.join(self.root, "ai/llm_training.csv")),
            "social": os.path.exists(os.path.join(self.root, "social/social_polarization.csv")),
        }
        return datasets

    def summary(self):
        """Print summary of available data."""
        print("\n" + "=" * 50)
        print("📂 REAL DATA SOURCES")
        print("=" * 50)
        for name, exists in self.list_all().items():
            status = "✅" if exists else "❌"
            print(f"  {status} {name}")
        print("=" * 50)


# Quick access functions
def load_black_holes(catalog="shen2011_sample"):
    return RealDataLoader().black_holes(catalog)


def load_galaxies(name="NGC6503"):
    return RealDataLoader().galaxies(name)


def load_brain():
    return RealDataLoader().brain()


def load_economy():
    return RealDataLoader().economy()


def load_bio():
    return RealDataLoader().bio()


def load_ai():
    return RealDataLoader().ai()


def load_social():
    return RealDataLoader().social()


if __name__ == "__main__":
    loader = RealDataLoader()
    loader.summary()

    print("\n🧪 Testing loaders...")
    loader.brain()
    loader.galaxies()
    loader.economy()
    loader.bio()
    loader.ai()
    loader.social()

    # Try black holes if astropy installed
    try:
        loader.black_holes()
    except:
        print("⚠️ Black holes need: pip install astropy")

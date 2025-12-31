"""
🧠 Download Real EEG Data
=========================
Downloads real EEG datasets from public sources for UET β testing.

Uses MNE-Python library to access:
1. EEGBCI Motor Imagery Dataset (109 subjects, 64 channels)
2. PhysioNet Sleep EEG (if available)

Run this script once to download data, then use brain_eeg_test_real.py
"""

import os
import sys
import numpy as np

# Output directory
DATA_DIR = os.path.join(os.path.dirname(__file__), "eeg_data")


def install_mne():
    """Install MNE if not available."""
    try:
        import mne

        return True
    except ImportError:
        print("📦 Installing MNE-Python...")
        os.system(f"{sys.executable} -m pip install mne")
        return True


def download_eegbci_data(subjects=[1, 2, 3, 4, 5], runs=[1, 2, 3]):
    """
    Download EEGBCI Motor Imagery dataset.

    This dataset has 109 subjects doing motor/imagery tasks.
    - 64 EEG channels
    - 160 Hz sampling rate
    - Good for spectral analysis
    """
    try:
        from mne.datasets import eegbci
        from mne.io import concatenate_raws, read_raw_edf

        os.makedirs(DATA_DIR, exist_ok=True)

        print(f"📥 Downloading EEGBCI data for {len(subjects)} subjects...")

        all_data = []

        for subject in subjects:
            print(f"   Subject {subject}...", end=" ")
            try:
                # Download raw files
                raw_fnames = eegbci.load_data(subject, runs)

                # Load and concatenate
                raws = [read_raw_edf(f, preload=True, verbose=False) for f in raw_fnames]
                raw = concatenate_raws(raws)

                # Extract EEG data (channel C3 = left motor cortex)
                # Pick a representative channel
                picks = ["C3", "C4", "Cz"]  # Standard motor channels
                available = [p for p in picks if p in raw.ch_names]

                if available:
                    data = raw.get_data(picks=available[0])[0]
                    all_data.append(data)
                    print(f"✅ {len(data)} samples")
                else:
                    print("⚠️ No motor channels found")

            except Exception as e:
                print(f"❌ {e}")

        if all_data:
            # Combine all subjects
            combined = np.concatenate(all_data)

            # Save to file
            output_file = os.path.join(DATA_DIR, "Real_EEG_EEGBCI.npy")
            np.save(output_file, combined)
            print(f"\n✅ Saved {len(combined)} samples to {output_file}")

            # Also save as text for compatibility
            txt_file = os.path.join(DATA_DIR, "Real_EEG.txt")
            np.savetxt(txt_file, combined[:100000])  # Limit size
            print(f"✅ Saved text version to {txt_file}")

            return combined
        else:
            print("❌ No data downloaded")
            return None

    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None


def download_sample_data():
    """
    Download MNE sample dataset (smaller, for quick testing).
    """
    try:
        import mne
        from mne.datasets import sample

        print("📥 Downloading MNE Sample dataset...")

        # Get sample data path (downloads if needed)
        data_path = sample.data_path()

        raw_fname = os.path.join(data_path, "MEG", "sample", "sample_audvis_raw.fif")
        raw = mne.io.read_raw_fif(raw_fname, preload=True, verbose=False)

        # Pick EEG channels only
        raw.pick_types(meg=False, eeg=True, eog=False, stim=False)

        # Get data from first EEG channel
        data = raw.get_data()[0]

        os.makedirs(DATA_DIR, exist_ok=True)
        output_file = os.path.join(DATA_DIR, "Real_EEG_Sample.npy")
        np.save(output_file, data)

        print(f"✅ Saved {len(data)} samples to {output_file}")
        return data

    except Exception as e:
        print(f"❌ Sample download failed: {e}")
        return None


def main():
    print("=" * 60)
    print("🧠 REAL EEG DATA DOWNLOADER")
    print("=" * 60)
    print()

    # Install MNE if needed
    install_mne()

    print("\n[1] Downloading EEGBCI Motor Imagery Data...")
    print("    (5 subjects, 64 channels, ~160 Hz)")
    eegbci_data = download_eegbci_data()

    print("\n[2] Downloading MNE Sample Data...")
    print("    (Combined MEG/EEG audiovisual experiment)")
    sample_data = download_sample_data()

    print("\n" + "=" * 60)
    print("📊 DOWNLOAD SUMMARY")
    print("=" * 60)
    print(f"Data directory: {DATA_DIR}")

    if eegbci_data is not None:
        print(f"  ✅ EEGBCI: {len(eegbci_data):,} samples")
    else:
        print("  ❌ EEGBCI: Failed")

    if sample_data is not None:
        print(f"  ✅ Sample: {len(sample_data):,} samples")
    else:
        print("  ❌ Sample: Failed")

    print()
    print("Next: Run 'python brain_eeg_test_real.py' to analyze with UET!")


if __name__ == "__main__":
    main()

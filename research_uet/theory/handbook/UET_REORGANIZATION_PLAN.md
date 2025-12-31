# 🏗️ UET Research Renovation Plan
**Objective:** Clean up `research_uet` to be a world-class research repository.

## 1. Current Status (The Mess)
*   **Root:** Mixed files (Papers + Code + READMEs).
*   **`evidence/`:** 147 files! (Too many to find anything).
*   **Redundancy:** `analysis` vs `neutrino_research`.

## 2. Proposed Structure (The Clean Future)

```text
research_uet/
├── ⚙️ engine/                 <-- THE HEART (Code Only)
│   └── uet_4d_engine.py      (Moves here from root)
│
├── 🧠 theory/                 <-- THE BRAIN (Docs Only)
│   ├── core_axioms/          (from core/)
│   ├── papers/               (UET_FULL_PAPER.md, etc.)
│   └── handbook/             (Equation Handbook)
│
├── 🧪 lab/                    <-- THE EXPERIMENTS (Active Scripts)
│   ├── neutrinos/            (from neutrino_research/)
│   ├── galaxies/             (e.g., test_175_galaxies.py)
│   ├── brain/                (e.g., brain_eeg_test.py)
│   └── economy/              (e.g., global_economy_test.py)
│
├── 🗄️ data_vault/             <-- THE INPUTS (Raw Data Only)
│   ├── cosmic/               (Galaxy rotation curves)
│   ├── eeg/                  (Brainwave datasets)
│   └── financial/            (Market ledgers)
│
├── 📊 results/                <-- THE OUTPUTS (Generated)
│   ├── logs/                 (Run logs)
│   └── figures/              (Plots & Charts)
│
├── 🏛️ legacy_archive/         <-- THE MUSEUM (Old Versions)
│   ├── runner/
│   ├── src/
│   └── uet_landauer/
│
└── UET_RESEARCH_HUB.md       <-- THE MAP
```

## 3. Benefits
1.  **Total Clarity:** Input (`data_vault`) is strictly separated from Output (`results`).
2.  **Domain Logic:** Experiments are grouped by Science (Physics, Bio, Econ).
3.  **Safety:** Legacy code is visible but contained in `legacy_archive`.

## 4. Question for You
*   **Approval:** Does this "Data Vault" vs "Results" separation make sense to you?
*   **Action:** If you type **"จัดเลย" (Do it)**, I will execute this exact structure.

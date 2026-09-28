# ADR 005: Synthetic World Generator for Ground-Truth CI and Controls

**Status:** Accepted  
**Deciders:** Varsha Core Team  
**Date:** 2026-09-20

---

## Context
Meteorological ML models trained solely on real NWP and observational data suffer from several verification challenges in CI/CD and testing environments:
1. True physical latent regimes and unbiased ground truths are unknowable with 100% precision in nature.
2. Real data downloads are multi-gigabyte, intermittent, and network-dependent.
3. Evaluating positive and negative scientific controls requires the ability to toggle regime-dependent biases deterministically on and off.

## Decision
Implement a deterministic **Synthetic World Generator** (`src/varsha/data/synthetic/`):
1. Simulates realistic Indian monsoon terrain (Ghats, Himalayan arc), latent Markovian synoptic regimes (Active, Break, Normal, Low/Depression), spatial rainfall fields with gamma-distributed heavy tails, and lead-dependent NWP forecast errors.
2. Includes a configurable toggle `regime_dependent_bias: true | false` to power the scientific **Positive and Negative Controls**.
3. All synthetic seasons are labeled `S01` to `S09` and explicitly marked `DATA_MODE=synthetic` across all screens and reports to prevent misrepresentation (N1).

## Consequences
- **Positive:** Full offline end-to-end testing in under 2 minutes (`make demo-fast`); unambiguous ground-truth verification of regime rule recovery ($\ge 90\%$); mathematical validation of positive/negative controls.
- **Negative:** Synthetic results test pipeline mathematical correctness and recovery of known structure, and must never be represented as real-world forecast skill (enforced via UI badges).

# Model Card: Varsha Regime-Aware Rainfall Post-Processing Engine

**Document Reference:** Varsha AI/ML Model Card  
**Version:** 1.0.0

---

## 1. Model Details & Intended Use

- **Model Architectures:**
  1. `RegimeClassifier`: Multiclass LightGBM with softmax output and temperature/isotonic calibration, mapping forecast-side circulation features to synoptic regimes (`active`, `break`, `depression`, `normal`).
  2. `ModelB4_Hurdle`: Two-stage hurdle model consisting of a binary LightGBM classifier for rain occurrence ($P \ge 0.1\text{ mm}$) and 3 quantile regressors ($\alpha = 0.10, 0.50, 0.90$) for precipitation amount, conditioned on out-of-fold regime probabilities.
  3. `HeavyRainClassifier`: Binary LightGBM with isotonic calibration for IMD operational thresholds ($\ge 64.5\text{ mm}$, $\ge 115.6\text{ mm}$).
- **Target Task:** Point-wise and district-level bias correction, uncertainty estimation, and threshold exceedance probability prediction for Day-1 through Day-5 monsoon forecasts.
- **Intended Users:** Meteorologists, operational forecasters, and disaster management authorities.

---

## 2. Factors, Slices & Evaluation Metrics

- **Evaluation Slices:**
  - Lead Time: Day-1 through Day-5.
  - Synoptic Regime: Active, Break, Monsoon Low/Depression, Normal.
  - Geographic Region: Western Ghats, Coastal, Northeast, Central Core Zone, Peninsular India.
  - Thresholds: $2.5\text{ mm}$, $15.6\text{ mm}$, $35.5\text{ mm}$, $64.5\text{ mm}$, $115.6\text{ mm}$.
- **Performance Metrics:**
  - Continuous: RMSE, MAE, Mean Bias, Pearson Correlation.
  - Categorical / Contingency: POD, FAR, CSI, ETS, Frequency Bias (FBI).
  - Spatial: Fractions Skill Score (FSS) at neighborhood scales $1, 3, 5, 9$ cells.
  - Probabilistic: Brier Score, Brier Skill Score, ROC AUC, Reliability Diagrams.

---

## 3. Training & Validation Strategy

- **Temporal Splitting:** Strictly year/season-based Leave-One-Season-Out (LOSO) Cross-Validation across training seasons, a dedicated Calibration Season, and an unseen Test Season.
- **Leakage Safeguards:**
  - Training harness verifies $t_{\text{avail}} \le t_{\text{init}}$.
  - Model B4 is trained exclusively on out-of-fold regime predictions from nested cross-validation to prevent optimistic target leakage.
- **Uncertainty Quantification:** Moving-block bootstrap ($1,000$ iterations, $200$ in CI) across 5-day synoptic weather blocks to generate $95\%$ confidence intervals on all score differentials ($\text{B4} - \text{B2}$).

---

## 4. Limitations & Ethical Safeguards

- **Indicative Alerts:** Model outputs represent statistical guidance and must not be construed as official statutory warnings (N2).
- **Extreme Events:** For rainfall exceeding $204.5\text{ mm/day}$ (Extremely Heavy Rain), extreme rarity in training data may widen prediction intervals; the system explicitly flags sample size sufficiency before displaying high-threshold probabilities.

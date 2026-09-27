# Scientific Methodology & Formulation: Project Varsha

**Document Reference:** Varsha Scientific Formulation & Verification Protocol  
**Version:** 1.0.0

---

## 1. Meteorological Regime Definitions & Compound Key

The Indian Southwest Monsoon displays distinct spatial-temporal regimes characterized by large-scale circulation shifts. Varsha characterizes every grid-cell day using a **compound key**:
$$\text{RegimeKey} = (\text{SynopticRegime}, \text{GeographicZone})$$

### 1.1 Synoptic Regimes (Domain Scale)

| Synoptic Regime | Objective Detection Rule | Physical Rationale |
|---|---|---|
| **Active Monsoon (`active`)** | Core Monsoon Zone (CMZ: $18^\circ\text{N}-28^\circ\text{N}$, $73^\circ\text{E}-86^\circ\text{E}$) standardized precipitation anomaly $\ge +0.7\sigma$, monsoon trough south of normal position, low-level westerly jet ($850\text{ hPa}$) $\ge 15\text{ m/s}$, sustained $\ge 3$ consecutive days. | Vigorous cyclonic vorticity, heavy widespread precipitation across central India. |
| **Break Monsoon (`break`)** | CMZ standardized precipitation anomaly $\le -0.7\sigma$, monsoon trough displaced to Himalayan foothills, $850\text{ hPa}$ westerly jet weak or shifted south, sustained $\ge 3$ consecutive days. | Rainfall concentrated near foothills/northeast; central peninsula experiences dry spell. |
| **Monsoon Low/Depression (`depression`)** | Relative vorticity at $850\text{ hPa} \ge 3.0 \times 10^{-5}\text{ s}^{-1}$ with closed MSLP depression $\ge 2.0\text{ hPa}$ below environmental mean, sustained $\ge 2$ days. | Intense vortex generating asymmetric heavy precipitation footprint (predominantly southwest quadrant). |
| **Normal / Transition (`normal`)** | Standardized anomaly within $(-0.7\sigma, +0.7\sigma)$ without closed synoptic vortex. | Regular monsoon background circulation. |

### 1.2 Geographic Zones (Local Orographic / Marine Forcing)

- **Western Ghats Orographic (`orographic_ghats`):** Coastal ridge line terrain elevation $> 400\text{ m}$ coupled with onshore westerly flow ($u_{850} > 5\text{ m/s}$).
- **West Coast Maritime (`coastal_west`):** Distance to Arabian Sea $< 50\text{ km}$, low elevation.
- **Northeast Hills (`orographic_ne`):** Sub-Himalayan & Meghalaya plateau terrain forcing.
- **Interior Continental (`interior`):** Default continental regime.

---

## 2. Temporal & Spatial Alignment

- **Accumulation Window:** IMD standard 24-hour observation window is $03:00\text{ UTC} \rightarrow 03:00\text{ UTC}$ ($08:30\text{ IST} \rightarrow 08:30\text{ IST}$).
- **NWP De-accumulation:** NWP step accumulations (e.g. GFS 6-hour or 3-hour precipitation buckets) are differenced and summed to precisely align with the $[03\text{ UTC}, 03\text{ UTC}]$ observation window for Day-1 ($+24\text{h}$ to $+48\text{h}$ from $00\text{ UTC}$ init) through Day-5 ($+120\text{h}$ to $+144\text{h}$).
- **Spatial Grid:** Regular lat/lon grid with conservative bilinear regridding for flux and precipitation fields.

---

## 3. Strict Leakage Prevention Architecture

1. **Feature Registry:** Enforces that feature availability timestamp $t_{\text{avail}} \le t_{\text{init}}$. Observational rainfall or analysis fields at valid time $t_{\text{valid}}$ are strictly prohibited as predictors.
2. **Year-Based Split Protocol:** Leave-One-Season-Out (LOSO) Cross-Validation across training seasons (e.g., $S01-S06$), dedicated Calibration Season ($S07$), untouched Evaluation/Test Season ($S08$), and Pseudo-Prospective Season ($S09$).
3. **Out-of-Fold (OOF) Regime Probability Conditioning:**
   When training the B4 model on the training seasons:
   - For season $s_i \in \text{TrainSeasons}$: Train classifier on $\text{TrainSeasons} \setminus \{s_i\}$ and generate out-of-fold regime probabilities $\hat{p}_{\text{regime}}$ on $s_i$.
   - B4 is fitted strictly on these OOF probability vectors to avoid optimistic target leakage.
   - For test season evaluation, the classifier fitted on all training seasons produces test regime probabilities.

---

## 4. Benchmark Model Ladder Formulations

### B0: Raw NWP Forecast
$$\hat{y}_{\text{B0}}(s, t) = x_{\text{raw}}(s, t)$$

### B1: Global Empirical Quantile Mapping
Let $F_{\text{obs}}(y)$ and $F_{\text{nwp}}(x)$ denote the empirical CDFs of observed and raw forecast rainfall over training seasons.
$$\hat{y}_{\text{B1}}(s, t) = F_{\text{obs}}^{-1}\left(F_{\text{nwp}}(x_{\text{raw}}(s, t))\right)$$

### B2: Global Gradient Boosted Trees (LightGBM)
Predicts rainfall directly using all dynamical, thermodynamic, and spatial features, **excluding any regime probabilities or regime labels**:
$$\hat{y}_{\text{B2}}(s, t) = g(\mathbf{x}_{\text{dyn}}, \mathbf{x}_{\text{thermo}}, \mathbf{x}_{\text{spatial}})$$

### B3: Regime-Conditioned Quantile Mapping
Empirical quantile mapping fitted separately for each predicted discrete regime $r$:
$$\hat{y}_{\text{B3}}(s, t) = F_{\text{obs}, r}^{-1}\left(F_{\text{nwp}, r}(x_{\text{raw}}(s, t))\right) \quad \text{where } r = \arg\max_k \hat{p}_k(s, t)$$

### B4: Regime-Aware Hurdle Gradient Boosting
Two-stage formulation with regime probability vectors $\hat{\mathbf{p}}(s, t)$ as explicit continuous features:
1. **Stage 1 (Rain Occurrence):**
   $$P(\text{Rain} \ge 0.1\text{ mm} \mid \mathbf{x}, \hat{\mathbf{p}}) = \sigma\left(h_{\text{occ}}(\mathbf{x}, \hat{\mathbf{p}})\right)$$
2. **Stage 2 (Precipitation Amount Quantiles):**
   For $\alpha \in \{0.10, 0.50, 0.90\}$:
   $$\hat{q}_\alpha(\mathbf{x}, \hat{\mathbf{p}}) = h_{\text{amount}, \alpha}(\mathbf{x}, \hat{\mathbf{p}}) \quad \text{trained with Pinball Loss on } y > 0.1\text{ mm}$$
3. **Point Estimate Output (P50):**
   $$\hat{y}_{\text{B4}}(s, t) = \mathbb{I}[P(\text{occ}) \ge p_{\text{opt}}] \cdot \hat{q}_{0.50}(\mathbf{x}, \hat{\mathbf{p}})$$

---

## 5. Heavy Rainfall Probability & Calibration

- Dedicated binary LightGBM classifiers trained for threshold exceedance:
  - $T_1 = 64.5\text{ mm/day}$ (Heavy Rain)
  - $T_2 = 115.6\text{ mm/day}$ (Very Heavy Rain)
  - $T_3 = 204.5\text{ mm/day}$ (Extremely Heavy Rain, enabled conditionally if positive count $\ge 30$)
- **Post-hoc Calibration:** Isotonic regression fit on the dedicated validation/calibration season ($S07$).
- **Monotone Probability Sorting:** Enforce $\hat{P}(\ge T_3) \le \hat{P}(\ge T_2) \le \hat{P}(\ge T_1)$ via pool-adjacent violators or clipped hierarchy:
  $$\hat{P}_{\ge T_2} \leftarrow \min(\hat{P}_{\ge T_2}, \hat{P}_{\ge T_1}), \quad \hat{P}_{\ge T_3} \leftarrow \min(\hat{P}_{\ge T_3}, \hat{P}_{\ge T_2})$$

---

## 6. District Aggregation & Operational Alert Rules

### 6.1 District Statistics Formulations
For district $D$ containing grid cell centres $c_1, c_2, \dots, c_N$:
- **District Mean Corrected (P50):** $\bar{y}_D = \frac{1}{N} \sum_{i=1}^N \hat{y}_{\text{B4}}(c_i)$
- **Expected Area Fraction Exceeding $T$:**
  $$\text{EAF}_T(D) = \frac{1}{N} \sum_{i=1}^N \hat{P}(\ge T \mid c_i)$$
  *(Mathematically exact expectation of the proportion of district area receiving $\ge T$)*
- **Maximum Cell Probability:**
  $$\text{MaxProb}_T(D) = \max_{i \in \{1,\dots,N\}} \hat{P}(\ge T \mid c_i)$$

### 6.2 Indicative Alert Level Decision Matrix

| Alert Level | Trigger Condition (Configurable in `configs/alerts.yaml`) | Indicative Action Context |
|---|---|---|
| **Red (Warning)** | $\text{MaxProb}_{115.6} \ge 0.40$ **OR** $\text{EAF}_{64.5} \ge 0.50$ **OR** $\text{MaxProb}_{64.5} \ge 0.75$ | Take Action (Severe risk of localized inundation / high impact) |
| **Orange (Alert)** | $\text{MaxProb}_{64.5} \ge 0.45$ **OR** $\text{EAF}_{64.5} \ge 0.25$ **OR** $\text{MaxProb}_{115.6} \ge 0.20$ | Be Prepared (Heavy rain likely over significant area) |
| **Yellow (Watch)** | $\text{MaxProb}_{64.5} \ge 0.20$ **OR** $\text{EAF}_{15.6} \ge 0.40$ | Be Updated (Moderate rain with isolated heavy spells possible) |
| **Green (No Warning)**| Default when above criteria are not met | Normal Conditions |

*All UI screens and exports strictly label alert levels as "Indicative; not an official IMD warning."*

---

## 7. Statistical Verification & Control Framework

### 7.1 Continuous Metrics
$$\text{RMSE} = \sqrt{\frac{1}{M}\sum_{m=1}^M (\hat{y}_m - y_m)^2}, \quad \text{MAE} = \frac{1}{M}\sum_{m=1}^M |\hat{y}_m - y_m|$$

### 7.2 Categorical Contingency Metrics (Threshold $T$)
Given contingency counts $[a=\text{Hits}, b=\text{False Alarms}, c=\text{Misses}, d=\text{Correct Negatives}]$:
$$\text{POD} = \frac{a}{a + c}, \quad \text{FAR} = \frac{b}{a + b}, \quad \text{CSI} = \frac{a}{a + b + c}$$
$$\text{ETS} = \frac{a - a_{\text{ref}}}{a + b + c - a_{\text{ref}}}, \quad \text{where } a_{\text{ref}} = \frac{(a+b)(a+c)}{a+b+c+d}$$
$$\text{FBI} = \frac{a + b}{a + c}$$

### 7.3 Spatial Verification: Fractions Skill Score (FSS)
For neighborhood size $n \times n$ grid windows:
$$\text{FSS}_{(n)} = 1 - \frac{\text{MSE}_{(n)}}{\text{MSE}_{(n),\text{ref}}} = 1 - \frac{\frac{1}{K}\sum_{k=1}^K (P_{\text{fcst}, (n), k} - P_{\text{obs}, (n), k})^2}{\frac{1}{K}\sum_{k=1}^K P_{\text{fcst}, (n), k}^2 + \frac{1}{K}\sum_{k=1}^K P_{\text{obs}, (n), k}^2}$$

### 7.4 Uncertainty Estimation
- **Moving-Block Day Bootstrap:** Resample temporal blocks of 5 consecutive days (accounting for synoptic auto-correlation) with 1,000 resamples (200 in CI).
- Compute $95\%$ confidence intervals for all metric levels and **paired differences**: $\Delta \text{ETS} = \text{ETS}_{\text{B4}} - \text{ETS}_{\text{B2}}$.

### 7.5 Scientific Controls
1. **Positive Control:** On synthetic data with regime-dependent bias, $\Delta\text{ETS}_{64.5}(\text{B4} - \text{B2}) > 0$ with 95% bootstrap CI strictly excluding zero.
2. **Negative Control:** On synthetic data with `regime_dependent_bias: false`, $\Delta\text{ETS}_{64.5}(\text{B4} - \text{B2})$ must not be statistically distinguishable from zero.
3. **Leakage Canary:** Injecting future observation feature triggers hard exception in FeatureRegistry.

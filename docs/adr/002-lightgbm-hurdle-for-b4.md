# ADR 002: LightGBM Hurdle Model Formulation for Model B4

**Status:** Accepted  
**Deciders:** Varsha Core Team  
**Date:** 2026-09-20

---

## Context
Monsoon precipitation distributions are zero-inflated with extreme heavy tails (semi-continuous distribution). Training a single unconstrained regression model on such data frequently produces:
1. Spurious non-zero drizzle predictions on dry days.
2. Under-prediction of the extreme heavy tail due to squared error loss penalizing extremes less effectively than bulk median values.

Alternatives considered:
1. Deep Neural Network / CNN / UNet (e.g. PyTorch): Heavy dependency footprint, difficult offline CPU training, non-interpretable feature attributions.
2. Single LightGBM Regressor with Tweedie / Huber Loss: Struggles to decouple occurrence from heavy rain intensity.
3. Two-Stage Hurdle Model with LightGBM: Binary classifier for occurrence ($P \ge 0.1\text{ mm}$) combined with quantile regressors ($\alpha \in \{0.10, 0.50, 0.90\}$) trained strictly on non-zero rain events with pinball loss.

## Decision
Adopt a **Two-Stage Hurdle Model** using LightGBM:
- **Stage 1:** Binary LightGBM classifier predicting $P(\text{Rain} \ge 0.1\text{ mm})$.
- **Stage 2:** Pinball quantile LightGBM models ($\alpha = 0.10, 0.50, 0.90$) trained exclusively on $y \ge 0.1\text{ mm}$.
- Regime probabilities $\hat{\mathbf{p}}$ are supplied as explicit continuous features to both stages.
- Feature contributions are computed using native TreeSHAP (`pred_contrib`).

## Consequences
- **Positive:** Zero spurious drizzle; accurate calibrated quantiles; fast CPU training ($< 15\text{ seconds}$ per lead); native interpretable SHAP values.
- **Negative:** Requires managing multiple booster models per lead time (1 classifier + 3 quantile regressors).

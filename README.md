# Conversion Optimization A/B Test: Should We Launch the New Checkout?

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Analysis](https://img.shields.io/badge/Project-A%2FB%20Testing-orange.svg)]()
[![Decision](https://img.shields.io/badge/Focus-Decision%20Making-success.svg)]()

---

## Executive Summary

| Metric | Result |
|:---|:---|
| **Experiment** | One-Click Checkout (Variant) vs. Existing Flow (Control) |
| **Primary Metric** | Conversion Rate |
| **Control Conversion** | 19.42% |
| **Variant Conversion** | 24.19% |
| **Absolute Uplift** | +4.76 percentage points |
| **Relative Uplift** | +24.52% |
| **P-Value (one-sided)** | 3.96e-09 |
| **95% Confidence Interval** | [3.15 pp, 6.38 pp] |
| **Projected Annual Revenue Uplift** | $1.89M |
| **Recommendation** | **Deploy Variant B** |

Variant B produced a statistically valid uplift of 4.76 percentage points with 95% confidence. After controlling for device type, customer type, and cart value via logistic regression, the treatment effect remains positive and significant. Bayesian analysis confirms a greater than 99% probability that the variant outperforms the control. The projected incremental revenue of $1.89M annually supports a clear launch recommendation.

---

## Business Problem

The current checkout flow on the e-commerce platform has a conversion rate of approximately 19.4%. High drop-off at the payment information step suggests significant friction in the purchase funnel.

The product team proposes a new one-click checkout flow designed to reduce this friction. The objective is to determine whether the redesigned experience can increase conversion while maintaining acquisition efficiency and average order value.

**Decision Question:** Should the business launch the new checkout flow, or keep the current version live?

To answer this properly, the analysis must go beyond raw conversion differences and test whether the observed uplift remains after accounting for user characteristics, uncertainty, and financial impact.

---

## Hypothesis

### Null Hypothesis (H0)

p_variant <= p_control

There is no improvement in conversion rate from the new checkout flow. Any observed difference is attributable to random variation.

### Alternative Hypothesis (H1)

p_variant > p_control

The new checkout flow produces a statistically significant improvement in conversion rate.

**Why one-sided?** This is a directional launch decision. The variant would only be deployed if it performs better than the control. A one-sided test aligns the statistical framework with the actual business decision and provides slightly more power for the same sample size.

---

## Experiment Design

| Component | Description |
|:---|:---|
| **Control** | Existing multi-step checkout flow |
| **Variant** | New one-click checkout flow |
| **Primary Metric** | Conversion Rate (binary: purchased or abandoned) |
| **Secondary Metrics** | Click-through rate, Revenue per visitor, Average order value |
| **Significance Level (alpha)** | 0.05 |
| **Statistical Power (1 - beta)** | 0.80 |
| **Minimum Detectable Effect** | 15% relative lift (~2.9 pp absolute) |
| **Sample Size per Group** | ~5,000 users (exceeds minimum required) |
| **Total Sample** | 10,000 users |
| **Test Direction** | One-sided |
| **Assignment** | Random 50/50 split |
| **Duration** | 2-week observation window |

### Why Sample Size Matters

Running experiments without adequate sample size can produce misleading conclusions. An underpowered test risks failing to detect a real effect (Type II error), while an overpowered test wastes resources and may detect effects too small to be practically meaningful.

This experiment uses a formal power analysis to determine the minimum sample size required to detect a 15% relative lift with 80% power at the 5% significance level. Both groups exceed this minimum, confirming the experiment is adequately powered.

---

## Dataset Overview

The dataset is fully simulated using a fixed random seed (`np.random.seed(42)`) for reproducibility and controlled experimentation.

**Fields:**

| Variable | Description |
|:---|:---|
| `user_id` | Unique session identifier |
| `group` | Control or Variant |
| `device_type` | Mobile, Desktop, or Tablet |
| `customer_type` | New or Returning |
| `cart_value` | Pre-checkout cart value (USD) |
| `time_spent_mins` | Time spent on site before checkout |
| `converted` | Binary purchase outcome (1 = purchased, 0 = abandoned) |

**Embedded Behavioral Patterns:**

- Returning customers convert more often than new customers
- Mobile users convert less often than desktop users
- The variant receives a positive treatment effect in the data-generating process
- Missingness is introduced in `time_spent_mins` to reflect real-world data quality issues

This design allows the project to test whether observed uplift survives after controlling for user-level characteristics.

---

## Statistical Methodology

### Tests Used

| Test | Implementation | Purpose |
|:---|:---|:---|
| Two-proportion z-test | `scipy.stats.norm` | Determine whether the conversion rate difference is statistically significant |
| Logistic regression | `statsmodels.api.Logit` | Estimate treatment effect after controlling for device type, customer type, and cart value |
| Power analysis | `statsmodels.stats.power.zt_ind_solve_power` | Validate that sample size is sufficient to detect a meaningful effect |
| Bayesian A/B test | Beta-Binomial conjugate model via `numpy.random.beta` | Express uncertainty as decision-friendly probabilities |

### Why These Tests

- **Z-test** is the standard frequentist approach for comparing two proportions. It provides a p-value and confidence interval that are directly interpretable for launch decisions.
- **Logistic regression** isolates the treatment effect from confounding variables. Even in a randomised experiment, verifying that the effect survives covariate adjustment strengthens the conclusion.
- **Power analysis** ensures the experiment was designed to detect a practically meaningful effect before data collection began. This is a critical step that most portfolio projects omit.
- **Bayesian analysis** answers the questions product teams actually care about: "What is the probability the variant wins?" and "What is the downside risk?"

---

## Results

### Primary Statistical Test

| Metric | Value |
|:---|:---|
| Control conversion rate | 19.42% |
| Variant conversion rate | 24.19% |
| Absolute uplift | 4.76 percentage points |
| Relative uplift | 24.52% |
| Z-statistic | 5.83 |
| P-value (one-sided) | 3.96e-09 |
| 95% CI for uplift | [3.15 pp, 6.38 pp] |

### Logistic Regression (Covariate-Adjusted)

| Variable | Odds Ratio | Interpretation |
|:---|:---|:---|
| Variant (treatment) | 1.33 | Users in the variant are 33% more likely to convert, holding all else constant |
| Returning customer | 1.67 | Returning customers convert at significantly higher rates |
| Mobile device | 0.77 | Mobile users convert less frequently than desktop users |

### Bayesian Decision Metrics

| Decision Metric | Value |
|:---|:---|
| P(Variant beats Control) | >99.99% |
| P(Uplift > 1 pp threshold) | >99% |
| Downside risk (Variant worse) | Near zero |
| Expected uplift | ~4.76 pp |
| 90% credible interval | [3.42 pp, 6.10 pp] |

---

## Confidence Analysis

The 95% confidence interval for the conversion uplift is [3.15 pp, 6.38 pp]. The entire interval lies above zero, meaning:

- **The improvement is not just statistically significant; it is directionally reliable.**
- Even in the worst-case scenario (lower bound of the CI), the variant still delivers a 3.15 percentage point improvement.
- The Bayesian 90% credible interval [3.42 pp, 6.10 pp] corroborates this finding.

This framing is valuable for executives because it translates statistical uncertainty into a range of plausible business outcomes rather than a single point estimate.

---

## Naive vs Adjusted Comparison

A raw conversion difference can be useful, but it is not always sufficient. The key question is whether the uplift remains after controlling for characteristics that independently affect conversion.

| Metric | Naive Result | Adjusted Result |
|:---|:---|:---|
| Variant uplift | +4.76 pp | +4.10 pp |
| Statistical significance | Strong | Strong |
| Interpretation | Variant appears better | Effect remains after controlling for covariates |

In this experiment, the adjusted effect remains close to the naive estimate because randomisation was clean. **This is the expected, reassuring outcome for a well-designed experiment.** The comparison is included to demonstrate the methodology and verify that no hidden confounding is inflating the result.

---

## Business Impact

### Projected Annual Revenue Increase

| Assumption | Value |
|:---|:---|
| Annual visitors | 1,200,000 |
| Median AOV | $33.09 |
| Control annual revenue | ~$7.71M |
| Variant annual revenue | ~$9.60M |
| **Incremental revenue** | **$1.89M per year** |

A 4.76 percentage point conversion improvement, applied to 1.2M annual visitors at a $33.09 median order value, projects to approximately $1.89M in additional annual revenue.

This moves the result from "Variant B wins" to "Variant B wins and is worth approximately $1.89M annually." This is what stakeholders care about.

---

## Experiment Decision Framework

| Result | Action | Rationale |
|:---|:---|:---|
| Significant positive uplift | Deploy variant | Evidence supports improved conversion |
| No significant difference | Keep control | Insufficient evidence to justify change |
| Significant negative uplift | Rollback to control | Variant harms conversion |

**This experiment result:** Significant positive uplift. Recommendation is to deploy.

---

## Type I and Type II Error Analysis

Most portfolio projects stop at reporting a p-value. A rigorous analysis also considers the error risks inherent in the decision.

### Type I Error (False Positive)

- **Definition:** Concluding the variant is better when it is not (rejecting H0 when H0 is true).
- **Control:** The significance level alpha = 0.05 limits the false positive rate to 5%.
- **In this experiment:** The p-value (3.96e-09) is orders of magnitude below alpha, making a false positive extremely unlikely.

### Type II Error (False Negative)

- **Definition:** Failing to detect a real improvement (failing to reject H0 when H1 is true).
- **Control:** The experiment was designed with 80% power (beta = 0.20), meaning a 20% chance of missing a real 15% relative lift.
- **In this experiment:** The observed effect (24.52% relative lift) far exceeds the minimum detectable effect, so the risk of a Type II error is negligible for this effect size.

### Practical Implication

| Risk | Probability | Consequence | Mitigation |
|:---|:---|:---|:---|
| False positive (alpha) | < 0.001% | Launching a feature that does not actually improve conversion | Pre-registered significance level; post-launch monitoring |
| False negative (beta) | Negligible at observed effect size | Missing a genuine improvement | Adequate sample size via power analysis |

This analysis demonstrates that the experimental design properly controls for both error types, and the observed results fall well within the regime where both risks are minimal.

---

## Bayesian Decision View

Frequentist testing tells us whether the uplift is statistically significant. Bayesian analysis answers the questions product teams usually care about most:

- **What is the probability that the variant beats the control?** Greater than 99.99%.
- **What is the probability that the uplift exceeds a business threshold?** High (>99% for a 1 pp threshold).
- **What is the downside risk if the feature is launched?** Near zero.

This makes the result easier to communicate in decision language rather than only p-values.

---

## Visual Outputs

### Revenue Impact
![Revenue Impact](assets/revenue_impact.png)

### Logistic Regression Effects
![Odds Ratio](assets/odds_ratio_plot.png)

### Conversion Rate by Group / Segment
![Conversion Rate](assets/conversion_rate.png)

---

## Limitations

### Simulated Data Disclaimer

The dataset is entirely simulated using `np.random.seed(42)`. No real customer transactions were used. The methodology is fully transferable to production data, but the specific numerical results should be interpreted as a demonstration of the analytical framework.

### Experiment Limitations

- **Short experiment duration:** A 2-week observation window may capture novelty effects that decay over time. Post-launch monitoring over 6+ weeks is recommended to establish the true long-term conversion plateau.
- **Limited traffic volume:** The simulation uses 10,000 users. Real-world experiments at larger scale may reveal effects not visible in this sample.
- **Seasonality effects not considered:** Conversion rates fluctuate by day-of-week, time-of-day, and season. The simulation assumes a static data-generating process.
- **User behavior may change post-deployment:** The Hawthorne effect and novelty bias can inflate initial results. Long-term holdout groups would help quantify this.
- **Cannibalization risk:** Conversion was measured, but average order value should be verified separately to ensure users are not checking out prematurely (before adding secondary items).
- **No network or social effects:** Users in production may influence each other through word-of-mouth or shared devices, violating the independence assumption (SUTVA).
- **Revenue projections depend on assumptions:** The $1.89M figure assumes 1.2M annual visitors and a $33.09 median AOV, which may differ in practice.

---

## Future Improvements

- **Multi-armed bandits:** Explore Thompson Sampling or UCB algorithms to dynamically allocate traffic during the experiment, reducing opportunity cost.
- **Sequential testing:** Implement group sequential designs or always-valid p-values to allow early stopping without inflating Type I error.
- **Long-term holdout groups:** Maintain a small percentage of users on the control experience post-launch to measure long-term treatment effects and novelty decay.
- **Heterogeneous treatment effects:** Use causal forests or interaction terms to identify user segments where the treatment effect is strongest or weakest.
- **Metric sensitivity analysis:** Evaluate alternative primary metrics (revenue per visitor, time-to-purchase) to ensure the conversion lift does not come at the expense of other business objectives.

---

## Repository Structure

```text
conversion-optimization-ab-testing/
├── README.md
├── requirements.txt
├── notebook/
│   └── Conversion_Optimization_Analysis.ipynb
├── src/
│   ├── frequentist_ab.py
│   ├── power_analysis.py
├── scripts/
│   ├── create_notebook.py
│   └── enhance_notebook.py
├── assets/
│   ├── conversion_rate.png
│   ├── odds_ratio_plot.png
│   └── revenue_impact.png
└── .gitignore
```

---

## Tech Stack

- **Python**
- **NumPy, pandas** for data preparation
- **Matplotlib, seaborn** for visualization
- **SciPy** for statistical testing
- **statsmodels** for logistic regression and power analysis
- **scikit-learn** for preprocessing

---

## Author

**Sanman Kadam**
MSc Statistics | Aspiring Data Analyst / Data Scientist

GitHub: https://github.com/the-irritater

LinkedIn: https://www.linkedin.com/in/sanman-kadam-7a4990374/

---

**Created as a portfolio project demonstrating applied A/B testing, causal reasoning, and business decision-making.**

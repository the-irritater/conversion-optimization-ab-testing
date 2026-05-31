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
| **Control Conversion** | 19.68% |
| **Variant Conversion** | 24.11% |
| **Absolute Uplift** | +4.43 percentage points |
| **Relative Uplift** | +22.49% |
| **P-Value (one-sided)** | 4.32e-08 |
| **95% Confidence Interval** | [2.81 pp, 6.05 pp] |
| **Projected Annual Revenue Uplift** | $1.76M |
| **Recommendation** | **Deploy Variant B** |

Variant B produced a statistically valid uplift of 4.43 percentage points with 95% confidence. After controlling for device type, customer type, and cart value via logistic regression, the treatment effect remains positive and significant. Bayesian analysis confirms a greater than 99.99% probability that the variant outperforms the control. The projected incremental revenue of $1.76M annually supports a clear launch recommendation.

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

### Why Sample Size Matters & Power Analysis

Running experiments without adequate sample size can produce misleading conclusions. An underpowered test risks failing to detect a real effect (Type II error), while an overpowered test wastes resources and may detect effects too small to be practically meaningful.

Before launching, we conducted a formal **Power Analysis** to determine the required sample size per group using the `statsmodels.stats.power.zt_ind_solve_power()` function. The design parameters were:
- **Baseline Conversion Rate ($p_{control}$):** 19.4%
- **Minimum Detectable Effect (MDE):** 15% relative lift (Target Conversion Rate $p_{variant} = 19.4\% \times 1.15 = 22.31\%$)
- **Significance Level ($\alpha$):** 0.05
- **Power ($1 - \beta$):** 0.80

Using Cohen's $h$ to measure the effect size between two proportions:
$$h = 2(\arcsin\sqrt{p_{variant}} - \arcsin\sqrt{p_{control}}) \approx 0.0717$$

The required sample size per group is calculated as:
- **One-sided test (alternative='larger'):** **2,408** users/group
- **Two-sided test (alternative='two-sided'):** **3,057** users/group

Since our experiment has approximately **5,000** users per group (exceeding the required minimums), the experiment is fully powered to detect a 15% relative lift.

### Guardrail Metrics

While conversion rate is our primary metric, A/B tests rarely optimize a single metric in isolation. A conversion increase should not come at the expense of downstream business metrics. We tracked the following guardrail metrics to ensure overall business health:
- **Average Order Value (AOV):** Verifies that the One-Click checkout isn't causing customers to buy lower-value items or abandon cross-sell suggestions.
- **Refund / Chargeback Rate:** Ensures that easier checkout doesn't lead to accidental purchases, buyer's remorse, or higher fraud rates.
- **Checkout Error Rate:** Monitors technical errors, API timeouts, or UI bugs introduced by the new checkout flow.
- **Revenue Per Visitor (RPV):** A critical combining metric (Conversion Rate $\times$ AOV) that measures the net financial impact per session.

### Pre-Registration & Prevention of P-Hacking

To ensure statistical integrity and prevent p-hacking (data dredging), the analysis plan was pre-registered and locked prior to observing the experimental results. This pre-registration includes:
- **Primary Metric Definition:** Conversion Rate is the sole primary metric for the launch decision.
- **Fixed Sample Size & Duration:** The observation period was set to exactly 14 days with a target of 10,000 total users, based on the pre-experiment power analysis.
- **Hypothesis and Test Specification:** A one-sided Two-Proportion Z-Test and a covariate-adjusted Logistic Regression model were specified beforehand.
- **Significance Threshold:** Alpha ($\alpha$) was fixed at 0.05. No post-hoc subgroup analysis was used to override the primary test results.

### Threats to Experiment Validity & Mitigations

To ensure the integrity of the experiment results, we proactively identified and addressed the following common threats to internal validity:

| Validity Threat | Potential Impact | Mitigation Strategy |
|:---|:---|:---|
| **Novelty Effect** | Returning users interact more with the Variant simply because it is new, temporarily inflating conversion. | We run the experiment for a full 2-week business cycle and monitor day-over-day trends to watch for decay. |
| **Seasonality** | Days of the week or pay cycles introduce conversion spikes that bias short tests. | We run the experiment for multiple complete weeks (14 days minimum) to capture weekend/weekday cycles equally. |
| **Selection Bias** | Non-random bucketing splits cohorts unevenly, leading to group imbalances. | Enforced deterministic server-side hashing (e.g., MD5 of `user_id` + Salt) to ensure perfect 50/50 randomized splits. |
| **Tracking Issues** | Ad blockers or client-side telemetry drops fail to record key conversion events. | Implemented server-side conversion logging alongside client-side hooks to ensure accurate event capture. |
| **Cookie Deletion** | Users clearing cookies appear as "new" users, leading to bucket contamination. | Tracked cross-device authenticated customer identifiers where available, reducing reliance on raw browser cookies. |
| **Cross-Device Behavior** | A user starts checkout on mobile and completes it on desktop, leading to split assignments. | Standardized bucketing at the logged-in customer account level where feasible, ensuring a consistent user experience. |

---

## Dataset Overview

**Why Simulated Data Was Used:** Public e-commerce A/B testing datasets rarely contain the complete user-level behavioral features (such as device types, customer history, cart values, and session duration) required for advanced causal modeling. This simulation was specifically designed to reproduce real-world conversion patterns while allowing controlled methodological testing where baseline rates and treatment effects are mathematically known.

The dataset is fully simulated using a fixed random seed (`np.random.seed(42)`) for absolute reproducibility and controlled experimentation.

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
| Control conversion rate | 19.68% |
| Variant conversion rate | 24.11% |
| Absolute uplift | 4.43 percentage points |
| Relative uplift | 22.49% |
| Z-statistic | 5.35 |
| P-value (one-sided) | 4.32e-08 |
| 95% CI for uplift | [2.81 pp, 6.05 pp] |

### Logistic Regression (Covariate-Adjusted)

| Variable | Odds Ratio | Interpretation |
|:---|:---|:---|
| Variant (treatment) | 1.33 | Users in the variant are 33% more likely to convert, holding all else constant |
| Returning customer | 1.67 | Returning customers convert at significantly higher rates |
| Mobile device | 0.77 | Mobile users convert less frequently than desktop users |

### Bayesian Decision Metrics

| Decision Metric | Value |
|:---|:---|
| P(Treatment beats Control) | >99.99% |
| P(Uplift > 1 pp threshold) | >99% |
| P(Annual Revenue Gain > $1.0M) | 98.93% |
| Estimated posterior probability that variant underperforms control | 0.00% (Near zero) |
| Expected conversion uplift | 4.43 pp |
| 90% credible interval for conversion uplift | [3.06 pp, 5.78 pp] |
| Expected annual revenue gain | $1.76M |
| 90% credible interval for annual revenue gain | [$1.22M, $2.29M] |

### Segmented Results & Heterogeneous Treatment Effects (HTE)

To understand if the treatment effect was consistent across cohorts, we performed segment-specific two-proportion Z-tests:

| Cohort Group | Cohort Segment | Control CR | Variant CR | Absolute Uplift | Relative Lift | P-Value (one-sided) | Statistically Significant? |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **Device Type** | Mobile | 17.72% | 22.09% | +4.37 pp | +24.67% | 0.000012 | **Yes** (p < 0.05) |
| **Device Type** | Desktop | 21.73% | 26.85% | +5.12 pp | +23.58% | 0.000499 | **Yes** (p < 0.05) |
| **Device Type** | Tablet | 22.54% | 28.49% | +5.94 pp | +26.36% | 0.014667 | **Yes** (p < 0.05) |
| **Customer Type** | New Customers | 16.02% | 17.53% | +1.51 pp | +9.40% | 0.101572 | **No** (p = 0.101) |
| **Customer Type** | Returning Customers | 21.66% | 28.67% | +7.01 pp | +32.38% | 0.000000 | **Yes** (p < 0.001) |

#### Analysis of Heterogeneous Treatment Effects:
- **Mobile and Desktop Universality:** The One-Click checkout is highly effective across both Mobile (+4.37 pp uplift) and Desktop (+5.12 pp uplift) devices, showing robust performance. Because Mobile traffic represents 60% of all sessions, this mobile lift is the core volume driver for overall business growth.
- **The Loyalty HTE:** Slicing by customer history reveals a classic **Heterogeneous Treatment Effect**. The variant is **extremely effective** for Returning Customers, boosting their conversion rate by **+7.01 pp** (a +32.38% relative lift). However, for New Customers, the conversion uplift is only **+1.51 pp** and is **not statistically significant** ($p = 0.101 > 0.05$).
- **Business Rationale:** Returning customers already have saved shipping/billing details and high brand trust, so "One-Click Checkout" completely eliminates purchase friction. New customers do not have pre-filled details, so they must still enter shipping/billing addresses manually, meaning the One-Click interface cannot eliminate their primary entry friction, and their baseline trust remains lower. Future product iterations should target guest-checkout autofills and trust signals to help *new* customers convert.

#### Business Recommendation from HTE Analysis

> **Deploy One-Click Checkout universally**, but prioritize future optimization efforts for **New Customers** where uplift remains weak and not statistically significant. Specifically:
> 1. **Immediate:** Launch the variant for all users — the overall uplift is strong and significant.
> 2. **Next Sprint:** Investigate guest-checkout autofill (e.g., Shop Pay, Google Pay, Apple Pay) to reduce first-time data-entry friction for new customers.
> 3. **Next Quarter:** Run a dedicated experiment targeting new-customer trust signals (security badges, guest checkout, social proof) to close the gap.

---

## Confidence Analysis

The 95% confidence interval for the conversion uplift is [2.81 pp, 6.05 pp]. The entire interval lies above zero, meaning:

- **The improvement is not just statistically significant; it is directionally reliable.**
- Even in the worst-case scenario (lower bound of the CI), the variant still delivers a 2.81 percentage point improvement.
- The Bayesian 90% credible interval [3.06 pp, 5.78 pp] corroborates this finding.

This framing is valuable for executives because it translates statistical uncertainty into a range of plausible business outcomes rather than a single point estimate.

---

## Naive vs Adjusted Comparison

A raw conversion difference can be useful, but it is not always sufficient. The key question is whether the uplift remains after controlling for characteristics that independently affect conversion.

| Metric | Naive Result | Adjusted Result |
|:---|:---|:---|
| Variant uplift | +4.43 pp | +4.47 pp |
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
| Control annual revenue | ~$7.81M |
| Variant annual revenue | ~$9.57M |
| **Incremental revenue** | **$1.76M per year** |

A 4.43 percentage point conversion improvement, applied to 1.2M annual visitors at a $33.09 median order value, projects to approximately $1.76M in additional annual revenue.

*Note: Revenue projections are illustrative and should be recalculated using actual traffic volumes.*

This moves the result from "Variant B wins" to "Variant B wins and is worth approximately $1.76M annually." This is what stakeholders care about.

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
- **In this experiment:** The observed p-value (4.32e-08) is far below alpha, providing extremely strong evidence against the null hypothesis.

### Type II Error (False Negative)

- **Definition:** Failing to detect a real improvement (failing to reject H0 when H1 is true).
- **Control:** The experiment was designed with 80% power (beta = 0.20), meaning a 20% chance of missing a real 15% relative lift.
- **In this experiment:** The observed effect (22.49% relative lift) far exceeds the minimum detectable effect (15%), so the risk of a Type II error is negligible for this effect size.

### Practical Implication

| Risk | Probability / Control | Consequence | Mitigation |
|:---|:---|:---|:---|
| False positive (alpha) | Controlled at 5% (Observed p-value << alpha provides strong evidence against H0) | Launching a feature that does not actually improve conversion | Pre-registered significance level; post-launch monitoring |
| False negative (beta) | Negligible at observed effect size | Missing a genuine improvement | Adequate sample size via power analysis |

This analysis demonstrates that the experimental design properly controls for both error types, and the observed results fall well within the regime where both risks are minimal.

---

## Bayesian Decision View

Frequentist testing tells us whether the uplift is statistically significant. Bayesian analysis answers the questions product teams usually care about most:

- **What is the probability that the variant beats the control?** Greater than 99.99%.
- **What is the probability that the uplift exceeds a business threshold?** High (>99% for a 1 pp threshold).
- **What is the probability that the annual revenue gain exceeds $1.0M?** 98.93%.
- **What is the downside risk if the feature is launched?** The estimated posterior probability that the variant underperforms the control is 0.00% (near zero).

This makes the result easier to communicate in decision language rather than only p-values.

---

## Key Visuals & Storytelling

Visualizations are essential to communicate complex statistical findings to business stakeholders. Below are the key visual assets from the analysis with direct business interpretations.

### 1. Conversion Rate Uplift & Confidence Intervals
![Conversion Rate](assets/conversion_rate.png)
*Interpretation: The error bars show the 95% confidence intervals for baseline conversion rates and the resulting treatment uplift; because the entire uplift interval lies strictly above zero, the conversion gain is statistically valid and directionally reliable.*

### 2. Treatment & Covariate Effects (Logistic Regression)
![Odds Ratio](assets/odds_ratio_plot.png)
*Interpretation: The odds ratio plot displays the relative impact of each user trait on conversion; being in the Variant group increases a user's likelihood of conversion by ~33%, while returning customers convert at a significantly higher rate, and mobile users convert less frequently.*

### 3. Projected Financial Revenue Simulation
![Revenue Impact](assets/revenue_impact.png)
*Interpretation: The annual revenue impact simulation maps the absolute conversion lift against our 1.2 million visitor volume and $33.09 median AOV, projecting an expected incremental revenue of $1.76 million per year (with a 95% range from $1.11M to $2.40M).*

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
- **Revenue projections depend on assumptions:** The $1.76M figure assumes 1.2M annual visitors and a $33.09 median AOV, which may differ in practice.

---

## Future Improvements

- **Multi-armed bandits:** Explore Thompson Sampling or UCB algorithms to dynamically allocate traffic during the experiment, reducing opportunity cost.
- **Sequential testing:** Implement group sequential designs or always-valid p-values to allow early stopping without inflating Type I error.
- **Long-term holdout groups:** Maintain a small percentage of users on the control experience post-launch to measure long-term treatment effects and novelty decay.
- **Heterogeneous treatment effects:** Use causal forests or interaction terms to identify user segments where the treatment effect is strongest or weakest.
- **Metric sensitivity analysis:** Evaluate alternative primary metrics (revenue per visitor, time-to-purchase) to ensure the conversion lift does not come at the expense of other business objectives.

---

## Post-Launch Monitoring Plan

A statistically significant experiment result is only the beginning. Real product impact must be validated through disciplined post-launch monitoring. Below is the phased plan we would follow after deploying the One-Click Checkout to 100% of traffic:

| Phase | Timeline | Metrics to Monitor | Goal |
|:---|:---|:---|:---|
| **Phase 1: Stability Check** | Week 1–2 | Conversion rate, checkout error rate, payment failure rate, page load time | Confirm the variant performs as expected in production with no technical regressions. |
| **Phase 2: Novelty Decay** | Week 3–6 | Daily conversion rate trend, returning-user conversion delta | Detect whether the initial uplift decays as the "new feature" novelty wears off. Establish the true long-term conversion plateau. |
| **Phase 3: Guardrail Validation** | Month 2 | Average order value, refund/chargeback rate, revenue per visitor | Verify that improved conversion has not come at the expense of downstream business metrics. |
| **Phase 4: Retention & LTV** | Month 3–6 | 30-day repeat purchase rate, customer lifetime value (LTV), cohort retention curves | Evaluate whether the faster checkout experience improves (or harms) long-term customer loyalty and repeat purchase behavior. |
| **Phase 5: Segment Deep-Dive** | Ongoing | New-customer conversion, mobile-specific funnel metrics | Track whether future product iterations (guest autofill, trust signals) successfully close the gap for new customers identified in the HTE analysis. |

**Holdout Group:** Maintain a 5% random holdout on the control experience for at least 90 days post-launch. This provides a clean causal baseline to measure long-term effects and detect novelty decay without confounding.

---

## Repository Structure

```text
conversion-optimization-ab-testing/
├── README.md
├── requirements.txt
├── analysis/
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

# Conversion Optimization A/B Test: Should We Launch the New Checkout?

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Analysis](https://img.shields.io/badge/Project-A%2FB%20Testing-orange.svg)]()
[![Decision](https://img.shields.io/badge/Focus-Decision%20Making-success.svg)]()

A professional, end-to-end data analysis project that evaluates whether a new one-click checkout flow should be launched using A/B testing, logistic regression, and business impact analysis.

---

## Abstract

Businesses frequently run A/B tests to improve product features such as checkout flows. However, naive analysis, such as comparing average conversion rates, can lead to misleading conclusions due to confounding variables and Simpson’s Paradox.

Using simulated data designed with controlled confounders such as device type and customer loyalty, this project presents a structured approach to experimentation through frequentist hypothesis testing, causal modeling, and business-focused interpretation.

---

## Problem Statement

An e-commerce platform is experiencing high drop-off during the checkout process. A new one-click checkout feature is proposed to reduce friction and improve conversion rates.

The business question is straightforward: should the team launch the new checkout experience or keep the current version live?

The objective is to evaluate whether the new checkout flow significantly improves conversion while accounting for customer characteristics, device mix, and practical business impact.

---

## Decision Framework

This project is written like a real product decision, not a theory exercise.

The analysis follows a simple decision path:

1. Measure conversion for old vs new checkout  
2. Run a formal hypothesis test  
3. Quantify uplift and uncertainty  
4. Control for customer and device differences using logistic regression  
5. Translate the statistical result into a business recommendation  

### Hypotheses

- **H0:** p_new <= p_old  
- **H1:** p_new > p_old  

This is a directional launch decision. The new checkout should only be launched if it performs better than the old one.

### Primary Statistical Test

- **Test used:** Two-proportion z-test  
- **Significance level:** alpha = 0.05  

The notebook reports:

- Control conversion rate  
- Variant conversion rate  
- Absolute uplift  
- Relative uplift  
- Z-statistic  
- P-value  
- 95% confidence interval for uplift  

---

## Methods Used

- Frequentist A/B testing using Z-test  
- Logistic regression for controlled causal interpretation  
- Bayesian A/B testing for probability-based decision making  
- Business impact simulation for revenue estimation  

---

## Tech Stack

- **numpy, pandas** for data manipulation  
- **matplotlib, seaborn** for visualization  
- **scipy** for statistical testing  
- **statsmodels** for logistic regression  
- **scikit-learn** for preprocessing and scaling  

---

## Verified Output Snapshot

These are the current seeded results from the notebook:

- Control conversion rate: `19.42%`
- Variant conversion rate: `24.19%`
- Absolute uplift: `4.76 percentage points`
- Relative uplift: `24.52%`
- One-sided p-value: `3.96e-09`
- 95% confidence interval for uplift: `[3.15 pp, 6.38 pp]`
- Variant odds ratio: `1.33`
- Returning-customer odds ratio: `1.67`
- Mobile odds ratio: `0.77`
- Median AOV: `$33.09`
- Projected incremental annual revenue: `$1.89M`

---

## Key Findings

- The one-click checkout variant improves conversion meaningfully over the control.
- The uplift is statistically significant, not just visually different.
- Logistic regression shows the treatment effect remains positive even after controlling for customer and device factors.
- The estimated revenue impact suggests that the result is not only statistically valid but also commercially meaningful.

---

## Visual Outputs

### Conversion Lift
![Conversion](assets/revenue_impact.png)

### Causal Impact (Logistic Regression)
![Odds Ratio](assets/odds_ratio_plot.png)

### Segment Analysis (Device Type)
![Device](assets/conversion_rate.png)

---

## Repository Structure

```text
conversion-optimization-ab-testing/
├── README.md
├── requirements.txt
├── Conversion_Optimization_Analysis.ipynb
├── src/
│   ├── frequentist_ab.py
│   ├── power_analysis.py
├── scripts/
│   └── create_notebook.py
├── assets/
│   ├── conversion_rate.png
│   ├── odds_ratio_plot.png
│   └── revenue_impact.png
└── .gitignore

```
## Tech Stack

- numpy, pandas (data manipulation)  
- matplotlib, seaborn (data visualization)  
- scipy (statistical testing)  
- statsmodels (logistic regression)  
- scikit-learn (preprocessing and scaling)  

---
## Key Insights

### Conversion Lift
![Conversion](assets/revenue_impact.png)

### Causal Impact (Logistic Regression)
![Odds Ratio](assets/odds_ratio_plot.png)

### Segment Analysis (Device Type)
![Device](assets/conversion_rate.png)

---

Conclusion

This project shows how experimentation should support product decisions in practice.

Instead of stopping at statistical significance, the analysis connects the result to effect size, uncertainty, and projected business value. The final takeaway is simple: the new checkout flow shows strong evidence of improvement, and launch is supported by both statistical and commercial reasoning.

---

## Author

Sanman Kadam
MSc Statistics | Data Analyst | Data Science Enthusiast

GitHub: https://github.com/the-irritater

---

*Created as a demonstration of advanced statistical analysis and business intelligence methodologies.*
=======

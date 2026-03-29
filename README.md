# E-Commerce Conversion Optimization: Causal A/B Testing Framework

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Data Science](https://img.shields.io/badge/Data%20Science-A%2FB%20Testing-orange.svg)]()
[![Causal Inference](https://img.shields.io/badge/Method-Causal%20Inference-success.svg)]()

A professional, end-to-end data analysis project demonstrating the lifecycle of an E-Commerce A/B experiment using statistical and causal inference techniques.

---

## Author
**Sanman Kadam**

---

## Abstract

Businesses frequently run A/B tests to improve product features such as checkout flows. However, naive analysis, such as comparing average conversion rates, can lead to misleading conclusions due to confounding variables and Simpson’s Paradox.

Using simulated data designed with controlled confounders (device type and customer loyalty), this project presents a structured approach to experimentation:

- Frequentist hypothesis testing (Z-Test)  
- Logistic regression for causal inference  
- Bayesian A/B testing for probability-based decision making  
- Business impact simulation for revenue estimation  

---

## Problem Statement

An e-commerce platform is experiencing high drop-off during the checkout process. A new “one-click checkout” feature is proposed to reduce friction and improve conversion rates.

The objective is to evaluate whether the new checkout flow significantly improves conversion while controlling for user behavior, device type, and customer characteristics.

---

## Repository Structure

```text
conversion-optimization-ab-testing/
│
├── README.md
├── requirements.txt
├── Conversion_Optimization_Analysis.ipynb
│
├── src/
│   ├── frequentist_ab.py
│   ├── power_analysis.py
│
├── scripts/
│   └── create_notebook.py
│
├── assets/
│   ├── conversion_rate.png
│   ├── odds_ratio_plot.png
│   └── device_conversion.png
│
└── .gitignore

```
## Tech Stack

- numpy, pandas (data manipulation)  
- matplotlib, seaborn (data visualization)  
- scipy (statistical testing)  
- statsmodels (logistic regression)  
- scikit-learn (preprocessing and scaling)  

---

## How to Run the Analysis

### Clone the repository
```bash
git clone https://github.com/the-irritater/conversion-optimization-ab-testing.git
cd conversion-optimization-ab-testing
```
---

**Explore the Notebook:** Open Conversion_Optimization_Analysis.ipynb using Jupyter Notebook, JupyterLab, or Visual Studio Code. 
Be sure to click **"Run All"** to execute the cells and view the saved visualizations and outputs. 
*(Note: The notebook can be cleanly re-generated from scratch locally at any time by running python create_notebook.py)* 

## Key Findings 
**Treatment Effect:** The "One-Click Checkout" variant successfully created an 18% relative uplift in conversion rate. *
**Causal Significance:** Even holding user demographics entirely constant, the variant reliably improves conversion odds by ~25% (O.R = ~1.25). * 
**Bayesian Outcome:** There is a nearly 100% probability that the variant outperforms the control, with almost zero expected loss. * 
**Business Value:** Projected $2.4M in annualized incremental revenue upon 100% rollout.*

---
## 📊 Key Insights

### Conversion Lift
![Conversion](assets/conversion_rate.png)

### Causal Impact (Logistic Regression)
![Odds Ratio](assets/odds_ratio_plot.png)

### Segment Analysis (Device Type)
![Device](assets/revenue_impact.png)

---

Conclusion

The analysis demonstrates that the proposed one-click checkout flow has a statistically significant and practically meaningful impact on conversion rates.

By combining traditional hypothesis testing with causal inference and Bayesian methods, this project highlights how data-driven experimentation can support confident business decision-making.

---

*Created as a demonstration of advanced statistical analysis and business intelligence methodologies.*

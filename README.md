# E-Commerce Conversion Optimization: Causal A/B Testing Framework

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Data Science](https://img.shields.io/badge/Data%20Science-A%2FB%20Testing-orange.svg)]()
[![Causal Inference](https://img.shields.io/badge/Method-Causal%20Inference-success.svg)]()

A professional, end-to-end data analysis portfolio project demonstrating the entire lifecycle of an **E-Commerce A/B Experiment** using rigorous statistical methods.

---

## Author
**Sanman Kadam**

---
## Abstract

Businesses frequently run A/B tests to improve product features (like checkout flows). However, naive analyses (like simply looking at average conversion rates) can lead to highly skewed conclusions due to confounding variables and Simpson's Paradox. 

Using **Simulated Data** specifically engineered with hidden confounders (device type, user loyalty), this project goes beyond standard testing by walking through:
1. **Frequentist Hypothesis Testing (Z-Test)** for baseline conversion lift.
2. **Causal Inference (Logistic Regression)** to isolate the Average Treatment Effect (ATE) while strictly controlling for confounders.
3. **Bayesian A/B Testing** using a Beta-Binomial model to determine the exact *Probability of Superiority* and *Expected Loss*, making the results highly interpretable for business stakeholders.
4. **Business Impact Simulation**, projecting statistical findings into annualized revenue metrics.

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

## 🛠️ Tech Stack & Requirements

The analysis relies on standard Python data science libraries:
- `numpy` & `pandas` (Data Manipulation)
- `matplotlib` & `seaborn` (Data Visualization)
- `scipy` (Frequentist and Bayesian Statistical computations)
- `statsmodels` (Logistic Regression Analysis)
- `scikit-learn` (Data scaling & preprocessing)

## How to Run the Analysis

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd causal-ab-testing-framework
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Explore the Notebook:**
   Open `Conversion_Optimization_Analysis.ipynb` using Jupyter Notebook, JupyterLab, or Visual Studio Code. Be sure to click **"Run All"** to execute the cells and view the saved visualizations and outputs.

   *(Note: The notebook can be cleanly re-generated from scratch locally at any time by running `python create_notebook.py`)*

## Key Findings
* **Treatment Effect:** The "One-Click Checkout" variant successfully created an 18% relative uplift in conversion rate.
* **Causal Significance:** Even holding user demographics entirely constant, the variant reliably improves conversion odds by ~25% (O.R = ~1.25).
* **Bayesian Outcome:** There is a nearly 100% probability that the variant outperforms the control, with almost zero expected loss.
* **Business Value:** Projected $2.4M in annualized incremental revenue upon 100% rollout.

---
*Created as a demonstration of advanced statistical analysis and business intelligence methodologies.*

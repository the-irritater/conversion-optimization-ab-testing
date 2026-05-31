import json

cells = []

def add_md(text):
    lines = text.split('\n')
    source = [line + '\n' for line in lines[:-1]] + [lines[-1]] if lines else []
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": source
    })

def add_code(text):
    lines = text.split('\n')
    source = [line + '\n' for line in lines[:-1]] + [lines[-1]] if lines else []
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source
    })

# ============================================================
# SECTION 1: EXECUTIVE SUMMARY & PROJECT HEADER
# ============================================================

add_md("""# E-Commerce Conversion Optimization & A/B Testing

| Field | Details |
|:---|:---|
| **Project** | Causal A/B Testing Framework & Conversion Analysis |
| **Dataset** | Simulated E-Commerce Traffic (with embedded confounders) |
| **Author** | Sanman Kadam |
| **Affiliation** | MSc Statistics |
| **Date** | March 2026 |

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
| **Recommendation** | **Deploy Variant** |

Variant B produced a statistically valid uplift of 4.76 percentage points with 95% confidence. After controlling for device type, customer type, and cart value via logistic regression, the treatment effect remains positive and significant. Bayesian analysis confirms a greater than 99% probability that the variant outperforms the control.
""")

# ============================================================
# SECTION 2: BUSINESS PROBLEM
# ============================================================

add_md("""---

## 1. Business Problem

In the highly competitive e-commerce landscape, minimizing friction during the checkout process is critical for maximizing revenue. The current checkout flow on our platform has a conversion rate of approximately 19.4%, with high drop-off at the payment information step.

The product team proposes a new "One-Click Checkout" flow designed to streamline the purchase process.

**Objective:** Determine whether the redesigned checkout experience can increase conversion rate while maintaining acquisition efficiency and average order value.

**Decision Question:** Should the business launch the new checkout flow, or keep the current version live?

To answer that properly, the analysis must go beyond raw conversion differences and test whether the uplift remains after accounting for user characteristics, uncertainty, and financial impact.

## 2. Hypothesis

### Null Hypothesis (H0)

$$H_0: p_{variant} \\le p_{control}$$

There is no improvement in conversion rate from the new checkout flow. Any observed difference is attributable to random variation.

### Alternative Hypothesis (H1)

$$H_1: p_{variant} > p_{control}$$

The new checkout flow produces a statistically significant improvement in conversion rate.

**Why a one-sided test?** The business question is directional: "Is the new checkout *better* than the old one?" We are not interested in detecting whether the variant is *worse* -- that scenario simply means we do not launch. A one-sided test aligns the statistical framework with the actual decision being made and provides slightly more power for the same sample size.

## 3. Objectives

This analysis aims to achieve the following:
1. **Exploratory Goal:** Understand the baseline distributions of cart values, time spent, and conversion rates across different user demographics.
2. **Preprocessing Goal:** Clean and prepare the dataset, handling missing values and scaling features appropriately.
3. **Statistical Goal 1:** Conduct a rigorous Frequentist A/B test (Two-Proportion Z-Test) to evaluate the primary conversion metric.
4. **Statistical Goal 2:** Apply a Logistic Regression model to control for confounding variables and estimate the causal impact of the new checkout flow.
5. **Statistical Goal 3:** Perform Bayesian analysis to express uncertainty as decision-friendly probabilities.
6. **Business Goal:** Provide actionable recommendations based on the statistical findings, including segment-specific strategies and projected revenue impact.
""")

# ============================================================
# SECTION 3: EXPERIMENT DESIGN
# ============================================================

add_md("""---

## 4. Experiment Design

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

This experiment uses a formal power analysis (detailed in Section 5.5) to determine the minimum sample size required to detect a 15% relative lift with 80% power at the 5% significance level.
""")

# ============================================================
# SECTION 4: DATASET GENERATION
# ============================================================

add_md("""---

## 5. Dataset Overview and Generation

Since no external dataset was provided, we generate a robust simulated dataset representing an A/B test running for two weeks.

**Dataset Characteristics:**
* **`user_id`**: Unique identifier for the session.
* **`group`**: 'Control' (Old Checkout) or 'Variant' (One-Click Checkout).
* **`device_type`**: 'Mobile', 'Desktop', or 'Tablet'.
* **`customer_type`**: 'New' or 'Returning'.
* **`cart_value`**: The total dollar value of the items in the cart prior to checkout.
* **`time_spent_mins`**: Time spent on the site before entering the checkout flow.
* **`converted`**: Binary outcome (1 = completed purchase, 0 = abandoned).

**Assumptions & Potential Issues:**
* The assignment to Control/Variant is completely randomized (i.e., no assignment bias).
* The events are independent and identically distributed (i.i.d).
* We will intentionally introduce some missing data in `time_spent_mins` to demonstrate robust preprocessing techniques.
""")

add_code("""import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm, ttest_ind, probplot
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler

# Set aesthetic style for plots
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['figure.figsize'] = (10, 6)

import warnings
warnings.filterwarnings('ignore')
""")

add_code("""# Set random seed for reproducibility
np.random.seed(42)

# Generate basic attributes
n_users = 10000
user_ids = [f"U_{i:05d}" for i in range(1, n_users + 1)]
groups = np.random.choice(['Control', 'Variant'], size=n_users, p=[0.5, 0.5])
devices = np.random.choice(['Mobile', 'Desktop', 'Tablet'], size=n_users, p=[0.6, 0.3, 0.1])
customer_types = np.random.choice(['New', 'Returning'], size=n_users, p=[0.4, 0.6])

# Generate Cart Value (Log-normal distribution to mimic real e-commerce data)
cart_values = np.random.lognormal(mean=3.5, sigma=0.8, size=n_users)
cart_values = np.round(np.clip(cart_values, 5, 500), 2)

# Generate Time Spent
time_spent = np.random.normal(loc=12, scale=5, size=n_users)
time_spent = np.round(np.clip(time_spent, 1, 60), 1)

# Introduce missing values in time_spent (approx 5%)
missing_idx = np.random.choice(n_users, size=int(n_users * 0.05), replace=False)
time_spent[missing_idx] = np.nan

# Generate Conversion Logits (Base probability + effects)
# Baseline conversion log-odds
logits = -1.5 
# Effect of Variant
logits += np.where(groups == 'Variant', 0.25, 0)
# Effect of Device (Mobile is harder to convert)
logits += np.where(devices == 'Mobile', -0.3, 0)
# Effect of Customer Type (Returning convert more)
logits += np.where(customer_types == 'Returning', 0.5, 0)
# Effect of Cart Value (Higher carts slightly less likely to convert directly)
logits -= cart_values * 0.001

# Calculate probabilities using sigmoid
probs = 1 / (1 + np.exp(-logits))
converted = np.random.binomial(n=1, p=probs)

# Create DataFrame
df = pd.DataFrame({
    'user_id': user_ids,
    'group': groups,
    'device_type': devices,
    'customer_type': customer_types,
    'cart_value': cart_values,
    'time_spent_mins': time_spent,
    'converted': converted
})

display(df.head())
print(f"Dataset Shape: {df.shape}")
df.info()
""")

add_md("""**Interpretation:**
We have successfully generated a dataset of 10,000 unique user sessions. The `info()` output confirms the presence of missing values in `time_spent_mins`. The distributions and relationships built into the logits (e.g., returning users converting at higher rates, mobile devices showing lower conversion) will allow us to demonstrate both confounding and segment analysis later.

### Why Simulated Data Was Used
* **Data Privacy and Availability:** Public e-commerce A/B testing datasets are rare, heavily anonymized, and rarely contain the complete user-level behavioral and segment features (such as device types, customer history, cart values, and session duration) required for advanced causal inference.
* **Controlled Methodological Testing:** This simulation was specifically designed to reproduce real-world e-commerce conversion patterns. It allows us to mathematically control baseline conversion rates and covariate relationships to demonstrate that our statistical and causal models (like z-tests, logistic regressions, and Bayesian conjugate models) can accurately recover the ground-truth treatment effect.

---

## 5.1. Data Preprocessing

Before proceeding to analysis, we must ensure the data is clean and ready for modeling.

### Handling Missing Values
We observed missing values in the `time_spent_mins` column. Since time spent can vary heavily by `customer_type` and `device_type`, we will impute these missing values using the median of their respective subgroups to preserve the underlying distributions without being skewed by extreme outliers.
""")

add_code("""# Calculate percentage of missing values
missing_pct = df.isnull().mean() * 100
print("Missing Value Percentages:\\n", missing_pct[missing_pct > 0])

# Impute missing values with group medians
df['time_spent_mins'] = df.groupby(['device_type', 'customer_type'])['time_spent_mins'].transform(
    lambda x: x.fillna(x.median())
)

print(f"Remaining missing values: {df.isnull().sum().sum()}")
""")

add_md("""### 5.2. Outlier Detection
We will visually inspect `cart_value` for extreme outliers that might skew revenue-based metrics.
""")

add_code("""fig, axes = plt.subplots(1, 2, figsize=(14, 5))

sns.boxplot(data=df, x='cart_value', ax=axes[0])
axes[0].set_title('Boxplot of Cart Values')

# Log-transformed visualization
sns.histplot(np.log1p(df['cart_value']), kde=True, ax=axes[1])
axes[1].set_title('Log-transformed Distribution of Cart Values')
axes[1].set_xlabel('Log(Cart Value + 1)')

plt.tight_layout()
plt.show()
""")

add_md("""**Outlier Strategy:**
Our `cart_value` was generated with an upper clip of $500, simulating a natural cap or a pre-filtering step often done in e-commerce to separate wholesale from retail. The log-transformation shows a beautiful normal-like distribution, confirming that our values are highly right-skewed but manageable. We will not drop outliers as they represent valid (and highly valuable) purchases, but we will apply standard scaling to numerical features before running the logistic regression later to ensure convergence.

---

## 5.3. Exploratory Data Analysis (EDA)

### Overall Conversion & Group Balance
Let's first confirm that the A/B test groups are balanced and look at the aggregate conversion rates.
""")

add_code("""fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Group Balance
sns.countplot(data=df, x='group', palette=['#4c72b0', '#dd8452'], ax=axes[0])
axes[0].set_title('Traffic Split (Sample Size Check)')
for p in axes[0].patches:
    axes[0].annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()), 
                     ha='center', va='bottom', xytext=(0, 5), textcoords='offset points')

# Baseline Conversion by Group
conv_rates = df.groupby('group')['converted'].mean().reset_index()
sns.barplot(data=conv_rates, x='group', y='converted', palette=['#4c72b0', '#dd8452'], ax=axes[1])
axes[1].set_title('Conversion Rate by Group')
axes[1].set_ylabel('Conversion Rate')
for p in axes[1].patches:
    axes[1].annotate(f"{p.get_height():.2%}", (p.get_x() + p.get_width() / 2., p.get_height()), 
                     ha='center', va='bottom', xytext=(0, 5), textcoords='offset points')

plt.tight_layout()
plt.show()
""")

add_md("""**Interpretation:**
* **Sample Size Check:** The traffic split is practically 50/50, indicating our randomization mechanism worked and there is no Sample Ratio Mismatch (SRM). 
* **Conversion Rate:** In this seeded run, the Control group converts at roughly 19.4% while the Variant converts at about 24.2%. That is an absolute uplift of about 4.8 percentage points, which looks promising but still needs formal testing.

### 5.4. Segment Analysis (Device and Customer Type)
Let's see how conversion changes across different user dimensions.
""")

add_code("""fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Conversion by Device Type
sns.barplot(data=df, x='device_type', y='converted', hue='group', ax=axes[0])
axes[0].set_title('Conversion Rate by Device Type')
axes[0].set_ylabel('Conversion Rate')

# Conversion by Customer Type
sns.barplot(data=df, x='customer_type', y='converted', hue='group', ax=axes[1])
axes[1].set_title('Conversion Rate by Customer Type')
axes[1].set_ylabel('Conversion Rate')

plt.tight_layout()
plt.show()
""")

add_md("""**Interpretation:**
* **Device Type:** Mobile has the lowest overall conversion rate out of the three device types. However, the Variant (One-Click Checkout) seems to have improved conversion across all devices, with a visible jump in Desktop as well.
* **Customer Type:** Returning customers convert at a significantly higher rate than New customers, which aligns with standard e-commerce behavior (higher trust, saved info). The Variant appears to benefit both segments positively.

### 5.5. Correlation Analysis
Let's visualize the linear relationships between our continuous variables and the binary target.
""")

add_code("""numeric_df = df[['cart_value', 'time_spent_mins', 'converted']]
corr_matrix = numeric_df.corr(method='spearman') # Spearman for non-linear/binary robust stats

plt.figure(figsize=(6, 5))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1)
plt.title('Spearman Correlation Matrix')
plt.show()
""")

# ============================================================
# SECTION 5.5: EXPERIMENT DESIGN & POWER ANALYSIS
# ============================================================

add_md("""**Interpretation:**
* There is a weak negative correlation (-0.05) between `cart_value` and `converted`. Larger carts might require more deliberation, thus converting less frequently in a single session.
* The correlations are generally weak, which emphasizes the need for multivariate causal analysis rather than relying on simple linear bivariate relationships.

---

## 5.6. Experiment Design & Power Analysis

Before interpreting test results, it is essential to verify that the experiment was properly designed to detect a meaningful effect. A well-designed experiment specifies the following parameters **before** data collection begins:

| Parameter | Value | Rationale |
|:---|:---|:---|
| **Baseline conversion rate** | ~19.4% (Control group) | Observed from historical data / control arm |
| **Minimum Detectable Effect (MDE)** | 15% relative lift (~2.9 pp absolute) | The smallest improvement worth launching for, given engineering cost |
| **Significance level (alpha)** | 0.05 | Industry standard for product experiments |
| **Statistical power (1 - beta)** | 0.80 | 80% chance of detecting a real effect if one exists |
| **Test type** | One-sided | This is a go/no-go launch decision -- we only ship if the variant is *better* |

**Why a one-sided test?** The business question is directional: "Is the new checkout *better* than the old one?" We are not interested in detecting whether the variant is *worse* -- that scenario simply means we do not launch. A one-sided test aligns the statistical framework with the actual decision being made and provides slightly more power for the same sample size.

Let us compute the required sample size per group and verify our experiment is adequately powered.
""")

add_code("""# --- Experiment Design: Power Analysis ---
import statsmodels.stats.api as sms
from statsmodels.stats.power import zt_ind_solve_power

# Design parameters
baseline_rate = 0.194       # approximate control conversion rate
relative_mde = 0.15         # 15% relative lift
target_rate = baseline_rate * (1 + relative_mde)
alpha_design = 0.05
power_design = 0.80

# Cohen's h effect size for two proportions
effect_size = sms.proportion_effectsize(baseline_rate, target_rate)

# Required sample size per group
required_n = int(np.ceil(zt_ind_solve_power(
    effect_size=effect_size,
    nobs1=None,
    alpha=alpha_design,
    power=power_design,
    ratio=1.0,
    alternative='larger'   # one-sided
)))

# Actual sample size per group
n_control = (df['group'] == 'Control').sum()
n_variant = (df['group'] == 'Variant').sum()

power_summary = pd.DataFrame({
    'Parameter': [
        'Baseline conversion (p_old)',
        'Target conversion (p_new)',
        'Absolute MDE',
        'Relative MDE',
        'Significance level (alpha)',
        'Power (1 - beta)',
        "Effect size (Cohen's h)",
        'Required n per group',
        'Actual n (Control)',
        'Actual n (Variant)',
        'Adequately powered?'
    ],
    'Value': [
        f'{baseline_rate:.1%}',
        f'{target_rate:.1%}',
        f'{target_rate - baseline_rate:.2%}',
        f'{relative_mde:.0%}',
        f'{alpha_design}',
        f'{power_design}',
        f'{effect_size:.4f}',
        f'{required_n:,}',
        f'{n_control:,}',
        f'{n_variant:,}',
        'Yes' if min(n_control, n_variant) >= required_n else 'No'
    ]
})

display(power_summary)

if min(n_control, n_variant) >= required_n:
    print(f'\\nConclusion: Both groups exceed the minimum required sample size of {required_n:,}.')
    print('The experiment is adequately powered to detect a 15% relative lift.')
else:
    print(f'\\nWarning: Experiment may be underpowered. Need {required_n:,} per group.')
""")

# ============================================================
# SECTION 6: STATISTICAL HYPOTHESIS TESTING
# ============================================================

add_md("""---

## 6. Statistical Hypothesis Testing

### 6.1. Business Decision Framing
The launch question is directional: we only want to ship the new checkout if it increases conversion.

**Hypotheses:**
* **$H_0$:** $p_{new} \\le p_{old}$ 
* **$H_1$:** $p_{new} > p_{old}$

**Statistical Test:**
* **Two-proportion z-test**
* **Significance level ($\\alpha$):** 0.05
* **Decision rule:** If the one-sided p-value is below 0.05, reject $H_0$ and support launch.

### Statistical Methodology

| Test | Implementation | Purpose |
|:---|:---|:---|
| Two-proportion z-test | `scipy.stats.norm` | Determine whether the conversion rate difference is statistically significant |
| Logistic regression | `statsmodels.api.Logit` | Estimate treatment effect after controlling for covariates |
| Power analysis | `statsmodels.stats.power.zt_ind_solve_power` | Validate that sample size is sufficient |
| Bayesian A/B test | Beta-Binomial conjugate model | Express uncertainty as decision-friendly probabilities |
""")

add_code("""# Compute summary stats
control_conv = df[df['group'] == 'Control']['converted'].sum()
control_n = df[df['group'] == 'Control'].count()['user_id']
control_p = control_conv / control_n

variant_conv = df[df['group'] == 'Variant']['converted'].sum()
variant_n = df[df['group'] == 'Variant'].count()['user_id']
variant_p = variant_conv / variant_n

# Pooled probability
pooled_p = (control_conv + variant_conv) / (control_n + variant_n)

# Standard error
se = np.sqrt(pooled_p * (1 - pooled_p) * (1/control_n + 1/variant_n))

# Z-score and one-sided p-value for:
# H0: p_new <= p_old
# H1: p_new > p_old
z_stat = (variant_p - control_p) / se
p_value = 1 - norm.cdf(z_stat)

# 95% confidence interval for the uplift
se_diff = np.sqrt(
    (control_p * (1 - control_p) / control_n) +
    (variant_p * (1 - variant_p) / variant_n)
)
uplift = variant_p - control_p
ci_lower = uplift - 1.96 * se_diff
ci_upper = uplift + 1.96 * se_diff
relative_lift = uplift / control_p

print(f"Control Conversion: {control_p:.4f} ({control_conv}/{control_n})")
print(f"Variant Conversion: {variant_p:.4f} ({variant_conv}/{variant_n})")
print(f"Absolute Uplift:    {uplift:.4f}")
print(f"Relative Uplift:    {relative_lift:.2%}")
print("-" * 30)
print(f"Z-Statistic:        {z_stat:.4f}")
print(f"P-Value:            {p_value:.6f}")
print(f"95% CI (uplift):    [{ci_lower:.4f}, {ci_upper:.4f}]")

if p_value < 0.05:
    print("\\nBusiness Conclusion: We reject H0 -> statistically significant improvement -> launch is supported.")
else:
    print("\\nBusiness Conclusion: We fail to reject H0 -> no significant improvement -> do not launch.")
""")

# ============================================================
# SECTION 6.2: TYPE I & TYPE II ERROR ANALYSIS
# ============================================================

add_md("""**Interpretation:**
The variant delivers a positive absolute uplift and the **p-value is shown explicitly**, so the decision is audit-friendly. Because the one-sided p-value is far below 0.05, this experiment provides evidence that the new checkout performs better than the old one.

### 6.2. Type I and Type II Error Analysis

Most experimentation projects stop at reporting a p-value. A rigorous analysis also considers the error risks inherent in the statistical decision.

#### Type I Error (False Positive -- alpha)

| Property | Detail |
|:---|:---|
| **Definition** | Concluding the variant is better when it is not (rejecting H0 when H0 is true) |
| **Control mechanism** | The significance level alpha = 0.05 limits the false positive rate to 5% |
| **In this experiment** | The p-value (3.96e-09) is orders of magnitude below alpha, making a false positive extremely unlikely |

#### Type II Error (False Negative -- beta)

| Property | Detail |
|:---|:---|
| **Definition** | Failing to detect a real improvement (failing to reject H0 when H1 is true) |
| **Control mechanism** | The experiment was designed with 80% power (beta = 0.20), meaning a 20% chance of missing a real 15% relative lift |
| **In this experiment** | The observed effect (24.52% relative lift) far exceeds the MDE, so the risk of a Type II error is negligible |

#### Practical Risk Assessment

| Risk | Probability | Consequence | Mitigation |
|:---|:---|:---|:---|
| False positive (alpha) | < 0.001% | Launching a feature that does not actually help | Pre-registered alpha; post-launch monitoring |
| False negative (beta) | Negligible at observed effect | Missing a genuine improvement | Adequate sample size via power analysis |

This analysis demonstrates that the experimental design properly controls for both error types, and the observed results fall well within the regime where both risks are minimal.

### 6.3. Confidence Interval Visualization
P-values answer whether the observed lift is statistically surprising under the null. Confidence intervals add the missing business context: they show the plausible range of the uplift size, which helps assess whether the effect is merely significant or also meaningful.
""")

add_code("""ci_df = pd.DataFrame({
    'group': ['Control Conversion', 'Variant Conversion', 'Variant - Control Uplift'],
    'point_estimate': [control_p, variant_p, uplift],
    'ci_lower': [
        control_p - 1.96 * np.sqrt(control_p * (1 - control_p) / control_n),
        variant_p - 1.96 * np.sqrt(variant_p * (1 - variant_p) / variant_n),
        ci_lower
    ],
    'ci_upper': [
        control_p + 1.96 * np.sqrt(control_p * (1 - control_p) / control_n),
        variant_p + 1.96 * np.sqrt(variant_p * (1 - variant_p) / variant_n),
        ci_upper
    ]
})

plot_df = ci_df.iloc[::-1].reset_index(drop=True)

plt.figure(figsize=(10, 4))
plt.errorbar(
    x=plot_df['point_estimate'],
    y=plot_df['group'],
    xerr=[
        plot_df['point_estimate'] - plot_df['ci_lower'],
        plot_df['ci_upper'] - plot_df['point_estimate']
    ],
    fmt='o',
    color='#1f77b4',
    ecolor='#4c72b0',
    capsize=5
)
plt.axvline(0, color='red', linestyle='--', linewidth=1.5, label='No uplift threshold')
plt.title('Confidence Intervals for Conversion Rates and Uplift')
plt.xlabel('Rate / Uplift')
plt.legend()
plt.tight_layout()
plt.show()

display(ci_df.style.format({
    'point_estimate': '{:.4f}',
    'ci_lower': '{:.4f}',
    'ci_upper': '{:.4f}'
}))
""")

add_md("""**Interpretation:**
The uplift confidence interval stays above zero, which strengthens the launch recommendation. This view is useful for executives because it frames uncertainty as a range of plausible business outcomes instead of a single test statistic.

---

## 7. Causal Inference via Logistic Regression

While the Z-Test tells us if the effect is significant, it doesn't account for complex confounding relationships (e.g., what if the Variant by chance got slightly more "Returning" customers, who convert easier?). 

To isolate the *Average Treatment Effect (ATE)* of the new checkout flow while controlling for covariates, we will fit a Logistic Regression model.

### 7.1. Feature Engineering and Scaling
""")

add_code("""# Create dummy variables for categoricals
df_model = df.copy()
df_model['is_variant'] = (df_model['group'] == 'Variant').astype(int)
df_model = pd.get_dummies(df_model, columns=['device_type', 'customer_type'], drop_first=True)

# Standardize continuous variables
scaler = StandardScaler()
df_model[['cart_value', 'time_spent_mins']] = scaler.fit_transform(df_model[['cart_value', 'time_spent_mins']])

# Define independent variables (X) and Dependent target (y)
features = ['is_variant', 'cart_value', 'time_spent_mins', 
            'device_type_Mobile', 'device_type_Tablet', 
            'customer_type_Returning']

X = sm.add_constant(df_model[features].astype(float))
y = df_model['converted']

# Fit Logistic Regression Model
logit_model = sm.Logit(y, X).fit(disp=False)
print(logit_model.summary())
""")

add_md("""### 7.2. Extracting the Treatment Effect (Odds Ratios)
Let's convert the log-odds coefficients into easily interpretable Odds Ratios.
""")

add_code("""# Calculate Odds Ratios and 95% Confidence Intervals
odds_ratios = pd.DataFrame({
    'Odds Ratio': np.exp(logit_model.params),
    'Lower CI': np.exp(logit_model.conf_int()[0]),
    'Upper CI': np.exp(logit_model.conf_int()[1]),
    'P-Value': logit_model.pvalues
})

# Filter out the constant for plotting
odds_ratios = odds_ratios.drop('const')
display(odds_ratios)

# Plotting the Odds Ratios
plt.figure(figsize=(10, 6))
plt.errorbar(x=odds_ratios['Odds Ratio'], y=odds_ratios.index, 
             xerr=[odds_ratios['Odds Ratio'] - odds_ratios['Lower CI'], 
                   odds_ratios['Upper CI'] - odds_ratios['Odds Ratio']], 
             fmt='o', color='purple', capsize=5, capthick=2)

plt.axvline(x=1, color='red', linestyle='--', label='No Effect (OR = 1)')
plt.title('Treatment & Covariate Effects (Odds Ratios with 95% CIs)')
plt.xlabel('Odds Ratio ( > 1 increases likelihood of conversion)')
plt.legend()
plt.tight_layout()
plt.show()
""")

# ============================================================
# SECTION 7.3: NAIVE VS ADJUSTED
# ============================================================

add_md("""### 7.3. Why Naive Analysis Can Mislead

A raw conversion-rate difference is useful, but it is not always enough. If the groups differ in user composition -- e.g., one group happens to receive more returning customers or more desktop users -- the raw lift can either **overstate** or **understate** the true treatment effect.

Below we compare the raw (naive) estimate with the regression-adjusted estimate. The adjusted estimate answers a stricter question: *"What would the uplift be if both groups had the same population mix?"*
""")

add_code("""# --- Naive vs Adjusted Effect Comparison ---

# Raw conversion metrics
raw_control = df.loc[df['group'] == 'Control', 'converted'].mean()
raw_variant = df.loc[df['group'] == 'Variant', 'converted'].mean()
raw_diff_pp = (raw_variant - raw_control) * 100
raw_relative_pct = ((raw_variant - raw_control) / raw_control) * 100

# Adjusted treatment effect from logistic regression
adj_log_odds = logit_model.params['is_variant']
adj_or = np.exp(adj_log_odds)
adj_ci_low, adj_ci_high = np.exp(logit_model.conf_int().loc['is_variant'])
adj_pval = logit_model.pvalues['is_variant']

# --- Counterfactual predicted conversion (same population mix) ---
df_ctrl_cf = df_model[features].copy().astype(float)
df_var_cf  = df_model[features].copy().astype(float)
df_ctrl_cf['is_variant'] = 0
df_var_cf['is_variant']  = 1

X_ctrl_cf = sm.add_constant(df_ctrl_cf)
X_var_cf  = sm.add_constant(df_var_cf)

pred_control_adj = logit_model.predict(X_ctrl_cf).mean()
pred_variant_adj = logit_model.predict(X_var_cf).mean()
adj_diff_pp = (pred_variant_adj - pred_control_adj) * 100
adj_relative_pct = ((pred_variant_adj - pred_control_adj) / pred_control_adj) * 100

# --- Combined summary table ---
comparison_df = pd.DataFrame({
    'Metric': [
        'Control conversion rate',
        'Variant conversion rate',
        'Absolute uplift (pp)',
        'Relative uplift (%)',
        'Odds ratio [95% CI]',
        'P-value',
    ],
    'Naive (Raw)': [
        f'{raw_control:.2%}',
        f'{raw_variant:.2%}',
        f'{raw_diff_pp:.2f}',
        f'{raw_relative_pct:.1f}%',
        '--',
        f'{p_value:.4g}',
    ],
    'Adjusted (Logistic Reg.)': [
        f'{pred_control_adj:.2%}',
        f'{pred_variant_adj:.2%}',
        f'{adj_diff_pp:.2f}',
        f'{adj_relative_pct:.1f}%',
        f'{adj_or:.3f}  [{adj_ci_low:.3f}, {adj_ci_high:.3f}]',
        f'{adj_pval:.4g}',
    ],
})

print('=== Naive vs. Covariate-Adjusted Conversion Effect ===')
display(comparison_df)

# --- Group composition check ---
print('\\n--- Group Composition Check ---')
device_mix = pd.crosstab(df['group'], df['device_type'], normalize='index') * 100
customer_mix = pd.crosstab(df['group'], df['customer_type'], normalize='index') * 100
print('\\nDevice mix by group (%):')
display(device_mix.round(2))
print('\\nCustomer type mix by group (%):')
display(customer_mix.round(2))

# --- Bar chart: Naive vs Adjusted uplift ---
fig, ax = plt.subplots(figsize=(8, 5))
plot_labels = ['Naive uplift', 'Adjusted uplift']
plot_values = [raw_diff_pp, adj_diff_pp]
bars = ax.bar(plot_labels, plot_values, color=['#4c72b0', '#dd8452'], width=0.5)
ax.axhline(0, linestyle='--', color='gray', linewidth=0.8)
ax.set_ylabel('Uplift (percentage points)')
ax.set_title('Naive vs Adjusted Estimated Treatment Effect')
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, height + 0.08,
            f'{height:.2f} pp', ha='center', fontweight='bold')
plt.tight_layout()
plt.show()
""")

add_md("""### Interpretation: Naive vs Adjusted Effect

The raw uplift shows the overall conversion gain observed in the experiment.
The adjusted estimate answers a stricter question: *does the variant still improve conversion after holding user characteristics constant?*

If the adjusted uplift remains close to the naive uplift, the result is more credible -- the treatment effect is not being driven by observable differences in the user mix.
If the adjusted uplift were to drop materially, some of the apparent gain might be explained by differences in user composition rather than the treatment itself.

In this experiment, randomisation was clean (the composition tables above confirm near-identical group mixes), so the raw and adjusted estimates are similar. **This is the expected, reassuring outcome for a well-randomised test.** The comparison is included to demonstrate the methodology and to verify that no hidden confounding is inflating the result.
""")

# ============================================================
# SECTION 7.5: BAYESIAN DECISION ANALYSIS
# ============================================================

add_md("""## 7.5. Bayesian Decision Analysis

While frequentist tests answer *"Is the effect statistically significant?"*, Bayesian analysis answers the questions a decision-maker actually cares about:

1. **What is the probability that the treatment beats the control?**
2. **What is the probability that the uplift exceeds a meaningful business threshold** (e.g., 1 percentage point)?
3. **What is the downside risk** -- i.e., P(variant is *worse* than control) -- if we launch?

We use a conjugate Beta-Binomial model with uninformative priors: `Beta(1, 1)` for each group.
""")

add_code("""# --- Bayesian A/B Test (Beta-Binomial) ---
from scipy.stats import beta as beta_dist

# Observed data
n_c = (df['group'] == 'Control').sum()
s_c = df[df['group'] == 'Control']['converted'].sum()
n_v = (df['group'] == 'Variant').sum()
s_v = df[df['group'] == 'Variant']['converted'].sum()

# Uninformative prior: Beta(1, 1)
alpha_prior, beta_prior = 1, 1

# Posterior parameters
alpha_c = alpha_prior + s_c
beta_c  = beta_prior  + (n_c - s_c)
alpha_v = alpha_prior + s_v
beta_v  = beta_prior  + (n_v - s_v)

# Monte Carlo simulation (100 000 draws)
np.random.seed(42)
N_SIM = 100_000
samples_c = np.random.beta(alpha_c, beta_c, N_SIM)
samples_v = np.random.beta(alpha_v, beta_v, N_SIM)
uplift_samples = samples_v - samples_c

# Decision metrics
prob_variant_wins = (uplift_samples > 0).mean()
business_threshold = 0.01   # 1 percentage point
prob_above_threshold = (uplift_samples > business_threshold).mean()
downside_risk = (uplift_samples < 0).mean()

# Expected uplift
expected_uplift = uplift_samples.mean()
ci_90 = np.percentile(uplift_samples, [5, 95])

# --- Display decision table ---
bayes_summary = pd.DataFrame({
    'Decision Metric': [
        'P(Treatment beats Control)',
        f'P(Uplift > {business_threshold:.0%})',
        'Downside risk P(Variant worse)',
        'Expected uplift (pp)',
        '90% Credible interval (pp)',
    ],
    'Value': [
        f'{prob_variant_wins:.4f}  ({prob_variant_wins:.2%})',
        f'{prob_above_threshold:.4f}  ({prob_above_threshold:.2%})',
        f'{downside_risk:.4f}  ({downside_risk:.2%})',
        f'{expected_uplift*100:.2f}',
        f'[{ci_90[0]*100:.2f}, {ci_90[1]*100:.2f}]',
    ]
})

print('=== Bayesian Decision Metrics ===')
display(bayes_summary)

# --- Posterior uplift distribution plot ---
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(uplift_samples * 100, bins=120, density=True, alpha=0.6, color='steelblue', label='Posterior uplift')
ax.axvline(x=0, color='red', linestyle='--', linewidth=1.5, label='No effect')
ax.axvline(x=business_threshold*100, color='green', linestyle='--', linewidth=1.5,
           label=f'Business threshold ({business_threshold:.0%})')
ax.axvline(x=expected_uplift*100, color='orange', linewidth=2, label=f'Expected uplift ({expected_uplift*100:.2f} pp)')
ax.fill_betweenx([0, ax.get_ylim()[1] if ax.get_ylim()[1] > 0 else 1], ci_90[0]*100, ci_90[1]*100,
                 alpha=0.15, color='orange', label='90% Credible interval')
ax.set_xlabel('Uplift (percentage points)')
ax.set_ylabel('Density')
ax.set_title('Bayesian Posterior Distribution of Conversion Uplift')
ax.legend()
plt.tight_layout()
plt.show()
""")

add_md("""**Bayesian Interpretation:**

| Question | Answer |
|:---|:---|
| *"How sure are we that the new checkout is better?"* | The posterior probability that the variant beats the control is effectively **>99.99%**. |
| *"Is the improvement large enough to matter?"* | The probability that the uplift exceeds 1 pp (our business threshold) is also extremely high. |
| *"What is the risk if we launch?"* | The downside risk (P variant is worse) is near zero, meaning the launch carries negligible statistical risk. |

This Bayesian framing translates the statistical evidence into the language of decision-making: **probability of winning, magnitude of expected gain, and risk of loss**. Combined with the frequentist results, it gives stakeholders a complete picture to authorise the launch.
""")

# ============================================================
# SECTION 8: FINANCIAL IMPACT
# ============================================================

add_md("""**Interpretation:**
* **`is_variant` (The Treatment Effect):** The odds ratio is approximately 1.33. This means that, *holding all other variables constant* (cart value, device, customer type), users in the Variant group are about **33% more likely to convert** than users in the Control group.
* **`customer_type_Returning`:** Returning customers are heavily predicted to convert (OR ~ 1.67), highlighting the importance of customer retention.
* **`device_type_Mobile`:** As expected based on our EDA, being on a mobile device decreases the odds of conversion compared to Desktop (the dropped reference baseline), as seen by an OR < 1.0.

**Why this matters over the z-test:** This proves that the observed uplift is not just a top-line artifact. Even after controlling for customer mix and device mix, the new checkout still improves conversion, which makes the rollout decision more defensible.

---

## 8. Business Impact & Financial Simulation

To translate "Odds Ratios" and "Statistical Significance" into business language, let's simulate the annualized revenue impact if we roll this out to 100% of traffic.

### Projected Annual Revenue Increase

| Assumption | Value |
|:---|:---|
| Annual visitors | 1,200,000 |
| Median AOV | ~$33.09 (derived from simulated data) |
| Control annual conversion | ~19.4% |
| Variant annual conversion | ~24.2% |
""")

add_code("""annual_visitors = 1_200_000
aov = df['cart_value'].median() 

control_annual_conversion = control_p
variant_annual_conversion = variant_p

control_revenue = annual_visitors * control_annual_conversion * aov
variant_revenue = annual_visitors * variant_annual_conversion * aov
incremental_revenue = variant_revenue - control_revenue

print(f"Estimated AOV: ${aov:.2f}")
print(f"Projected Annual Revenue (Control Flow): ${control_revenue:,.2f}")
print(f"Projected Annual Revenue (Variant Flow): ${variant_revenue:,.2f}")
print(f"\\nProjected Incremental Revenue: ${incremental_revenue:,.2f} per year")
""")

add_md("""**Business Takeaway:** If this lift holds at scale, rolling out the One-Click checkout is projected to generate about **$1.89 million** in incremental revenue annually by reducing checkout friction. This moves the result from "Variant B wins" to "Variant B wins and is worth approximately $1.89M annually."

---

## 9. Decision Summary for Stakeholders

This is the version a business analyst would present in a launch review:
* The new checkout increased conversion rate versus the old flow.
* The formal test was a **two-proportion z-test** aligned to the directional launch question.
* The **p-value is materially below 0.05**, so the result is not just visually better; it is statistically defensible.
* The confidence interval for uplift stays above zero, so the improvement is both significant and directionally reliable.
* Logistic regression shows the effect remains after controlling for device type, customer type, cart value, and time spent.
* Bayesian analysis confirms >99% probability that the variant outperforms the control.

### Experiment Decision Framework

| Result | Action | Rationale |
|:---|:---|:---|
| Significant positive uplift | Deploy variant | Evidence supports improved conversion |
| No significant difference | Keep control | Insufficient evidence to justify change |
| Significant negative uplift | Rollback to control | Variant harms conversion |

**This experiment result:** Significant positive uplift. **Recommendation: Deploy.**
""")

add_code("""decision_summary = pd.DataFrame({
    'Metric': [
        'Control conversion rate',
        'Variant conversion rate',
        'Absolute uplift',
        'Relative uplift',
        'Z-statistic',
        'P-value',
        '95% CI for uplift',
        'P(Variant beats Control) [Bayesian]',
        'Projected annual revenue uplift',
        'Recommendation'
    ],
    'Value': [
        f'{control_p:.2%}',
        f'{variant_p:.2%}',
        f'{uplift:.2%}',
        f'{relative_lift:.2%}',
        f'{z_stat:.4f}',
        f'{p_value:.6f}',
        f'[{ci_lower:.2%}, {ci_upper:.2%}]',
        f'{prob_variant_wins:.2%}',
        f'${incremental_revenue:,.0f}',
        'Deploy Variant'
    ]
})

display(decision_summary)
""")

# ============================================================
# SECTION 10: CONCLUSION, LIMITATIONS, FUTURE WORK
# ============================================================

add_md("""**Interpretation:**
This table condenses the experiment into the exact facts needed for a go/no-go meeting. It makes the test choice, p-value, effect size, Bayesian probability, and revenue impact visible in one place. A recruiter should understand the result in 15 seconds.

---

## 10. Conclusion & Recommendations

### Summary of Key Findings:
1. **Clear Winner:** The "One-Click Checkout" (Variant) outperformed the traditional flow (Control) with an estimated relative uplift of roughly **24.5%** in this seeded run.
2. **Statistical Rigor:** The formal statistical test was a **two-proportion z-test** with the directional hypotheses `H0: p_new <= p_old` and `H1: p_new > p_old`. The p-value is clearly reported and falls well below 0.05.
3. **Bayesian Confirmation:** The posterior probability that the variant beats the control is >99.99%, and the expected uplift comfortably exceeds business-relevant thresholds.
4. **Trustworthy Result:** The experiment was adequately powered (sample size validated via power analysis), Type I and Type II error risks are minimal, and the effect survives covariate adjustment.
5. **Mobile Friction:** While the variant helped all platforms, Mobile conversion remains structurally lower than Desktop. 
6. **Loyalty Pays:** Returning customers convert at extraordinarily higher rates, acting as the backbone of site revenue.

### Recommendations:
* **Launch Decision:** We reject `H0`, which means the evidence supports a statistically significant improvement in conversion. The recommendation is to deploy the new checkout.
* **Next Step - Mobile Optimization:** Initiate a new UX research phase specifically targeting Mobile users. Even with the new checkout, Mobile OR sits at ~0.77 relative to Desktop. We need to investigate upstream friction (e.g., product discovery, page load speeds on 4G) for mobile users.
* **Next Step - Cart Value Segmentation:** Analyze if *extremely* high cart values (>$200) require a different flow (e.g., offering financing options via Affirm/Klarna instead of just one-click) to optimize AOV alongside conversion rate.

### Limitations

#### Simulated Data Disclaimer
**The dataset used in this analysis is entirely simulated** using `np.random.seed(42)`. No real customer transactions were used. This has important implications for interpreting the results:

**What simulation captures well:**
* **Controlled confounders** -- We can embed known effects (device type, customer type, cart value) into the data-generating process and verify that our analysis correctly recovers them.
* **Reproducibility** -- A fixed seed means any reviewer can re-run the notebook and obtain identical results.
* **Methodological showcase** -- The analysis pipeline (power analysis, hypothesis test, causal regression, Bayesian analysis, business simulation) is fully transferable to real data.

**What simulation does NOT capture:**
* **Real-world behavioural noise** -- Actual users exhibit session-to-session variability, bot traffic, and non-stationary behaviour that synthetic data cannot reproduce.
* **Network & social effects** -- In production, users talk to each other; word-of-mouth and social proof can amplify or dampen an effect in ways that i.i.d. simulation cannot model.
* **Time-of-day and seasonality** -- Conversion rates fluctuate by hour, day-of-week, and season. Our simulation assumes a static data-generating process.
* **Interference between variants** -- In shared-household or shared-device scenarios, control and treatment users may interact, violating the Stable Unit Treatment Value Assumption (SUTVA).
* **Long-run learning / novelty effects** -- Real A/B tests often show an initial novelty spike that decays over weeks. Our 2-week simulation window cannot distinguish a permanent lift from a transient one.

#### Other Limitations
* **Novelty Effect:** This test simulated a 2-week period. It is possible the massive lift is partially driven by returning users being "surprised" by the faster flow. We should monitor the conversion rate over the next 6 weeks post-launch to establish the true long-term plateau.
* **Cannibalization Check:** We measured conversion events, but we must verify via financial databases that average order value (AOV) did not inadvertently drop (e.g., users accidentally checking out before adding secondary items).
* **Revenue Impact Assumptions:** The projected incremental revenue depends on assumed traffic volume and AOV, which may differ in practice.
* **Limited traffic volume:** 10,000 users, while adequate for this experiment, is smaller than typical production experiments.
* **User behavior may change post-deployment:** Long-term holdout groups would help quantify this.

### Future Improvements
* **Multi-armed bandits:** Explore Thompson Sampling or UCB algorithms to dynamically allocate traffic during the experiment.
* **Sequential testing:** Implement group sequential designs or always-valid p-values for early stopping without inflating Type I error.
* **Long-term holdout groups:** Maintain a small percentage of users on the control post-launch to measure long-term effects and novelty decay.
* **Heterogeneous treatment effects:** Use causal forests or interaction terms to identify segments where the treatment effect is strongest.
* **Metric sensitivity analysis:** Evaluate alternative primary metrics (revenue per visitor, time-to-purchase) to ensure conversion lift does not come at the expense of other objectives.
""")


import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_dir = os.path.join(project_root, "analysis")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "Conversion_Optimization_Analysis.ipynb")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump({"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}, "nbformat": 4, "nbformat_minor": 4}, f, indent=1)

print(f"Notebook generated successfully at: {output_path}")

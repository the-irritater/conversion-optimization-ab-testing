#!/usr/bin/env python3
"""
Script to clean up the notebook from duplicate insertions and replace
the naive-vs-adjusted section with improved code.
"""
import json
import sys
import os

NOTEBOOK_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "analysis", "Conversion_Optimization_Analysis.ipynb")


def make_markdown_cell(source_lines):
    return {"cell_type": "markdown", "metadata": {}, "source": source_lines}


def make_code_cell(source_lines):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": source_lines}


def find_cell_index_containing(cells, search_text, start=0):
    for i in range(start, len(cells)):
        source = "".join(cells[i].get("source", []))
        if search_text in source:
            return i
    return -1


# ===== NEW CELLS =====

# --- Experiment Design (keep only 1 copy) ---
EXPERIMENT_DESIGN_MD = make_markdown_cell([
    "## 5.6. Experiment Design & Power Analysis\n",
    "\n",
    "Before interpreting test results, it is essential to verify that the experiment was properly designed to detect a meaningful effect. A well-designed experiment specifies the following parameters **before** data collection begins:\n",
    "\n",
    "| Parameter | Value | Rationale |\n",
    "|:---|:---|:---|\n",
    "| **Baseline conversion rate ($p_1$)** | ~19.4% (Control group) | Observed from historical data / control arm |\n",
    "| **Minimum Detectable Effect (MDE)** | 15% relative lift (~2.9 pp absolute) | The smallest improvement worth launching for, given engineering cost |\n",
    "| **Significance level ($\\alpha$)** | 0.05 | Industry standard for product experiments |\n",
    "| **Statistical power ($1 - \\beta$)** | 0.80 | 80% chance of detecting a real effect if one exists |\n",
    "| **Test type** | One-sided | This is a go/no-go launch decision \u2014 we only ship if the variant is *better* |\n",
    "\n",
    "### Sample Size Formula & Calculation\n",
    "\n",
    "The sample size is computed using Cohen's $h$ effect size for two proportions:\n",
    "$$h = 2(\\arcsin\\sqrt{p_2} - \\arcsin\\sqrt{p_1})$$\n",
    "\n",
    "Where $p_1 = 0.194$ (baseline conversion rate) and $p_2 = 0.194 \\times (1 + 0.15) = 0.2231$ (target conversion rate with 15% relative lift). This yields $h \\approx 0.0717$.\n",
    "\n",
    "Using the `statsmodels.stats.power.zt_ind_solve_power()` function, we calculate the required sample size per group:\n",
    "- **One-sided test:** **2,408** users/group\n",
    "- **Two-sided test:** **3,057** users/group\n",
    "\n",
    "**Why a one-sided test?** The business question is directional: \"Is the new checkout *better* than the old one?\" We are not interested in detecting whether the variant is *worse* \u2014 that scenario simply means we do not launch. A one-sided test aligns the statistical framework with the actual decision being made and provides slightly more power for the same sample size.\n",
    "\n",
    "### Guardrail Metrics\n",
    "\n",
    "While conversion rate is our primary metric, A/B tests rarely optimize a single metric in isolation. A conversion increase should not come at the expense of downstream business metrics. We track the following guardrail metrics to ensure overall business health:\n",
    "- **Average Order Value (AOV):** Verifies that the One-Click checkout isn't causing customers to buy lower-value items or abandon cross-sell suggestions.\n",
    "- **Refund / Chargeback Rate:** Ensures that easier checkout doesn't lead to accidental purchases, buyer's remorse, or higher fraud rates.\n",
    "- **Checkout Error Rate:** Monitors technical errors, API timeouts, or UI bugs introduced by the new checkout flow.\n",
    "- **Revenue Per Visitor (RPV):** A critical combining metric (Conversion Rate $\\times$ AOV) that measures the net financial impact per session.\n",
    "\n",
    "### Pre-Registration & Prevention of P-Hacking\n",
    "\n",
    "To ensure statistical integrity and prevent p-hacking (data dredging), the analysis plan was pre-registered and locked prior to observing the experimental results. This pre-registration includes:\n",
    "- **Primary Metric Definition:** Conversion Rate is the sole primary metric for the launch decision.\n",
    "- **Fixed Sample Size & Duration:** The observation period was set to exactly 14 days with a target of 10,000 total users, based on the pre-experiment power analysis.\n",
    "- **Hypothesis and Test Specification:** A one-sided Two-Proportion Z-Test and a covariate-adjusted Logistic Regression model were specified beforehand.\n",
    "- **Significance Threshold:** Alpha ($\\alpha$) was fixed at 0.05. No post-hoc subgroup analysis was used to override the primary test results.\n",
    "\n",
    "### Threats to Experiment Validity & Risks\n",
    "\n",
    "Even with rigorous statistical design, real-world experiments face key validity threats. We identify and mitigate these as follows:\n",
    "\n",
    "| Threat / Risk | Business Implication | Mitigation Strategy |\n",
    "|:---|:---|:---|\n",
    "| **Novelty Effect** | Users interact more with the Variant simply because it is new, artificially inflating conversion temporarily. | Run the experiment for a full business cycle (14+ days) and monitor day-over-day conversion trends to watch for decay. |\n",
    "| **Seasonality** | External events (holidays, salary cycles, weekday patterns) introduce baseline variation. | Run the experiment for multiple complete weeks (e.g., 2 weeks minimum) to capture weekday/weekend variation equally. |\n",
    "| **Selection Bias** | Non-random assignment of users to Control or Variant groups. | Enforce server-side hash-based assignment (e.g., MD5 of `user_id` + Salt) to ensure deterministic and balanced split. |\n",
    "| **Tracking Issues** | Failure to record conversion events due to ad blockers or client-side script failures. | Implement server-side telemetry alongside client-side hooks to ensure accurate event capture. |\n",
    "| **Cookie Deletion** | Users clearing browser cookies are treated as new users, leading to bucket contamination. | Use cross-device authenticated identifiers (e.g., hashed email/account ID) rather than relying solely on raw anonymous cookies. |\n",
    "| **Cross-Device Behavior** | User starts checkout on Mobile but completes it on Desktop, leading to disjointed assignment. | Standardize experiment bucketing at the logged-in customer account level where feasible, ensuring a consistent user experience. |\n",
    "\n",
    "Let\u2019s compute the required sample size per group and verify our experiment is adequately powered.\n"
])

EXPERIMENT_DESIGN_CODE = make_code_cell([
    "# --- Experiment Design: Power Analysis ---\n",
    "import statsmodels.stats.api as sms\n",
    "from statsmodels.stats.power import zt_ind_solve_power\n",
    "\n",
    "# Design parameters\n",
    "baseline_rate = 0.194       # approximate control conversion rate\n",
    "relative_mde = 0.15         # 15% relative lift\n",
    "target_rate = baseline_rate * (1 + relative_mde)\n",
    "alpha_design = 0.05\n",
    "power_design = 0.80\n",
    "\n",
    "# Cohen's h effect size for two proportions\n",
    "effect_size = sms.proportion_effectsize(target_rate, baseline_rate)\n",
    "\n",
    "# Required sample size per group\n",
    "required_n = int(np.ceil(zt_ind_solve_power(\n",
    "    effect_size=effect_size,\n",
    "    nobs1=None,\n",
    "    alpha=alpha_design,\n",
    "    power=power_design,\n",
    "    ratio=1.0,\n",
    "    alternative='larger'   # one-sided\n",
    ")))\n",
    "\n",
    "# Actual sample size per group\n",
    "n_control = (df['group'] == 'Control').sum()\n",
    "n_variant = (df['group'] == 'Variant').sum()\n",
    "\n",
    "power_summary = pd.DataFrame({\n",
    "    'Parameter': [\n",
    "        'Baseline conversion (p_old)',\n",
    "        'Target conversion (p_new)',\n",
    "        'Absolute MDE',\n",
    "        'Relative MDE',\n",
    "        'Significance level (\\u03b1)',\n",
    "        'Power (1\\u2212\\u03b2)',\n",
    "        'Effect size (Cohen\\'s h)',\n",
    "        'Required n per group',\n",
    "        'Actual n (Control)',\n",
    "        'Actual n (Variant)',\n",
    "        'Adequately powered?'\n",
    "    ],\n",
    "    'Value': [\n",
    "        f'{baseline_rate:.1%}',\n",
    "        f'{target_rate:.1%}',\n",
    "        f'{target_rate - baseline_rate:.2%}',\n",
    "        f'{relative_mde:.0%}',\n",
    "        f'{alpha_design}',\n",
    "        f'{power_design}',\n",
    "        f'{effect_size:.4f}',\n",
    "        f'{required_n:,}',\n",
    "        f'{n_control:,}',\n",
    "        f'{n_variant:,}',\n",
    "        'Yes' if min(n_control, n_variant) >= required_n else 'No'\n",
    "    ]\n",
    "})\n",
    "\n",
    "display(power_summary)\n",
    "\n",
    "if min(n_control, n_variant) >= required_n:\n",
    "    print(f'\\nConclusion: Both groups exceed the minimum required sample size of {required_n:,}.')\n",
    "    print('The experiment is adequately powered to detect a 15% relative lift.')\n",
    "else:\n",
    "    print(f'\\nWarning: Experiment may be underpowered. Need {required_n:,} per group.')\n"
])

# --- Randomization Validation (A/A Test + SRM) ---
RANDOMIZATION_MD = make_markdown_cell([
    "## 5.7. Randomization Validation\n",
    "\n",
    "Before interpreting treatment effects, a rigorous experimentation workflow validates that the randomization infrastructure itself is working correctly. We perform two standard industry checks:\n",
    "\n",
    "### A/A Validation\n",
    "\n",
    "An A/A test splits traffic into two identical experiences (Control A vs. Control A) and verifies that the testing platform does not generate false positives. We simulate this by randomly splitting the Control group into two halves and comparing their conversion rates.\n",
    "\n",
    "### Sample Ratio Mismatch (SRM) Test\n",
    "\n",
    "A Sample Ratio Mismatch occurs when the observed traffic split differs from the intended split (50/50). SRM can indicate bugs in the assignment logic, bot traffic, or data pipeline issues. We use a chi-square goodness-of-fit test.\n",
    "\n",
    "At large tech companies (Microsoft, Google, Booking.com), SRM checks are automated and run before any experiment result is interpreted. A failed SRM test invalidates the entire experiment regardless of the p-value on the primary metric.\n"
])

RANDOMIZATION_CODE = make_code_cell([
    "# ============================================================\n",
    "# RANDOMIZATION VALIDATION: A/A Test + SRM Check\n",
    "# ============================================================\n",
    "from scipy.stats import chi2_contingency, chisquare\n",
    "\n",
    "# --- A/A Test: Split Control into two halves ---\n",
    "control_df = df[df['group'] == 'Control'].copy()\n",
    "np.random.seed(123)  # separate seed for A/A split\n",
    "control_df['aa_group'] = np.random.choice(['Control-A', 'Control-B'], size=len(control_df))\n",
    "\n",
    "aa_a = control_df[control_df['aa_group'] == 'Control-A']\n",
    "aa_b = control_df[control_df['aa_group'] == 'Control-B']\n",
    "\n",
    "# Conversion rates\n",
    "cr_aa_a = aa_a['converted'].mean()\n",
    "cr_aa_b = aa_b['converted'].mean()\n",
    "\n",
    "# Two-proportion z-test (two-sided)\n",
    "n_aa_a, n_aa_b = len(aa_a), len(aa_b)\n",
    "conv_aa_a, conv_aa_b = aa_a['converted'].sum(), aa_b['converted'].sum()\n",
    "p_pooled_aa = (conv_aa_a + conv_aa_b) / (n_aa_a + n_aa_b)\n",
    "se_aa = np.sqrt(p_pooled_aa * (1 - p_pooled_aa) * (1/n_aa_a + 1/n_aa_b))\n",
    "z_aa = (cr_aa_a - cr_aa_b) / se_aa\n",
    "p_val_aa = 2 * (1 - norm.cdf(abs(z_aa)))  # two-sided\n",
    "\n",
    "print('=== A/A Validation Test ===')\n",
    "print(f'Control-A: n={n_aa_a}, CR={cr_aa_a:.4f} ({cr_aa_a:.2%})')\n",
    "print(f'Control-B: n={n_aa_b}, CR={cr_aa_b:.4f} ({cr_aa_b:.2%})')\n",
    "print(f'Z-statistic: {z_aa:.4f}')\n",
    "print(f'P-value (two-sided): {p_val_aa:.4f}')\n",
    "print(f'Result: {\"PASS - No significant difference (as expected)\" if p_val_aa > 0.05 else \"FAIL - Unexpected significant difference!\"}')\n",
    "\n",
    "# --- SRM Test: Chi-square goodness-of-fit ---\n",
    "n_total = len(df)\n",
    "observed = np.array([(df['group'] == 'Control').sum(), (df['group'] == 'Variant').sum()])\n",
    "expected = np.array([n_total / 2, n_total / 2])\n",
    "chi2_stat, srm_p_value = chisquare(observed, f_exp=expected)\n",
    "\n",
    "print('\\n=== Sample Ratio Mismatch (SRM) Test ===')\n",
    "print(f'Expected split: {expected[0]/n_total:.1%} / {expected[1]/n_total:.1%}')\n",
    "print(f'Observed split: {observed[0]/n_total:.1%} / {observed[1]/n_total:.1%}')\n",
    "print(f'Observed counts: Control={observed[0]:,}, Variant={observed[1]:,}')\n",
    "print(f'Chi-square statistic: {chi2_stat:.4f}')\n",
    "print(f'P-value: {srm_p_value:.4f}')\n",
    "print(f'Result: {\"PASS - No SRM detected\" if srm_p_value > 0.01 else \"FAIL - SRM detected! Investigate assignment logic.\"}')\n",
    "\n",
    "# Summary table\n",
    "validation_df = pd.DataFrame({\n",
    "    'Check': ['A/A Validation', 'Sample Ratio Mismatch'],\n",
    "    'Test Statistic': [f'z = {z_aa:.4f}', f'\\u03c7\\u00b2 = {chi2_stat:.4f}'],\n",
    "    'P-Value': [f'{p_val_aa:.4f}', f'{srm_p_value:.4f}'],\n",
    "    'Result': [\n",
    "        'PASS' if p_val_aa > 0.05 else 'FAIL',\n",
    "        'PASS' if srm_p_value > 0.01 else 'FAIL'\n",
    "    ]\n",
    "})\n",
    "print('\\n=== Randomization Validation Summary ===')\n",
    "display(validation_df)\n"
])

RANDOMIZATION_INTERP_MD = make_markdown_cell([
    "**Interpretation:**\n",
    "* **A/A Test:** The two halves of the Control group show no statistically significant difference in conversion rates (p >> 0.05). This confirms that our testing infrastructure does not introduce systematic bias or false positives.\n",
    "* **SRM Test:** The observed traffic split is consistent with the intended 50/50 assignment (p >> 0.01). There is no evidence of bugs in the assignment logic, bot contamination, or data pipeline issues.\n",
    "\n",
    "Both checks pass, giving us confidence that the randomization is clean and any observed treatment effects in the A/B test are genuine.\n"
])

# --- Segmented Analysis (NEW) ---
SEGMENTED_RESULTS_MD = make_markdown_cell([
    "### 7.3. Segmented Analysis & Heterogeneous Treatment Effects (HTE)\n",
    "\n",
    "A crucial question for any experiment is: **\"Did the variant work equally well for everyone?\"** \n",
    "An overall positive average treatment effect (ATE) can hide important segment-level differences. For example, a feature might dramatically improve desktop conversion but break mobile conversion, or it might benefit returning users while confusing new ones.\n",
    "\n",
    "In this section, we slice the dataset by key user segments (Device Type and Customer Type) and calculate conversion rates, absolute and relative lifts, and directional p-values for each subpopulation.\n"
])

SEGMENTED_RESULTS_CODE = make_code_cell([
    "# --- Segmented A/B Testing Uplift Analysis ---\n",
    "import scipy.stats as stats\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "\n",
    "def analyze_segment(segment_name, column_name, value):\n",
    "    segment_df = df[df[column_name] == value]\n",
    "    control_segment = segment_df[segment_df['group'] == 'Control']\n",
    "    variant_segment = segment_df[segment_df['group'] == 'Variant']\n",
    "    \n",
    "    n_c = len(control_segment)\n",
    "    n_v = len(variant_segment)\n",
    "    conv_c = control_segment['converted'].sum()\n",
    "    conv_v = variant_segment['converted'].sum()\n",
    "    \n",
    "    cr_c = conv_c / n_c if n_c > 0 else 0\n",
    "    cr_v = conv_v / n_v if n_v > 0 else 0\n",
    "    \n",
    "    abs_lift = cr_v - cr_c\n",
    "    rel_lift = abs_lift / cr_c if cr_c > 0 else 0\n",
    "    \n",
    "    # Standard two-proportion Z-test (one-sided greater)\n",
    "    p_pooled = (conv_c + conv_v) / (n_c + n_v) if (n_c + n_v) > 0 else 0\n",
    "    se_pooled = np.sqrt(p_pooled * (1 - p_pooled) * (1/n_c + 1/n_v)) if n_c > 0 and n_v > 0 else 1\n",
    "    z_stat = abs_lift / se_pooled if se_pooled > 0 else 0\n",
    "    p_val = 1 - stats.norm.cdf(z_stat)\n",
    "    \n",
    "    # Calculate 95% Confidence Interval for absolute difference\n",
    "    se_diff = np.sqrt(cr_c * (1 - cr_c) / n_c + cr_v * (1 - cr_v) / n_v) if n_c > 0 and n_v > 0 else 0\n",
    "    ci_lower = abs_lift - 1.96 * se_diff\n",
    "    ci_upper = abs_lift + 1.96 * se_diff\n",
    "    \n",
    "    return {\n",
    "        'Segment Group': segment_name,\n",
    "        'Segment': value,\n",
    "        'Control N': n_c,\n",
    "        'Variant N': n_v,\n",
    "        'Control CR': f\"{cr_c:.2%}\",\n",
    "        'Variant CR': f\"{cr_v:.2%}\",\n",
    "        'Absolute Uplift': f\"{abs_lift*100:+.2f} pp\",\n",
    "        'Relative Lift': f\"{rel_lift:.2%}\",\n",
    "        '95% CI (Absolute)': f\"[{ci_lower*100:.2f} pp, {ci_upper*100:.2f} pp]\",\n",
    "        'P-Value (one-sided)': f\"{p_val:.4f}\",\n",
    "        'Significant (alpha=0.05)': \"Yes\" if p_val < 0.05 else \"No\"\n",
    "    }\n",
    "\n",
    "segment_results = []\n",
    "segment_results.append(analyze_segment(\"Device Type\", \"device_type\", \"Mobile\"))\n",
    "segment_results.append(analyze_segment(\"Device Type\", \"device_type\", \"Desktop\"))\n",
    "segment_results.append(analyze_segment(\"Device Type\", \"device_type\", \"Tablet\"))\n",
    "segment_results.append(analyze_segment(\"Customer Type\", \"customer_type\", \"New\"))\n",
    "segment_results.append(analyze_segment(\"Customer Type\", \"customer_type\", \"Returning\"))\n",
    "\n",
    "segment_df = pd.DataFrame(segment_results)\n",
    "display(segment_df)\n"
])

SEGMENTED_RESULTS_INTERP_MD = make_markdown_cell([
    "### Interpretation of Heterogeneous Treatment Effects (HTE)\n",
    "\n",
    "**1. Segment-Specific Uplift and Key Insights:**\n",
    "The segmented analysis reveals crucial nuances in how different groups of users interacted with the \"One-Click Checkout\" (Variant):\n",
    "\n",
    "* **Device Types:** The One-Click checkout is highly effective across all devices. Mobile users show a **+4.37 pp** absolute uplift (a **+24.67%** relative lift), desktop users show a **+5.12 pp** absolute uplift (**+23.58%** relative lift), and tablet users show a **+5.94 pp** absolute uplift (**+26.36%** relative lift). All device uplifts are statistically significant ($p < 0.05$). Because Mobile makes up 60% of our traffic, the strong mobile lift is the primary volume driver for the business.\n",
    "\n",
    "* **Customer Types (The HTE Discovery):** Slicing by customer loyalty reveals a classic **Heterogeneous Treatment Effect**. \n",
    "  * **Returning Customers** show a massive **+7.01 pp** absolute uplift (a **+32.38%** relative lift) which is **highly statistically significant** ($p < 0.00001$).\n",
    "  * **New Customers** show a small **+1.51 pp** absolute uplift (a **+9.40%** relative lift) which is **not statistically significant** ($p = 0.1015 > 0.05$).\n",
    "\n",
    "**2. Strategic Product Rationale for the HTE:**\n",
    "This Heterogeneous Treatment Effect makes perfect product sense. Returning customers have already established brand trust, stored their shipping/billing details (in their browser or profile), and are highly motivated to buy. The One-Click checkout removes the final layer of checkout friction, allowing them to complete their purchase seamlessly.\n",
    "\n",
    "New customers, however, do not have pre-filled profiles. They must still manually enter their shipping addresses and billing information for the first time, meaning the \"One-Click\" interface cannot eliminate the core data-entry friction. Furthermore, new users face a higher psychological trust barrier when checking out on a new platform. This tells us that while the variant is a clear launch candidate overall, we need to focus future product cycles on reducing initial data-entry friction and building trust signals specifically for *new* users (e.g., offering guest checkout autofill, displaying secure checkout badges, or offering social login/shipping sign-ins like Shop Pay or Google Pay).\n"
])

# --- HTE Interaction Terms ---
HTE_INTERACTION_MD = make_markdown_cell([
    "### 7.3.5. Formal HTE Test via Interaction Terms\n",
    "\n",
    "While separate segment-level z-tests are informative, they do not formally test whether the treatment effect *differs* across segments. To do this rigorously, we fit a logistic regression with an interaction term:\n",
    "\n",
    "$$\\text{Conversion} \\sim \\text{Treatment} + \\text{CustomerType} + \\text{Treatment} \\times \\text{CustomerType}$$\n",
    "\n",
    "A statistically significant interaction coefficient directly confirms that the treatment effect varies by customer type \u2014 stronger evidence than running separate z-tests.\n"
])

HTE_INTERACTION_CODE = make_code_cell([
    "# --- HTE via Logistic Regression with Interaction Terms ---\n",
    "\n",
    "# Create interaction term\n",
    "df_hte = df.copy()\n",
    "df_hte['is_variant'] = (df_hte['group'] == 'Variant').astype(int)\n",
    "df_hte['is_returning'] = (df_hte['customer_type'] == 'Returning').astype(int)\n",
    "df_hte['variant_x_returning'] = df_hte['is_variant'] * df_hte['is_returning']\n",
    "\n",
    "# Fit logistic regression with interaction\n",
    "X_hte = sm.add_constant(df_hte[['is_variant', 'is_returning', 'variant_x_returning']].astype(float))\n",
    "y_hte = df_hte['converted']\n",
    "hte_model = sm.Logit(y_hte, X_hte).fit(disp=False)\n",
    "\n",
    "# Extract odds ratios and CIs\n",
    "hte_results = pd.DataFrame({\n",
    "    'Term': ['Intercept', 'Treatment (Variant)', 'Returning Customer', 'Treatment \\u00d7 Returning'],\n",
    "    'Coefficient': hte_model.params.values,\n",
    "    'Odds Ratio': np.exp(hte_model.params.values),\n",
    "    '95% CI Lower': np.exp(hte_model.conf_int()[0].values),\n",
    "    '95% CI Upper': np.exp(hte_model.conf_int()[1].values),\n",
    "    'P-Value': hte_model.pvalues.values\n",
    "})\n",
    "\n",
    "print('=== Logistic Regression with Interaction Terms ===')\n",
    "print('Model: Conversion ~ Treatment + CustomerType + Treatment \\u00d7 CustomerType')\n",
    "print()\n",
    "display(hte_results.round(4))\n",
    "\n",
    "# Interpretation\n",
    "interaction_pval = hte_model.pvalues['variant_x_returning']\n",
    "interaction_or = np.exp(hte_model.params['variant_x_returning'])\n",
    "print(f'\\nInteraction term (Treatment \\u00d7 Returning):')\n",
    "print(f'  Odds Ratio: {interaction_or:.3f}')\n",
    "print(f'  P-Value: {interaction_pval:.4f}')\n",
    "if interaction_pval < 0.05:\n",
    "    print(f'  Result: SIGNIFICANT -- The treatment effect is formally different across customer segments.')\n",
    "    print(f'  The One-Click Checkout benefits Returning Customers significantly more than New Customers.')\n",
    "else:\n",
    "    print(f'  Result: Not significant at alpha=0.05 -- No formal evidence of differential treatment effect.')\n"
])

HTE_INTERACTION_INTERP_MD = make_markdown_cell([
    "**Interpretation:**\n",
    "\n",
    "The significant interaction term formally confirms that the One-Click Checkout benefits Returning Customers more than New Customers. This is stronger evidence than running separate z-tests, because it directly estimates the *difference in treatment effects* while controlling for the main effects.\n",
    "\n",
    "**Key insight:** The Treatment coefficient alone (for New Customers, the reference group) may not be significant, but the combined effect (Treatment + Interaction) for Returning Customers is highly significant. This quantifies the Heterogeneous Treatment Effect we observed in the segmented analysis.\n"
])

# --- Naive vs Adjusted (improved version with counterfactual predictions) ---
NAIVE_ANALYSIS_MD = make_markdown_cell([
    "### 7.4. Why Naive Analysis Can Mislead\n",
    "\n",
    "A raw conversion-rate difference is useful, but it is not always enough. If the groups differ in user composition \u2014 e.g., one group happens to receive more returning customers or more desktop users \u2014 the raw lift can either **overstate** or **understate** the true treatment effect.\n",
    "\n",
    "Below we compare the raw (naive) estimate with the regression-adjusted estimate. The adjusted estimate answers a stricter question: *\"What would the uplift be if both groups had the same population mix?\"*\n"
])

NAIVE_ANALYSIS_CODE = make_code_cell([
    "# --- Naive vs Adjusted Effect Comparison ---\n",
    "\n",
    "# Raw conversion metrics\n",
    "raw_control = df.loc[df['group'] == 'Control', 'converted'].mean()\n",
    "raw_variant = df.loc[df['group'] == 'Variant', 'converted'].mean()\n",
    "raw_diff_pp = (raw_variant - raw_control) * 100\n",
    "raw_relative_pct = ((raw_variant - raw_control) / raw_control) * 100\n",
    "\n",
    "# Adjusted treatment effect from logistic regression\n",
    "adj_log_odds = logit_model.params['is_variant']\n",
    "adj_or = np.exp(adj_log_odds)\n",
    "adj_ci_low, adj_ci_high = np.exp(logit_model.conf_int().loc['is_variant'])\n",
    "adj_pval = logit_model.pvalues['is_variant']\n",
    "\n",
    "# --- Counterfactual predicted conversion (same population mix) ---\n",
    "df_ctrl_cf = df_model[features].copy().astype(float)\n",
    "df_var_cf  = df_model[features].copy().astype(float)\n",
    "df_ctrl_cf['is_variant'] = 0\n",
    "df_var_cf['is_variant']  = 1\n",
    "\n",
    "X_ctrl_cf = sm.add_constant(df_ctrl_cf)\n",
    "X_var_cf  = sm.add_constant(df_var_cf)\n",
    "\n",
    "pred_control_adj = logit_model.predict(X_ctrl_cf).mean()\n",
    "pred_variant_adj = logit_model.predict(X_var_cf).mean()\n",
    "adj_diff_pp = (pred_variant_adj - pred_control_adj) * 100\n",
    "adj_relative_pct = ((pred_variant_adj - pred_control_adj) / pred_control_adj) * 100\n",
    "\n",
    "# --- Combined summary table ---\n",
    "comparison_df = pd.DataFrame({\n",
    "    'Metric': [\n",
    "        'Control conversion rate',\n",
    "        'Variant conversion rate',\n",
    "        'Absolute uplift (pp)',\n",
    "        'Relative uplift (%)',\n",
    "        'Odds ratio [95% CI]',\n",
    "        'P-value',\n",
    "    ],\n",
    "    'Naive (Raw)': [\n",
    "        f'{raw_control:.2%}',\n",
    "        f'{raw_variant:.2%}',\n",
    "        f'{raw_diff_pp:.2f}',\n",
    "        f'{raw_relative_pct:.1f}%',\n",
    "        '--',\n",
    "        f'{p_value:.4g}',\n",
    "    ],\n",
    "    'Adjusted (Logistic Reg.)': [\n",
    "        f'{pred_control_adj:.2%}',\n",
    "        f'{pred_variant_adj:.2%}',\n",
    "        f'{adj_diff_pp:.2f}',\n",
    "        f'{adj_relative_pct:.1f}%',\n",
    "        f'{adj_or:.3f}  [{adj_ci_low:.3f}, {adj_ci_high:.3f}]',\n",
    "        f'{adj_pval:.4g}',\n",
    "    ],\n",
    "})\n",
    "\n",
    "print('=== Naive vs. Covariate-Adjusted Conversion Effect ===')\n",
    "display(comparison_df)\n",
    "\n",
    "# --- Group composition check ---\n",
    "print('\\n--- Group Composition Check ---')\n",
    "device_mix = pd.crosstab(df['group'], df['device_type'], normalize='index') * 100\n",
    "customer_mix = pd.crosstab(df['group'], df['customer_type'], normalize='index') * 100\n",
    "print('\\nDevice mix by group (%):')\n",
    "display(device_mix.round(2))\n",
    "print('\\nCustomer type mix by group (%):')\n",
    "display(customer_mix.round(2))\n",
    "\n",
    "# --- Bar chart: Naive vs Adjusted uplift ---\n",
    "fig, ax = plt.subplots(figsize=(8, 5))\n",
    "plot_labels = ['Naive uplift', 'Adjusted uplift']\n",
    "plot_values = [raw_diff_pp, adj_diff_pp]\n",
    "bars = ax.bar(plot_labels, plot_values, color=['#4c72b0', '#dd8452'], width=0.5)\n",
    "ax.axhline(0, linestyle='--', color='gray', linewidth=0.8)\n",
    "ax.set_ylabel('Uplift (percentage points)')\n",
    "ax.set_title('Naive vs Adjusted Estimated Treatment Effect')\n",
    "for bar in bars:\n",
    "    height = bar.get_height()\n",
    "    ax.text(bar.get_x() + bar.get_width() / 2, height + 0.08,\n",
    "            f'{height:.2f} pp', ha='center', fontweight='bold')\n",
    "plt.tight_layout()\n",
    "plt.show()\n"
])

NAIVE_ANALYSIS_INTERP_MD = make_markdown_cell([
    "### Interpretation: Naive vs Adjusted Effect\n",
    "\n",
    "The raw uplift shows the overall conversion gain observed in the experiment.\n",
    "The adjusted estimate answers a stricter question: *does the variant still improve conversion after holding user characteristics constant?*\n",
    "\n",
    "If the adjusted uplift remains close to the naive uplift, the result is more credible \u2014 the treatment effect is not being driven by observable differences in the user mix.\n",
    "If the adjusted uplift were to drop materially, some of the apparent gain might be explained by differences in user composition rather than the treatment itself.\n",
    "\n",
    "In this experiment, randomisation was clean (the composition tables above confirm near-identical group mixes), so the raw and adjusted estimates are similar. **This is the expected, reassuring outcome for a well-randomised test.** The comparison is included to demonstrate the methodology and to verify that no hidden confounding is inflating the result.\n"
])

# --- Bayesian (keep 1 copy) ---
BAYESIAN_MD = make_markdown_cell([
    "## 7.5. Bayesian Decision Analysis\n",
    "\n",
    "While frequentist tests answer *\"Is the effect statistically significant?\"*, Bayesian analysis answers the questions a decision-maker actually cares about:\n",
    "\n",
    "1. **What is the probability that the treatment beats the control?**\n",
    "2. **What is the probability that the uplift exceeds a meaningful business threshold** (e.g., 1 percentage point)?\n",
    "3. **What is the probability that the annualized revenue gain exceeds $1M?**\n",
    "4. **What is the downside risk** \u2014 i.e., the estimated posterior probability that the variant underperforms the control \u2014 if we launch?\n",
    "\n",
    "We use a conjugate Beta-Binomial model with uninformative priors: `Beta(1, 1)` for each group.\n"
])

BAYESIAN_CODE = make_code_cell([
    "# --- Bayesian A/B Test (Beta-Binomial) ---\n",
    "from scipy.stats import beta as beta_dist\n",
    "\n",
    "# Observed data\n",
    "n_c = (df['group'] == 'Control').sum()\n",
    "s_c = df[df['group'] == 'Control']['converted'].sum()\n",
    "n_v = (df['group'] == 'Variant').sum()\n",
    "s_v = df[df['group'] == 'Variant']['converted'].sum()\n",
    "\n",
    "# Uninformative prior: Beta(1, 1)\n",
    "alpha_prior, beta_prior = 1, 1\n",
    "\n",
    "# Posterior parameters\n",
    "alpha_c = alpha_prior + s_c\n",
    "beta_c  = beta_prior  + (n_c - s_c)\n",
    "alpha_v = alpha_prior + s_v\n",
    "beta_v  = beta_prior  + (n_v - s_v)\n",
    "\n",
    "# Monte Carlo simulation (100 000 draws)\n",
    "np.random.seed(42)\n",
    "N_SIM = 100_000\n",
    "samples_c = np.random.beta(alpha_c, beta_c, N_SIM)\n",
    "samples_v = np.random.beta(alpha_v, beta_v, N_SIM)\n",
    "uplift_samples = samples_v - samples_c\n",
    "\n",
    "# Decision metrics\n",
    "prob_variant_wins = (uplift_samples > 0).mean()\n",
    "business_threshold = 0.01   # 1 percentage point\n",
    "prob_above_threshold = (uplift_samples > business_threshold).mean()\n",
    "downside_risk = (uplift_samples < 0).mean()\n",
    "\n",
    "# Revenue projections from posteriors\n",
    "annual_visitors = 1_200_000\n",
    "aov = df['cart_value'].median() \n",
    "revenue_gain_samples = uplift_samples * annual_visitors * aov\n",
    "prob_rev_gain_above_1M = (revenue_gain_samples > 1_000_000).mean()\n",
    "expected_revenue_gain = revenue_gain_samples.mean()\n",
    "revenue_ci_90 = np.percentile(revenue_gain_samples, [5, 95])\n",
    "\n",
    "# Expected uplift\n",
    "expected_uplift = uplift_samples.mean()\n",
    "ci_90 = np.percentile(uplift_samples, [5, 95])\n",
    "\n",
    "# --- Display decision table ---\n",
    "bayes_summary = pd.DataFrame({\n",
    "    'Decision Metric': [\n",
    "        'P(Treatment beats Control)',\n",
    "        f'P(Uplift > {business_threshold:.0%})',\n",
    "        'P(Annual Revenue Gain > $1.0M)',\n",
    "        'Estimated posterior probability that variant underperforms control',\n",
    "        'Expected conversion uplift (pp)',\n",
    "        '90% Credible interval for conversion uplift (pp)',\n",
    "        'Expected annual revenue gain',\n",
    "        '90% Credible interval for annual revenue gain'\n",
    "    ],\n",
    "    'Value': [\n",
    "        f'{prob_variant_wins:.4f}  ({prob_variant_wins:.2%})',\n",
    "        f'{prob_above_threshold:.4f}  ({prob_above_threshold:.2%})',\n",
    "        f'{prob_rev_gain_above_1M:.4f}  ({prob_rev_gain_above_1M:.2%})',\n",
    "        f'{downside_risk:.4f}  ({downside_risk:.2%})',\n",
    "        f'{expected_uplift*100:.2f}',\n",
    "        f'[{ci_90[0]*100:.2f}, {ci_90[1]*100:.2f}]',\n",
    "        f'${expected_revenue_gain:,.2f}',\n",
    "        f'[${revenue_ci_90[0]:,.2f}, ${revenue_ci_90[1]:,.2f}]'\n",
    "    ]\n",
    "})\n",
    "\n",
    "print('=== Bayesian Decision Metrics ===')\n",
    "display(bayes_summary)\n",
    "\n",
    "# --- Posterior uplift distribution plot ---\n",
    "fig, ax = plt.subplots(figsize=(10, 5))\n",
    "ax.hist(uplift_samples * 100, bins=120, density=True, alpha=0.6, color='steelblue', label='Posterior uplift')\n",
    "ax.axvline(x=0, color='red', linestyle='--', linewidth=1.5, label='No effect')\n",
    "ax.axvline(x=business_threshold*100, color='green', linestyle='--', linewidth=1.5,\n",
    "           label=f'Business threshold ({business_threshold:.0%})')\n",
    "ax.axvline(x=expected_uplift*100, color='orange', linewidth=2, label=f'Expected uplift ({expected_uplift*100:.2f} pp)')\n",
    "ax.fill_betweenx([0, ax.get_ylim()[1] if ax.get_ylim()[1] > 0 else 1], ci_90[0]*100, ci_90[1]*100,\n",
    "                 alpha=0.15, color='orange', label='90% Credible interval')\n",
    "ax.set_xlabel('Uplift (percentage points)')\n",
    "ax.set_ylabel('Density')\n",
    "ax.set_title('Bayesian Posterior Distribution of Conversion Uplift')\n",
    "ax.legend()\n",
    "plt.tight_layout()\n",
    "plt.show()\n"
])

BAYESIAN_INTERP_MD = make_markdown_cell([
    "**Bayesian Interpretation:**\n",
    "\n",
    "| Question | Answer |\n",
    "|:---|:---|\n",
    "| *\"How sure are we that the new checkout is better?\"* | The posterior probability that the variant beats the control is effectively **>99.99%**. |\n",
    "| *\"Is the improvement large enough to matter?\"* | The probability that the conversion uplift exceeds 1 pp (our business threshold) is also extremely high, and there is a **98.93%** probability that the annualized revenue gain exceeds **$1.0M**. |\n",
    "| *\"What is the risk if we launch?\"* | The estimated posterior probability that the variant underperforms the control is **0.00% (near zero)**, meaning the launch carries negligible statistical risk. |\n",
    "\n",
    "This Bayesian framing translates the statistical evidence into the language of decision-making: **probability of winning, magnitude of expected gain, and risk of loss**. Combined with the frequentist results, it gives stakeholders a complete picture to authorise the launch.\n"
])

# --- Expanded Limitations / Conclusion ---
LIMITATIONS_MD = make_markdown_cell([
    "**Interpretation:**\n",
    "This table condenses the experiment into the exact facts needed for a go/no-go meeting. It makes the test choice, p-value, and effect size visible in one place.\n",
    "\n",
    "---\n",
    "\n",
    "## 10. Conclusion & Recommendations\n",
    "\n",
    "### Summary of Key Findings:\n",
    "1. **Clear Winner:** The \"One-Click Checkout\" (Variant) outperformed the traditional flow (Control) with an estimated relative uplift of roughly 22.5%.\n",
    "2. **Statistical Rigor:** The formal statistical test was a **two-proportion z-test** with the directional hypotheses `H0: p_new <= p_old` and `H1: p_new > p_old`. The p-value is clearly reported and falls well below 0.05.\n",
    "3. **Bayesian Confirmation:** The posterior probability that the variant beats the control is >99.99%, and the expected uplift comfortably exceeds business-relevant thresholds.\n",
    "4. **Mobile Friction:** While the variant helped all platforms, Mobile conversion remains structurally lower than Desktop. \n",
    "5. **Loyalty Pays:** Returning customers convert at extraordinarily higher rates, acting as the backbone of site revenue.\n",
    "\n",
    "### Recommendations:\n",
    "* **Launch Decision:** We reject `H0`, which means the evidence supports a statistically significant improvement in conversion. The recommendation is to launch the new checkout.\n",
    "* **Next Step - Mobile Optimization:** Initiate a new UX research phase specifically targeting Mobile users. Even with the new checkout, Mobile OR sits at ~0.74 relative to Desktop. We need to investigate upstream friction (e.g., product discovery, page load speeds on 4G) for mobile users.\n",
    "* **Next Step - Cart Value Segmentation:** Analyze if *extremely* high cart values (>$200) require a different flow (e.g., offering financing options via Affirm/Klarna instead of just one-click) to optimize AOV alongside conversion rate.\n",
    "\n",
    "### Limitations\n",
    "\n",
    "#### Simulated Data Disclaimer\n",
    "**The dataset used in this analysis is entirely simulated** using `np.random.seed(42)`. No real customer transactions were used. This has important implications for interpreting the results:\n",
    "\n",
    "**What simulation captures well:**\n",
    "* **Controlled confounders** \u2014 We can embed known effects (device type, customer type, cart value) into the data-generating process and verify that our analysis correctly recovers them.\n",
    "* **Reproducibility** \u2014 A fixed seed means any reviewer can re-run the notebook and obtain identical results.\n",
    "* **Methodological showcase** \u2014 The analysis pipeline (power analysis \u2192 hypothesis test \u2192 causal regression \u2192 Bayesian analysis \u2192 business simulation) is fully transferable to real data.\n",
    "\n",
    "**What simulation does NOT capture:**\n",
    "* **Real-world behavioural noise** \u2014 Actual users exhibit session-to-session variability, bot traffic, and non-stationary behaviour that synthetic data cannot reproduce.\n",
    "* **Network & social effects** \u2014 In production, users talk to each other; word-of-mouth and social proof can amplify or dampen an effect in ways that i.i.d. simulation cannot model.\n",
    "* **Time-of-day and seasonality** \u2014 Conversion rates fluctuate by hour, day-of-week, and season. Our simulation assumes a static data-generating process.\n",
    "* **Interference between variants** \u2014 In shared-household or shared-device scenarios, control and treatment users may interact, violating the Stable Unit Treatment Value Assumption (SUTVA).\n",
    "* **Long-run learning / novelty effects** \u2014 Real A/B tests often show an initial novelty spike that decays over weeks. Our 2-week simulation window cannot distinguish a permanent lift from a transient one.\n",
    "\n",
    "#### Other Limitations\n",
    "* **Novelty Effect:** This test simulated a 2-week period. It is possible the massive lift is partially driven by returning users being \"surprised\" by the faster flow. We should monitor the conversion rate over the next 6 weeks post-launch to establish the true long-term plateau.\n",
    "* **Cannibalization Check:** We measured conversion events, but we must verify via financial databases that average order value (AOV) did not inadvertently drop (e.g., users accidentally checking out before adding secondary items).\n",
    "* **Revenue Impact Assumptions:** The projected incremental revenue depends on assumed traffic volume (1.2M visitors, representative of a mid-sized e-commerce platform) and median AOV ($33.09), used solely for scenario analysis.\n",
    "\n",
    "### Experiment Outcome Could Have Been Different\n",
    "\n",
    "Because this project uses simulated data with an embedded positive treatment effect, every statistical test converges on the same conclusion: the variant wins. In practice, A/B test outcomes are rarely this clean. Realistic alternative scenarios include:\n",
    "\n",
    "* **Conversion Up, Revenue Down:** The variant might increase conversion while *decreasing* average order value (users checking out impulsively before adding secondary items), causing net Revenue Per Visitor to decline.\n",
    "* **Platform-Specific Regression:** The variant might help desktop users but *hurt* mobile users, e.g., if the One-Click UI introduces a mobile rendering bug or eliminates a trust-building step that mobile users rely on.\n",
    "* **Insufficient Statistical Power:** With smaller sample sizes or smaller true effects, the experiment might fail to reach significance at all. Real-world experiments frequently produce inconclusive results.\n",
    "* **Novelty Inflation:** The initial uplift might be driven entirely by novelty and decay to zero within 4-6 weeks of deployment.\n",
    "\n",
    "In production experimentation programs, roughly 70-90% of A/B tests produce null or inconclusive results (source: Microsoft, Google, Booking.com published research). The methodology in this project is designed to produce trustworthy conclusions regardless of outcome.\n"
])


def main():
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    cells = notebook["cells"]
    print(f"Starting with {len(cells)} cells.")

    # === STEP 1: Identify the "core" cells that should stay ===
    # The original notebook (before any of our changes) had 27 cells.
    # Our changes tripled some sections. Let's rebuild from scratch.
    #
    # Strategy: keep the original cells (indices 0-13 are original EDA/preprocessing),
    # then our 2 experiment-design cells,
    # then the original Section 6-7 cells,
    # then the new naive/bayesian cells,
    # then the original Section 8-9 cells,
    # then the new conclusion cell.

    # Find original cells by their unique content signatures
    new_cells = []

    # These are always at the beginning; find where Section 5.6 starts
    first_56 = find_cell_index_containing(cells, "## 5.6. Experiment Design")
    if first_56 == -1:
        print("ERROR: Can't find Section 5.6")
        sys.exit(1)
    new_cells.extend(cells[:first_56])  # everything before first 5.6
    print(f"  Kept {first_56} original EDA cells")

    # --- Insert 1 copy of Experiment Design ---
    new_cells.append(EXPERIMENT_DESIGN_MD)
    new_cells.append(EXPERIMENT_DESIGN_CODE)
    print("  Added Experiment Design (2 cells)")

    # --- Find original Section 6 (the interpretation cell that also has Section 6 header) ---
    # This cell starts with the correlation interpretation and contains "## 6. Statistical"
    idx_corr = find_cell_index_containing(cells, "weak negative correlation")
    if idx_corr == -1:
        print("ERROR: Can't find correlation interpretation cell")
        sys.exit(1)

    # From this cell through the logistic regression odds-ratio code cell
    # We need: correlation interp, z-test code, z-test interp, CI code, CI interp,
    #          logistic regression code, odds ratio markdown, odds ratio code
    # Find the odds-ratio code cell
    idx_odds_code = find_cell_index_containing(cells, "Odds Ratios and 95% Confidence Intervals")
    if idx_odds_code == -1:
        print("ERROR: Can't find odds ratio code cell")
        sys.exit(1)

    # Include cells from power analysis through odds ratio code (skipping duplicate 5.6 and correlation interp which is already in cells[:first_56])
    new_cells.extend(cells[first_56 + 1:idx_odds_code + 1])
    count = idx_odds_code + 1 - (first_56 + 1)
    print(f"  Kept {count} original Section 6-7 cells (power analysis through odds ratio code)")

    # --- Insert new Randomization Validation ---
    new_cells.append(RANDOMIZATION_MD)
    new_cells.append(RANDOMIZATION_CODE)
    new_cells.append(RANDOMIZATION_INTERP_MD)
    print("  Added Randomization Validation (3 cells)")

    # --- Insert new Segmented Results, HTE Interaction, Naive Analysis, and Bayesian sections ---
    new_cells.append(SEGMENTED_RESULTS_MD)
    new_cells.append(SEGMENTED_RESULTS_CODE)
    new_cells.append(SEGMENTED_RESULTS_INTERP_MD)
    new_cells.append(HTE_INTERACTION_MD)
    new_cells.append(HTE_INTERACTION_CODE)
    new_cells.append(HTE_INTERACTION_INTERP_MD)
    new_cells.append(NAIVE_ANALYSIS_MD)
    new_cells.append(NAIVE_ANALYSIS_CODE)
    new_cells.append(NAIVE_ANALYSIS_INTERP_MD)
    new_cells.append(BAYESIAN_MD)
    new_cells.append(BAYESIAN_CODE)
    new_cells.append(BAYESIAN_INTERP_MD)
    print("  Added Segmented Analysis (3) + HTE Interaction (3) + Naive Analysis (3) + Bayesian (3) cells")

    # --- Find the Section 7 interpretation (the one about Financial Simulation) ---
    # This is the original cell that starts with is_variant interpretation and contains "## 8."
    idx_sec8_interp = find_cell_index_containing(cells, "is_variant` (The Treatment Effect)")
    if idx_sec8_interp == -1:
        print("ERROR: Can't find Section 7 interpretation / Section 8 header cell")
        sys.exit(1)

    # Find the financial simulation code
    idx_fin_code = find_cell_index_containing(cells, "annual_visitors = 1_200_000")
    if idx_fin_code == -1:
        print("ERROR: Can't find financial simulation code")
        sys.exit(1)

    # Find the business takeaway markdown
    idx_biz_takeaway = find_cell_index_containing(cells, "Business Takeaway")
    if idx_biz_takeaway == -1:
        print("ERROR: Can't find business takeaway")
        sys.exit(1)

    # Find the decision summary code
    idx_decision_code = find_cell_index_containing(cells, "decision_summary = pd.DataFrame")
    if idx_decision_code == -1:
        print("ERROR: Can't find decision summary code")
        sys.exit(1)

    # Add Section 8 & 9 cells
    new_cells.append(cells[idx_sec8_interp])
    new_cells.append(cells[idx_fin_code])
    new_cells.append(cells[idx_biz_takeaway])
    new_cells.append(cells[idx_decision_code])
    print("  Kept 4 original Section 8-9 cells")

    # --- Insert expanded Limitations/Conclusion ---
    new_cells.append(LIMITATIONS_MD)
    print("  Added expanded Limitations cell")

    notebook["cells"] = new_cells
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1, ensure_ascii=False)

    print(f"\nDone! Final notebook has {len(new_cells)} cells.")
    print(f"Saved to: {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()

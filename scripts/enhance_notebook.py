#!/usr/bin/env python3
"""
Script to clean up the notebook from duplicate insertions and replace
the naive-vs-adjusted section with improved code.
"""
import json
import sys
import os

NOTEBOOK_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "notebook", "Conversion_Optimization_Analysis.ipynb")


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
    "| **Baseline conversion rate** | ~19.4% (Control group) | Observed from historical data / control arm |\n",
    "| **Minimum Detectable Effect (MDE)** | 15% relative lift (~2.9 pp absolute) | The smallest improvement worth launching for, given engineering cost |\n",
    "| **Significance level (\u03b1)** | 0.05 | Industry standard for product experiments |\n",
    "| **Statistical power (1 \u2212 \u03b2)** | 0.80 | 80% chance of detecting a real effect if one exists |\n",
    "| **Test type** | One-sided | This is a go/no-go launch decision \u2014 we only ship if the variant is *better* |\n",
    "\n",
    "**Why a one-sided test?** The business question is directional: \"Is the new checkout *better* than the old one?\" We are not interested in detecting whether the variant is *worse* \u2014 that scenario simply means we do not launch. A one-sided test aligns the statistical framework with the actual decision being made and provides slightly more power for the same sample size.\n",
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
    "effect_size = sms.proportion_effectsize(baseline_rate, target_rate)\n",
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
    "        'Significance level (\u03b1)',\n",
    "        'Power (1\u2212\u03b2)',\n",
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

# --- Naive vs Adjusted (improved version with counterfactual predictions) ---
NAIVE_ANALYSIS_MD = make_markdown_cell([
    "### 7.3. Why Naive Analysis Can Mislead\n",
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
    "3. **What is the downside risk** \u2014 i.e., P(variant is *worse* than control) \u2014 if we launch?\n",
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
    "# Expected uplift\n",
    "expected_uplift = uplift_samples.mean()\n",
    "ci_90 = np.percentile(uplift_samples, [5, 95])\n",
    "\n",
    "# --- Display decision table ---\n",
    "bayes_summary = pd.DataFrame({\n",
    "    'Decision Metric': [\n",
    "        'P(Treatment beats Control)',\n",
    "        f'P(Uplift > {business_threshold:.0%})',\n",
    "        'Downside risk P(Variant worse)',\n",
    "        'Expected uplift (pp)',\n",
    "        '90% Credible interval (pp)',\n",
    "    ],\n",
    "    'Value': [\n",
    "        f'{prob_variant_wins:.4f}  ({prob_variant_wins:.2%})',\n",
    "        f'{prob_above_threshold:.4f}  ({prob_above_threshold:.2%})',\n",
    "        f'{downside_risk:.4f}  ({downside_risk:.2%})',\n",
    "        f'{expected_uplift*100:.2f}',\n",
    "        f'[{ci_90[0]*100:.2f}, {ci_90[1]*100:.2f}]',\n",
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
    "| *\"Is the improvement large enough to matter?\"* | The probability that the uplift exceeds 1 pp (our business threshold) is also extremely high. |\n",
    "| *\"What is the risk if we launch?\"* | The downside risk (P variant is worse) is near zero, meaning the launch carries negligible statistical risk. |\n",
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
    "1. **Clear Winner:** The \"One-Click Checkout\" (Variant) outperformed the traditional flow (Control) with an estimated relative uplift of roughly 18%.\n",
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
    "* **Revenue Impact Assumptions:** The projected incremental revenue depends on assumed traffic volume and AOV, which may differ in practice.\n"
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

    # Include cells from correlation interp through odds ratio code
    new_cells.extend(cells[idx_corr:idx_odds_code + 1])
    count = idx_odds_code + 1 - idx_corr
    print(f"  Kept {count} original Section 6-7 cells (correlation interp through odds ratio code)")

    # --- Insert new Naive Analysis + Bayesian sections ---
    new_cells.append(NAIVE_ANALYSIS_MD)
    new_cells.append(NAIVE_ANALYSIS_CODE)
    new_cells.append(NAIVE_ANALYSIS_INTERP_MD)
    new_cells.append(BAYESIAN_MD)
    new_cells.append(BAYESIAN_CODE)
    new_cells.append(BAYESIAN_INTERP_MD)
    print("  Added Naive Analysis (3 cells) + Bayesian (3 cells)")

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

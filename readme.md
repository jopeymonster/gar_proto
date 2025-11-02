<p align="center">
  <img src="docs/logo.png" alt="Google Ads Reporter Logo" width="400"/>
</p>

# Google Ads Reporter

Google Ads Reporter is a command-line package that authenticates against the Google Ads API, executes curated GAQL queries, and presents the results in both **interactive console mode** and **direct CLI mode**.

---

## Features

* Built on Python 3.11+ with the official `google-ads` client library.
* Uses gRPC to communicate with the Google Ads API.
* Interactive menus for **performance, audit, and budgeting reports**.
* CLI arguments for automation (headless mode).
* Supports both **OAuth** and **Service Account** authentication.
* CSV/JSON export modes available.

---

## Report Types

The reporter supports multiple reporting scopes, each with its own options:

- **Performance Reports**  
  Break down campaign, ad group, and ad-level metrics. Supports toggles such as devices, channels, and campaign info.  

- **Audit Reports**  
  Provide diagnostic views of labels, campaign groups, and label assignments to help validate account hygiene and consistency.  

- **Budget Reports**  
  Summarize spend, pacing, and related KPIs across single or multiple accounts.

  
### Performance

- **MAC (Marketing Attribution Code)**
  A custom extension for deeper analysis.
  - Embed a custom identifier in your campaign naming convention:
    ```
    Campaign Name :marketing_attribution_code
    ```
    Examples:
    - `Nike Shoes - Holiday Sales :nikeholidaysales`
    - `Chicago - Legal - FRG :chi_frg_legal`
    - `GoogleAdsCampaign: MyCampaign :my_marketing_attribution_code`
  - Uses:
    - Audit UTM parameters against campaigns.
    - Link Ads activity with ERP or CRM systems.
    - Add a flexible reporting dimension for cross-channel analysis.
  - If no `:marketing_attribution_code` is present, the report will return `None`/blank.

---

- **Account**  
  High-level KPIs at the account level. Useful for executive summaries or quick health checks across accounts without drilling into campaign details.  

---

- **Ads**
  Campaign, ad group, and ad-level performance reporting.
  - Standard metrics: impressions, clicks, conversions, costs.
  - Dimensions: device breakdowns, channel type, campaign metadata.
  - Includes MAC values where available.

---

- **GLCID / Click View**  
  Exposes **click-level data** tied to Google Click Identifiers (GCLID).  
  - Shows both valid and invalid clicks.  
  - **Limitations**:  
    - Must query a **single day**.  
    - Only available for data within the **last 90 days**.  
  - Use cases: validating click-level tracking, fraud auditing, and attribution analysis.  

---

- **Paid & Organic Search Terms (POSTV)**  
  Combines paid ads + organic results at the query level.  
  - Aggregated at **ad group scope**.  
  - Available metrics include:  
    - Paid CPC, organic clicks, combined impressions, query frequency.  
  - Ideal for identifying **keyword gaps** or measuring **incremental lift** when ads + organic overlap.  

---

### Auditing

- **Account Labels**  
  Fetches all labels assigned to the account for review.  
  - Does not return any associating campaigns, ad groups, or ads.  
  - Use cases: verifying naming conventions and label hygiene.  

---

- **Campaign Groups**  
  Returns the account's current campaign groups by name and ID.
  - Does not return any associating campaigns, ad groups, or ads.  
  - Use cases: confirming campaign group assignments, validating group-level strategy.  

---

- **Campaign and Ad Group Label Audit**  
  Obtains all campaign group and label designations for campaign and ad group scopes.  
  - Includes campaign/ad group details and applied labels.  
  - Use cases: checking compliance with internal naming/labeling standards, surfacing unlabeled assets.  

---

### Budgeting

- **Budget Overview**  
  Summarizes monthly budgets, current spend, and pacing.  
  - View across one or multiple accounts.  
  - Use cases: monitoring over/under-spend, pacing against plan, budget caps.  

---

- **Under Construction**  
  Future enhancements may include:  
  - Forecasting based on historical spend + seasonality.  
  - Budget vs performance efficiency scoring.  
  - Alerts for anomalies or pacing concerns.  

---

## Installation

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/jopeymonster/gar_proto.git
cd gar_proto
python -m venv .venv
source .venv/bin/activate   # or `.venv\Scripts\activate` on Windows
pip install --upgrade pip
pip install -r requirements.txt
```

You can also install it in **editable mode** for development:

```bash
pip install -e .
```

This registers the package so you can run it anywhere with:

```bash
python -m gar
```

---

## Authentication

1. **Create or select a Google Cloud project.** Enable the Google Ads API.
2. **Choose authentication type:**

   * **OAuth client credentials**: client ID/secret + refresh token.
   * **Service account credentials**: JSON key file with delegated access.
3. **Prepare configuration file:**

   * Copy `gar/google-ads-template.yaml` to a local path.
   * Fill in:

     * Developer token
     * Manager (login) customer ID
     * OAuth or Service account values
   * Save as `google-ads.yaml`.
4. **Reference config file at runtime** with `--yaml` if not in the default location.

**Important:** keep `google-ads.yaml` out of version control.

For additional background, consult the [Google Ads API getting started guide](https://developers.google.com/google-ads/api/docs/get-started/oauth-cloud-project).

---

## Usage

### Interactive Mode (default)

```bash
python -m gar
```

Drops you into an interactive workflow for selecting reports, accounts, and export options.

### CLI Mode (automation)

Provide arguments to skip menus:

```bash
# Run a performance report on account 1234567890
python -m gar --report performance:ads --account single:1234567890 --output csv --yaml authfiles/google-ads.yaml
```

**Examples:**

* Report with report scope + option:

  ```bash
  python -m gar --report performance:mac
  ```
* Account targeting:

  ```bash
  python -m gar --account single:1234567890
  python -m gar --account all
  ```
* Date ranges:

  ```bash
  python -m gar --date last30days
  python -m gar --date specific:2025-01-15
  ```
* Toggles:

  ```bash
  python -m gar --device include
  python -m gar --channel-types exclude
  ```

Run `python -m gar --help` for the full argument list.

---

## Development & Contributing

1. **Branching strategy**

   * `codex`: agent-driven experiments
   * `develop`: integration before `main`
   * `main`: stable, tagged releases
   * `f01.x`: feature scratchpad branches
   * `issues`: critical bugfixes

2. **Workflow**

   * Work from feature branches (`f01.2`, etc.).
   * Submit PRs > `develop` > `main`.
   * `main` and `develop` are protected (no direct pushes).

3. **Before committing**

   ```bash
   ruff check .
   ruff format .
   pytest
   ```

4. **Pull Requests**

   * Include test coverage for new args/features.
   * Keep docstrings and CLI help updated.

---

## License

This project is licensed under the [MIT License](LICENSE).

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## Contributors

* Joe Thompson (@jopeymonster)

---

## Legal

The developers and contributors of this application, and all logic found within, are not responsible for actions taken using this application or services.
Your privacy is respected when using our products and our [Privacy Policy](https://jopeymonster.github.io/privacy/) applies.

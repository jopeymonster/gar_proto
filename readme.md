# Google Ads Reporter

Google Ads Reporter is a command-line tool that authenticates against the Google Ads API, executes curated GAQL queries, and presents the results in an interactive console workflow.

## Overview

- Built with Python and the official `google-ads` client library.
- Uses gRPC to communicate with the Google Ads API.
- Supports automated account discovery and multiple reporting menus (performance, auditing, budgeting).

## Prerequisites

- Python 3.11 or later.
- Access to a Google Ads manager account with a valid developer token.
- Permission to enable and use the Google Ads API within a Google Cloud project.

## Authentication Workflow

1. **Create or select a Google Cloud project.** Enable the Google Ads API in the Google Cloud Console.
2. **Decide on your credential type.**
   - *OAuth client credentials*: create OAuth client ID and client secret, then generate a refresh token for the Google Ads manager account.
   - *Service account credentials*: create a service account, delegate access to the Google Ads manager account, and download the JSON key file.
3. **Prepare the configuration file.**
   - Copy `google-ads-template.yaml` from this repository.
   - Fill in your developer token, login customer ID (manager account), and the credential values that correspond to your chosen auth method.
   - Reference any JSON key file paths exactly as they exist on your machine.
4. **Save the file as `google-ads.yaml`.** Place it next to `main.py`, or provide a full path at runtime.
5. **Verify connectivity.** The application validates the file during startup and exits with an error if the configuration or credentials are incomplete.

For additional background, consult the [Google Ads API getting started guide](https://developers.google.com/google-ads/api/docs/get-started/oauth-cloud-project).

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Usage

Run the interactive reporter from the project root:

```bash
python main.py
```

To point to a configuration file in another location, supply the path via `--yaml` (short form `-y`):

```bash
python main.py --yaml /path/to/google-ads.yaml
```

Once authenticated, follow the on-screen prompts to select the account scope and reporting menu you need. The tool retrieves data, displays tabular summaries, and offers export options through the helper prompts.

## Standard Workflow Guidelines

1. Activate the virtual environment for every session (`source .venv/bin/activate`).
2. Keep `google-ads.yaml` outside of version control; use the provided template for local copies.
3. Run automated tests before committing changes:
   ```bash
   pytest
   ```
4. When adding new reporting logic, mirror the existing patterns in `services.py`, `helpers.py`, and `prompts.py` to maintain consistent menu flows and data handling.

## License

This project is licensed under the [MIT License](LICENSE).

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Contributors

- Joe Thompson (@jopeymonster)
- https://github.com/jopeymonster

## Legal Notice

The developers and contributors of this application, and all logic found within, are not responsible for actions taken using this application or services.

Your privacy is respected when using our products and our **Privacy Policy** can be found here: [https://jopeymonster.github.io/privacy/](https://jopeymonster.github.io/privacy/)

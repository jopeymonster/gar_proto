# Google Ads Reporter
This is a CLI application automates the fetching and reporting of Google Ads data.
Reporting options are available in limited format.

## Features
This application was designed using Python and communciates with the Google Ads API using gRPC methods. 
It is designed to be compliant with networking and API constraints.

## Installation
Requires a valid YAML configuration file for Google Ads API authentication.  
Information and setup guides can be found here: [Setup a Google API Console project](https://developers.google.com/google-ads/api/docs/get-started/oauth-cloud-project)

The YAML file should contain the the developer token (required) and one of the following combinations of credentials:
- OAuth2 credentials: client ID, client secret, refresh token
- Service account credentials: service-account.json file obtain through Google Cloud Project

The file should be named 'google-ads.yaml' and located in the same directory as the 'main.py' file.
The script will check if the YAML file exists and is valid before proceeding.
If the YAML file is not found or is invalid, an error message will be printed and the script will exit.

## Usage
This app supports ingestion of a different YAML file using argparse:
"-y", "--yaml"

EXAMPLE:
python main.py /path/to/google-ads.yaml

Ensure the path to your JSON authorization file (client-secrets/service-account) is present in the YAML.

## License
This project is licensed under the [MIT License](LICENSE).

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Contributors
- Joe Thompson (@jopeymonster)
- https://github.com/jopeymonster

## Legal Notice

The developers and contributors of this application, and all logic found within, are not responsible for actions taken using this application or services.

Your privacy is respected when using our products and our **Privacy Policy** can be found here:
[https://jopeymonster.github.io/privacy/](https://jopeymonster.github.io/privacy/)
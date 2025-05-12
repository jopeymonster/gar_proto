# updated - 5/5/25

# imports
import os
import sys

# gads
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

def generate_services(yaml_loc=None):
    """
    Authenticates the Google Ads client using the provided YAML file and generates the service for use in API calls.
    
    Requires a valid YAML configuration file for Google Ads API authentication.
    The YAML file must be created following the instructions in the README file and placed in the authfiles directory.
    
    The YAML file should contain the the developer token (required) and one of the following combinations of credentials:
     - OAuth2 credentials: client ID, client secret, refresh token
     - Service account credentials: service-account.json file obtain through Google Cloud Project

    The file should be named 'gads_auth.yaml' and located in the 'authfiles' directory.
    The 'authfiles' directory should be in the same directory as this script.
    The script will check if the YAML file exists and is valid before proceeding.
    If the YAML file is not found or is invalid, an error message will be printed and the script will exit.

    Args:
        yaml_loc (str): Optional path to the YAML config file. If None, use default.
    
    Returns:
        gads_service (GoogleAdsService): The Google Ads service object, used for making API calls.
        client (GoogleAdsClient): The Google Ads client object used for authentication and configuration.
    """
    # establish vars
    if yaml_loc is None:
        YAML = "gads_auth.yaml" # default yaml file name
        filepath = os.path.dirname(os.path.realpath(__file__))
        auth_dir = os.path.join(filepath, "authfiles")
        yaml_loc = os.path.join(auth_dir, YAML)
    # check if yaml file exists
    if not os.path.exists(yaml_loc):
        print("The authorization process is incomplete...\n"
              f"ERROR: {yaml_loc} not found. Please check the file path.")
        sys.exit(1)
    # check if yaml file is valid
    try:
        client = GoogleAdsClient.load_from_storage(yaml_loc)
    except GoogleAdsException as ex:
        print(f"Google Ads API error: {ex}")
        sys.exit(1)
    # check if yaml file is valid
    if not client:
        print("Google Ads API client is not valid. Please check the file path.")
        sys.exit(1)
    if not client.developer_token:
        print("Google Ads API client is not valid. Please check the file path.")
        sys.exit(1)
    print(f"yaml loc: {yaml_loc}\n")
    gads_service = client.get_service("GoogleAdsService")
    return gads_service, client
# updated - 5/5/25

# imports
import os
import sys

# gads
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

def authenticate():
    """
    Authenticates the Google Ads API client using the provided YAML file.
    """
    # establish vars
    YAML = "gads_auth.yaml" # This file must be created following the instructions in the README file and placed in the authfiles directory.
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
    return client
"""
This file contains the account information for the Google Ads API.
All managed account information only (stand alone or sub accounts only)

Account dictionary structure:
{
    "Account Reference": ["Account ID", "Description"],
    ...
}

- Account Reference is an arbitrary identifier for the account
- Account ID is the 10 digit number used in the Google Ads API, referred to as the customer ID
- Description is the name of the account or the URL of the website

All managed accounts should be present in the 'PROP_INFO' dictionary. 
Properties/Accounts can be grouped for reporting purposes depending on the needs of the user.

Examples of the dictionary structure and property groups are provided below.
"""

# example account dictionary
PROP_INFO = {
"EXAMPLE1": ["1234567890", "Example Corp 1 / example.com"],
"EXAMPLE2": ["0987654321", "Example Corp 2 / example2.com"],
"EXAMPLE3": ["1122334455", "Example Corp 3 / example3.com"],
"EXAMPLE4": ["5566778899", "Example Corp 4 / example4.com"],
"EXAMPLE5": ["2233445566", "Example Corp 5 / example5.com"],
}

# Grouping of accounts
US_PROPS = ["EXAMPLE1", "EXAMPLE2"]
EU_PROPS = ["EXAMPLE3", "EXAMPLE4"]
AU_PROPS = ["EXAMPLE5"]
SOFTGOODS_PROPS = ["EXAMPLE1", "EXAMPLE2", "EXAMPLE3"]
HARDGROODS_PROPS = ["EXAMPLE4", "EXAMPLE5"]

CAMPAIGN_TYPES = [
"UNSPECIFIED",
"UNKNOWN",
"SEARCH",
"DISPLAY",
"SHOPPING",
"HOTEL",
"VIDEO",
"MULTI_CHANNEL",
"LOCAL",
"SMART",
"PERFORMANCE_MAX",
"LOCAL_SERVICES",
"TRAVEL",
"DEMAND_GEN"
]

REPORTING_OPTIONS = {
"1": "Account",
"2": "Campaign",
"3": "Ad Group",
"4": "GCLID",
"5": "Label",
"6": "Campaign Group",
}

AUDIT_OPTIONS = {
"1": "Ad Group",
"2": "Campaign",
"3": "Label",
"4": "Campaign Group",
}
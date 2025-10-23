# -*- coding: utf-8 -*-
import os
import sys
import requests
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.api_core.exceptions import TooManyRequests, ResourceExhausted, Unauthenticated
import helpers
import queries

def generate_services(yaml_loc=None):
    """
    Authenticates the Google Ads client using the provided YAML file and generates the service for use in API calls.
    
    Requires a valid YAML configuration file for Google Ads API authentication.
    
    The YAML file should contain the the developer token (required) and one of the following combinations of credentials:
     - OAuth2 credentials: client ID, client secret, refresh token
     - Service account credentials: service-account.json file obtain through Google Cloud Project

    The file should be named 'google-ads.yaml' and located in the same directory as the 'main.py' file.
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
        yaml_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), "google-ads.yaml")
    # check if yaml file exists
    if not os.path.exists(yaml_loc):
        print("The authorization process is incomplete...\n"
              f"ERROR: {yaml_loc} not found. Please check the file path.")
        sys.exit(1)
    else:
        print(f"Using YAML file: {yaml_loc}\n")
    try:
        client = GoogleAdsClient.load_from_storage(yaml_loc)
    except GoogleAdsException as ex:
        print(f"Google Ads API error: {ex}")
        sys.exit(1)
    # check if client file is valid
    if not client:
        print("Google Ads API client is not valid. Please check the file path.")
        sys.exit(1)
    if not client.developer_token:
        print("Google Ads API client is not valid. Please check the file path.")
        sys.exit(1)
    # print(f"yaml loc: {yaml_loc}\n")
    gads_service = client.get_service("GoogleAdsService")
    customer_service = client.get_service("CustomerService")
    return gads_service, customer_service, client

def get_accounts(gads_service, customer_service, client):
    """
    Fetches subaccounts (non-manager) under the authenticated MCC.

    Args: 
        Google Ads Authorized Client objects:
            - gads_service (GoogleAdsService): The Google Ads service object, used for making API calls.
            - customer_service (CustomerService): Google accounts service object, used for authorization and customer lookup.
            - client (GoogleAdsClient): The Google Ads client object used for authentication and configuration.

    Returns:
        tuple: (accounts_list, headers, accounts_dict, number_of_accounts)
    """
    customer_client_query = queries.customer_client_query()
    mcc_id = str(client.login_customer_id)
    mcc_response = gads_service.search_stream(customer_id=mcc_id, query=customer_client_query)
    accounts_list = []
    accounts_dict = {}
    for mcc_data in mcc_response:
        for row in mcc_data.results:
            if row.customer_client.manager:
                continue  # skip manager accounts, include only subaccounts
            account_id = str(row.customer_client.id)
            account_name = str(row.customer_client.descriptive_name)
            accounts_list.append([account_id, account_name])
            accounts_dict[account_id] = account_name
    headers = ["account id", "account name"]
    protected_accounts_dict = {str(k): str(v) for k, v in accounts_dict.items()}
    return accounts_list, headers, protected_accounts_dict, len(protected_accounts_dict)

"""
DECODERS/GETTERS
"""

def get_enums(client):
    """
    Fetches the enums for AdvertisingChannelType and AdGroupType from the Google Ads API client.

    Args: 
        client (GoogleAdsClient): The Google Ads client object used for authentication and configuration.

    Returns:
        tuple:
            - channel_type_enum
            - ad_group_type_enum
            - ad_type_enum
            - serp_type
            - click_type_enum
            - keyword_match_type_enum
            - device_type_enum
    """
    channel_type_enum = client.enums.AdvertisingChannelTypeEnum
    ad_group_type_enum = client.enums.AdGroupTypeEnum
    ad_type_enum = client.enums.AdTypeEnum
    serp_type_enum = client.enums.SearchEngineResultsPageTypeEnum
    click_type_enum = client.enums.ClickTypeEnum
    keyword_match_type_enum = client.enums.KeywordMatchTypeEnum
    device_type_enum = client.enums.DeviceEnum
    return channel_type_enum, ad_group_type_enum, ad_type_enum, serp_type_enum, click_type_enum, keyword_match_type_enum, device_type_enum

def get_labels(gads_service, client, customer_id):
    label_query = queries.label_query()
    label_response = gads_service.search_stream(customer_id=customer_id, query=label_query)
    label_dict = {}
    label_table = []
    for label_data in label_response:
        for row in label_data.results:
            label_id = str(row.label.id) # store label_id as a string
            label_name = row.label.name
            label_dict[label_id] = label_name
            label_table.append([
                label_name,
                label_id
            ])
    label_table_headers = [
        "Label Name",
        "Label ID"
    ]
    return label_table, label_table_headers, label_dict

def get_campaign_groups(gads_service, client, customer_id):
    camp_group_query = queries.camp_group_query()
    camp_group_response = gads_service.search_stream(customer_id=customer_id, query=camp_group_query)
    camp_group_dict = {}
    camp_group_table = []
    for camp_group_data in camp_group_response:
        for row in camp_group_data.results:
            camp_group_id = str(row.campaign_group.id) # store campaign_group_id as a string
            camp_group_name = row.campaign_group.name
            camp_group_dict[camp_group_id] = camp_group_name
            camp_group_table.append([
                camp_group_name,
                camp_group_id
            ])
    camp_group_headers = [
        "Campaign Group Name",
        "Campaign Group ID"
    ]
    return camp_group_table, camp_group_headers, camp_group_dict

# exceptions wrapper
def handle_exceptions(func):
    def print_error(func_name, error):
        print(f"\nError in function '{func_name}': {repr(error)} - Exiting...\n")
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        # GAds specific errors
        except Unauthenticated as e:
            print("Unable to authenticate or invalid credentials.  Please check your YAML or SECRETS file.")
            print_error(func.__name__, e)
        except GoogleAdsException as ex:
            print("Google Ads API error encountered: \n"
                  f"Request with ID '{ex.request_id}' failed with status '{ex.error.code().name}' and includes the following errors:\n")
            for error in ex.failure.errors:
                print(f"\tError with message '{error.message}'.")
                if error.location:
                    for field_path_element in error.location.field_path_elements:
                        print(f"\t\tOn field: {field_path_element.field_name}")
        except TooManyRequests as e:
            print("Too many requests. API quota may have been reached or accessed too quickly. Please try again later.")
            print_error(func.__name__, e)
        except ResourceExhausted as e:
            print("Resource exhausted. API quota may have been reached or accessed too quickly. Please try again later.")
            print_error(func.__name__, e)
        # generic requests exceptions
        except requests.exceptions.RequestException as e:
            print_error(func.__name__, e)
        # other exceptions
        except KeyboardInterrupt:
            print("\nExiting the program...")
            sys.exit(0)
        except EOFError as e:
            print_error(func.__name__, e)
        except OSError as e:
            print_error(func.__name__, e)
        except TypeError as e:
            print_error(func.__name__, e)
        except ValueError as e:
            print_error(func.__name__, e)
        except FileNotFoundError as e:
            print_error(func.__name__, e)
        except AttributeError as e:
            print_error(func.__name__, e)
        except Exception as e:
            print_error(func.__name__, e)
    return wrapper

"""
AUDITING REPORTS
"""
def complete_labels_audit(gads_service, client, customer_id):
    # enum decoders
    undecoded_enums = get_enums(client)
    channel_type_enum, ad_group_type_enum, *extra = undecoded_enums
    # get label and campaign group metadata
    label_table, label_table_headers, label_dict = get_labels(gads_service, client, customer_id)
    camp_group_table, camp_group_headers, camp_group_dict = get_campaign_groups(gads_service, client, customer_id)
    # GAQL query
    label_audit_query = queries.label_audit_query()
    response = gads_service.search_stream(customer_id=customer_id, query=label_audit_query)
    audit_table = []
    audit_dict = {}
    for batch in response:
        for row in batch.results:
            # decode enum fields
            channel_type = channel_type_enum.AdvertisingChannelType.Name(
                row.campaign.advertising_channel_type
            ) if hasattr(row.campaign, 'advertising_channel_type') else 'UNDEFINED'
            ad_group_type = ad_group_type_enum.AdGroupType.Name(
                row.ad_group.type_
            ) if hasattr(row.ad_group, 'type_') else 'UNDEFINED'
            # resolve labels
            campaign_labels = [
                label_dict.get(label.split('/')[-1], 'UNDEFINED') for label in row.campaign.labels
            ]
            ad_group_labels = [
                label_dict.get(label.split('/')[-1], 'UNDEFINED') for label in row.ad_group.labels
            ]
            # campaign group name
            campaign_group_id = row.campaign.campaign_group.split('/')[-1]
            campaign_group_name = camp_group_dict.get(campaign_group_id, 'UNDEFINED')
            # build flat row
            audit_table.append([
                row.customer.id,
                row.customer.descriptive_name,
                row.campaign.id,
                row.campaign.name,
                channel_type,
                campaign_group_name,
                ', '.join(campaign_labels),
                row.ad_group.id,
                row.ad_group.name,
                ad_group_type,
                ', '.join(ad_group_labels)
            ])
            # build structured dict
            audit_dict[(row.campaign.id, row.ad_group.id)] = {
                "customer_id": row.customer.id,
                "customer_name": row.customer.descriptive_name,
                "campaign_id": row.campaign.id,
                "campaign_name": row.campaign.name,
                "campaign_type": channel_type,
                "campaign_group": campaign_group_name,
                "campaign_labels": campaign_labels,
                "ad_group_id": row.ad_group.id,
                "ad_group_name": row.ad_group.name,
                "ad_group_type": ad_group_type,
                "ad_group_labels": ad_group_labels,
            }
    audit_headers = [
        "account id",
        "account name",
        "campaign id",
        "campaign name",
        "campaign type",
        "campaign group",
        "campaign labels",
        "ad_group id",
        "ad_group name",
        "ad_group type",
        "ad_group labels"
    ]
    return audit_table, audit_headers, audit_dict

"""
PERFORMANCE REPORTS
"""
def arc_report_single(gads_service, client, start_date, end_date, time_seg, customer_id, **kwargs):
    """
    Replicates the Ad Response Codes report for the selected customerID/account,
    aggregating spend by Date, Account, ARC, and Channel Type, and optionally
    summarizing all channel types into ARC-level totals.

    Args:
        gads_service: The Google Ads service client.
        client: The authenticated Google Ads client.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        time_seg (str): Time segmentation (e.g., 'date', 'month').
        include_channel_types (bool): Whether to include channel types in output.
        customer_id (str): Google Ads account customer ID.
        kwargs (dict): Contains report toggle options

    Returns:
        tuple:
            (table_data, headers)
    """
    # enum decoders
    undecoded_enums = get_enums(client)
    channel_type_enum, *extra = undecoded_enums
    time_seg_string = f"segments.{time_seg}"
    include_channel_types = kwargs.get("include_channel_types", False)
    include_campaign_info = kwargs.get("include_campaign_info", False)
    # GAQL query
    arc_report_query = queries.arc_report_query(start_date, end_date, time_seg_string, **kwargs)
    arc_query_response = gads_service.search_stream(customer_id=customer_id, query=arc_report_query)
    # initialize empty list
    table_data = []
    # fetch data and populate list
    for batch in arc_query_response:
        for row in batch.results:
            arc = helpers.extract_arc(row.campaign.name)
            channel_type = (
                channel_type_enum.AdvertisingChannelType.Name(row.campaign.advertising_channel_type)
                if hasattr(row.campaign, "advertising_channel_type") else "UNDEFINED"
            )
            date_value = getattr(row.segments, time_seg)
            cost_value = helpers.micros_to_decimal(row.metrics.cost_micros, Decimal("0.01"))
            # build dict, primary dims/metrics first
            arc_dict = {
                "Date": date_value,
                "Account name": row.customer.descriptive_name,
                "Customer ID": row.customer.id,
                "ARC": arc,
                "Cost": cost_value,
            }
            # append campaign info if selected
            if include_campaign_info:
                arc_dict["Campaign"] = row.campaign.name
            # append channel types if selected
            if include_channel_types:
                arc_dict["Campaign type"] = channel_type
    
            # append dict
            table_data.append(arc_dict)
    # define headers
    headers = ["Date", "Account name", "Customer ID"] # primary dimensions
    if include_campaign_info:
        headers.append("Campaign")
    if include_channel_types:
        headers.append("Campaign type")
    headers += ["ARC", "Cost"] # primary metrics
    # aggregate if campaign info is not included
    if not include_campaign_info:
        # determine grouping keys
        if include_channel_types:
            group_keys = ["Date", "Account name", "Customer ID", "Campaign type", "ARC"]
        else:
            group_keys = ["Date", "Account name", "Customer ID", "ARC"]
        # Aggregate by key
        aggregated = defaultdict(lambda: Decimal("0.00")) # <--- EVALUATE: this may be affecting cost calc
        for row in table_data:
            key = tuple(row[k] for k in group_keys)
            aggregated[key] += row["Cost"]
        # convert aggregated dict into row of dicts
        table_data = [
            dict(zip(group_keys, key), Cost=value) for key, value in aggregated.items()
        ]
        headers = group_keys + ["Cost"]
    # sort by date ascending, cost descending
    table_data_sorted = sorted(
        table_data, 
        key=lambda r: (r["Date"], -float(r["Cost"])))
    filtered_data = [[row.get(h) for h in headers] for row in table_data_sorted]
    return filtered_data, headers

def arc_report_all(gads_service, client, start_date, end_date, time_seg, accounts_info, **kwargs):
    """
    Generates the Ad Response Codes report for all accounts listed in account_info.

    Args:
        gads_service: The Google Ads service client.
        client: The authenticated Google Ads client.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        time_seg (str): Time segment or label.
        accounts_info (dict): Dictionary mapping account codes to [customer_id, descriptive_name].
        kwargs (dict): Contains report toggle options

    Returns:
        tuple: (all_data_sorted, headers) for display or export.
    """
    all_data = []
    headers = None
    for customer_id, account_descriptive in accounts_info.items():
        print(f"Processing {account_descriptive}...")
        try:
            table_data, headers = arc_report_single(
                gads_service, client, start_date, end_date, time_seg, customer_id, **kwargs
            )
            all_data.extend(table_data)
        except Exception as e:
            print(f"Error processing {account_descriptive} ({customer_id}): {e}")
    if not all_data:
        print("No data returned for any accounts.")
        return [], []
    # sort by: time index (0), account name, descending cost
    acct_idx = headers.index("Account name") if "Account name" in headers else 1
    cost_idx = headers.index("Cost") if "Cost" in headers else -1
    if cost_idx >= 0:
        all_data_sorted = sorted(
            all_data,
            key=lambda r: (r[0], r[acct_idx], -float(r[cost_idx]))
        )
    else:
        all_data_sorted = sorted(all_data, key=lambda r: (r[0], r[acct_idx]))
    return all_data_sorted, headers

def account_report_single(gads_service, client, start_date, end_date, time_seg, customer_id, **kwargs):
    """
    Generates a top level performance report for the selected customerID/account.

    Args:
        gads_service: The Google Ads service client.
        client: The authenticated Google Ads client.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        time_seg (str): Time segment or label.
        customer_id (str): The selected account customerID.
        kwargs (dict): Contains report toggle options if available.

    Returns:
        tuple: (table_data_sorted, headers) for display or export.
    """
    # enum decoders
    time_seg_string = f'segments.{time_seg}'
    # initialize an empty list to store the data
    table_data = []
    # GAQL query
    account_report_query = queries.account_report_query(start_date, end_date, time_seg_string)
    # fetch data and populate the table_data list
    account_report_response = gads_service.search_stream(customer_id=customer_id, query=account_report_query)
    for data in account_report_response:
        for row in data.results:
            date_value = getattr(row.segments, time_seg)
            # build dict struct
            clicks = getattr(row.metrics, "clicks", 0) or 0
            invalid_clicks = getattr(row.metrics, "invalid_clicks", 0) or 0
            invalid_click_pct = (
                (Decimal(invalid_clicks) / Decimal(clicks)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
                if clicks else Decimal("0.0000")
            )
            account_report_dict = {
                "date": date_value,
                "account": row.customer.descriptive_name,
                "customer id": row.customer.id,
                "cost": helpers.micros_to_decimal(row.metrics.cost_micros, Decimal("0.01")),
                "clicks": clicks,
                "invalid clicks": invalid_clicks,
                "invalid click %": invalid_click_pct,
                "interactions": row.metrics.interactions,
                "impressions": row.metrics.impressions,
                "ctr": row.metrics.ctr,
                "avg cpc": helpers.micros_to_decimal(row.metrics.average_cpc, Decimal("0.001")),
                "avg cpm": helpers.micros_to_decimal(row.metrics.average_cpm, Decimal("0.001")),
                "abs top is": row.metrics.absolute_top_impression_percentage,
                "top is %": row.metrics.top_impression_percentage,
                }
            # append data
            table_data.append(account_report_dict)
    # define the headers for the table
    headers = ["date","account","customer id"] # primary dimensions
    # seperate metric headers, in case needing to expand later
    headers += [
        "cost",
        "clicks",
        "invalid clicks",
        "invalid click %",
        "interactions",
        "impressions",
        "ctr",
        "avg cpc",
        "avg cpm",
        "abs top is",
        "top is %",
        ]
    filtered_data = [[row[h] for h in headers] for row in table_data]
    # sort by: time index (0), descending cost
    table_data_sorted = sorted(
        filtered_data,
        key=lambda r:(r[0], -float(r[headers.index("cost")]))
    )
    return table_data_sorted, headers

def account_report_all(gads_service, client, start_date, end_date, time_seg, accounts_info, **kwargs):
    """
    Generates a top level performance report for all accounts listed in account_info.

    Args:
        gads_service: The Google Ads service client.
        client: The authenticated Google Ads client.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        time_seg (str): Time segment or label.
        accounts_info (dict): Dictionary mapping account codes to [customer_id, descriptive_name].
        kwargs (dict): Contains report toggle options if applicable.

    Returns:
        tuple: (all_data_sorted, headers) for display or export.
    """
    all_data = []
    headers = None
    for customer_id, account_descriptive in accounts_info.items():
        print(f"Processing {account_descriptive}...")
        try:
            table_data, headers = account_report_single(
                gads_service, client, start_date, end_date, time_seg, customer_id
            )
            all_data.extend(table_data)
        except Exception as e:
            print(f"Error processing {account_descriptive} ({customer_id}): {e}")
    if not all_data:
        print("No data returned for any accounts.")
        return [], []
    # sort by: time index (0), account name (1), descending cost
    cost_idx = headers.index("cost") if "cost" in headers else None
    acct_idx = headers.index("account") if "account" in headers else None
    if cost_idx is not None and acct_idx is not None:
        all_data_sorted = sorted(
            all_data,
            key=lambda r: (r[0], r[acct_idx], -float(r[cost_idx]))
        )
    else:
        # fallback to date sort if error
        all_data_sorted = sorted(all_data, key=lambda r: r[0])
    return all_data_sorted, headers

def ad_level_report_single(gads_service, client, start_date, end_date, time_seg, customer_id, **kwargs):
    """
    Replicates the Google Ads Report Studio by pulling ad performance data
    with ad group and ad types using ad_group_ad as the main resource,
    and campaign-level data for Performance Max.

    Args:
        gads_service: The Google Ads service client.
        client: The authenticated Google Ads client.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        time_seg (str): Time segment or label.
        customer_id (str): The selected account customerID.
        kwargs (dict): Contains report toggle options:
            - include_channel_types
            - include_campaign_info
            - include_adgroup_info

    Returns:
        tuple: (table_data, headers) for display or export.
    """
    # enum decoders
    undecoded_enums = get_enums(client)
    channel_type_enum, ad_group_type_enum, ad_type_enum, *extra = undecoded_enums
    # time_seg transform
    time_seg_string = f'segments.{time_seg}'
    # toggles unpack
    include_channel_types = kwargs.get("include_channel_types", False)
    include_campaign_info = kwargs.get("include_campaign_info", False)
    include_adgroup_info = kwargs.get("include_adgroup_info", False)
    table_data = []
    # ad_group_ad scoped query, will not capture PMAX campaigns due to lack of ad or ad_group scope dimension in Pmax
    ad_group_ad_query = queries.ad_group_ad_query(start_date, end_date, time_seg_string)
    ad_group_ad_response = gads_service.search_stream(customer_id=customer_id, query=ad_group_ad_query)
    for batch in ad_group_ad_response:
        for row in batch.results:
            arc = helpers.extract_arc(row.campaign.name)
            channel_type = (
                channel_type_enum.AdvertisingChannelType.Name(row.campaign.advertising_channel_type)
                if hasattr(row.campaign, 'advertising_channel_type') else 'UNDEFINED'
            )
            ad_group_type = (
                ad_group_type_enum.AdGroupType.Name(row.ad_group.type_)
                if hasattr(row.ad_group, 'type_') else 'UNDEFINED'
            )
            ad_type = (
                ad_type_enum.AdType.Name(row.ad_group_ad.ad.type_)
                if hasattr(row.ad_group_ad.ad, 'type_') else 'UNDEFINED'
            )
            date_value = getattr(row.segments, time_seg)
            # build dict struct
            cost_value = helpers.micros_to_decimal(row.metrics.cost_micros, Decimal("0.01"))
            impressions = getattr(row.metrics, "impressions", 0) or 0
            avg_cpm_value = (
                helpers.micros_to_decimal(row.metrics.average_cpm, Decimal("0.001"))
                if impressions else Decimal("0.000")
            )
            clicks = getattr(row.metrics, "clicks", 0) or 0
            avg_cpc_value = (
                helpers.micros_to_decimal(row.metrics.average_cpc, Decimal("0.001"))
                if clicks else Decimal("0.000")
            )
            video_views = getattr(row.metrics, "video_views", 0) or 0
            conversions_metric = Decimal(str(getattr(row.metrics, "conversions", 0) or 0))
            conv_value_metric = Decimal(str(getattr(row.metrics, "conversions_value", 0) or 0)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            ad_group_ad_dict = {
                "Date": date_value,
                "Customer ID": row.customer.id,
                "Account name": row.customer.descriptive_name,
                "ARC": arc,
                "Campaign ID": row.campaign.id,
                "Campaign name": row.campaign.name,
                "Campaign type": channel_type,
                "Ad group ID": row.ad_group.id,
                "Ad group name": row.ad_group.name,
                "Ad group type": ad_group_type,
                "Ad ID": row.ad_group_ad.ad.id,
                "Ad type": ad_type,
                "Cost": cost_value,
                "Impr.": impressions,
                "Abs Top Imp%": row.metrics.absolute_top_impression_percentage,
                "Top Imp%": row.metrics.top_impression_percentage,
                "Avg CPM": avg_cpm_value,
                "Interactions": getattr(row.metrics, "interactions", 0) or 0,
                "Clicks": clicks,
                "Avg CPC": avg_cpc_value,
                "Video Views": video_views,
                "Conversions": conversions_metric,
                "Conv. value": conv_value_metric,
                }
            table_data.append(ad_group_ad_dict)
    # campaign scoped query for pmax campaigns
    pmax_campaign_query = queries.pmax_campaign_query(start_date, end_date, time_seg_string)
    pmax_campaign_response = gads_service.search_stream(customer_id=customer_id, query=pmax_campaign_query)
    for batch in pmax_campaign_response:
        for row in batch.results:
            # ENUM decoding with fallbacks
            arc = helpers.extract_arc(row.campaign.name)
            channel_type = (
                channel_type_enum.AdvertisingChannelType.Name(row.campaign.advertising_channel_type)
                if hasattr(row.campaign, 'advertising_channel_type') else 'UNDEFINED'
            )
            date_value = getattr(row.segments, time_seg)
            cost_value = helpers.micros_to_decimal(row.metrics.cost_micros, Decimal("0.01"))
            impressions = getattr(row.metrics, "impressions", 0) or 0
            avg_cpm_value = (
                helpers.micros_to_decimal(row.metrics.average_cpm, Decimal("0.001"))
                if impressions else Decimal("0.000")
            )
            clicks = getattr(row.metrics, "clicks", 0) or 0
            avg_cpc_value = (
                helpers.micros_to_decimal(row.metrics.average_cpc, Decimal("0.001"))
                if clicks else Decimal("0.000")
            )
            video_views = getattr(row.metrics, "video_views", 0) or 0
            conversions_metric = Decimal(str(getattr(row.metrics, "conversions", 0) or 0))
            conv_value_metric = Decimal(str(getattr(row.metrics, "conversions_value", 0) or 0)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            pmax_dict = {
                "Date": date_value,
                "Customer ID": row.customer.id,
                "Account name": row.customer.descriptive_name,
                "ARC": arc,
                "Campaign ID": row.campaign.id,
                "Campaign name": row.campaign.name,
                "Campaign type": channel_type,
                "Ad group ID": row.campaign.id,   # PMAX placeholder
                "Ad group name": row.campaign.name,  # PMAX placeholder
                "Ad group type": "PERFORMANCE_MAX",
                "Ad ID": row.campaign.id,  # PMAX placeholder
                "Ad type": "PERFORMANCE_MAX",
                "Cost": cost_value,
                "Impr.": impressions,
                "Abs Top Imp%": row.metrics.absolute_top_impression_percentage,
                "Top Imp%": row.metrics.top_impression_percentage,
                "Avg CPM": avg_cpm_value,
                "Interactions": getattr(row.metrics, "interactions", 0) or 0,
                "Clicks": clicks,
                "Avg CPC": avg_cpc_value,
                "Video Views": video_views,
                "Conversions": conversions_metric,
                "Conv. value": conv_value_metric,
            }
            table_data.append(pmax_dict)
    headers = [ "Date", "Customer ID", "Account name", "ARC"] # primary dimensions
    if include_campaign_info:
        headers += ["Campaign ID","Campaign name"]
    if include_channel_types:
        headers.append("Campaign type")
    if include_adgroup_info:
        headers += ["Ad group ID","Ad group name","Ad group type","Ad ID","Ad type"]
    headers += [ # metric headers
        "Cost",
        "Impr.",
        "Abs Top Imp%",
        "Top Imp%",
        "Avg CPM",
        "Interactions",
        "Clicks",
        "Avg CPC",
        "Video Views",
        "Conversions",
        "Conv. value",
    ]
    metric_fields = {
        "Cost",
        "Impr.",
        "Abs Top Imp%",
        "Top Imp%",
        "Avg CPM",
        "Interactions",
        "Clicks",
        "Avg CPC",
        "Video Views",
        "Conversions",
        "Conv. value",
    }
    dimension_fields = [h for h in headers if h not in metric_fields]
    aggregated = {}
    for row in table_data:
        key = tuple(row.get(field) for field in dimension_fields)
        if key not in aggregated:
            aggregated[key] = {field: row.get(field) for field in dimension_fields}
            aggregated[key].update({
                "Cost": Decimal("0.00"),
                "Impr.": 0,
                "Interactions": 0,
                "Clicks": 0,
                "Video Views": 0,
                "Conversions": Decimal("0"),
                "Conv. value": Decimal("0.00"),
                "_abs_top_weight": Decimal("0"),
                "_top_weight": Decimal("0"),
            })
        entry = aggregated[key]
        cost_value = row.get("Cost", Decimal("0.00"))
        if not isinstance(cost_value, Decimal):
            cost_value = Decimal(str(cost_value))
        entry["Cost"] += cost_value
        impressions = row.get("Impr.", 0) or 0
        entry["Impr."] += impressions
        entry["Interactions"] += row.get("Interactions", 0) or 0
        clicks = row.get("Clicks", 0) or 0
        entry["Clicks"] += clicks
        entry["Video Views"] += row.get("Video Views", 0) or 0
        conversions_value = row.get("Conversions", Decimal("0"))
        if not isinstance(conversions_value, Decimal):
            conversions_value = Decimal(str(conversions_value))
        entry["Conversions"] += conversions_value
        conv_value_metric = row.get("Conv. value", Decimal("0.00"))
        if not isinstance(conv_value_metric, Decimal):
            conv_value_metric = Decimal(str(conv_value_metric))
        entry["Conv. value"] += conv_value_metric
        abs_top_is_value = Decimal(str(row.get("Abs Top Imp%") or 0))
        top_is_pct_value = Decimal(str(row.get("Top Imp%") or 0))
        entry["_abs_top_weight"] += abs_top_is_value * Decimal(impressions)
        entry["_top_weight"] += top_is_pct_value * Decimal(impressions)
    aggregated_rows = []
    for entry in aggregated.values():
        impressions = entry.get("Impr.", 0)
        clicks = entry.get("Clicks", 0)
        cost_value = entry.get("Cost", Decimal("0.00"))
        abs_top_weight = entry.pop("_abs_top_weight", Decimal("0"))
        top_weight = entry.pop("_top_weight", Decimal("0"))
        entry["Cost"] = cost_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        conversions_value = entry.get("Conversions", Decimal("0"))
        entry["Conversions"] = conversions_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        conv_value_total = entry.get("Conv. value", Decimal("0.00"))
        entry["Conv. value"] = conv_value_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        entry["Avg CPC"] = (
            (entry["Cost"] / Decimal(clicks)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
            if clicks else Decimal("0.000")
        )
        entry["Avg CPM"] = (
            ((entry["Cost"] / Decimal(impressions)) * Decimal("1000")).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
            if impressions else Decimal("0.000")
        )
        entry["Abs Top Imp%"] = (
            (abs_top_weight / Decimal(impressions)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
            if impressions else Decimal("0")
        )
        entry["Top Imp%"] = (
            (top_weight / Decimal(impressions)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
            if impressions else Decimal("0")
        )
        aggregated_rows.append(entry)
    aggregated_rows_sorted = sorted(
        aggregated_rows,
        key=lambda r:(r.get("Date"), -float(r.get("Cost", Decimal("0"))))
    )
    filtered_data = [[row.get(h) for h in headers] for row in aggregated_rows_sorted]
    return filtered_data, headers

def ad_level_report_all(gads_service, client, start_date, end_date, time_seg, accounts_info, **kwargs):
    """
    Generates ad scoped report for all accounts listed in account_info.

    Args:
        gads_service: The Google Ads service client.
        client: The authenticated Google Ads client.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        time_seg (str): Time segment or label.
        customer_dict (dict): All available customer accounts.
        kwargs (dict): Contains report toggle options

    Returns:
        tuple: (all_data_sorted, headers) for display or export.
    """
    all_data = []
    headers = None
    for customer_id, account_descriptive in accounts_info.items():
        print(f"Processing {account_descriptive}...")
        try:
            table_data, headers = ad_level_report_single(
                gads_service, client, start_date, end_date, time_seg, customer_id, **kwargs
            )
            all_data.extend(table_data)
        except Exception as e:
            print(f"Error processing {account_descriptive} ({customer_id}): {e}")
    if not all_data:
        print("No data returned for any accounts.")
        return [], []
    # dynamic sort by cost, account name
    cost_idx = headers.index("Cost") if "Cost" in headers else None
    acct_idx = headers.index("Account name") if "Account name" in headers else None
    if cost_idx is not None and acct_idx is not None:
        all_data_sorted = sorted(
            all_data,
            key=lambda r: (r[0], r[acct_idx], -float(r[cost_idx]))
        )
    else:
        # fallback to date sort if error
        all_data_sorted = sorted(all_data, key=lambda r: r[0])
    return all_data_sorted, headers

def click_view_report_single(gads_service, client, start_date, end_date, time_seg, customer_id, **kwargs):
    """
    Generates a click view performance report for the selected customerID/account.

    Args:
        gads_service: The Google Ads service client.
        client: The authenticated Google Ads client.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        time_seg (str): Time segment or label.
        customer_id (str): The selected account customerID.
        kwargs: Dynamic toggles for channel types, campaign info, adgroup info, and device info.

    Returns:
        tuple: (table_data_sorted, headers) for display or export.
    """
    # enum decoders
    time_seg_string = f'segments.{time_seg}'
    undecoded_enums = get_enums(client)
    channel_type_enum, *extra, click_type_enum, keyword_match_type_enum, device_type_enum = undecoded_enums
    # unpack toggles
    include_channel_types = kwargs.get("include_channel_types", False)
    include_campaign_info = kwargs.get("include_campaign_info", False)
    include_adgroup_info = kwargs.get("include_adgroup_info", False)
    include_device_info = kwargs.get("include_device_info", False)
    # GAQL query
    click_view_query = queries.click_view_query(start_date, end_date, time_seg_string)
    # fetch data 
    response = gads_service.search_stream(customer_id=customer_id, query=click_view_query)
    # initialize an empty list to store the data
    table_data = []
    # populate the table_data list
    for data in response:
        for row in data.results:
            date_value = getattr(row.segments, time_seg)
            channel_type = (
                channel_type_enum.AdvertisingChannelType.Name(row.campaign.advertising_channel_type)
                if hasattr(row.campaign, 'advertising_channel_type') else 'UNDEFINED'
            )
            click_type = (
                click_type_enum.ClickType.Name(row.segments.click_type)
                if hasattr(row.segments, 'click_type') else 'UNDEFINED'
            )
            keyword_match_type = (
                keyword_match_type_enum.KeywordMatchType.Name(row.click_view.keyword_info.match_type)
                if getattr(row.click_view, "keyword_info", None) 
                and hasattr(row.click_view.keyword_info, "match_type")
                else "UNDEFINED"
            )
            device_type = (
                device_type_enum.Device.Name(row.segments.device)
                if hasattr(row.segments, 'device') else 'UNDEFINED'
            )
            # cleaning needed for text, returning values with '=' (also '+' but those are bid modifiers from old targets)
            keyword_text = (row.click_view.keyword_info.text).strip() if getattr(row.click_view, "keyword_info", None) else None
            # build row dict with response
            click_view_dict = {
                "Date": date_value,
                "Account name": row.customer.descriptive_name,
                "Customer ID": row.customer.id,
                "Campaign name": row.campaign.name,
                "Campaign ID": row.campaign.id,
                "Campaign type": channel_type,
                "Ad group name": row.ad_group.name,
                "Ad group ID": row.ad_group.id,
                # "Ad": row.click_view.ad_group_ad, # needs resource parsing
                "gclid": row.click_view.gclid,
                # "keyword target": row.click_view.keyword, # needs resource parsing
                "keyword match type": keyword_match_type,
                "keyword text": keyword_text,
                "SERP #": row.click_view.page_number,
                # "loc_country": row.click_view.location_of_presence.country,
                # "loc_region": row.click_view.location_of_presence.region,
                # "loc_metro": row.click_view.location_of_presence.metro,
                # "loc_city": row.click_view.location_of_presence.city,
                # "loc_specific": row.click_view.location_of_presence.most_specific,
                # "interest_country": row.click_view.area_of_interest.country,
                # "interest_region": row.click_view.area_of_interest.region,
                # "interest_metro": row.click_view.area_of_interest.metro,
                # "interest_city": row.click_view.area_of_interest.city,
                # "interest_specific": row.click_view.area_of_interest.most_specific,
                "device": device_type,
                "click type": click_type,
                "clicks": row.metrics.clicks,
            }
            # append dict
            table_data.append(click_view_dict)
    # define the headers for the table
    headers = ["Date", "Account name", "Customer ID"] # primary dimensions
    if include_campaign_info:
        headers += ["Campaign ID", "Campaign name"]
    if include_channel_types:
        headers.append("Campaign type")
    if include_adgroup_info:
        headers += ["Ad group ID", "Ad group name"]
    headers += ["gclid", "keyword match type", "keyword text", "SERP #"]
    if include_device_info:
        headers.append("device")
    headers += ["click type", "clicks"] # metrics
    metric_fields = {"clicks"}
    dimension_fields = [h for h in headers if h not in metric_fields]
    aggregated = {}
    for row in table_data:
        key = tuple(row.get(field) for field in dimension_fields)
        if key not in aggregated:
            aggregated[key] = {field: row.get(field) for field in dimension_fields}
            aggregated[key]["clicks"] = 0
        aggregated[key]["clicks"] += row.get("clicks", 0) or 0
    aggregated_rows = sorted(
        aggregated.values(),
        key=lambda r: (r.get("Date"), -float(r.get("clicks", 0)))
    )
    filtered_data = [[row.get(h) for h in headers] for row in aggregated_rows]
    return filtered_data, headers

def click_view_report_all(gads_service, client, start_date, end_date, time_seg, accounts_info, **kwargs):
    """
    Generates a click view performance report for all accounts listed in account_info.

    Args:
        gads_service: The Google Ads service client.
        client: The authenticated Google Ads client.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        time_seg (str): Time segment or label.
        accounts_info (dict): Dictionary mapping account codes to [customer_id, descriptive_name].
        kwargs: Dynamic toggles for channel types, campaign info, adgroup info, and device info.

    Returns:
        tuple: (all_data_sorted, headers) for display or export.
    """
    all_data = []
    headers = None
    for customer_id, account_descriptive in accounts_info.items():
        print(f"Processing {account_descriptive}...")
        try:
            table_data, headers = click_view_report_single(
                gads_service, client, start_date, end_date, time_seg, customer_id, **kwargs
            )
            all_data.extend(table_data)
        except Exception as e:
            print(f"Error processing {account_descriptive} ({customer_id}): {e}")
    if not all_data:
        print("No data returned for any accounts.")
        return [], []
    # sort by: time index (0), account name, descending clicks
    acct_idx = headers.index("Account name") if "Account name" in headers else 1
    clicks_idx = headers.index("clicks") if "clicks" in headers else -1
    if clicks_idx >= 0:
        all_data_sorted = sorted(
            all_data,
            key=lambda r: (r[0], r[acct_idx], -float(r[clicks_idx]))
        )
    else:
        all_data_sorted = sorted(all_data, key=lambda r: (r[0], r[acct_idx]))
    return all_data_sorted, headers

def paid_org_search_term_report_single(gads_service, client, start_date, end_date, time_seg, customer_id, **kwargs):
    """
    Generates a Paid and Organic Search Term report for the selected customerID/account.

    Args:
        gads_service: The Google Ads service client.
        client: The authenticated Google Ads client.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        time_seg (str): Time segment or label.
        customer_id (str): The selected account customerID.

    Returns:
        tuple: (table_data_sorted, headers) for display or export.
    """
    # enum decoders
    time_seg_string = f'segments.{time_seg}'
    undecoded_enums = get_enums(client)
    channel_type_enum, *extra, serp_type_enum, click_type, keyword_match_type_enum, device_type_enum = undecoded_enums
    # unpack toggles
    include_channel_types = kwargs.get("include_channel_types", False)
    include_campaign_info = kwargs.get("include_campaign_info", False)
    include_adgroup_info = kwargs.get("include_adgroup_info", False)
    include_device_info = kwargs.get("include_device_info", False)
    # GAQL query
    paid_org_search_term_query = queries.paid_organic_search_term_view_query(start_date, end_date, time_seg_string)
    # fetch data and populate the table_data list
    response = gads_service.search_stream(customer_id=customer_id, query=paid_org_search_term_query)
    # initialize an empty list to store the data
    table_data = []
    # populate the table_data list
    for data in response:
        for row in data.results:
            date_value = getattr(row.segments, time_seg)
            channel_type = (
                channel_type_enum.AdvertisingChannelType.Name(row.campaign.advertising_channel_type)
                if hasattr(row.campaign, 'advertising_channel_type') else 'UNDEFINED'
            )
            serp_type = (
                serp_type_enum.SearchEngineResultsPageType.Name(row.segments.search_engine_results_page_type)
                if hasattr(row.segments, 'search_engine_results_page_type') else 'UNDEFINED'
            )
            keyword_match_type = (
                keyword_match_type_enum.KeywordMatchType.Name(row.segments.keyword.info.match_type)
                if getattr(row.segments, "keyword", None)
                and hasattr(row.segments.keyword, "info")
                and hasattr(row.segments.keyword.info, "match_type")
                else "UNDEFINED"
            )
            device_type = (
                device_type_enum.Device.Name(row.segments.device)
                if hasattr(row.segments, 'device') else 'UNDEFINED'
            )
            organic_queries = getattr(row.metrics, "organic_queries", 0) or 0
            organic_impressions = getattr(row.metrics, "organic_impressions", 0) or 0
            organic_clicks = getattr(row.metrics, "organic_clicks", 0) or 0
            paid_impressions = getattr(row.metrics, "impressions", 0) or 0
            paid_clicks = getattr(row.metrics, "clicks", 0) or 0
            combined_queries = getattr(row.metrics, "combined_queries", 0) or 0
            combined_clicks = getattr(row.metrics, "combined_clicks", 0) or 0
            combined_clicks_per_query = getattr(row.metrics, "combined_clicks_per_query", 0) or 0
            organic_impr_per_query = getattr(row.metrics, "organic_impressions_per_query", 0) or 0
            organic_clicks_per_query = getattr(row.metrics, "organic_clicks_per_query", 0) or 0
            paid_ctr_raw = getattr(row.metrics, "ctr", 0) or 0
            avg_cpc_micros = getattr(row.metrics, "average_cpc", 0) or 0
            total_impressions = organic_impressions + paid_impressions
            avg_cpc_value = (
                helpers.micros_to_decimal(avg_cpc_micros, Decimal("0.001"))
                if paid_clicks else Decimal("0.000")
            )
            keyword_info = getattr(getattr(row.segments, "keyword", None), "info", None)
            keyword_text = getattr(keyword_info, "text", None) if keyword_info else None
            # build row dict with response
            paid_org_search_term_dict = {
                "Date": date_value,
                "Account name": row.customer.descriptive_name,
                "Customer ID": row.customer.id,
                "Campaign name": row.campaign.name,
                "Campaign ID": row.campaign.id,
                "Campaign type": channel_type,
                "Ad group name": row.ad_group.name,
                "Ad group ID": row.ad_group.id,
                "device": device_type,
                "SERP type": serp_type,
                "keyword match type": keyword_match_type,
                "keyword text": keyword_text,
                "org queries": organic_queries,
                "org impr": organic_impressions,
                "org impr per query": organic_impr_per_query,
                "org clicks": organic_clicks,
                "org clicks per query": organic_clicks_per_query,
                "paid impr": paid_impressions,
                "paid clicks": paid_clicks,
                "paid ctr": paid_ctr_raw,
                "avg cpc": avg_cpc_value,
                "total queries": combined_queries,
                "total impr": total_impressions,
                "total clicks": combined_clicks,
                "total clicks per query": combined_clicks_per_query,
            }
            # append dict
            table_data.append(paid_org_search_term_dict)
    # define the headers for the table
    headers = ["Date", "Account name", "Customer ID"] # primary dimensions
    if include_campaign_info:
        headers += ["Campaign name", "Campaign ID"]
    if include_channel_types: 
        headers.append("Campaign type")
    if include_adgroup_info:
        headers += ["Ad group name", "Ad group ID"]
    if include_device_info:
        headers.append("device")
    # metrics
    headers += ["SERP type",
                "keyword match type",
                "keyword text",
                "org queries",
                "org impr",
                "org impr per query",
                "org clicks",
                "org clicks per query",
                "paid impr",
                "paid clicks",
                "paid ctr",
                "avg cpc",
                "total cost",
                "total queries",
                "total impr",
                "total clicks",
                "total clicks per query"]
    metric_fields = {
        "org queries",
        "org impr",
        "org impr per query",
        "org clicks",
        "org clicks per query",
        "paid impr",
        "paid clicks",
        "paid ctr",
        "avg cpc",
        "total cost",
        "total queries",
        "total impr",
        "total clicks",
        "total clicks per query",
    }
    dimension_fields = [h for h in headers if h not in metric_fields]
    aggregated = {}
    for row in table_data:
        key = tuple(row.get(field) for field in dimension_fields)
        if key not in aggregated:
            aggregated[key] = {field: row.get(field) for field in dimension_fields}
            aggregated[key].update({
                "org queries": 0,
                "org impr": 0,
                "org clicks": 0,
                "paid impr": 0,
                "paid clicks": 0,
                "total queries": 0,
                "total impr": 0,
                "total clicks": 0,
                "_total_cost": Decimal("0.00"),
            })
        entry = aggregated[key]
        entry["org queries"] += row.get("org queries", 0) or 0
        entry["org impr"] += row.get("org impr", 0) or 0
        entry["org clicks"] += row.get("org clicks", 0) or 0
        entry["paid impr"] += row.get("paid impr", 0) or 0
        paid_clicks = row.get("paid clicks", 0) or 0
        entry["paid clicks"] += paid_clicks
        entry["total queries"] += row.get("total queries", 0) or 0
        entry["total impr"] += row.get("total impr", 0) or 0
        entry["total clicks"] += row.get("total clicks", 0) or 0
        avg_cpc_value = row.get("avg cpc", Decimal("0.000"))
        if not isinstance(avg_cpc_value, Decimal):
            avg_cpc_value = Decimal(str(avg_cpc_value))
        entry["_total_cost"] += avg_cpc_value * Decimal(paid_clicks)
    aggregated_rows = []
    for entry in aggregated.values():
        org_queries = entry.get("org queries", 0)
        paid_impr = entry.get("paid impr", 0)
        paid_clicks = entry.get("paid clicks", 0)
        total_queries = entry.get("total queries", 0)
        total_cost_raw = entry.pop("_total_cost", Decimal("0.00"))
        entry["org impr per query"] = (
            (Decimal(entry["org impr"]) / Decimal(org_queries)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
            if org_queries else Decimal("0")
        )
        entry["org clicks per query"] = (
            (Decimal(entry["org clicks"]) / Decimal(org_queries)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
            if org_queries else Decimal("0")
        )
        entry["paid ctr"] = (
            (Decimal(paid_clicks) / Decimal(paid_impr)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
            if paid_impr else Decimal("0")
        )
        entry["avg cpc"] = (
            (total_cost_raw / Decimal(paid_clicks)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
            if paid_clicks else Decimal("0.000")
        )
        entry["total cost"] = total_cost_raw.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        entry["total clicks per query"] = (
            (Decimal(entry["total clicks"]) / Decimal(total_queries)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
            if total_queries else Decimal("0")
        )
        aggregated_rows.append(entry)
    aggregated_rows_sorted = sorted(
        aggregated_rows,
        key=lambda r: (r.get("Date"), -float(r.get("total clicks", 0)))
    )
    filtered_data = [[row.get(h) for h in headers] for row in aggregated_rows_sorted]
    return filtered_data, headers

def paid_org_search_term_report_all(gads_service, client, start_date, end_date, time_seg, accounts_info, **kwargs):
    """
    Generates a Paid and Organic Search Term report for all accounts listed in account_info.

    Args:
        gads_service: The Google Ads service client.
        client: The authenticated Google Ads client.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        time_seg (str): Time segment or label.
        accounts_info (dict): Dictionary mapping account codes to [customer_id, descriptive_name].
        kwargs: Dynamic toggles for channel types, campaign info, adgroup info, and device info.

    Returns:
        tuple: (all_data_sorted, headers) for display or export.
    """
    all_data = []
    headers = None
    for customer_id, account_descriptive in accounts_info.items():
        print(f"Processing {account_descriptive}...")
        try:
            table_data, headers = paid_org_search_term_report_single(
                gads_service, client, start_date, end_date, time_seg, customer_id, **kwargs
            )
            all_data.extend(table_data)
        except Exception as e:
            print(f"Error processing {account_descriptive} ({customer_id}): {e}")
    if not all_data:
        print("No data returned for any accounts.")
        return [], []
    # sort by: time index (0), account name (1), descending total combined clicks
    acct_idx = headers.index("Account name") if "Account name" in headers else 1
    comb_clicks_idx = headers.index("total combined clicks") if "total combined clicks" in headers else -1
    if comb_clicks_idx >= 0:
        all_data_sorted = sorted(
            all_data,
            key=lambda r: (r[0], r[acct_idx], -float(r[comb_clicks_idx]))
        )
    else:
        all_data_sorted = sorted(all_data, key=lambda r: (r[0], r[acct_idx]))
    return all_data_sorted, headers

"""
BUDGET REPORTS
"""
def budget_report_single(gads_service, client, start_date, end_date, time_seg, customer_id):
    print("Budget report - single", "test complete!")

def budget_report_all(gads_service, client, start_date, end_date, time_seg, accounts_info):
    print("Budget report - all, test complete!")

# Prototyping/testing
"""
def test_query(gads_service, client, customer_id):
    return
"""
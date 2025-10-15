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
        except KeyboardInterrupt as e:
            print_error(func.__name__, e)
        except FileNotFoundError as e:
            print_error(func.__name__, e)
        except AttributeError as e:
            print_error(func.__name__, )
        except Exception as e:
            print_error(func.__name__, e)
    def print_error(func_name, error):
        print(f"\nError in function '{func_name}': {repr(error)} - Exiting...\n")
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
def arc_report_single(gads_service, client, start_date, end_date, time_seg, include_channel_types, customer_id):
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

    Returns:
        tuple:
            (table_data, headers)
    """
    # enum decoders
    undecoded_enums = get_enums(client)
    channel_type_enum, *extra = undecoded_enums
    time_seg_string = f"segments.{time_seg}"
    # GAQL query
    arc_campaign_query = queries.arc_campaign_query(start_date, end_date, time_seg_string)
    arc_query_response = gads_service.search_stream(customer_id=customer_id, query=arc_campaign_query)
    table_data = []
    for batch in arc_query_response:
        for row in batch.results:
            arc = helpers.extract_arc(row.campaign.name)
            channel_type = (
                channel_type_enum.AdvertisingChannelType.Name(row.campaign.advertising_channel_type)
                if hasattr(row.campaign, "advertising_channel_type") else "UNDEFINED"
            )
            date_value = getattr(row.segments, time_seg)
            cost_value = Decimal(row.metrics.cost_micros / 1e6).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            table_data.append([
                date_value,                    # 0 - Date
                row.customer.descriptive_name, # 1 - Account name
                row.customer.id,               # 2 - Customer ID
                channel_type,                  # 3 - Campaign type
                arc,                           # 4 - ARC
                cost_value,                    # 5 - Cost
            ])
    # aggregation
    if include_channel_types:
        # channel detailed (date, account, channel type, arc)
        grouped_data = defaultdict(Decimal)
        for row in table_data:
            key = (row[0], row[1], row[3], row[4]) # (date, account, channel type, arc)
            grouped_data[key] += row[5]
        aggregated = [
            [date, account, customer_id, channel, arc, cost]
            for (date, account, channel, arc), cost in grouped_data.items()
        ]
        headers = ["Date", "Account name", "Customer ID", "Campaign type", "ARC", "Cost"]
    else:
        # arc aggregate (all channels combined)
        grouped_data = defaultdict(Decimal)
        for row in table_data:
            key = (row[0], row[1], row[4])
            grouped_data[key] += row[5]
        aggregated = [
            [date, account, customer_id, arc, cost]
            for (date, account, arc), cost in grouped_data.items()
        ]
        headers = ["Date", "Account name", "Customer ID", "ARC", "Cost"]
    # sort by date ascending, cost descending
    table_data_sorted = sorted(aggregated, key=lambda r: (r[0], -float(r[-1])))
    return table_data_sorted, headers

def arc_report_all(gads_service, client, start_date, end_date, time_seg, include_channel_types, accounts_info):
    """
    Generates the Ad Response Codes report for all accounts listed in account_info.

    Args:
        gads_service: The Google Ads service client.
        client: The authenticated Google Ads client.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        time_seg (str): Time segment or label.
        accounts_info (dict): Dictionary mapping account codes to [customer_id, descriptive_name].

    Returns:
        tuple: (all_data_sorted, headers) for display or export.
    """
    all_data = []
    headers = None
    for customer_id, account_descriptive in accounts_info.items():
        print(f"Processing {account_descriptive}...")
        try:
            table_data, headers = arc_report_single(
                gads_service, client, start_date, end_date, time_seg, include_channel_types, customer_id
            )
            all_data.extend(table_data)
        except Exception as e:
            print(f"Error processing {account_descriptive} ({customer_id}): {e}")
    if not all_data:
        print("No data returned for any accounts.")
        return [], []
    # sort by: time index (0), account name (1), descending cost (5) if channels included
    if include_channel_types:
        all_data_sorted = sorted(
            all_data,
            key=lambda r: (r[0], r[1], -float(r[5]))
        )
    # sort by: time index (0), account name (1), descending cost (4) if channels excluded
    else: all_data_sorted = sorted( 
        all_data,
        key=lambda r: (r[0], r[1], -float(r[4]))
    )
    return all_data_sorted, headers

def account_report_single(gads_service, client, start_date, end_date, time_seg, customer_id):
    """
    Generates a top level performance report for the selected customerID/account.

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
    # GAQL query
    account_report_query = queries.account_report_query(start_date, end_date, time_seg_string)
    # initialize an empty list to store the data
    table_data = []
    # fetch data and populate the table_data list
    response = gads_service.search_stream(customer_id=customer_id, query=account_report_query)
    for data in response:
        for row in data.results:
            date_value = getattr(row.segments, time_seg)
            # append each row's data as a list or tuple to the table_data list
            
            table_data.append([
                date_value,
                row.customer.descriptive_name,
                row.customer.id,
                Decimal(row.metrics.cost_micros / 1e6).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                row.metrics.clicks,
                row.metrics.invalid_clicks,
                (row.metrics.invalid_clicks / row.metrics.clicks), # invalid clicks %
                row.metrics.interactions,
                # (row.metrics.clicks / row.metrics.interactions), # interactions click %
                row.metrics.impressions,
                row.metrics.ctr,
                Decimal(row.metrics.average_cpc / 1e6).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP),
                Decimal(row.metrics.average_cpm / 1e6).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP),
                row.metrics.absolute_top_impression_percentage,
                row.metrics.top_impression_percentage,
            ])
    # define the headers for the table
    headers = [
        "date",
        "account",
        "customer id",
        "cost",
        "clicks",
        "invalid clicks",
        "invalid click %",
        "interactions",
        # "interactions click %",
        "impressions",
        "ctr",
        "avg cpc",
        "avg cpm",
        "abs top is",
        "top is %",
        ]
    # sort by: time index (0), descending cost (3)
    table_data_sorted = sorted(
        table_data,
        key=lambda r: (r[0], -float(r[3]))
        )
    return table_data_sorted, headers

def account_report_all(gads_service, client, start_date, end_date, time_seg, accounts_info):
    """
    Generates a top level performance report for all accounts listed in account_info.

    Args:
        gads_service: The Google Ads service client.
        client: The authenticated Google Ads client.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        time_seg (str): Time segment or label.
        accounts_info (dict): Dictionary mapping account codes to [customer_id, descriptive_name].

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
    # sort by: time index (0), account name (1), descending cost (3)
    all_data_sorted = sorted(
        all_data,
        key=lambda r: (r[0], r[1], -float(r[3]))
    )
    return all_data_sorted, headers

def ad_level_report_single(gads_service, client, start_date, end_date, time_seg, customer_id):
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

    Returns:
        tuple: (table_data, headers) for display or export.
    """
    # enum decoders
    undecoded_enums = get_enums(client)
    channel_type_enum, ad_group_type_enum, ad_type_enum, *extra = undecoded_enums
    # time_seg transform
    time_seg_string = f'segments.{time_seg}'
    # ad_group_ad scoped query, will not capture PMAX campaigns due to lack of ad or ad_group scope dimension in Pmax
    ad_group_ad_query = queries.ad_group_ad_query(start_date, end_date, time_seg_string)
    ad_group_ad_response = gads_service.search_stream(customer_id=customer_id, query=ad_group_ad_query)
    table_data = []
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
            table_data.append([
                date_value,
                row.customer.id,
                row.customer.descriptive_name,
                arc,
                row.campaign.id,
                row.campaign.name,
                channel_type,
                row.ad_group.id,
                row.ad_group.name,
                ad_group_type,
                row.ad_group_ad.ad.id,
                ad_type,
                Decimal(row.metrics.cost_micros / 1e6).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                row.metrics.impressions,
                row.metrics.absolute_top_impression_percentage,
                row.metrics.top_impression_percentage,
                Decimal(row.metrics.average_cpm / 1e6).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP),
                row.metrics.interactions,
                row.metrics.clicks,
                Decimal(row.metrics.average_cpc / 1e6).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP),
                row.metrics.video_views,
                row.metrics.conversions,
                row.metrics.conversions_value,
            ])
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
            # insert values for pmax ad group & ad info
            pmax_camp_id = row.campaign.id
            pmax_camp_name = row.campaign.name
            date_value = getattr(row.segments, time_seg)
            table_data.append([
                date_value,
                row.customer.id,
                row.customer.descriptive_name,
                arc,
                row.campaign.id,
                row.campaign.name,
                channel_type,
                pmax_camp_id, # pmax ad_group.id placeholder
                pmax_camp_name, # pmax ad_group.name placeholder
                "PERFORMANCE_MAX", # pmax ad_group.type
                pmax_camp_id, # pmax ad id placeholder
                "PERFORMANCE_MAX", # pmax ad type
                Decimal(row.metrics.cost_micros / 1e6).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                row.metrics.impressions,
                row.metrics.absolute_top_impression_percentage,
                row.metrics.top_impression_percentage,
                Decimal(row.metrics.average_cpm / 1e6).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP),
                row.metrics.interactions,
                row.metrics.clicks,
                Decimal(row.metrics.average_cpc / 1e6).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP),
                row.metrics.video_views,
                row.metrics.conversions,
                row.metrics.conversions_value,
            ])
    headers = [
        "Date",
        "Customer ID",
        "Account name",
        "ARC",
        "Campaign ID",
        "Campaign name",
        "Campaign type",
        "Ad group ID",
        "Ad group name",
        "Ad group type",
        "Ad ID",
        "Ad type",
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
    # sort by: time index (0), descending cost (12)
    table_data_sorted = sorted(
        table_data,
        key=lambda r:(r[0], -float(r[12]))
    )
    return table_data_sorted, headers

def ad_level_report_all(gads_service, client, start_date, end_date, time_seg, accounts_info):
    """
    Generates ad scoped report for all accounts listed in account_info.

    Args:
        gads_service: The Google Ads service client.
        client: The authenticated Google Ads client.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        time_seg (str): Time segment or label.
        accounts_info (dict): Dictionary mapping account codes to [customer_id, descriptive_name].

    Returns:
        tuple: (all_data_sorted, headers) for display or export.
    """
    all_data = []
    headers = None
    for customer_id, account_descriptive in accounts_info.items():
        print(f"Processing {account_descriptive}...")
        try:
            table_data, headers = ad_level_report_single(
                gads_service, client, start_date, end_date, time_seg, customer_id
            )
            all_data.extend(table_data)
        except Exception as e:
            print(f"Error processing {account_descriptive} ({customer_id}): {e}")
    if not all_data:
        print("No data returned for any accounts.")
        return [], []
    # sort by: time index (0), account name (2), descending cost (12)
    all_data_sorted = sorted(
        all_data,
        key=lambda r: (r[0], r[2], -float(r[12]))
    )
    return all_data_sorted, headers

def click_view_report_single(gads_service, client, start_date, end_date, time_seg, customer_id):
    """
    Generates a click view performance report for the selected customerID/account.

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
    channel_type_enum, *extra, click_type_enum, keyword_match_type_enum, device_type_enum = undecoded_enums
    # GAQL query
    click_view_query = queries.click_view_query(start_date, end_date, time_seg_string)
    # initialize an empty list to store the data
    table_data = []
    # fetch data and populate the table_data list
    response = gads_service.search_stream(customer_id=customer_id, query=click_view_query)
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
                if getattr(row.click_view, "keyword_info", None) and hasattr(row.click_view.keyword_info, "match_type")
                else "UNDEFINED"
            )
            device_type = (
                device_type_enum.Device.Name(row.segments.device)
                if hasattr(row.segments, 'device') else 'UNDEFINED'
            )
            kw_text = (row.click_view.keyword_info.text).strip()
            # append each row's data as a list or tuple to the table_data list
            table_data.append([
                date_value,
                row.customer.descriptive_name,
                row.customer.id,
                row.campaign.name,
                row.campaign.id,
                channel_type, 
                row.ad_group.name,
                row.ad_group.id,
                row.click_view.ad_group_ad,
                row.click_view.gclid,
                row.click_view.keyword,
                keyword_match_type,
                row.click_view.keyword_info.text,
                row.click_view.page_number,
                # row.click_view.location_of_presence.country,
                # row.click_view.location_of_presence.region,
                # row.click_view.location_of_presence.metro,
                # row.click_view.location_of_presence.city,
                # row.click_view.location_of_presence.most_specific,
                device_type,
                click_type,
                row.metrics.clicks
            ])
    # define the headers for the table
    headers = [
        "Date",
        "Account name",
        "Customer ID",
        "Campaign name",
        "Campaign ID",
        "Campaign type",
        "Ad group name",
        "Ad group ID",
        "Ad",
        "gclid",
        "keyword",
        "keyword_match_type",
        "keyword_text",
        "page_number",
        # "location_of_presence_country",
        # "location_of_presence_region",
        # "location_of_presence_metro",
        # "location_of_presence_city",
        # "location_of_presence_most_specific",
        "device",
        "click type",
        "clicks",
        ]
    # sort by: time index (0), descending clicks (16)
    table_data_sorted = sorted(
        table_data,
        key=lambda r: (r[0], -float(r[16]))
        )
    return table_data_sorted, headers

def click_view_report_all(gads_service, client, start_date, end_date, time_seg, accounts_info):
    """
    Generates a click view performance report for all accounts listed in account_info.

    Args:
        gads_service: The Google Ads service client.
        client: The authenticated Google Ads client.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        time_seg (str): Time segment or label.
        accounts_info (dict): Dictionary mapping account codes to [customer_id, descriptive_name].

    Returns:
        tuple: (all_data_sorted, headers) for display or export.
    """
    all_data = []
    headers = None
    for customer_id, account_descriptive in accounts_info.items():
        print(f"Processing {account_descriptive}...")
        try:
            table_data, headers = click_view_report_single(
                gads_service, client, start_date, end_date, time_seg, customer_id
            )
            all_data.extend(table_data)
        except Exception as e:
            print(f"Error processing {account_descriptive} ({customer_id}): {e}")
    if not all_data:
        print("No data returned for any accounts.")
        return [], []
    # sort by: time index (0), account name (1), descending clicks (16)
    all_data_sorted = sorted(
        all_data,
        key=lambda r: (r[0], r[1], -float(r[16]))
    )
    return all_data_sorted, headers

def paid_org_search_term_report_single(gads_service, client, start_date, end_date, time_seg, customer_id):
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
    # GAQL query
    paid_org_search_term_query = queries.paid_organic_search_term_view_query(start_date, end_date, time_seg_string)
    # initialize an empty list to store the data
    table_data = []
    # fetch data and populate the table_data list
    response = gads_service.search_stream(customer_id=customer_id, query=paid_org_search_term_query)
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
            kw_text = (row.segments.keyword.info.text).strip()
            # append each row's data as a list or tuple to the table_data list
            table_data.append([
                date_value,
                row.customer.descriptive_name,
                row.customer.id,
                row.campaign.name,
                row.campaign.id,
                channel_type, 
                row.ad_group.name,
                row.ad_group.id,
                device_type,
                serp_type,
                keyword_match_type,
                row.segments.keyword.info.text,
                row.metrics.organic_queries,
                row.metrics.organic_impressions,
                row.metrics.organic_impressions_per_query,
                row.metrics.organic_clicks,
                row.metrics.organic_clicks_per_query,
                row.metrics.impressions, # paid impressions
                row.metrics.clicks, # paid clicks
                row.metrics.ctr, # paid ctr
                Decimal(row.metrics.average_cpc / 1e6).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP),
                row.metrics.combined_queries,
                (row.metrics.organic_impressions+row.metrics.impressions), # total combined impressions
                row.metrics.combined_clicks,
                row.metrics.combined_clicks_per_query,
            ])
    # define the headers for the table
    headers = [
        "Date",
        "Account name",
        "Customer ID",
        "Campaign name",
        "Campaign ID",
        "Campaign type",
        "Ad group name",
        "Ad group ID",
        "device",
        "SERP type",
        "keyword match type",
        "keyword text",
        "organic queries",
        "organic impr.",
        "organic impr. per query",
        "organic clicks",
        "organic clicks per query",
        "paid impr.",
        "paid clicks",
        "paid ctr",
        "avg cpc",
        "total combined queries",
        "total combined impr.",
        "total combined clicks",
        "combined clicks per query",
        ]
    # sort by: time index (0), descending total combined clicks (23)
    table_data_sorted = sorted(
        table_data,
        key=lambda r: (r[0], -float(r[23]))
        )
    return table_data_sorted, headers

def paid_org_search_term_report_all(gads_service, client, start_date, end_date, time_seg, accounts_info):
    """
    Generates a Paid and Organic Search Term report for all accounts listed in account_info.

    Args:
        gads_service: The Google Ads service client.
        client: The authenticated Google Ads client.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        time_seg (str): Time segment or label.
        accounts_info (dict): Dictionary mapping account codes to [customer_id, descriptive_name].

    Returns:
        tuple: (all_data_sorted, headers) for display or export.
    """
    all_data = []
    headers = None
    for customer_id, account_descriptive in accounts_info.items():
        print(f"Processing {account_descriptive}...")
        try:
            table_data, headers = click_view_report_single(
                gads_service, client, start_date, end_date, time_seg, customer_id
            )
            all_data.extend(table_data)
        except Exception as e:
            print(f"Error processing {account_descriptive} ({customer_id}): {e}")
    if not all_data:
        print("No data returned for any accounts.")
        return [], []
    # sort by: time index (0), account name (1), descending total combined clicks (23)
    all_data_sorted = sorted(
        all_data,
        key=lambda r: (r[0], r[1], -float(r[23]))
    )
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
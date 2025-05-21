import pydoc
from tabulate import tabulate
from decimal import Decimal, ROUND_HALF_UP
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.api_core.exceptions import TooManyRequests, ResourceExhausted
import helpers

# imports for testing
import sys

def arc_sales_report_single(gads_service, client, start_date, end_date, time_seg, customer_id):
    """
    Replicates the Google Ads Report Studio by pulling ad performance data
    with ad group and ad types using ad_group_ad as the main resource.
    """
    # Enum decoders
    channel_type_enum, ad_group_type_enum, ad_type_enum = get_enums(client)
    query = f"""
        SELECT
            segments.date,
            customer.id,
            customer.descriptive_name,
            campaign.id,
            campaign.name,
            campaign.advertising_channel_type,
            ad_group.id,
            ad_group.name,
            ad_group.type,
            ad_group_ad.ad.id,
            ad_group_ad.ad.type,
            metrics.cost_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.video_views,
            metrics.conversions,
            metrics.conversions_value
        FROM ad_group_ad
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY segments.date ASC, campaign.name ASC
    """
    response = gads_service.search_stream(customer_id=customer_id, query=query)
    table_data = []
    for batch in response:
        for row in batch.results:
            # ENUM decoding with fallbacks
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
            table_data.append([
                row.segments.date,
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
                row.metrics.clicks,
                row.metrics.video_views,
                row.metrics.conversions,
                row.metrics.conversions_value,
            ])
    headers = [
        "Day",
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
        "Clicks",
        "Views",
        "Conversions",
        "Conv. value",
    ]
    return table_data, headers

def arc_sales_report_all(gads_service, client, start_date, end_date, time_seg, accounts_info):
    """
    Generates ARC sales report for all accounts listed in account_info.

    Args:
        gads_service: The Google Ads service client.
        client: The authenticated Google Ads client.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        time_seg (str): Time segment or label.
        accounts_info (dict): Dictionary mapping account codes to [customer_id, descriptive_name].

    Returns:
        tuple: (sorted_data, headers) for display or export.
    """
    all_data = []
    headers = None
    for customer_id, account_descriptive in accounts_info.items():
        print(f"Processing {account_descriptive}...")
        try:
            table_data, headers = arc_sales_report_single(
                gads_service, client, start_date, end_date, time_seg, customer_id
            )
            all_data.extend(table_data)
        except Exception as e:
            print(f"Error processing {account_descriptive} ({customer_id}): {e}")
    if not all_data:
        print("No data returned for any accounts.")
        return [], []
    # Sort by: Day (0), Account name (2), descending Cost (12)
    table_data = sorted(
        all_data,
        key=lambda r: (r[0], r[2], -float(r[12]))
    )
    return table_data, headers

def account_report(gads_service, client, start_date, end_date, time_seg, customer_id):
    query = f"""
    SELECT
    customer.descriptive_name,
    customer.id,
    metrics.clicks,
    metrics.impressions,
    metrics.ctr,
    metrics.average_cpc,
    metrics.cost_micros,
    metrics.absolute_top_impression_percentage,
    metrics.top_impression_percentage,
    metrics.average_cpm
    FROM customer
    WHERE customer.status = 'ENABLED'
    AND segments.date BETWEEN '{start_date}' AND '{end_date}'
    ORDER BY 
        customer.descriptive_name DESC
    """ 
    # Initialize an empty list to store the data
    table_data = []
    # Fetch data and populate the table_data list
    response = gads_service.search_stream(customer_id=customer_id, query=query)
    for data in response:
        for row in data.results:
            # Append each row's data as a list or tuple to the table_data list
            table_data.append([
                row.customer.descriptive_name,
                row.customer.id,
                row.metrics.clicks,
                row.metrics.impressions,
                row.metrics.ctr,
                row.metrics.average_cpc,
                row.metrics.cost_micros,
                row.metrics.absolute_top_impression_percentage,
                row.metrics.top_impression_percentage,
                row.metrics.average_cpm,
            ])
    # Define the headers for the table
    headers = [
        "property",
        "customer id",
        "clicks",
        "impressions",
        ]
    return table_data, headers

def complete_labels_audit(gads_service, client, customer_id):
    channel_type_enum, ad_group_type_enum, _ = get_enums(client)
    # get label and campaign group metadata
    label_table, label_table_headers, label_dict = get_labels(gads_service, client, customer_id)
    camp_group_table, camp_group_headers, camp_group_dict = get_campaign_groups(gads_service, client, customer_id)
    # query campaigns + ad groups
    audit_query = """
        SELECT
            customer.id,
            customer.descriptive_name,
            campaign.id,
            campaign.name,
            campaign.advertising_channel_type,
            campaign.campaign_group,
            campaign.labels,
            ad_group.id,
            ad_group.name,
            ad_group.type,
            ad_group.labels
        FROM ad_group
        WHERE ad_group.status != 'REMOVED'
        ORDER BY customer.descriptive_name ASC, campaign.name ASC, ad_group.name ASC
    """
    response = gads_service.search_stream(customer_id=customer_id, query=audit_query)
    audit_table = []
    audit_dict = {}
    for batch in response:
        for row in batch.results:
            # Decode enum fields
            channel_type = channel_type_enum.AdvertisingChannelType.Name(
                row.campaign.advertising_channel_type
            ) if hasattr(row.campaign, 'advertising_channel_type') else 'UNDEFINED'
            ad_group_type = ad_group_type_enum.AdGroupType.Name(
                row.ad_group.type_
            ) if hasattr(row.ad_group, 'type_') else 'UNDEFINED'
            # Resolve labels
            campaign_labels = [
                label_dict.get(label.split('/')[-1], 'UNDEFINED') for label in row.campaign.labels
            ]
            ad_group_labels = [
                label_dict.get(label.split('/')[-1], 'UNDEFINED') for label in row.ad_group.labels
            ]
            # Campaign group name
            campaign_group_id = row.campaign.campaign_group.split('/')[-1]
            campaign_group_name = camp_group_dict.get(campaign_group_id, 'UNDEFINED')
            # Build flat row
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
            # Build structured dict
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

def get_accounts(gads_service, customer_service, client):
    """
    Fetches the accounts from the Google Ads API client.
    """
    customer_resource_query = """
        SELECT
        customer.id, 
        customer.descriptive_name 
        FROM customer
    """
    accounts_list = []
    # placeholder for building dict with account hierarchy
    customer_dict = {}
    customer_resources = (
        customer_service.list_accessible_customers().resource_names
        )
    customer_ids = [
        gads_service.parse_customer_path(customer_resource)["customer_id"] for customer_resource in customer_resources
        ]
    """ a better build for customer_dict once testing is complete
    account_dict = {
        str(row.customer.id): str(row.customer.descriptive_name)
        for customer_id in customer_ids
        for batch in gads_service.search_stream(customer_id=customer_id, query=customer_resource_query)
        for row in batch.results
    }
    """
    for customer_id in customer_ids:
        customer_response = gads_service.search_stream(
            customer_id=customer_id, 
            query=customer_resource_query
            )
        for data in customer_response:
            for row in data.results:
                accounts_list.append([
                    row.customer.id,
                    row.customer.descriptive_name,
                ])
                customer_dict[row.customer.id] = row.customer.descriptive_name
    account_headers = [
        "account id",
        "account name"
    ]
    account_dict = {str(k): str(v) for k, v in customer_dict.items()} # type protect customer_dict
    return accounts_list, account_headers, account_dict, len(customer_ids)

def get_enums(client):
    """
    Fetches the enums for AdvertisingChannelType and AdGroupType from the Google Ads API client.
    """
    channel_type_enum = client.enums.AdvertisingChannelTypeEnum
    ad_group_type_enum = client.enums.AdGroupTypeEnum
    ad_type_enum = client.enums.AdTypeEnum
    return channel_type_enum, ad_group_type_enum, ad_type_enum

def get_labels(gads_service, client, customer_id):
    label_query = """
        SELECT 
        label.name, 
        label.id
        FROM label
        WHERE label.status = 'ENABLED'
        ORDER BY label.name ASC
    """
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
    camp_group_query = """
        SELECT
        campaign_group.name,
        campaign_group.id
        FROM campaign_group
        WHERE campaign_group.status = 'ENABLED'
        ORDER BY campaign_group.name ASC 
    """
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

def test_query(gads_service, client, customer_id):
    return

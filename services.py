import pydoc
from tabulate import tabulate
from decimal import Decimal, ROUND_HALF_UP
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.api_core.exceptions import TooManyRequests, ResourceExhausted
import helpers

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
            ad_type = (
                ad_type_enum.AdType.Name(row.ad_group_ad.ad.type_)
                if hasattr(row.ad_group_ad.ad, 'type_') else 'UNDEFINED'
            )
            ad_group_type = (
                ad_group_type_enum.AdGroupType.Name(row.ad_group.type_)
                if hasattr(row.ad_group, 'type_') else 'UNDEFINED'
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
    Generates ARC sales report for all accounts listed in prop_info.

    Args:
        gads_service: The Google Ads service client.
        client: The authenticated Google Ads client.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str): End date (YYYY-MM-DD).
        time_seg (str): Time segment or label.
        prop_info (dict): Dictionary mapping account codes to [customer_id, domain].

    Returns:
        tuple: (sorted_data, headers) for display or export.
    """
    all_data = []
    headers = None
    for prop_reference, (customer_id, prop_descriptive) in accounts_info.items():
        print(f"Processing {prop_reference}...")
        try:
            table_data, headers = arc_sales_report_single(
                gads_service, client, start_date, end_date, time_seg, customer_id
            )
            all_data.extend(table_data)
        except Exception as e:
            print(f"Error processing {prop_reference} ({customer_id}): {e}")
    if not all_data:
        print("No data returned for any accounts.")
        return [], []
    # Sort by: Day (0), Account name (2), descending Cost (12)
    table_data = sorted(
        all_data,
        key=lambda r: (r[0], r[2], -float(r[12]))
    )
    return table_data, headers

def account_report(client, customer_id):
    gads_service = client.get_service("GoogleAdsService")
    query = """
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

def label_service_audit(gads_service, client, customer_id):
    gads_service = client.get_service("GoogleAdsService")
    query = """
        SELECT 
        label.name, 
        label.id, 
        customer.descriptive_name 
        FROM label
        WHERE label.status = 'ENABLED'
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
                row.label.name,
                row.label.id,
            ])
    # Define the headers for the table
    headers = [
        "property",
        "label name",
        "label id",
        ]
    # Display the data using tabulate
    input("Report ready for viewing. Press ENTER to display results and 'Q' to exit output when done...")
    pydoc.pager(tabulate(table_data, headers=headers, tablefmt="simple_grid"))

def complete_labels_audit(gads_service, client, start_date, end_date, time_seg, customer_id):
    channel_type_enum, ad_group_type_enum, ad_type_enum = get_enums(client)
    # Fetch label data
    label_query = """
        SELECT 
        label.name, 
        label.id, 
        customer.descriptive_name 
        FROM label
        WHERE label.status = 'ENABLED'
        ORDER BY 
            customer.descriptive_name DESC
    """
    label_response = gads_service.search_stream(customer_id=customer_id, query=label_query)
    # process label data
    label_data = {}
    for batch in label_response:
        for row in batch.results:
            label_data[str(row.label.id)] = row.label.name
    # fetch campaign group data
    camp_group_query = """
        SELECT
        campaign_group.name,
        campaign_group.id,
        customer.descriptive_name
        FROM campaign_group
        WHERE
        campaign_group.status = 'ENABLED'
        ORDER BY
        customer.descriptive_name   
    """
    camp_group_response = gads_service.search_stream(customer_id=customer_id, query=camp_group_query)
    # Process campaign group data
    camp_group_data = {}
    for batch in camp_group_response:
        for row in batch.results:
            camp_group_data[str(row.campaign_group.id)] = row.campaign_group.name
    # Fetch ad group metrics data
    metrics_query = f"""
        SELECT
        segments.date,
        customer.descriptive_name,
        campaign.name,
        campaign.campaign_group,
        campaign.labels,
        ad_group.name,
        ad_group.labels,
        ad_group.id,
        campaign.id,
        campaign.advertising_channel_type,
        metrics.cost_micros,
        metrics.impressions,
        metrics.clicks,
        metrics.interactions,
        metrics.conversions,
        metrics.conversions_value,
        customer.id
        FROM ad_group 
        WHERE 
        metrics.clicks > 0
        AND segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY 
        segments.date ASC,
        customer.descriptive_name ASC,
        campaign.name ASC,
        ad_group.name ASC
    """
    # Initialize list
    table_data = []
    response = gads_service.search_stream(customer_id=customer_id, query=metrics_query)
    # Process ad group metrics data
    for batch in response:
        for row in batch.results:
            # Transform campaign type
            channel_type_value = row.campaign.advertising_channel_type
            channel_type_name = channel_type_enum.AdvertisingChannelType.Name(channel_type_value)
            # campaign_type = str(row.campaign.advertising_channel_type)
            # campaign_type = campaign_type if campaign_type in ac.CAMPAIGN_TYPES else 'UNDEFINED'
            # Transform ad group labels
            ad_group_label_list = []
            for label_string in row.ad_group.labels:
                label_id = label_string.split('/')[-1]
                label_name = label_data.get(label_id, 'UNDEFINED')
                ad_group_label_list.append(label_name)
            # Transform campaign labels
            campaign_label_list = []
            for label_string in row.campaign.labels:
                label_id = label_string.split('/')[-1]
                label_name = label_data.get(label_id, 'UNDEFINED')
                campaign_label_list.append(label_name)
            # Transform campaign group
            campaign_group_id = row.campaign.campaign_group.split('/')[-1]
            campaign_group_name = camp_group_data.get(campaign_group_id, 'UNDEFINED')
            # Append data rows, ensure continuity
            table_data.append([
                row.segments.date,
                row.customer.descriptive_name,
                row.campaign.name,
                campaign_group_name,  # Transformed campaign group name
                ', '.join(campaign_label_list),  # Combine transformed campaign label names into a single string
                row.ad_group.name,
                ', '.join(ad_group_label_list),  # Combine transformed ad group label names into a single string
                row.ad_group.id,
                row.campaign.id,
                channel_type_name,
                Decimal(row.metrics.cost_micros / 1e6).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                row.metrics.impressions,
                row.metrics.clicks,
                row.metrics.interactions,
                row.metrics.conversions,
                row.metrics.conversions_value,
                row.customer.id
            ])
    # Define headers
    headers = [
        "date",
        "property",
        "campaign name",
        "campaign group",
        "campaign labels",
        "ad_group name",
        "ad_group labels",
        "ad_group id",
        "campaign id",
        "campaign channel_type",
        "cost",
        "impressions",
        "clicks",
        "interactions",
        "conversions",
        "conversions value",
        "property id"
    ]

    # Display using tabulate
    print("NOTICE: Current timeframe displayed is LAST 7 DAYS for testing. ")
    input("Report ready for viewing. Press ENTER to display results...")
    pydoc.pager(tabulate(table_data, headers=headers, tablefmt="simple_grid"))

def campaign_group_audit(client, customer_id):
    gads_service = client.get_service("GoogleAdsService")
    query = """
        SELECT
        campaign_group.name,
        campaign_group.id,
        customer.descriptive_name
        FROM campaign_group
        WHERE
        campaign_group.status = 'ENABLED'
        ORDER BY
        customer.descriptive_name  
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
                row.campaign_group.name,
                row.campaign_group.id,
            ])
    # Define the headers for the table
    headers = [
        "property",
        "group name",
        "group id",
        ]
    # Display the data using tabulate
    input("Report ready for viewing. Press ENTER to display results and 'Q' to exit output when done...")
    pydoc.pager(tabulate(table_data, headers=headers, tablefmt="simple_grid"))

    # fetch campaign_group data
    camp_group_query = """
        SELECT
        campaign_group.name,
        campaign_group.id,
        customer.descriptive_name
        FROM campaign_group
        WHERE
        campaign_group.status = 'ENABLED'
        ORDER BY
        customer.descriptive_name   
    """
    camp_group_response = gads_service.search_stream(customer_id=customer_id, query=camp_group_query)
    # process label data
    camp_group_data = {}
    for data in camp_group_response:
        for row in data.results:
            camp_group_data[str(row.campaign_group.id)] = row.campaign_group.name

            # transform campaign labels
            campaign_group_list = []
            for camp_group_string in row.campaign.campaign_group:
                camp_group_id = camp_group_string.split('/')[-1]
                camp_group_name = camp_group_data.get(camp_group_id, 'UNDEFINED')
                campaign_group_list.append(camp_group_name)

def label_service(client, customer_id):
    gads_service = client.get_service("GoogleAdsService")
    query = """
        SELECT 
        label.name, 
        label.id, 
        customer.descriptive_name 
        FROM label
        WHERE label.status = 'ENABLED'
        ORDER BY 
            customer.descriptive_name DESC
    """
    response = gads_service.search_stream(customer_id=customer_id, query=query)
    labels = {}
    for batch in response:
        for row in batch.results:
            label_id = str(row.label.id)  # Ensure label_id is stored as a string
            label_name = row.label.name
            labels[label_id] = label_name
    return labels

def get_enums(client):
    """
    Fetches the enums for AdvertisingChannelType and AdGroupType from the Google Ads API client.
    """
    channel_type_enum = client.enums.AdvertisingChannelTypeEnum
    ad_group_type_enum = client.enums.AdGroupTypeEnum
    ad_type_enum = client.enums.AdTypeEnum
    return channel_type_enum, ad_group_type_enum, ad_type_enum

def get_labels(client, customer_id):
    # Fetch label data
    label_query = """
        SELECT 
        label.name, 
        label.id, 
        customer.descriptive_name 
        FROM label
        WHERE label.status = 'ENABLED'
        ORDER BY 
            customer.descriptive_name DESC
    """
    label_response = client.search_stream(customer_id=customer_id, query=label_query)
    # process label data
    label_data = {}
    for batch in label_response:
        for row in batch.results:
            label_data[str(row.label.id)] = row.label.name
    return label_data

def get_campaign_groups(client, customer_id):
    # fetch campaign group data
    camp_group_query = """
        SELECT
        campaign_group.name,
        campaign_group.id,
        customer.descriptive_name
        FROM campaign_group
        WHERE
        campaign_group.status = 'ENABLED'
        ORDER BY
        customer.descriptive_name   
    """
    camp_group_response = client.search_stream(customer_id=customer_id, query=camp_group_query)
    # process campaign group data
    camp_group_data = {}
    for batch in camp_group_response:
        for row in batch.results:
            camp_group_data[str(row.campaign_group.id)] = row.campaign_group.name
    return camp_group_data

def test_query(gads_service, client, customer_id):
    return
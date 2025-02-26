import pydoc
from tabulate import tabulate
from authfiles import account_constants as ac
from decimal import Decimal, ROUND_HALF_UP
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.api_core.exceptions import TooManyRequests, ResourceExhausted

def label_service_audit(client, customer_id):
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

def ad_group_metrics_service_report(client, start_date, end_date, time_seg, customer_id):
    gads_service = client.get_service("GoogleAdsService")
    channel_type_enum = client.get_type('AdvertisingChannelTypeEnum', version='v18')
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


"""
# MAIN SERVICE
 
The following function encompasses needed processes for collecting, store and writing necessary group and label data for campaigns and ad groups
1. fetch identifiers for campaigns & ad_groups
2. fetch metrics in 'ad_group' scope
3. process table with transformed lists
4. write to file or display 


def ad_group_metrics_report(client, customer_id, start_date, end_date, time_seg):
    gads_service = client.get_service("GoogleAdsService")
    # fetch campaign_group data
    camp_group_query = 
        SELECT
        campaign_group.name,
        campaign_group.id,
        customer.descriptive_name
        FROM campaign_group
        WHERE
        campaign_group.status = 'ENABLED'
        ORDER BY
        customer.descriptive_name   
    
    camp_group_response = gads_service.search_stream(customer_id=customer_id, query=camp_group_query)
    # process label data
    camp_group_data = {}
    for data in camp_group_response:
        for row in data.results:
            camp_group_data[str(row.campaign_group.id)] = row.campaign_group.name
    # fetch label data
    label_query = 
        SELECT 
        label.name, 
        label.id, 
        customer.descriptive_name 
        FROM label
        WHERE label.status = 'ENABLED'
        ORDER BY 
            customer.descriptive_name DESC
    
    label_response = gads_service.search_stream(customer_id=customer_id, query=label_query)
    # process label data
    label_data = {}
    for data in label_response:
        for row in data.results:
            label_data[str(row.label.id)] = row.label.name
    # fetch metrics data
    metrics_query = f
        SELECT
        segments.{time_seg},
        customer.descriptive_name,
        campaign.name,
        campaign.campaign_group,
        campaign.labels,
        ad_group.name,
        ad_group.labels,
        campaign.advertising_channel_type,
        metrics.cost_micros,
        metrics.impressions,
        metrics.clicks,
        metrics.interactions,
        metrics.conversions,
        metrics.conversions_value,
        customer.id,
        campaign.id,
        ad_group.id
        FROM ad_group 
        WHERE 
        metrics.clicks > 0
        AND segments.{time_seg} BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY 
        segments.{time_seg} ASC,
        customer.descriptive_name ASC,
        campaign.name ASC,
        ad_group.name ASC
    
    #debug - query
    print(f"Query:\n"
          f"{metrics_query}")
    input("Pause for debug, enter 'ex' to exit or ENTER to continue.")
    
    # init
    table_data = []
    metrics_response = gads_service.search_stream(customer_id=customer_id, query=metrics_query)
    # process data
    for data in metrics_response:
        for row in data.results:
            # transform campaign type
            campaign_type = _constants.CAMPAIGN_TYPES.get(str(row.campaign.advertising_channel_type), 'UNDEFINED')
            # Transform campaign group
            campaign_group_id = row.campaign.campaign_group.split('/')[-1]
            campaign_group_name = camp_group_data.get(campaign_group_id, 'UNDEFINED')
            # transform ad group labels
            ad_group_label_list = []
            for label_string in row.ad_group.labels:
                label_id = label_string.split('/')[-1]
                label_name = label_data.get(label_id, 'UNDEFINED')
                ad_group_label_list.append(label_name)
            # transform campaign labels
            campaign_label_list = []
            for label_string in row.campaign.labels:
                label_id = label_string.split('/')[-1]
                label_name = label_data.get(label_id, 'UNDEFINED')
                campaign_label_list.append(label_name)
            # append data rows, ensure continuity
            table_data.append([
                row.segments.date,
                row.customer.descriptive_name,
                row.campaign.name,
                campaign_group_name, # campaign.groups
                ', '.join(campaign_label_list), # campaign.labels
                row.ad_group.name,
                ', '.join(ad_group_label_list), # ad_group.labels
                row.ad_group.id,
                row.campaign.id,
                campaign_type,  # Transformed to descriptive name
                Decimal(row.metrics.cost_micros / 1e6).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                row.metrics.impressions,
                row.metrics.clicks,
                row.metrics.interactions,
                row.metrics.conversions,
                row.metrics.conversions_value,
                row.customer.id
            ])
    # headers for table
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
    # display
    input("Report ready for viewing. Press ENTER to display results and 'Q' to exit output when done...")
    pydoc.pager(tabulate(table_data, headers=headers, tablefmt="simple_grid"))

    
old services functions:

# cid param
def display_cid_list():
    # init an empty list to store the data
    table_data = []
    # populate the table_data list with data
    for pID, cID in _constants.CUSTOMER_IDS.items():
        table_data.append([pID, cID])
    # headers
    headers = ['Property', 'CustomerID']
    # display
    print((tabulate(table_data, headers=headers, tablefmt="simple_grid")))

NEEDS TESTING - then move to query
def get_timerange():
    while True:
        print("Search for:\n"
              "1. Specific date\n"
              "2. Range of dates\n")
        date_opt_input = input("Enter 1 or 2: ")
        if date_opt_input == '1':
            date_opt = 'Specific date'
            spec_date = input("What day would you like to retrieve data for (YYYY-MM-DD): ")
            start_date = spec_date
            end_date = spec_date
            time_seg = 'date'  # time_reg day options as below
            return date_opt, start_date, end_date, time_seg
        elif date_opt_input == '2':
            date_opt = 'Date range'
            start_date_input = input("Start Date (YYYY-MM-DD): ")
            end_date_input = input("End Date (YYYY-MM-DD): ")
            # placeholders if needing to convert input
            start_date = start_date_input
            end_date = end_date_input
            while True:
                print("Select a time segmentation for your requested date range: \n"
                      "1. Day\n"
                      "2. Week\n"
                      "3. Month\n"
                      "4. Quarter\n"
                      "5. Year")
                time_seg_input = input("Select one of the options (1-5) from above: ")
                if time_seg_input not in ['1', '2', '3', '4', '5']:
                    print("Invalid option, please choose from one of the provided options.")
                else:
                    # transform time_seg
                    time_seg_options = {'1': 'date', '2': 'week', '3': 'month', '4': 'quarter', '5': 'year'}
                    time_seg = time_seg_options.get(time_seg_input)
                    if time_seg is None:
                        raise ValueError("Invalid time segmentation option provided.")
                    return date_opt, start_date, end_date, time_seg
        else:
            print("Invalid option")

# service function for fetching label data only
v1
def label_service(client, customer_id):
    gads_service = client.get_service("GoogleAdsService")
    query = 
        SELECT 
        label.name, 
        label.id, 
        customer.descriptive_name 
        FROM label
        WHERE label.status = 'ENABLED'
        ORDER BY 
            customer.descriptive_name DESC

    response = gads_service.search_stream(customer_id=customer_id, query=query)
    labels = {}
    for batch in response:
        for row in batch.results:
            label_id = str(row.label.id)  # Ensure label_id is stored as a string
            label_name = row.label.name
            labels[label_id] = label_name
    return labels

v2?
def label_service_audit(client, customer_id):
    gads_service = client.get_service("GoogleAdsService")
    query = 
        SELECT 
        label.name, 
        label.id, 
        customer.descriptive_name 
        FROM label
        WHERE label.status = 'ENABLED'
        ORDER BY 
            customer.descriptive_name DESC
        
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

# service function for fetching campaign groups only
def campaign_group_audit(client, customer_id):
    gads_service = client.get_service("GoogleAdsService")
    query = 
        SELECT
        campaign_group.name,
        campaign_group.id,
        customer.descriptive_name
        FROM campaign_group
        WHERE
        campaign_group.status = 'ENABLED'
        ORDER BY
        customer.descriptive_name  
        
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


"""
# updated - 5/5/25

# imports
import os
import sys
from datetime import datetime
from pathlib import Path

# gads
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# helpers
import auth
import helpers
import services
from authfiles import account_constants

# establish vars
prop_dict = account_constants.PROP_INFO
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
default_file_name = f"gads_report_{timestamp}.csv"

# MENUS
def main_menu(gads_service, client):
    """    
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
        """
    
    print("Select a property to report on:\n")
    prop_info = helpers.display_prop_list(prop_dict)
    prop_name, prop_id, prop_url = prop_info

    # debug constants info
    print(f"\nSelected prop info:\n"
          f"prop_name: {prop_name}\n"
          f"prop_id: {prop_id}\n"
          f"prop_url: {prop_url}")
    input("Pause for debug...")

    print("Select a data scope:\n"
          "1. Reporting\n"
          "2. Auditing\n")
    data_scope = input("Choose 1 or 2 ('exit' to exit): ")
    if data_scope == '1':
        print("Reporting selected.")
        report_menu(gads_service, client, prop_info)
    elif data_scope == '2':
        print("Auditing selected.")
        audit_menu(gads_service, client, prop_info)
    else:
        print("Invalid input, please select one of the indicated numbered options.")
        # exit
        sys.exit(1)

def report_menu(gads_service, client, prop_info):
    prop_name, prop_id, prop_url = prop_info
    print("Reporting Options:\n"
        "1. ARC Sales Report\n"
        "9. Test Query\n"
        "Or type 'exit' at any prompt to quit immediately.\n")
    service_opt = input("Choose 1, 2, 3, 4, etc ('exit' to exit): ")
    if service_opt == '1':
        # date_opt, start_date, end_date, time_seg = _query.get_timerange()
        report_date_details = helpers.get_timerange()
        date_opt, start_date, end_date, time_seg = report_date_details
        # date_opt = report_date_details[0]
        # time_seg = report_date_details[3]
        # start_date = report_date_details[1]
        # end_date = report_date_details[2]
        date_vars = {}
        start_string_value = "start"
        end_string_value = "end"
        date_vars[start_string_value] = f"'{start_date}'"
        date_vars[end_string_value] = f"'{end_date}'"
        """ testing - timeframe transformations, date_opt scope      
        if date_opt == 'EQUALS': # AD_GROUP_SINGLE
            time_condition = '='
            start_date = date_vars["start"]
        elif date_opt == 'BETWEEN': # AD_GROUP_RANGE
            time_condition = date_opt
            start_date = date_vars["start"]
            end_date = date_vars["end"]
        elif date_opt == 'DURING': # AD_GROUP_SINGLE
            start_date = time_seg
            time_condition = date_opt
            time_seg = 'date'
        else:
            raise ValueError("Improper input or incorrect report date details")
        """
        # query testing
        print("\nServices params passback after get_timerange:\n"
            f"date_opt: {date_opt}\n"
            f"time_seg: {time_seg}\n"
            f"start_date: {start_date}\n"
            f"end_date: {end_date}\n")
            # f"time_condition: {time_condition}")
        input("\nPause for debug - press ENTER to continue or input 'exit' to exit")

        table_data, headers = services.arc_sales_report(
            gads_service, client, start_date, end_date, time_seg, customer_id=prop_id)
        print("Report complied! How would yo like to view the report?\n"
              "1. CSV\n"
              "2. Display table on screen\n")
        report_view = input("Choose 1 or 2 ('exit' to exit): ")
        if report_view == '1':
            # save to csv
            helpers.save_csv(table_data, headers)
        elif report_view == '2':
            # display table
            helpers.display_table(table_data, headers)
        else:
            print("Invalid input, please select one of the indicated options.")
            # exit
            sys.exit(1)

    elif service_opt == '9':
        services.test_query(gads_service, client, customer_id=prop_id)
    else:
        print("Invalid input, please select one of the indicated options.")
        # exit
        sys.exit(1)

def audit_menu(gads_service, client, prop_info):
    prop_name, prop_id, prop_url = prop_info
    print("Auditing Options:\n"
        "1. Account Labels List\n"
        "2. Campaign Group List\n"
        "3. Campaign and Ad Group Label Assignments\n"
        "Or type 'exit' at any prompt to quit immediately.\n")
    service_opt = input("Choose 1, 2, 3, 4, etc ('exit' to exit): ")
    if service_opt == '1':
        # label_service_audit(client, customer_id)
        services.label_service_audit(gads_service, client, customer_id=prop_id)
    elif service_opt == '2':
        # campaign_group_audit((client, customer_id)
        services.campaign_group_audit(gads_service, client, customer_id=prop_id)
    elif service_opt == '3':
        # date_opt, start_date, end_date, time_seg = _query.get_timerange()
        report_date_details = helpers.get_timerange()
        date_opt, start_date, end_date, time_seg = report_date_details
        # date_opt = report_date_details[0]
        # time_seg = report_date_details[3]
        # start_date = report_date_details[1]
        # end_date = report_date_details[2]
        date_vars = {}
        start_string_value = "start"
        end_string_value = "end"
        date_vars[start_string_value] = f"'{start_date}'"
        date_vars[end_string_value] = f"'{end_date}'"
        """ testing - timeframe transformations, date_opt scope      
        if date_opt == 'EQUALS': # AD_GROUP_SINGLE
            time_condition = '='
            start_date = date_vars["start"]
        elif date_opt == 'BETWEEN': # AD_GROUP_RANGE
            time_condition = date_opt
            start_date = date_vars["start"]
            end_date = date_vars["end"]
        elif date_opt == 'DURING': # AD_GROUP_SINGLE
            start_date = time_seg
            time_condition = date_opt
            time_seg = 'date'
        else:
            raise ValueError("Improper input or incorrect report date details")
        """
        # query testing
        print("\nServices params passback after get_timerange:\n"
            f"date_opt: {date_opt}\n"
            f"time_seg: {time_seg}\n"
            f"start_date: {start_date}\n"
            f"end_date: {end_date}\n")
            # f"time_condition: {time_condition}")
        input("\nPause for debug - press ENTER to continue or input 'exit' to exit")

        # time_detail = _query.TIME_DETAIL_STRINGS.get(date_opt)

        # debug
        # print(time_detail)
        # input("Pause for debug, enter 'exit' to exit or ENTER to continue.")

        # execute full report
        services.ad_group_metrics_service_report(gads_service, client, start_date, end_date, time_seg, customer_id=prop_id)
        # services.ad_group_metrics_service_report(client, time_condition, start_date, end_date, time_seg, customer_id=prop_id)
    elif service_opt == '4':
        services.click_view_metrics_report(gads_service, client, customer_id=prop_id)
    else:
        print("Invalid input, please select one of the indicated options.")


# @helpers.handle_exceptions
def main():
    print("\nGoogle Ads Reporter, developed by JDT using GAds API and gRPC\n"
          "NOTE: Enter 'exit' at any prompt will exit this reporting tool.")
    input("Press Enter When Ready...")
    # generate service
    gads_service, client = auth.generate_services()
    main_menu(gads_service, client)

if __name__ == '__main__':
    main()
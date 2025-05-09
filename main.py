# updated - 5/5/25

# imports
import os
import sys
from datetime import datetime
from pathlib import Path
import time

# gads
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# helpers
import auth
import helpers
import services

# establish vars
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
default_file_name = f"gads_report_{timestamp}.csv"

# MENUS
def main_menu(gads_service, client):
    print("Main Menu - Select from the options below:\n"
          "1. ARC Reporting\n"
          "2. Auditing\n")
    data_scope = input("Choose a numbered option (1, 2, etc or 'exit' to exit): ")
    if data_scope == '1':
        print("ARC Reporting selected.")
        report_menu(gads_service, client)
    elif data_scope == '2':
        print("Auditing selected.")
        audit_menu(gads_service, client)
    else:
        print("Invalid input, please select one of the indicated numbered options.")
        # exit
        sys.exit(1)

def report_menu(gads_service, client):
    print("Reporting Options:\n"
        "1. ARC Sales Report - Single Property\n"
        "2. ARC Sales Report - All Properties\n"
        # "3. ARC Sales Report - US Properties\n"
        # "4. ARC Sales Report - EU Properties\n"
        # "5. ARC Sales Report - AU Properties\n"
        # "6. ARC Sales Report - TW Properties\n"
        # "7. ARC Sales Report - RW Properties\n"
        # "8. ARC Sales Report - PKW Properties\n"
        # "9. ARC Sales Report - PAD Properties\n"
        "X. Test Query\n"
        "Or type 'exit' at any prompt to quit immediately.\n")
    service_opt = input("Choose 1, 2, 3, 4, etc ('exit' to exit): ").lower()
    if service_opt == '1':
        print("ARC Sales Report - Single Property selected...")
        prop_info = services.get_account_properties()
        prop_name, prop_id, prop_url = prop_info
        report_date_details = helpers.get_timerange()
        date_opt, start_date, end_date, time_seg = report_date_details
        date_vars = {}
        start_string_value = "start"
        end_string_value = "end"
        date_vars[start_string_value] = f"'{start_date}'"
        date_vars[end_string_value] = f"'{end_date}'"

        # debug
        print("\nServices params passback after get_timerange:\n"
            f"date_opt: {date_opt}\n"
            f"time_seg: {time_seg}\n"
            f"start_date: {start_date}\n"
            f"end_date: {end_date}\n")
            # f"time_condition: {time_condition}")
        input("\nPause for debug - press ENTER to continue or input 'exit' to exit")

        # start time
        start_time = time.time()
        table_data, headers = services.arc_sales_report_single(
            gads_service, client, start_date, end_date, time_seg, customer_id=prop_id)
        end_time = time.time()
        print(f"Report complied!\n"
              f"Execution time: {end_time - start_time:.2f} seconds\n")
        # handle data
        helpers.data_handling_options(table_data, headers)
    elif service_opt == '2':
        print("ARC Sales Report - All Properties selected.")
        report_date_details = helpers.get_timerange()
        date_opt, start_date, end_date, time_seg = report_date_details
        date_vars = {}
        start_string_value = "start"
        end_string_value = "end"
        date_vars[start_string_value] = f"'{start_date}'"
        date_vars[end_string_value] = f"'{end_date}'"

        # query testing
        print("\nServices params passback after get_timerange:\n"
            f"date_opt: {date_opt}\n"
            f"time_seg: {time_seg}\n"
            f"start_date: {start_date}\n"
            f"end_date: {end_date}\n")
            # f"time_condition: {time_condition}")
        input("\nPause for debug - press ENTER to continue or input 'exit' to exit")

        all_prop_data, headers = services.arc_sales_report_all(
            gads_service, client, start_date, end_date, time_seg)
        # handle data
        helpers.data_handling_options(all_prop_data, headers)

    elif service_opt == 'x':
        services.test_query(gads_service, client, customer_id=prop_id)
    else:
        print("Invalid input, please select one of the indicated options.")
        # exit
        sys.exit(1)

def audit_menu(gads_service, client):
    print("Auditing Options:\n"
        "1. Account Labels List\n"
        "2. Campaign Group List\n"
        "3. Campaign and Ad Group Label Assignments\n"
        "Or type 'exit' at any prompt to quit immediately.\n")
    service_opt = input("Choose 1, 2, 3, 4, etc ('exit' to exit): ")
    if service_opt == '1':
        prop_info = services.get_account_properties()
        prop_name, prop_id, prop_url = prop_info
        # label_service_audit(client, customer_id)
        services.label_service_audit(gads_service, client, customer_id=prop_id)
    elif service_opt == '2':
        prop_info = services.get_account_properties()
        prop_name, prop_id, prop_url = prop_info
        # campaign_group_audit((client, customer_id)
        services.campaign_group_audit(gads_service, client, customer_id=prop_id)
    elif service_opt == '3':
        prop_info = services.get_account_properties()
        prop_name, prop_id, prop_url = prop_info
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
        services.complete_labels_audit(gads_service, client, start_date, end_date, time_seg, customer_id=prop_id)
    # elif service_opt == '4':
        # services.click_view_metrics_report(gads_service, client, customer_id=prop_id)
    else:
        print("Invalid input, please select one of the indicated options.")


@helpers.handle_exceptions
def main():
    print("\nGoogle Ads Reporter, developed by JDT using GAds API and gRPC\n"
          "NOTE: Enter 'exit' at any prompt will exit this reporting tool.")
    input("Press Enter When Ready...")
    # generate service
    gads_service, client = auth.generate_services()
    main_menu(gads_service, client)

if __name__ == '__main__':
    main()
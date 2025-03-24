# updated - 2/25/25

# imports
import os
import sys
from datetime import datetime
from pathlib import Path

# gads
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# helpers
import helpers
import services
from authfiles import account_constants

# establish vars
YAML = "gads_auth.yaml"
filepath = os.path.dirname(os.path.realpath(__file__))
auth_dir = os.path.join(filepath, "authfiles")
yaml_loc = os.path.join(auth_dir, YAML)
prop_dict = account_constants.PROP_INFO
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
default_file_name = f"gads_report_{timestamp}.csv"

# MENUS
def services_menu(prop_info):
    client = GoogleAdsClient.load_from_storage(yaml_loc)
    prop_name, prop_id, prop_url = prop_info
    while True:
        print(f"Which service to execute for {prop_name}?\n"
            "1. Labels Audit\n"
            "2. Campaign Group Audit\n"
            "3. Ad Group Report w/Labels\n")
            # "4. Gclid Report - TESTING")
        service_opt = input("Choose 1, 2, 3, or 4 ('exit' to exit): ")
        if service_opt == '1':
            # label_service_audit(client, customer_id)
            services.label_service_audit(client, customer_id=prop_id)
        elif service_opt == '2':
            # campaign_group_audit((client, customer_id)
            services.campaign_group_audit(client, customer_id=prop_id)
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
            services.ad_group_metrics_service_report(client, start_date, end_date, time_seg, customer_id=prop_id)
            # services.ad_group_metrics_service_report(client, time_condition, start_date, end_date, time_seg, customer_id=prop_id)
        elif service_opt == '4':
            services.click_view_metrics_report(client, customer_id=prop_id)
        else:
            print("Invalid input, please select one of the indicated options.")

# @helpers.handle_exceptions
def main():
    print("\nGoogle Ads Reporter, developed by JDT using GAds API and gRPC\n"
          "NOTE: Enter 'exit' at any prompt will exit this reporting tool.")
    input("Press Enter When Ready...")
    print(f"yaml loc: {yaml_loc}\n")
    prop_info = helpers.display_prop_list(prop_dict)
    prop_name, prop_id, prop_url = prop_info
    
    # debug constants info
    print(f"\nSelected prop info:\n"
          f"prop_name: {prop_name}\n"
          f"prop_id: {prop_id}\n"
          f"prop_url: {prop_url}")
    input("Pause for debug...")
    services_menu(prop_info)


if __name__ == '__main__':
    main()
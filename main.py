# -*- coding: utf-8 -*-

# IMPORTS
# standard
import sys
import time
import argparse
import json
# gads
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
# helpers
import auth
import helpers
import services

# MENUS
def init_menu(yaml_loc=None, accounts_path=None):
    print("\nGoogle Ads Reporter, developed by JDT using GAds API and gRPC\n"
          "NOTE: Enter 'exit' at any prompt will exit this reporting tool.")
    input("Press Enter When Ready...")
    # generate service
    print("Authorization in progress...")
    gads_service, customer_service, client = auth.generate_services(yaml_loc)
    print("Authorization complete!\n")

    # test and debug get_acccounts()
    try:
        customer_list, account_headers, customer_dict, num_accounts = services.get_accounts(gads_service, customer_service, client)
        print("\nAccount information retrieved successfully!\n"
              f"Number of accounts found: {num_accounts}\n")
        helpers.data_handling_options(table_data=customer_list, headers=account_headers)
    except GoogleAdsException as ex:
        print(f"Request with ID '{ex.request_id}' failed with status '{ex.error.code().name}'"
              f" and includes the following errors:\n")
        for error in ex.failure.errors:
            print(f"\tError with message '{error.message}'.")
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")
    input("\nPause for debug - press ENTER to continue or input 'exit' to exit")

    # check dict
    print(json.dumps(customer_dict, indent=2))
    input("\nPause for debug - press ENTER to continue or input 'exit' to exit")

    main_menu(gads_service, client, accounts_info=customer_dict)

def main_menu(gads_service, client, accounts_info):
    print("Main Menu - Select from the options below:\n"
          "1. ARC Reporting\n"
          "2. Auditing\n")
    data_scope = input("Choose a numbered option (1, 2, etc or 'exit' to exit): ")
    if data_scope == '1':
        print("ARC Reporting selected.")
        report_menu(gads_service, client, accounts_info)
    elif data_scope == '2':
        print("Auditing selected.")
        audit_menu(gads_service, client, accounts_info)
    else:
        print("Invalid input, please select one of the indicated numbered options.")
        # exit
        sys.exit(1)

def report_menu(gads_service, client, accounts_info):
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
    # single property ARC report
    if service_opt == '1':
        print("ARC Sales Report - Single Property selected...")
        account_info = helpers.get_account_properties(accounts_info)
        account_id, account_name = account_info
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
            gads_service, client, start_date, end_date, time_seg, customer_id=account_id)
        end_time = time.time()
        print(f"Report complied!\n"
              f"Execution time: {end_time - start_time:.2f} seconds\n")
        # handle data
        helpers.data_handling_options(table_data, headers)
    # all properties ARC report
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

        # start time
        start_time = time.time()
        all_account_data, headers = services.arc_sales_report_all(
            gads_service, client, start_date, end_date, time_seg, accounts_info)
        end_time = time.time()
        print(f"Report complied!\n"
              f"Execution time: {end_time - start_time:.2f} seconds\n")
        # handle data
        helpers.data_handling_options(all_account_data, headers)

    # elif service_opt == '4':
        # services.click_view_metrics_report(gads_service, client, customer_id=account_id)

    elif service_opt == 'x':
        services.test_query(gads_service, client, customer_id=account_id)
    else:
        print("Invalid input, please select one of the indicated options.")
        # exit
        sys.exit(1)

def audit_menu(gads_service, client, accounts_info):
    print("Auditing Options:\n"
        "1. Account Labels List\n"
        "2. Campaign Group List\n"
        "3. Campaign and Ad Group Label Assignments\n"
        "Or type 'exit' at any prompt to quit immediately.\n")
    service_opt = input("Choose 1, 2, 3, 4, etc ('exit' to exit): ")
    if service_opt == '1':
        print("Account Labels Only Audit selected...")
        account_info = helpers.get_account_properties(accounts_info)
        account_id, account_name = account_info

        # debug
        print(f"Account ID: {account_id}\n")
        input("\nPause for debug - press ENTER to continue or input 'exit' to exit")

        label_table, label_table_headers, label_dict = services.get_labels(gads_service, client, customer_id=account_id)
        # handle data
        helpers.data_handling_options(label_table, label_table_headers)
    elif service_opt == '2':
        print("Campaign Group Only Audit selected...")
        account_info = helpers.get_account_properties(accounts_info)
        account_id, account_name = account_info
        camp_group_table, camp_group_headers, camp_group_dict = services.get_campaign_groups(gads_service, client, customer_id=account_id)
        # handle data
        helpers.data_handling_options(camp_group_table, camp_group_headers)
    elif service_opt == '3':
        print("Campaign and Ad Group Label Assignments Audit selected...")
        account_info = helpers.get_account_properties(accounts_info)
        account_id, account_name = account_info
        # execute full report
        full_audit_table, full_audit_headers, full_audit_dict = services.complete_labels_audit(gads_service, client, customer_id=account_id)
        # handle data
        helpers.data_handling_options(full_audit_table, full_audit_headers)
    else:
        print("Invalid input, please select one of the indicated options.")

# @helpers.handle_exceptions
def main():
    parser = argparse.ArgumentParser(
        prog="GAR",
        description="Google Ads Reporter",
        epilog="Developed by Joe Thompson",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-y", "--yaml",
        help="Path to a YAML config file containing OAuth or Service Account credentials. If not provided, the default will be used.",
    )
    parser.add_argument(
        "-a", "--accounts",
        default="account_constants_example.py",
        help="Path to a account constants file containing 'ACCOUNTS_INFO' dictionary. If not provided, the program will exit.",
    )
    args=parser.parse_args()
    # normal user entry > auth then services
    accounts_path = None
    if args.accounts:
        try: 
            accounts_path = helpers.load_account_constants(args.accounts)
        except Exception as e:
            print(f"Error loading account constants file: {e}")
            sys.exit(1)
    init_menu(yaml_loc=args.yaml, accounts_path=args.accounts)

if __name__ == '__main__':
    main()
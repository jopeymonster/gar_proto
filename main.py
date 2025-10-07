# -*- coding: utf-8 -*-
import sys
import time
import argparse
import helpers
import services

# MENUS
def init_menu(yaml_loc=None):
    print("\nGoogle Ads Reporter, developed by JDT using GAds API and gRPC\n"
          "NOTE: Enter 'exit' at any prompt will exit this reporting tool.")
    input("Press Enter When Ready...")
    # generate service
    print("Authorization in progress...")
    gads_service, customer_service, client = services.generate_services(yaml_loc)
    print("Authorization complete!\n")
    print("Retrieving account information...")
    # get accounts
    full_accounts_info = services.get_accounts(gads_service, customer_service, client)
    customer_list, account_headers, customer_dict, num_accounts = full_accounts_info
    print("\nAccount information retrieved successfully!\n"
            f"Number of accounts found: {num_accounts}\n")
    helpers.data_handling_options(table_data=customer_list, headers=account_headers, auto_view=True)
    main_menu(gads_service, client, full_accounts_info)

def main_menu(gads_service, client, full_accounts_info):
    print("Main Menu - Select from the options below:\n"
          "1. Performance Reporting\n"
          "2. Account Auditing\n"
          "3. Budget Reporting\n")
    data_scope = input("Choose a numbered option (1, 2, etc or 'exit' to exit): ")
    if data_scope == '1':
        print("ARC Reporting selected.")
        report_menu(gads_service, client, full_accounts_info)
    elif data_scope == '2':
        print("Auditing selected.")
        audit_menu(gads_service, client, full_accounts_info)
    elif data_scope == '3':
        print("Budget Reporting selected.")
        budget_menu(gads_service, client, full_accounts_info)
    else:
        print("Invalid input, please select one of the indicated numbered options.")
        # exit
        sys.exit(1)

def report_menu(gads_service, client, full_accounts_info):
    customer_list, account_headers, customer_dict, num_accounts = full_accounts_info
    """
    full_accounts_info tuple:
        customer_list[0], list
        account_headers[1], list
        customer_dict[2], dict
        num_accounts[3], int
    """
    print("Reporting Options:\n"
        "1. ARC Report - Single Property\n"
        "2. ARC Report - All Properties\n"
        "3. Account Report - Single Property\n"
        "4. Account Report - All Properties\n"
        "5. Ads Report - Single Property\n"
        "6. Ads Report - All Properties\n"
        # "X. Test Query\n"
        "Or type 'exit' at any prompt to quit immediately.\n")
    service_opt = input("Choose 1, 2, 3, 4, etc ('exit' to exit): ").lower()
    # single property ARC report
    if service_opt == '1':
        print("ARC Report - Single Property selected...")
        account_info = helpers.get_account_properties(customer_dict) # parse single account info
        account_id, account_name = account_info # parse single accountID
        report_date_details = helpers.get_timerange()
        date_opt, start_date, end_date, time_seg = report_date_details
        include_channel_types = helpers.include_channel_types()

        # debug
        print("\nServices params passback after prompts:\n"
            f"date_opt: {date_opt}\n"
            f"time_seg: {time_seg}\n"
            f"start_date: {start_date}\n"
            f"end_date: {end_date}\n"
            f"include_channel_types: {include_channel_types}")
            # f"time_condition: {time_condition}")
        input("\nPause for debug - press ENTER to continue or input 'exit' to exit: ")

        # start time
        start_time = time.time()
        table_data, headers = services.arc_report_single(
            gads_service, client, start_date, end_date, time_seg, include_channel_types, customer_id=account_id) # pass single accountID
        end_time = time.time()
        print(f"Report compiled!\n"
              f"Execution time: {end_time - start_time:.2f} seconds\n")
        # handle data
        helpers.data_handling_options(table_data, headers, auto_view=False)
    # all properties ARC report
    elif service_opt == '2':
        print("ARC Report - All Properties selected.")
        report_date_details = helpers.get_timerange()
        date_opt, start_date, end_date, time_seg = report_date_details
        include_channel_types = helpers.include_channel_types()

        # debug
        print("\nServices params passback after prompts:\n"
            f"date_opt: {date_opt}\n"
            f"time_seg: {time_seg}\n"
            f"start_date: {start_date}\n"
            f"end_date: {end_date}\n"
            f"include_channel_types: {include_channel_types}")
            # f"time_condition: {time_condition}")
        input("\nPause for debug - press ENTER to continue or input 'exit' to exit: ")

        # start time
        start_time = time.time()
        all_account_data, headers = services.arc_report_all(
            gads_service, client, start_date, end_date, time_seg, include_channel_types, customer_dict) # pass all accounts
        end_time = time.time()
        print(f"Report compiled!\n"
              f"Execution time: {end_time - start_time:.2f} seconds\n")
        # handle data
        helpers.data_handling_options(all_account_data, headers, auto_view=False)
    elif service_opt == '3':
        print("Accounts Report - Single Property selected...")
        account_info = helpers.get_account_properties(customer_dict)
        account_id, account_name = account_info
        report_date_details = helpers.get_timerange()
        date_opt, start_date, end_date, time_seg = report_date_details

        # debug
        print("\nServices params passback after prompts:\n"
            f"date_opt: {date_opt}\n"
            f"time_seg: {time_seg}\n"
            f"start_date: {start_date}\n"
            f"end_date: {end_date}\n")
            # f"time_condition: {time_condition}")
        input("\nPause for debug - press ENTER to continue or input 'exit' to exit: ")

        # start time
        start_time = time.time()
        all_account_data, headers = services.account_report_single(
            gads_service, client, start_date, end_date, time_seg, customer_dict)
        end_time = time.time()
        print(f"Report compiled!\n"
              f"Execution time: {end_time - start_time:.2f} seconds\n")
        # handle data
        helpers.data_handling_options(all_account_data, headers, auto_view=False)
    elif service_opt == '4':
        print("Accounts Report - All Properties selected.")
        report_date_details = helpers.get_timerange()
        date_opt, start_date, end_date, time_seg = report_date_details

        # debug
        print("\nServices params passback after prompts:\n"
            f"date_opt: {date_opt}\n"
            f"time_seg: {time_seg}\n"
            f"start_date: {start_date}\n"
            f"end_date: {end_date}\n")
            # f"time_condition: {time_condition}")
        input("\nPause for debug - press ENTER to continue or input 'exit' to exit: ")

        # start time
        start_time = time.time()
        all_account_data, headers = services.account_report_all(
            gads_service, client, start_date, end_date, time_seg, customer_dict)
        end_time = time.time()
        print(f"Report compiled!\n"
              f"Execution time: {end_time - start_time:.2f} seconds\n")
        # handle data
        helpers.data_handling_options(all_account_data, headers, auto_view=False)
    elif service_opt =='5':
        print("Ads Report - Single Property selected.")
        account_info = helpers.get_account_properties(customer_dict) # parse single account info
        account_id, account_name = account_info # parse accountID
        report_date_details = helpers.get_timerange()
        date_opt, start_date, end_date, time_seg = report_date_details

        # debug
        print("\nServices params passback after prompts:\n"
            f"date_opt: {date_opt}\n"
            f"time_seg: {time_seg}\n"
            f"start_date: {start_date}\n"
            f"end_date: {end_date}\n")
            # f"time_condition: {time_condition}")
        input("\nPause for debug - press ENTER to continue or input 'exit' to exit: ")
        
        start_time = time.time()
        all_account_data, headers = services.ad_level_report_single(
            gads_service, client, start_date, end_date, time_seg, customer_id=account_id) # pass single accountID
        end_time = time.time()
        print(f"Report compiled!\n"
              f"Execution time: {end_time - start_time:.2f} seconds\n")
        # handle data
        helpers.data_handling_options(all_account_data, headers, auto_view=False)
    elif service_opt == '6':
        print("Ads Report - All Properties selected.")
        report_date_details = helpers.get_timerange()
        date_opt, start_date, end_date, time_seg = report_date_details

        # query testing
        print("\nServices params passback after get_timerange:\n"
            f"date_opt: {date_opt}\n"
            f"time_seg: {time_seg}\n"
            f"start_date: {start_date}\n"
            f"end_date: {end_date}\n")
            # f"time_condition: {time_condition}")
        input("\nPause for debug - press ENTER to continue or input 'exit' to exit: ")

        start_time = time.time()
        all_account_data, headers = services.ad_level_report_all(
            gads_service, client, start_date, end_date, time_seg, customer_dict) # pass all accounts
        end_time = time.time()
        print(f"Report compiled!\n"
              f"Execution time: {end_time - start_time:.2f} seconds\n")
        # handle data
        helpers.data_handling_options(all_account_data, headers, auto_view=False)

    # elif service_opt == '0':
        # services.click_view_metrics_report(gads_service, client, customer_id=account_id)

    elif service_opt == 'x':
        services.test_query(gads_service, client, customer_id=account_id)
    else:
        print("Invalid input, please select one of the indicated options.")
        # exit
        sys.exit(1)

def audit_menu(gads_service, client, full_accounts_info):
    customer_list, account_headers, customer_dict, num_accounts = full_accounts_info
    """
    full_accounts_info tuple:
        customer_list[0], list
        account_headers[1], list
        customer_dict[2], dict
        num_accounts[3], int
    """
    print("Auditing Options:\n"
        "1. Account Labels List\n"
        "2. Campaign Group List\n"
        "3. Campaign and Ad Group Label Assignments\n"
        "Or type 'exit' at any prompt to quit immediately.\n")
    service_opt = input("Choose 1, 2, 3, 4, etc ('exit' to exit): ")
    if service_opt == '1':
        print("Account Labels Only Audit selected...")
        account_info = helpers.get_account_properties(customer_dict)
        account_id, account_name = account_info

        # debug
        print(f"Account ID: {account_id}\n")
        input("\nPause for debug - press ENTER to continue or input 'exit' to exit: ")

        label_table, label_table_headers, label_dict = services.get_labels(gads_service, client, customer_id=account_id)
        # handle data
        helpers.data_handling_options(label_table, label_table_headers, auto_view=False)
    elif service_opt == '2':
        print("Campaign Group Only Audit selected...")
        account_info = helpers.get_account_properties(customer_dict)
        account_id, account_name = account_info
        camp_group_table, camp_group_headers, camp_group_dict = services.get_campaign_groups(gads_service, client, customer_id=account_id)
        # handle data
        helpers.data_handling_options(camp_group_table, camp_group_headers, auto_view=False)
    elif service_opt == '3':
        print("Campaign and Ad Group Label Assignments Audit selected...")
        account_info = helpers.get_account_properties(customer_dict)
        account_id, account_name = account_info
        # execute full report
        full_audit_table, full_audit_headers, full_audit_dict = services.complete_labels_audit(gads_service, client, customer_id=account_id)
        # handle data
        helpers.data_handling_options(full_audit_table, full_audit_headers, auto_view=False)
    else:
        print("Invalid input, please select one of the indicated options.")

def budget_menu(gads_service, client, full_accounts_info):
    print("Budget Options:\n"
          "1. Budget Report - Single Property\n"
          "2. Budget Report - All Properties\n"
          "Or type 'exit' at any prompt to quit immediately.\n")
    customer_list, account_headers, customer_dict, num_accounts = full_accounts_info
    """
    full_accounts_info tuple:
        customer_list[0], list
        account_headers[1], list
        customer_dict[2], dict
        num_accounts[3], int
    """

#@services.handle_exceptions
def main():
    parser = argparse.ArgumentParser(
        prog="GAR",
        description="Google Ads Reporter",
        epilog="Developed by Joe Thompson",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-y", "--yaml",
        help="Path to a YAML config file containing OAuth or Service Account credentials.",
    )
    args = parser.parse_args()
    init_menu(yaml_loc=args.yaml)

if __name__ == '__main__':
    main()